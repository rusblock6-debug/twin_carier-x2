#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер потоков данных для бизнес-аналитиков и продуктовых менеджеров.
Отслеживает движение данных от момента ввода пользователем до сохранения результатов моделирования.
"""

import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict


class BusinessDataFlowParser:
    """Парсер потоков данных для бизнес-аналитиков."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.business_entities: Dict[str, Dict] = {}  # Бизнес-сущности (Экскаватор, Самосвал и т.д.)
        self.data_flows: List[Dict] = []  # Потоки данных между сущностями
        self.parameters: Dict[str, Dict] = {}  # Параметры (характеристики экскаватора и т.д.)
        self.parameter_dependencies: Dict[str, List[str]] = defaultdict(list)  # Зависимости параметров
        self.layer_definitions = {
            "Ввод данных": "Пользовательский ввод и интерфейсы",
            "Параметры": "Характеристики техники и объектов",
            "Валидация": "Проверка и нормализация данных",
            "Модели данных": "Логические модели и ORM",
            "Хранение": "База данных и постоянные хранилища",
            "Сервис симуляции": "Оркестрация подготовки к запуску",
            "Сериализация": "Трансформация данных под движок симуляции",
            "Симуляция": "Исполнение сценария и управление событиями",
            "Расчеты": "Формулы эффективности и KPI",
            "Результаты": "Хранилища отчетов/телеметрии",
            "Техника": "Подвижные объекты карьера",
            "Инфраструктура": "Статические объекты и карта",
            "Конфигурация": "Сценарии, ограничения и настройки",
            "Событие": "Расписания, взрывы, простои"
        }
        self.business_model_catalog = {
            'Shovel': {'name': 'Экскаватор', 'icon': '🔧', 'category': 'Техника', 'detail_layer': 'Техника · Экскаваторы'},
            'Truck': {'name': 'Самосвал', 'icon': '🚛', 'category': 'Техника', 'detail_layer': 'Техника · Самосвалы'},
            'FuelStation': {'name': 'Заправка', 'icon': '⛽', 'category': 'Инфраструктура', 'detail_layer': 'Инфраструктура · Заправки'},
            'Unload': {'name': 'Пункт разгрузки', 'icon': '📍', 'category': 'Инфраструктура', 'detail_layer': 'Инфраструктура · Пункты разгрузки'},
            'RoadNet': {'name': 'Дорожная сеть', 'icon': '🛣️', 'category': 'Инфраструктура', 'detail_layer': 'Инфраструктура · Дороги'},
            'Trail': {'name': 'Маршрут', 'icon': '🛤️', 'category': 'Инфраструктура', 'detail_layer': 'Инфраструктура · Маршруты'},
            'IdleArea': {'name': 'Зона ожидания', 'icon': '⏸️', 'category': 'Инфраструктура', 'detail_layer': 'Инфраструктура · Зоны ожидания'},
            'MapOverlay': {'name': 'Слой карты', 'icon': '🗺️', 'category': 'Инфраструктура', 'detail_layer': 'Инфраструктура · Слои карты'},
            'Quarry': {'name': 'Карьер', 'icon': '🏭', 'category': 'Объект', 'detail_layer': 'Объект · Карьеры'},
            'Scenario': {'name': 'Сценарий', 'icon': '📋', 'category': 'Конфигурация', 'detail_layer': 'Конфигурация · Сценарии'},
            'Blasting': {'name': 'Взрывные работы', 'icon': '💥', 'category': 'Событие', 'detail_layer': 'События · Взрывы'},
            'PlannedIdle': {'name': 'Плановый простой', 'icon': '⏸️', 'category': 'Событие', 'detail_layer': 'События · Простоя'},
            'FuelStationTemplate': {'name': 'Шаблон заправки', 'icon': '🧩', 'category': 'Шаблоны', 'detail_layer': 'Шаблоны · Заправки'},
            'ShovelTemplate': {'name': 'Шаблон экскаватора', 'icon': '🧩', 'category': 'Шаблоны', 'detail_layer': 'Шаблоны · Экскаваторы'},
            'TruckTemplate': {'name': 'Шаблон самосвала', 'icon': '🧩', 'category': 'Шаблоны', 'detail_layer': 'Шаблоны · Самосвалы'},
            'UnloadTemplate': {'name': 'Шаблон разгрузки', 'icon': '🧩', 'category': 'Шаблоны', 'detail_layer': 'Шаблоны · Пункты разгрузки'},
            'TrailTruckAssociation': {'name': 'Связь маршрут-самосвал', 'icon': '🔗', 'category': 'Техника', 'detail_layer': 'Техника · Привязки'},
            'UploadedFile': {'name': 'Загруженный файл', 'icon': '📁', 'category': 'Данные', 'detail_layer': 'Данные · Файлы'}
        }
        self.formula_library = {
            "entity:Shovel": {
                "text": "Производительность = Объем ковша × Коэффициент наполнения × Ходок/час",
                "source": {
                    "file": "app/sim_engine/core/calculations/shovel.py",
                    "pattern": "def calculate_cycle"
                }
            },
            "entity:Truck": {
                "text": "Время рейса = (Расстояние туда / Скорость груженого) + (Расстояние обратно / Скорость порожнего)",
                "source": {
                    "file": "app/sim_engine/core/calculations/truck.py",
                    "pattern": "calculate_time_motion_by_edges"
                }
            },
            "entity:Unload": {
                "text": "Пропускная способность = Кол-во позиций × 60 / Время разгрузки",
                "source": {
                    "file": "app/sim_engine/core/calculations/unload.py",
                    "pattern": "total_time"
                }
            },
            "entity:FuelStation": {
                "text": "Время заправки = Объем дозаправки / Скорость подачи топлива",
                "source": {
                    "file": "app/sim_engine/core/simulations/fuel_station.py",
                    "pattern": "refuel_time"
                }
            },
            "simulation_core": {
                "text": "Цикл симуляции = Σ (время перемещения + загрузки + разгрузки + сервисные задержки)",
                "source": {
                    "file": "app/sim_engine/simulate.py",
                    "pattern": "class Simulation"
                }
            },
            "calculations": {
                "text": "KPI: Производительность = Перевезённый объем / Длительность смены",
                "source": {
                    "file": "app/sim_engine/core/calculations/trucks_needed.py",
                    "pattern": "T_cycle"
                }
            },
            "results_writer": {
                "text": "Размер батча = Кол-во кадров за интервал × Размер кадра",
                "source": {
                    "file": "app/sim_engine/writer.py",
                    "pattern": "class DictReliabilityWriter"
                }
            }
        }

    def _make_snippet(self, lines: List[str], lineno: Optional[int], context: int = 2) -> str:
        if lineno is None:
            lineno = 1
        start = max(lineno - context - 1, 0)
        end = min(lineno + context, len(lines))
        snippet = "\n".join(lines[start:end]).strip()
        return snippet

    def _resolve_formula_source(self, meta: Optional[Dict]) -> Optional[Dict]:
        if not meta:
            return None
        rel_path = meta.get("file")
        if not rel_path:
            return None
        file_path = self.project_root / rel_path
        if not file_path.exists():
            return {
                "file": rel_path,
                "line": None,
                "code": "",
                "error": "file not found"
            }
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            return {
                "file": rel_path,
                "line": None,
                "code": "",
                "error": "cannot read file"
            }
        pattern = meta.get("pattern")
        line_no: Optional[int] = meta.get("line")
        if pattern:
            pattern_lower = pattern.lower()
            for idx, line in enumerate(lines, start=1):
                if pattern_lower in line.lower():
                    line_no = idx
                    break
        snippet = self._make_snippet(lines, line_no or 1)
        return {
            "file": rel_path.replace("\\", "/"),
            "line": line_no,
            "code": snippet
        }

    def _attach_formula_metadata(self, node: Dict, formula_id: str):
        formula_meta = self.formula_library.get(formula_id)
        if not formula_meta:
            return
        node["formula"] = formula_meta.get("text", "")
        source_payload = self._resolve_formula_source(formula_meta.get("source"))
        if source_payload:
            node["formula_source"] = source_payload
    
    def _extract_business_entities_from_models(self, file_path: Path):
        """Извлекает бизнес-сущности из models.py."""
        try:
            file_content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(file_content)
            lines = file_content.splitlines()
        except:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name in self.business_model_catalog:
                    entity_id = f"entity:{node.name}"
                    model_info = self.business_model_catalog[node.name]
                    business_layer = model_info['category']
                    entity_payload = {
                        "id": entity_id,
                        "name": model_info['name'],
                        "technical_name": node.name,
                        "icon": model_info['icon'],
                        "category": model_info['category'],
                        "layer": business_layer,
                        "layer_detail": model_info.get('detail_layer', business_layer),
                        "type": "business_entity",
                        "file_path": str(file_path.relative_to(self.project_root)).replace("\\", "/"),
                        "definition_line": getattr(node, "lineno", None),
                        "definition_snippet": self._make_snippet(lines, getattr(node, "lineno", None))
                    }
                    self._attach_formula_metadata(entity_payload, entity_id)
                    self.business_entities[entity_id] = entity_payload
    
    def _extract_parameters_from_forms(self, file_path: Path):
        """Извлекает параметры из forms.py."""
        try:
            file_content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(file_content)
            lines = file_content.splitlines()
        except:
            return
        
        # Справочник параметров
        all_params = {
            # Параметры экскаватора
            'bucket_volume': {'name': 'Объем ковша', 'unit': 'м³', 'entity': 'Экскаватор', 'entity_id': 'entity:Shovel', 'formula': 'Полезный объем = длина × ширина × глубина × коэффициент наполнения'},
            'bucket_lift_speed': {'name': 'Скорость подъема ковша', 'unit': 'м/с', 'entity': 'Экскаватор', 'entity_id': 'entity:Shovel', 'formula': 'Время подъема = Высота подъема / Скорость'},
            'arm_turn_speed': {'name': 'Скорость поворота стрелы', 'unit': 'рад/с', 'entity': 'Экскаватор', 'entity_id': 'entity:Shovel', 'formula': 'Время поворота = Угол / Скорость'},
            'bucket_dig_speed': {'name': 'Скорость врезки ковша', 'unit': 'м/с', 'entity': 'Экскаватор', 'entity_id': 'entity:Shovel', 'formula': 'Время копания = Глубина врезки / Скорость'},
            'bucket_fill_speed': {'name': 'Скорость наполнения ковша', 'unit': 'м/с', 'entity': 'Экскаватор', 'entity_id': 'entity:Shovel', 'formula': 'Время наполнения = Объем ковша / Скорость'},
            'bucket_fill_coef': {'name': 'Коэффициент наполнения ковша', 'unit': '', 'entity': 'Экскаватор', 'entity_id': 'entity:Shovel', 'formula': 'Полезный объем = Объем ковша × Коэффициент'},
            'payload_type': {'name': 'Тип породы', 'unit': '', 'entity': 'Экскаватор', 'entity_id': 'entity:Shovel', 'formula': 'Плотность породы влияет на массу одной ходки'},
            'initial_operating_time': {'name': 'Начальное время работы', 'unit': 'ч', 'entity': 'Экскаватор', 'entity_id': 'entity:Shovel', 'formula': 'Коэффициент надежности = e^{-(время/MTBF)}'},
            'initial_failure_count': {'name': 'Начальное количество отказов', 'unit': '', 'entity': 'Экскаватор', 'entity_id': 'entity:Shovel', 'formula': 'Вероятность отказа = Кол-во отказов / Время'},
            'average_repair_duration': {'name': 'Средняя длительность ремонта', 'unit': 'ч', 'entity': 'Экскаватор', 'entity_id': 'entity:Shovel', 'formula': 'Потерянное время = Кол-во ремонтов × Средняя длительность'},
            
            # Параметры самосвала
            'body_capacity': {'name': 'Вместимость кузова', 'unit': 'м³', 'entity': 'Самосвал', 'entity_id': 'entity:Truck', 'formula': 'Масса загрузки = Объем × Плотность породы'},
            'speed_empty': {'name': 'Скорость порожнего', 'unit': 'км/ч', 'entity': 'Самосвал', 'entity_id': 'entity:Truck', 'formula': 'Время возврата = Расстояние / Скорость'},
            'speed_loaded': {'name': 'Скорость груженого', 'unit': 'км/ч', 'entity': 'Самосвал', 'entity_id': 'entity:Truck', 'formula': 'Время движения = Расстояние / Скорость'},
            'fuel_capacity': {'name': 'Емкость бака', 'unit': 'л', 'entity': 'Самосвал', 'entity_id': 'entity:Truck', 'formula': 'Ресурс без дозаправки = Емкость / Удельный расход'},
            'fuel_specific_consumption': {'name': 'Удельный расход топлива', 'unit': 'л/ч', 'entity': 'Самосвал', 'entity_id': 'entity:Truck', 'formula': 'Расход топлива в рейсе = Расход × Время рейса'},
            'fuel_threshold_critical': {'name': 'Критический уровень топлива', 'unit': 'л', 'entity': 'Самосвал', 'entity_id': 'entity:Truck', 'formula': 'Триггер дозаправки при достижении порога'},
            'fuel_threshold_planned': {'name': 'Плановый уровень топлива', 'unit': 'л', 'entity': 'Самосвал', 'entity_id': 'entity:Truck', 'formula': 'Окно плановой дозаправки = Порог плановый ± Δ'},
        }
        
        # Извлекаем параметры из классов
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Ищем классы с параметрами (ShovelArgsMixin, TruckArgsMixin и т.д.)
                if 'Shovel' in node.name or 'Truck' in node.name or 'ArgsMixin' in node.name:
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            param_name = item.target.id
                            if param_name in all_params:
                                param_id = f"param:{param_name}"
                                param_info = all_params[param_name]
                                line_no = getattr(item, "lineno", None)
                                self.parameters[param_id] = {
                                    "id": param_id,
                                    "name": param_info['name'],
                                    "technical_name": param_name,
                                    "unit": param_info['unit'],
                                    "entity": param_info['entity'],
                                    "entity_id": param_info['entity_id'],
                                    "type": "parameter",
                                    "category": "Параметр",
                                    "layer": "Параметры",
                                    "layer_detail": f"Параметры · {param_info['entity']}",
                                    "formula": param_info.get('formula', ''),
                                    "source_file": str(file_path.relative_to(self.project_root)).replace("\\", "/"),
                                    "source_line": line_no,
                                    "source_code": self._make_snippet(lines, line_no)
                                }
    
    def _build_data_flow_chain(self):
        """Строит цепочку потоков данных от ввода до результатов."""
        
        # 1. Пользователь вводит параметры → Параметры
        for param_id, param in self.parameters.items():
            unit_suffix = f" ({param['unit']})" if param.get('unit') else ""
            self._add_data_flow(
                "user_input",
                param_id,
                f"Пользователь вводит: {param['name']}{unit_suffix}",
                "input",
                {"parameter": param_id, "unit": param.get('unit', '')}
            )
        
        # 2. Параметры → Формы валидации
        for param_id, param in self.parameters.items():
            unit_suffix = f" ({param['unit']})" if param.get('unit') else ""
            self._add_data_flow(
                param_id,
                "forms_validation",
                f"Параметр '{param['name']}{unit_suffix}' проходит валидацию",
                "validation",
                {"parameter": param_id, "unit": param.get('unit', '')}
            )
        
        # 3. Формы валидации → Бизнес-сущности, на которые влияют параметры
        for param_id, param in self.parameters.items():
            entity_id = param.get('entity_id')
            if entity_id and entity_id in self.business_entities:
                self._add_data_flow(
                    "forms_validation",
                    entity_id,
                    f"Параметр '{param['name']}' сохраняется в {self.business_entities[entity_id]['name']}",
                    "storage",
                    {"entity": entity_id, "parameter": param_id}
                )
        
        # 4. Модели данных → База данных
        for entity_id, entity in self.business_entities.items():
            if entity.get('type') == 'business_entity':
                self._add_data_flow(
                    entity_id,
                    "models_data",
                    f"{entity['name']} обновляет модели данных",
                    "storage",
                    {"entity": entity_id}
                )

        self._add_data_flow(
            "models_data",
            "database",
            "Данные сохраняются в базу данных",
            "storage",
            {}
        )
        
        # 5. База данных → Сервис запуска симуляции
        self._add_data_flow(
            "database",
            "simulation_service",
            "Данные загружаются для симуляции",
            "processing",
            {}
        )
        
        # 6. Сервис симуляции → Сериализация данных
        self._add_data_flow(
            "simulation_service",
            "data_serialization",
            "Данные подготавливаются для симуляции",
            "processing",
            {}
        )
        
        # 7. Сериализация → Менеджер симуляции
        self._add_data_flow(
            "data_serialization",
            "simulation_manager",
            "Данные передаются в менеджер симуляции",
            "simulation",
            {}
        )
        
        # 8. Менеджер симуляции → Ядро симуляции
        self._add_data_flow(
            "simulation_manager",
            "simulation_core",
            "Запуск симуляции с параметрами техники",
            "simulation",
            {}
        )
        
        # 9. Ядро симуляции → Расчеты
        self._add_data_flow(
            "simulation_core",
            "calculations",
            "Выполнение расчетов (время загрузки, движения, разгрузки)",
            "calculation",
            {}
        )
        
        # 10. Расчеты → Запись результатов
        self._add_data_flow(
            "calculations",
            "results_writer",
            "Запись кадров телеметрии и событий",
            "output",
            {}
        )
        
        # 11. Запись результатов → Хранилище результатов
        self._add_data_flow(
            "results_writer",
            "results_storage",
            "Сохранение результатов в Redis",
            "output",
            {}
        )
        
        # Связи параметров с сущностями и потоками данных
        for param_id, param in self.parameters.items():
            entity_id = param.get('entity_id')
            if entity_id and entity_id in self.business_entities:
                self.parameter_dependencies[param_id].append(entity_id)
                
                # Параметр влияет на сущность
                self._add_data_flow(
                    param_id,
                    entity_id,
                    f"Параметр '{param['name']}' влияет на {self.business_entities[entity_id]['name']}",
                    "parameter_impact",
                    {"parameter": param_id, "entity": entity_id}
                )
                
                # Сущность влияет на расчеты
                self._add_data_flow(
                    entity_id,
                    "calculations",
                    f"Характеристики {self.business_entities[entity_id]['name']} используются в расчетах",
                    "calculation_input",
                    {"entity": entity_id}
                )
    
    def _add_data_flow(self, source: str, target: str, description: str, category: str, metadata: Dict):
        """Добавляет поток данных."""
        metadata_key = ""
        if metadata:
            metadata_key = "|".join(sorted(f"{k}:{v}" for k, v in metadata.items()))
        flow_id = f"{source}->{target}:{category}:{metadata_key}"
        if not any(f["id"] == flow_id for f in self.data_flows):
            self.data_flows.append({
                "id": flow_id,
                "source": source,
                "target": target,
                "description": description,
                "category": category,
                "metadata": metadata
            })
    
    def _create_system_components(self):
        """Создает системные компоненты для потока данных."""
        system_components = [
            {
                "id": "user_input",
                "name": "Ввод пользователя",
                "description": "Пользователь вводит параметры техники через веб-интерфейс",
                "icon": "👤",
                "category": "Ввод данных",
                "layer": "Ввод данных",
                "layer_detail": "Ввод данных · Пользователь",
                "type": "system_component",
                "formula": ""
            },
            {
                "id": "forms_validation",
                "name": "Валидация данных",
                "description": "Проверка и валидация введенных параметров",
                "icon": "✅",
                "category": "Обработка",
                "layer": "Валидация",
                "layer_detail": "Валидация · Формы",
                "type": "system_component",
                "formula": ""
            },
            {
                "id": "models_data",
                "name": "Модели данных",
                "description": "Структуры данных для хранения информации о технике",
                "icon": "📊",
                "category": "Хранение",
                "layer": "Модели данных",
                "layer_detail": "Хранение · ORM модели",
                "type": "system_component",
                "formula": ""
            },
            {
                "id": "database",
                "name": "База данных",
                "description": "PostgreSQL - постоянное хранилище данных",
                "icon": "💾",
                "category": "Хранение",
                "layer": "Хранение",
                "layer_detail": "Хранение · БД",
                "type": "system_component",
                "formula": ""
            },
            {
                "id": "simulation_service",
                "name": "Сервис симуляции",
                "description": "Сервис запуска симуляции - собирает данные и запускает процесс",
                "icon": "🚀",
                "category": "Обработка",
                "layer": "Сервис симуляции",
                "layer_detail": "Сервис симуляции · Оркестрация",
                "type": "system_component",
                "formula": ""
            },
            {
                "id": "data_serialization",
                "name": "Сериализация данных",
                "description": "Преобразование данных из БД в формат для симуляции",
                "icon": "🔄",
                "category": "Обработка",
                "layer": "Сериализация",
                "layer_detail": "Сериализация · Подготовка данных",
                "type": "system_component",
                "formula": ""
            },
            {
                "id": "simulation_manager",
                "name": "Менеджер симуляции",
                "description": "Управление процессом симуляции",
                "icon": "🎮",
                "category": "Симуляция",
                "layer": "Симуляция",
                "layer_detail": "Симуляция · Менеджер",
                "type": "system_component",
                "formula": self.formula_library.get("simulation_core", "")
            },
            {
                "id": "simulation_core",
                "name": "Ядро симуляции",
                "description": "Основной движок симуляции - моделирование работы техники",
                "icon": "⚙️",
                "category": "Симуляция",
                "layer": "Симуляция",
                "layer_detail": "Симуляция · Ядро",
                "type": "system_component",
                "formula": self.formula_library.get("simulation_core", "")
            },
            {
                "id": "calculations",
                "name": "Расчеты",
                "description": "Математические расчеты: время загрузки, движения, разгрузки",
                "icon": "🧮",
                "category": "Расчеты",
                "layer": "Расчеты",
                "layer_detail": "Расчёты · KPI",
                "type": "system_component",
                "formula": self.formula_library.get("calculations", "")
            },
            {
                "id": "results_writer",
                "name": "Запись результатов",
                "description": "Запись кадров телеметрии и событий симуляции",
                "icon": "📝",
                "category": "Вывод",
                "layer": "Результаты",
                "layer_detail": "Результаты · Запись",
                "type": "system_component",
                "formula": self.formula_library.get("results_writer", "")
            },
            {
                "id": "results_storage",
                "name": "Хранилище результатов",
                "description": "Redis - временное хранилище результатов симуляции",
                "icon": "📦",
                "category": "Вывод",
                "layer": "Результаты",
                "layer_detail": "Результаты · Хранилище",
                "type": "system_component",
                "formula": ""
            }
        ]
        
        for comp in system_components:
            self._attach_formula_metadata(comp, comp["id"])
            if comp["id"] not in self.business_entities:
                self.business_entities[comp["id"]] = comp
    
    def parse(self) -> Dict:
        """Главный метод парсинга проекта."""
        print(f"Сканирование потоков данных для бизнес-аналитиков: {self.project_root}")
        
        # Ищем models.py
        models_file = self.project_root / "app" / "models.py"
        if models_file.exists():
            self._extract_business_entities_from_models(models_file)
            print(f"Найдено {len(self.business_entities)} бизнес-сущностей")
        
        # Ищем forms.py
        forms_file = self.project_root / "app" / "forms.py"
        if forms_file.exists():
            self._extract_parameters_from_forms(forms_file)
            print(f"Найдено {len(self.parameters)} параметров")
        
        # Создаем системные компоненты
        self._create_system_components()
        
        # Строим цепочку потоков данных
        self._build_data_flow_chain()
        print(f"Создано {len(self.data_flows)} потоков данных")
        
        # Формируем итоговую структуру
        return {
            "metadata": {
                "project_root": str(self.project_root),
                "total_entities": len(self.business_entities),
                "total_parameters": len(self.parameters),
                "total_data_flows": len(self.data_flows),
            },
            "entities": list(self.business_entities.values()),
            "parameters": list(self.parameters.values()),
            "data_flows": self.data_flows,
            "parameter_dependencies": dict(self.parameter_dependencies),
        }
    
    def generate_markdown_report(self, data: Dict, output_path: Path):
        """Генерирует Markdown-отчет для аналитиков."""
        name_map = {}
        for entity in data["entities"]:
            name_map[entity["id"]] = entity["name"]
        for param in data["parameters"]:
            name_map[param["id"]] = param["name"]
        
        flows_from = defaultdict(list)
        flows_to = defaultdict(list)
        for flow in data["data_flows"]:
            flows_from[flow["source"]].append(flow)
            flows_to[flow["target"]].append(flow)
        
        lines = []
        lines.append("# Отчет по потокам данных системы qsimmine12\n")
        lines.append(f"- Всего компонентов: **{data['metadata']['total_entities']}**")
        lines.append(f"- Всего параметров: **{data['metadata']['total_parameters']}**")
        lines.append(f"- Потоков данных: **{data['metadata']['total_data_flows']}**\n")
        
        lines.append("## Компоненты\n")
        lines.append("| Компонент | Слой | Подслой | Что делает | Основные входы | Основные выходы | Источник |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for entity in data["entities"]:
            inputs = ", ".join({name_map.get(flow["source"], flow["source"]) for flow in flows_to.get(entity["id"], [])})
            outputs = ", ".join({name_map.get(flow["target"], flow["target"]) for flow in flows_from.get(entity["id"], [])})
            source_path = entity.get("file_path") or entity.get("source_file") or "—"
            source_line = entity.get("definition_line") or entity.get("source_line")
            if source_path != "—" and source_line:
                source_path = f"{source_path}:{source_line}"
            lines.append(
                f"| {entity['icon'] if entity.get('icon') else '📦'} {entity['name']} "
                f"| {entity.get('layer','—')} "
                f"| {entity.get('layer_detail', entity.get('layer','—'))} "
                f"| {entity.get('description','—')} "
                f"| {inputs or '—'} | {outputs or '—'} | {source_path} |"
            )
        lines.append("")
        
        lines.append("## Параметры\n")
        lines.append("| Параметр | Единица | Относится к | Влияет на | Формула |")
        lines.append("| --- | --- | --- | --- | --- |")
        for param in data["parameters"]:
            deps = [name_map.get(dep, dep) for dep in data["parameter_dependencies"].get(param["id"], [])]
            lines.append(f"| {param['name']} | {param.get('unit','—') or '—'} | {param.get('entity','—')} | {', '.join(deps) or '—'} | {param.get('formula','—') or '—'} |")
        lines.append("")
        
        lines.append("## Основные цепочки потока данных\n")
        key_chain = [
            "Пользователь → Параметры техники → Валидация → Модель данных → База данных",
            "База данных → Сервис симуляции → Сериализация → Менеджер симуляции → Ядро → Расчеты",
            "Расчеты → Запись результатов → Хранилище результатов"
        ]
        for chain in key_chain:
            lines.append(f"- {chain}")
        lines.append("")
        
        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Markdown-отчет сохранён в {output_path}")
    
    def save(self, output_path: Path):
        """Сохраняет результат в JSON файл."""
        data = self.parse()
        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Результат сохранён в {output_path}")
        
        markdown_path = Path(__file__).parent / "S.architecture.md"
        self.generate_markdown_report(data, markdown_path)


def main():
    """Точка входа."""
    if len(sys.argv) >= 2:
        project_root = Path(sys.argv[1]).resolve()
    else:
        project_root = (Path(__file__).parent / "qsimmine12").resolve()
    
    if not project_root.exists():
        print(f"Ошибка: путь не найден: {project_root}")
        sys.exit(1)
    
    output_file = Path(__file__).parent / "S.architecture.json"
    
    parser = BusinessDataFlowParser(project_root)
    parser.save(output_file)
    
    print(f"\nГотово! Файл S.architecture.json создан.")
    print(f"Откройте S.viewer.html в браузере для просмотра потоков данных.")


if __name__ == "__main__":
    main()
