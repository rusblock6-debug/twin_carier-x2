import json
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from pydantic import ValidationError

from app.models import TrailTruckAssociation, TYPE_MODEL_MAP, validate_object_type
from app.forms import (
    BlastingSchema,
    TemplateMixin,
    TemplateRefMixin,
    RoadNetSchema,
    MapOverlaySchema,
    TYPE_SCHEMA_MAP,
    ObjectActionRequest
)
from app.services.blasting_service import CreateBlastingService
from app.services.planned_idle_service import CreatePlannedIdleService


# region DAO
class ObjectDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, model, obj_id: int):
        stmt = select(model).where(model.id == obj_id)
        return self.db.execute(stmt).scalar()

    def delete_scenario_associations(self, scenario_id: int):
        self.db.execute(
            delete(TrailTruckAssociation).where(
                TrailTruckAssociation.scenario_id == scenario_id
            )
        )

    def association_exists(self, scenario_id: int, trail_id: int, truck_id: int) -> bool:
        stmt = select(TrailTruckAssociation).where(
            TrailTruckAssociation.scenario_id == scenario_id,
            TrailTruckAssociation.trail_id == trail_id,
            TrailTruckAssociation.truck_id == truck_id,
        )
        return self.db.execute(stmt).scalar() is not None

    def create_association(self, scenario_id: int, trail_id: int, truck_id: int):
        assoc = TrailTruckAssociation(
            scenario_id=scenario_id,
            trail_id=trail_id,
            truck_id=truck_id,
        )
        self.db.add(assoc)
# endregion

# region Service
class ObjectService:
    def __init__(self, db: Session):
        self.db = db
        self.dao = ObjectDAO(db)

    def create_object(self, data: ObjectActionRequest):
        return self._dispatch(data, action="create")

    def update_object(self, obj_id: int, data: ObjectActionRequest):
        data.data["id"] = obj_id
        return self._dispatch(data, action="update")

    def _dispatch(self, data: ObjectActionRequest, action: str):
        if not data.data:
            raise HTTPException(status_code=400, detail="Invalid data")

        validate_object_type(data.type)

        schema_cls = TYPE_SCHEMA_MAP.get(data.type)
        model = TYPE_MODEL_MAP.get(data.type)

        if data.type == "scenario":
            service = ScenarioObjectService(self.db, self.dao, model, schema_cls)
        elif data.type in ("blasting", "planned_idle"):
            service = ScheduleObjectService(self.db, self.dao, model, schema_cls)
        else:
            service = GenericObjectService(self.db, self.dao, model, schema_cls)

        return service.process(data, action)

class BaseObjectService:
    def __init__(self, db: Session, dao: ObjectDAO, model, schema_cls):
        self.db = db
        self.dao = dao
        self.model = model
        self.schema_cls = schema_cls

    def _prepare_data(self, data: dict, action: str) -> dict:
        obj_data = data.copy()
        if action == "create":
            obj_data.pop("id", None)

        if "segments" in obj_data:
            obj_data["raw_graph"] = json.dumps(obj_data.get("segments", []))
            obj_data.pop("segments", None)
        return obj_data

    def _validate_form(self, obj_data: dict):
        try:
            return self.schema_cls(**obj_data)
        except ValidationError as exc:
            raise HTTPException(
                status_code=400,
                detail={"error": "Form validation failed", "errors": exc.errors()},
            )

    def _get_or_create(self, obj_id, action: str):
        if action == "update":
            if not obj_id:
                raise HTTPException(status_code=400, detail="Missing id for update")
            obj = self.dao.get_by_id(self.model, obj_id)
            if not obj:
                raise HTTPException(status_code=400, detail="Couldn't find object by id")
            return obj
        obj = self.model()
        self.db.add(obj)
        return obj

    def _apply_form(self, form, obj):
        data_dict = form.dict(exclude_unset=True)
        for field, value in data_dict.items():
            if field in ("id", "geojson_data", "geojson_points_data", "convert_overlay"):
                continue
            setattr(obj, field, value)


class GenericObjectService(BaseObjectService):
    def process(self, data: ObjectActionRequest, action: str):
        obj_data = self._prepare_data(data.data, action)

        form = self._validate_form(obj_data)

        obj = self._get_or_create(obj_data.get("id"), action)
        
        if isinstance(form, TemplateMixin):
            try:
                form.verify_template_bond_reversed(obj)
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        self._apply_form(form, obj)

        if isinstance(form, TemplateRefMixin):
            form.verify_template_bond(obj)

        if isinstance(form, RoadNetSchema):
            form.save_geojson_data(obj)

        if isinstance(form, MapOverlaySchema):
            form.convert_dxf(obj)

        self.db.commit()
        self.db.refresh(obj)

        return {"success": True, "id": obj.id}


class ScheduleObjectService(BaseObjectService):
    def process(self, data: ObjectActionRequest, action: str):
        obj_data = self._prepare_data(data.data, action)
        form = self._validate_form(obj_data)

        if action == "create":
            schedule_type = "blasting" if isinstance(form, BlastingSchema) else "planned_idle"

            if schedule_type == "blasting":
                service = CreateBlastingService(self.db)
                return service(form)
            else:
                service = CreatePlannedIdleService(self.db)
                return service(obj_data, self.model, schedule_type)

        obj = self._get_or_create(obj_data.get("id"), action)
        self._apply_form(form, obj)
        self.db.commit()
        self.db.refresh(obj)

        return {"success": True, "id": obj.id}


class ScenarioObjectService(BaseObjectService):
    def process(self, data: ObjectActionRequest, action: str):
        obj_data = self._prepare_data(data.data, action)
        form = self._validate_form(obj_data)
        obj = self._get_or_create(obj_data.get("id"), action)

        self._apply_form(form, obj)

        if "trails" in obj_data:
            if action == "update":
                self.dao.delete_scenario_associations(obj.id)

            for trail in obj_data["trails"]:
                trail_id = trail.get("id")
                for truck_id in trail.get("trucks", []):
                    if not self.dao.association_exists(obj.id, trail_id, truck_id):
                        self.dao.create_association(obj.id, trail_id, truck_id)

        if isinstance(form, TemplateRefMixin):
            form.verify_template_bond(obj)

        self.db.commit()
        self.db.refresh(obj)
        return {"success": True, "id": obj.id}
# endregion
