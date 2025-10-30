# app/services/quarry_data_service.py

from typing import List, Dict, Any, Tuple
import json

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, defer, selectinload

from app.models import (
    Quarry, Shovel, Truck, Unload, Trail,
    FuelStation, IdleArea, Scenario, MapOverlay,
    PlannedIdle, RoadNet
)

# region DTO
class QuarryDataDTO(BaseModel):
    """
    DTO, возвращаемый сервисом — содержит список карьеров в виде словарей.
    """
    quarry_list: List[Dict[str, Any]]
# endregion

# region DAO
class QuarryDAO:
    def __init__(self, db_session: Session):
        self.db = db_session

    def fetch_all(self, model) -> List:
        """
        Универсальный fetch для простых моделей: select(model).order_by(model.id.asc()).
        Возвращает список экземпляров модели.
        """
        stmt = select(model).order_by(model.id.asc())
        return self.db.execute(stmt).scalars().all()

    def fetch_roadnet_id_pairs(self) -> List[Tuple[int, int]]:
        """
        Возвращает список (roadnet.id, roadnet.quarry_id) упорядоченных по id ASC.
        """
        stmt = select(RoadNet.id, RoadNet.quarry_id).order_by(RoadNet.id.asc())
        return self.db.execute(stmt).all()

    def fetch_map_overlays_deferred_geojson(self) -> List:
        """
        Возвращает MapOverlay без подгрузки большого поля geojson_data.
        """
        stmt = select(MapOverlay).order_by(MapOverlay.id.asc()).options(defer(MapOverlay.geojson_data))
        return self.db.execute(stmt).scalars().all()

    def fetch_trails_with_quarry_id(self) -> List[Tuple["Trail", int]]:
        """
        Возвращает список кортежей (Trail, quarry_id) — делается join через Shovel.
        Также подгружаем associations (selectinload).
        """
        stmt = (
            select(Trail, Shovel.quarry_id)
            .join(Shovel, Trail.shovel_id == Shovel.id)
            .options(selectinload(Trail.truck_associations))
            .order_by(Trail.id.asc())
        )
        return self.db.execute(stmt).all()
# endregion

