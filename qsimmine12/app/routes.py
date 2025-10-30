# region LibsImports
import json
import os
import pathlib
import uuid
from datetime import datetime, timedelta
from operator import itemgetter
from zoneinfo import ZoneInfo
from typing import Optional, List, Dict, Any

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    UploadFile, 
    File, 
    Form,
    Request,
)
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError
# endregion

# region AppImports
from app import get_db, get_redis
from app.consts import STORED_RESULTS_NUMBER
from app.forms import (
    BlastingSchema,
    PlannedIdleSchema,
)
from app.models import (
    TYPE_MODEL_MAP,
    TYPE_SCHEDULE_MAP,
    DefaultValuesMixin,
    MapOverlay,
    RoadNet,
    UploadedFile,
    validate_schedule_type,
)

from app.forms import ObjectActionRequest
from app.services.date_time_service import StartEndTimeGenerateService
from app.services.template_service import AllTemplatesListService
from app.services.quarry_data_service import QuarryDataService
from app.services.schedule_data_service import ScheduleDataService, ScheduleDataResponseDTO
from app.services.scenario_service import ScenarioService, ScenarioDTO
from app.services.object_service import ObjectService
from app.services.simulation_id_service import GetSimIdService, SimulationRequestDTO

from app.shift import ShiftConfigDataException, ShiftConfigParseException
from app.sim_engine.writer import BatchWriter
from app.simulate_test import generate_simulation_data
from app.sim_engine.simulation_manager import SimulationManager
from app.utils import secure_filename
# endregion

router = APIRouter()

# region Pydantic models
class TimeRange(BaseModel):
    start_time: str
    end_time: str

class QuarryDataResponse(BaseModel):
    time: TimeRange
    templates: Dict[str, List[Dict]]
    quarry_list: List[Dict]

class UpdateLocationRequest(BaseModel):
    object_db_id: int
    object_type: str
    lat: float
    lon: float

class DeleteObjectRequest(BaseModel):
    type: str
    id: int

class ScheduleDataRequest(BaseModel):
    date: str
    quarry_id: int
    type: str
    shift_number: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
# endregion Pydantic models


# region planning
@router.get("/handbook", response_class=HTMLResponse)
async def index(request: Request):
    return FileResponse("static/index.html")

@router.get("/api/quarry-data", response_model=QuarryDataResponse)
async def quarry_data(db: Session = Depends(get_db)):
    time = StartEndTimeGenerateService()().model_dump(mode="json")
    templates = AllTemplatesListService(db_session=db)().model_dump()
    all_quarry_data = QuarryDataService(db_session=db)().model_dump(mode="json")

    result_dict = {
        "time": time,
        "templates": templates,
        **all_quarry_data
    }

    return result_dict

@router.get("/api/schedule-data-by-date-shift", response_model=ScheduleDataResponseDTO)
async def schedule_data_by_date_shift(
    date: str,
    quarry_id: int,
    type: str = Depends(validate_schedule_type),
    shift_number: Optional[int] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    db=Depends(get_db),
):
    model = TYPE_SCHEDULE_MAP[type]

    enterprise_tz = ZoneInfo(os.getenv("TZ", "UTC"))
    try:
        service = ScheduleDataService(db)
        dto = service(
            model=model,
            date_str=date,
            quarry_id=quarry_id,
            schedule_type=type,
            enterprise_tz=enterprise_tz,
            shift_number=shift_number,
            start_time=start_time,
            end_time=end_time,
        )
        return dto
    except (ShiftConfigDataException, ShiftConfigParseException) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/update-location")
async def update_location(data: UpdateLocationRequest, db: Session = Depends(get_db)):
    model = TYPE_MODEL_MAP.get(data.object_type)
    if not model:
        raise HTTPException(status_code=400, detail='Invalid object type')

    obj = db.execute(select(model).where(model.id == data.object_db_id)).scalar()
    if not obj:
        raise HTTPException(status_code=404, detail='Object not found')

    obj.initial_lat = data.lat
    obj.initial_lon = data.lon

    db.commit()

    return {'success': True, 'id': obj.id, 'lat': obj.initial_lat, 'lon': obj.initial_lon}

@router.get("/api/scenarios", response_model=List[ScenarioDTO])
async def get_scenarios(db: Session = Depends(get_db)):
    scenarios = ScenarioService(db)()
    return scenarios

@router.get("/api/road-net/{rn_id}")
async def get_road_net(rn_id: int, db: Session = Depends(get_db)):
    rn = db.execute(select(RoadNet).where(RoadNet.id == rn_id)).scalar()
    if not rn:
        raise HTTPException(status_code=404, detail='Road net not found')
    return rn.geojson_data

