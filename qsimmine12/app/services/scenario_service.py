from typing import List, Dict, Any, Optional
import json

from pydantic import BaseModel
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.models import Scenario, Trail, Shovel


# region DTO
class TrailDTO(BaseModel):
    id: int
    trail_type: str | None
    shovel_id: int | None
    unload_id: int | None
    segments: List[Any]
    trucks: List[int]

class ScenarioDTO(BaseModel):
    id: int
    name: str | None
    start_time: datetime | None
    end_time: datetime | None
    quarry_id: int | None
    is_auto_truck_distribution: bool | None
    is_calc_reliability_enabled: bool | None
    solver_type: int | None
    trails: List[TrailDTO]
# endregion

# region DAO
class ScenarioDAO:
    def __init__(self, db_session: Session):
        self.db = db_session

    def fetch_all_with_assocs(self) -> List[Scenario]:
        """
        Возвращает все Scenario.
        """
        stmt = (
            select(Scenario)
            .options(
                selectinload(Scenario.truck_associations),
                selectinload(Scenario.quarry)
            )
            .order_by(Scenario.id.asc())
        )
        return self.db.execute(stmt).scalars().all()

    def fetch_trails_by_quarry(self, quarry_id: int) -> List[Trail]:
        """
        Возвращает Trail, принадлежащие карьерам quarry_id (через Shovel).
        """
        stmt = (
            select(Trail)
            .join(Shovel, Trail.shovel_id == Shovel.id)
            .where(Shovel.quarry_id == quarry_id)
            .options(selectinload(Trail.truck_associations))
            .order_by(Trail.id.asc())
        )
        return self.db.execute(stmt).scalars().all()
# endregion

# region Service
class ScenarioService:
    def __init__(self, db_session: Session):
        self.dao = ScenarioDAO(db_session)

    def __call__(self) -> List[ScenarioDTO]:
        scenarios = self.dao.fetch_all_with_assocs()
        return [self._scenario_to_dto(scenario) for scenario in scenarios]

    def _scenario_to_dto(self, scenario) -> ScenarioDTO:
        assoc_by_trail = self._build_assoc_map(scenario)
        trails = self._load_and_transform_trails(scenario.quarry_id, assoc_by_trail)

        return ScenarioDTO(
            id=scenario.id,
            name=scenario.name,
            start_time=getattr(scenario, "start_time", None),
            end_time=getattr(scenario, "end_time", None),
            quarry_id=getattr(scenario, "quarry_id", None),
            is_auto_truck_distribution=getattr(scenario, "is_auto_truck_distribution", None),
            is_calc_reliability_enabled=getattr(scenario, "is_calc_reliability_enabled", None),
            solver_type=getattr(scenario, "solver_type", None),
            trails=trails
        )

    def _build_assoc_map(self, scenario) -> Dict[int, List[int]]:
        assoc_by_trail: Dict[int, List[int]] = {}
        for assoc in getattr(scenario, "truck_associations", []) or []:
            trail_id = getattr(assoc, "trail_id", None)
            truck_id = getattr(assoc, "truck_id", None)
            if trail_id is None or truck_id is None:
                continue
            assoc_by_trail.setdefault(trail_id, []).append(truck_id)
        return assoc_by_trail

    def _load_and_transform_trails(
        self,
        quarry_id: Optional[int],
        assoc_by_trail: Dict[int, List[int]]
    ) -> List[TrailDTO]:
        if quarry_id is None:
            return []

        trail_objs: List[Trail] = self.dao.fetch_trails_by_quarry(quarry_id)
        trails_dto: List[TrailDTO] = [
            self._trail_to_dto(trail, assoc_by_trail) for trail in trail_objs
        ]
        return trails_dto

    def _trail_to_dto(self, trail, assoc_by_trail: Dict[int, List[int]]) -> TrailDTO:
        segments = self._parse_segments(getattr(trail, "raw_graph", None))
        trucks_in_scenario = assoc_by_trail.get(getattr(trail, "id"), [])

        return TrailDTO(
            id=trail.id,
            trail_type=trail.trail_type,
            shovel_id=trail.shovel_id,
            unload_id=trail.unload_id,
            segments=segments,
            trucks=trucks_in_scenario
        )

    @staticmethod
    def _parse_segments(raw_graph: Optional[str]) -> List[Any]:
        if not raw_graph:
            return []

        try:
            parsed = json.loads(raw_graph)
            return parsed if isinstance(parsed, list) else []
        except json.decoder.JSONDecodeError:
            return []
# endregion