# region Service
class QuarryDataService:
    """
    Сервис, собирающий всю необходимую информацию по карьерам.
    Возвращает QuarryDataDTO — связи с роутером происходят через DTO.
    Внутри — DAO для запросов к БД.
    """

    # Модели, по которым просто собираются списки (используются в _load_related_models)
    SIMPLE_RELATED_MODELS = (
        Shovel, Truck, Unload, FuelStation, IdleArea, Scenario, PlannedIdle
    )
    # Модели, для которых создаём пустые списки при инициализации quarry
    ALL_RELATION_MODELS = (
        Shovel, Truck, Unload, Trail, FuelStation, IdleArea, Scenario, MapOverlay, PlannedIdle
    )

    def __init__(self, db_session: Session):
        self.dao = QuarryDAO(db_session)

    @staticmethod
    def _model_to_dict(model, instance) -> Dict[str, Any]:
        """
        Преобразовать экземпляр модели в словарь по колонкам таблицы.
        """
        column_names = [col.name for col in model.__table__.columns]
        return {col_name: getattr(instance, col_name) for col_name in column_names}

    def __call__(self) -> QuarryDataDTO:
        """
        Выполнить сбор всей информации и вернуть QuarryDataDTO.
        """
        quarry_map: Dict[int, Dict[str, Any]] = {}

        # 1) Инициализация карьеров (основные поля + пустые списки для связей)
        self._init_quarries(quarry_map)

        # 2) Простые связанные модели (Shovel, Truck, ... PlannedIdle)
        self._load_related_models(quarry_map)

        # 3) RoadNet — присваиваем первый найденный roadnet.id для quarry
        self._apply_roadnet(quarry_map)

        # 4) MapOverlay — без поля geojson_data
        self._load_map_overlays(quarry_map)

        # 5) Trail — special processing (raw_graph -> segments, truck associations)
        self._load_trails(quarry_map)

        # Собираем результат в DTO
        dto = QuarryDataDTO(quarry_list=list(quarry_map.values()))
        return dto

    def _init_quarries(self, quarry_map: Dict[int, Dict[str, Any]]):
        """
        Создаёт запись в quarry_map для каждого Quarry: копирует все колонки таблицы
        и создаёт пустые списки для связанных коллекций.
        """
        quarry_cols = [col.name for col in Quarry.__table__.columns]
        quarry_instances = self.dao.fetch_all(Quarry)
        road_net_key_name = f'{RoadNet.__tablename__}_id'

        for quarry in quarry_instances:
            qdict = {col_name: getattr(quarry, col_name) for col_name in quarry_cols}
            # создаём пустые списки для связей
            for model in self.ALL_RELATION_MODELS:
                qdict[f'{model.__tablename__}_list'] = []
            qdict[road_net_key_name] = None
            quarry_map[quarry.id] = qdict

    def _load_related_models(self, quarry_map: Dict[int, Dict[str, Any]]):
        """
        Загружает простые связанные сущности (без специальных преобразований).
        """
        for model in self.SIMPLE_RELATED_MODELS:
            model_key_name = f'{model.__tablename__}_list'
            instances = self.dao.fetch_all(model)
            model_cols = [col.name for col in model.__table__.columns]

            for inst in instances:
                quarry_id = getattr(inst, "quarry_id", None)
                if quarry_id is None or quarry_id not in quarry_map:
                    continue
                item = {col: getattr(inst, col) for col in model_cols}
                quarry_map[quarry_id][model_key_name].append(item)

    def _apply_roadnet(self, quarry_map: Dict[int, Dict[str, Any]]):
        """
        Устанавливает первую встреченную roadnet.id для каждого карьера (roadnet_id).
        """
        road_net_key_name = f'{RoadNet.__tablename__}_id'
        pairs = self.dao.fetch_roadnet_id_pairs()
        for rn_id, quarry_id in pairs:
            if quarry_id not in quarry_map:
                continue
            quarry_map[quarry_id][road_net_key_name] = quarry_map[quarry_id][road_net_key_name] or rn_id

    def _load_map_overlays(self, quarry_map: Dict[int, Dict[str, Any]]):
        """
        Загружает MapOverlay без поля geojson_data.
        """
        mo_instances = self.dao.fetch_map_overlays_deferred_geojson()
        mo_cols = [col.name for col in MapOverlay.__table__.columns]
        key_name = f'{MapOverlay.__tablename__}_list'

        for mo in mo_instances:
            quarry_id = getattr(mo, "quarry_id", None)
            if quarry_id is None or quarry_id not in quarry_map:
                continue
            item = {col: getattr(mo, col) for col in mo_cols if col != 'geojson_data'}
            quarry_map[quarry_id][key_name].append(item)

    def _load_trails(self, quarry_map: Dict[int, Dict[str, Any]]):
        """
        Загружает Trail c преобразованием raw_graph -> segments и сбором truck_associations.
        DAO возвращает [(Trail, quarry_id), ...]
        """
        trail_key_name = f'{Trail.__tablename__}_list'
        trail_rows = self.dao.fetch_trails_with_quarry_id()

        for trail, quarry_id in trail_rows:
            if quarry_id not in quarry_map:
                continue
            # raw_graph -> segments (обработка ошибок JSON)
            segments = []
            raw = getattr(trail, 'raw_graph', None)
            if raw:
                try:
                    segments = json.loads(raw)
                except json.decoder.JSONDecodeError:
                    segments = []

            # truck associations -> список id грузовиков
            trucks = [assoc.truck_id for assoc in getattr(trail, "truck_associations", [])]

            trail_dict = {
                'id': trail.id,
                'quarry_id': quarry_id,
                'trail_type': trail.trail_type,
                'shovel_id': trail.shovel_id,
                'unload_id': trail.unload_id,
                'segments': segments,
                'trucks': trucks
            }
            quarry_map[quarry_id][trail_key_name].append(trail_dict)
# endregion