@router.get("/api/defaults")
async def defaults_data():
    defaults_dict = DefaultValuesMixin.collect_default_values_of_all_models()
    return defaults_dict

@router.post("/api/object", status_code=201)
async def create_object(data: ObjectActionRequest, db: Session = Depends(get_db)):
    """
    Создание объекта (ранее action == 'create')
    """
    service = ObjectService(db)
    try:
        if data.action == "update":
            obj_id = data.data.get('id')
            result = service.update_object(obj_id, data)
        else:
            result = service.create_object(data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/object/{obj_id}")
async def update_object(obj_id: int, data: ObjectActionRequest, db: Session = Depends(get_db)):
    """
    Обновление объекта (ранее action == 'update')
    """
    service = ObjectService(db)
    try:
        result = service.update_object(obj_id, data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/object")
async def delete_object(data: DeleteObjectRequest, db: Session = Depends(get_db)):
    # For schedule types (blasting, planned_idle) call schedule delete helpers
    if data.type == 'blasting':
        try:
            form = BlastingSchema(**data.dict())
        except ValidationError:
            # We only need the schedule-delete behavior; instantiate minimally
            form = BlastingSchema()
        return form.handle_schedule_delete(data.dict(), TYPE_SCHEDULE_MAP.get('blasting'), 'blasting')

    if data.type == 'planned_idle':
        try:
            form = PlannedIdleSchema(**data.dict())
        except ValidationError:
            form = PlannedIdleSchema()
        return form.handle_schedule_delete(data.dict(), TYPE_SCHEDULE_MAP.get('planned_idle'), 'planned_idle')

    model = TYPE_MODEL_MAP.get(data.type)
    if not model:
        raise HTTPException(status_code=400, detail='Invalid type')

    if issubclass(model, MapOverlay):
        obj = db.execute(
            select(model).where(model.id == data.id)
        ).scalar()
        if obj is None:
            raise HTTPException(status_code=400, detail='Couldn\'t find object by given id')
        db.delete(obj)
        if obj.source_file_id:
            UploadedFile.delete_with_file(db, obj.source_file_id)
    else:
        deleted_id = db.execute(
            delete(model).where(model.id == data.id).returning(model.id)
        ).scalar()
        if deleted_id is None:
            raise HTTPException(status_code=400, detail='Couldn\'t find object by given id')

    db.commit()
    return {'success': True}
# endregion planning

# region simulation
@router.post("/run-simulation")
async def run_simulation(
    data: SimulationRequestDTO,
    db: Session = Depends(get_db),
    redis_client=Depends(get_redis),
):
    sim_id = await GetSimIdService(data, db, redis_client)()
    return RedirectResponse(url=f"/simulation_view/{sim_id}", status_code=303)

@router.post("/api/run-simulation")
async def api_run_simulation(
    data: SimulationRequestDTO,
    db: Session = Depends(get_db),
    redis_client=Depends(get_redis),
):
    try:
        sim_id = await GetSimIdService(data, db, redis_client)()
        return {"sim_id": sim_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error {type(e)}: {e}")

@router.get("/api/simulation/{sim_id}/meta")
async def get_simulation_meta(sim_id: str, redis_client=Depends(get_redis)):
    key = next(redis_client.scan_iter(f'simulation:*:{sim_id}:meta', 1), None)
    if not key:
        raise HTTPException(status_code=404, detail='Simulation not found')
    
    meta_json = redis_client.get(key)
    if not meta_json:
        raise HTTPException(status_code=404, detail='Simulation not found')
        
    return json.loads(meta_json)

@router.get("/api/simulation/{sim_id}/batch/{batch_index}")
async def get_simulation_batch(sim_id: str, batch_index: int, redis_client=Depends(get_redis)):
    key = next(redis_client.scan_iter(f'simulation:*:{sim_id}:batch:{batch_index}', 1), None)
    if not key:
        raise HTTPException(status_code=404, detail='Batch not found')
        
    batch_data = redis_client.get(key)
    if not batch_data:
        raise HTTPException(status_code=404, detail='Batch not found')
        
    return json.loads(batch_data)

@router.get("/api/simulation/{sim_id}/batches")
async def get_simulation_batches(sim_id: str, indices: List[int] = None, redis_client=Depends(get_redis)):
    if not indices:
        raise HTTPException(status_code=400, detail='No indices provided')
        
    meta_key = next(redis_client.scan_iter(f'simulation:*:{sim_id}:meta', 1), None)
    if not meta_key:
        raise HTTPException(status_code=404, detail='Batches not found')

    base_sim_key = meta_key.replace(':meta', '')
    batch_keys = [
        f'{base_sim_key}:batch:{idx}'
        for idx in indices
    ]

    batches = []
    batch_vals = redis_client.mget(batch_keys)
    batches.extend([json.loads(val) for val in batch_vals if val])

    return {"batches": batches}

@router.get("/api/simulation/{sim_id}/summary")
async def get_simulation_summary(sim_id: str, redis_client=Depends(get_redis)):
    key = next(redis_client.scan_iter(f'simulation:*:{sim_id}:summary', 1), None)
    if not key:
        raise HTTPException(status_code=404, detail='Summary not found')
        
    summary_data = redis_client.get(key)
    if not summary_data:
        raise HTTPException(status_code=404, detail='Summary not found')
        
    return json.loads(summary_data)

@router.get("/api/simulation/{sim_id}/events")
async def get_simulation_events(sim_id: str, redis_client=Depends(get_redis)):
    key = next(redis_client.scan_iter(f'simulation:*:{sim_id}:events', 1), None)
    if not key:
        raise HTTPException(status_code=404, detail='Events not found')
        
    events_data = redis_client.get(key)
    if not events_data:
        raise HTTPException(status_code=404, detail='Events not found')
        
    return json.loads(events_data)
# endregion simulation

# region Uploaded file
@router.get("/api/file/{id_or_name}")
async def handle_file_get(id_or_name: str, db: Session = Depends(get_db)):
    file_name = id_or_name
    try:
        file_id = int(id_or_name)
    except ValueError:
        file_id = None

    if file_id:
        where_expr = UploadedFile.id == file_id
    else:
        where_expr = UploadedFile.name == file_name
        
    uf = db.execute(select(UploadedFile).where(where_expr)).scalar()
    if uf is None:
        raise HTTPException(status_code=400, detail='Couldn\'t find file record by given id or name')

    return {
        'id': uf.id,
        'name': uf.name,
        'path': uf.path,
        'size': uf.size,
        'created_at': uf.created_at.isoformat(),
        'url': f"/upload/{uf.name}",
    }

@router.post("/api/file")
async def handle_file_post(
    request: Request,
    file: UploadFile = File(...),
    name: str = Form(None),
    db: Session = Depends(get_db)
):
    upload_folder = pathlib.Path(request.app.state.config['UPLOAD_FOLDER'])

    save_name = secure_filename(name or file.filename, allow_unicode=True)
    save_path = upload_folder / save_name
    save_path_orig = save_path

    i = 1
    while save_path.exists() and i < 1000:
        str_i = str(i)
        str_i = '0' * (3 - len(str_i)) + str_i
        save_path = save_path_orig.with_stem(f'{save_path_orig.stem}_{str_i}')
        i += 1

    with open(save_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    try:
        uf = UploadedFile(
            name=save_path.name,
            path=str(save_path),
            size=save_path.stat().st_size
        )
        db.add(uf)
        db.commit()
    except Exception:
        save_path.unlink()
        raise

    return {
        'success': True,
        'file': {
            'id': uf.id,
            'name': uf.name,
            'url': f"/upload/{uf.name}",
        }
    }

@router.delete("/api/file/{id_or_name}")
async def handle_file_delete(id_or_name: str, db: Session = Depends(get_db)):
    file_name = id_or_name
    try:
        file_id = int(id_or_name)
    except ValueError:
        file_id = None

    result = UploadedFile.delete_with_file(db, file_id, file_name)
    if not result:
        raise HTTPException(status_code=400, detail='Couldn\'t find file record by given id or name')

    db.commit()
    return {'success': True}

@router.get("/upload/{filename:path}")
async def uploaded_file_route(filename: str, request: Request):
    upload_dir = pathlib.Path(request.app.state.config['UPLOAD_FOLDER']).resolve()
    return FileResponse(upload_dir / filename)

@router.get("/api/map-overlay/{mo_id}")
async def get_map_overlay(mo_id: int, db: Session = Depends(get_db)):
    mo = db.execute(select(MapOverlay).where(MapOverlay.id == mo_id)).scalar()
    if not mo:
        raise HTTPException(status_code=404, detail='Map overlay not found')

    return {
        'success': True,
        'id': mo.id,
        'name': mo.name,
        'created_at': mo.created_at.isoformat(),
        'updated_at': mo.updated_at.isoformat(),
        'is_active': mo.is_active,
        'quarry_id': mo.quarry_id,
        'source_file_id': mo.source_file_id,
        'anchor_lat': mo.anchor_lat,
        'anchor_lon': mo.anchor_lon,
        'anchor_height': mo.anchor_height,
        'color': mo.color,
        'geojson_data': mo.geojson_data,
    }
# endregion Uploaded file
