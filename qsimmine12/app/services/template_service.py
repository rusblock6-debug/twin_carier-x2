from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.forms import ShovelTemplate, TruckTemplate, UnloadTemplate, FuelStationTemplate

# region DTO
class AllTemplatesDTO(BaseModel):
    shovel_template_list: List[Dict[str, Any]]
    truck_template_list: List[Dict[str, Any]]
    unload_template_list: List[Dict[str, Any]]
    fuel_station_template_list: List[Dict[str, Any]]
# endregion

# region DTO
class TemplateDAO:
    """
    DAO для получения моделей из БД.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def fetch_all(self, model) -> List:
        """
        Вернуть все строки модели, упорядоченные по id ASC.
        """
        stmt = select(model).order_by(model.id.asc())
        result = self.db.execute(stmt).scalars().all()
        return result
# endregion

# region Service
class AllTemplatesListService:
    """
    Собирает все шаблоны в словарь списков и возвращает DTO.
    """

    # Явно перечисляем модели и соответствующие поля DTO
    TEMPLATES = [
        (ShovelTemplate, "shovel_template_list"),
        (TruckTemplate, "truck_template_list"),
        (UnloadTemplate, "unload_template_list"),
        (FuelStationTemplate, "fuel_station_template_list"),
    ]

    def __init__(self, db_session: Session):
        self.dao = TemplateDAO(db_session)

    @staticmethod
    def _model_to_dict_list(model, instances: List) -> List[Dict[str, Any]]:
        """
        Преобразование модели в List[Dict].
        """

        column_names = [col.name for col in model.__table__.columns]
        return [
            {col_name: getattr(inst, col_name) for col_name in column_names}
            for inst in instances
        ]

    def _generate_templates_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Генерация словаря для шаблонов.
        """
        result: Dict[str, List[Dict[str, Any]]] = {}
        for model, dto_field in self.TEMPLATES:
            instances = self.dao.fetch_all(model)
            result[dto_field] = self._model_to_dict_list(model, instances)
        return result

    def __call__(self) -> AllTemplatesDTO:
        templates_dict = self._generate_templates_dict()

        dto_payload = {
            "shovel_template_list": templates_dict.get("shovel_template_list", []),
            "truck_template_list": templates_dict.get("truck_template_list", []),
            "unload_template_list": templates_dict.get("unload_template_list", []),
            "fuel_station_template_list": templates_dict.get("fuel_station_template_list", []),
        }

        return AllTemplatesDTO(**dto_payload)
# endregion
