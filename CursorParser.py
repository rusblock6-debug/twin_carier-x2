# generate_class_tables.py
# Usage:
#   python generate_class_tables.py d:/Work/twin_carier_x2/qsimmine12
# Prints Markdown tables to stdout.

import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import date

ROOT_HINTS = {
    "orm": {
        "path_substr": ["app/models.py"],
        "how_created": "ORM через API (/api/object, /api/file, delete-роуты)",
        "data_source": "БД",
    },
    "forms": {
        "path_substr": ["app/forms.py"],
        "how_created": "Создаются в ObjectService при обработке HTTP JSON",
        "data_source": "HTTP JSON",
    },
    "routes_dto": {
        "path_substr": ["app/routes.py"],
        "how_created": "Инициализируются роутами FastAPI",
        "data_source": "HTTP JSON/параметры запроса",
    },
    "services": {
        "path_substr": ["app/services/"],
        "how_created": "Создаются в роутере/других сервисах",
        "data_source": "БД/Redis/входные параметры",
    },
    "sim_serializer": {
        "path_substr": ["app/sim_engine/serializer.py"],
        "how_created": "Вызывается при запуске симуляции",
        "data_source": "JSON из API/БД",
    },
    "sim_writer": {
        "path_substr": ["app/sim_engine/writer.py"],
        "how_created": "Создаётся в SimulationManager",
        "data_source": "События/результаты симуляции",
    },
    "sim_manager": {
        "path_substr": ["app/sim_engine/simulation_manager.py"],
        "how_created": "Создаётся в роуте запуска симуляции",
        "data_source": "Запрос/конфиг/Writer",
    },
    "sim_props": {
        "path_substr": ["app/sim_engine/core/props.py"],
        "how_created": "Создаются в SimDataSerializer",
        "data_source": "JSON из API/БД",
    },
    "sim_states_events_behaviors": {
        "path_substr": [
            "app/sim_engine/states.py",
            "app/sim_engine/events.py",
            "app/sim_engine/core/behaviors/",
        ],
        "how_created": "Императивно внутри симуляции",
        "data_source": "Внутренние данные симуляции",
    },
    "planner": {
        "path_substr": ["app/sim_engine/core/planner/"],
        "how_created": "Создаются планировщиком",
        "data_source": "InputPlanningData/SimData",
    },
    "calculations": {
        "path_substr": ["app/sim_engine/core/calculations/"],
        "how_created": "Используются внутри симуляции",
        "data_source": "ТТХ/события",
    },
    "dxf": {
        "path_substr": ["app/dxf_converter.py"],
        "how_created": "Вызывается схемой MapOverlaySchema",
        "data_source": "Загруженные файлы",
    },
    "logger": {
        "path_substr": ["app/sim_engine/infra/logger/"],
        "how_created": "Инициализируется при запуске",
        "data_source": "Логи симуляции",
    },
}

# Бизнес-описания и потоки для некоторых «ключевых» классов
BUSINESS_OVERRIDES: Dict[str, Dict[str, str]] = {
    # ORM
    "Quarry": {
        "purpose": "Карьер: конфигурация смен, часовой пояс, связи с объектами",
        "flows": "QuarryDataService → API → SimDataSerializer",
        "affects": "Тайминг симуляции, обеды/пересменки, фильтр объектов",
    },
    "Scenario": {
        "purpose": "Сценарий моделирования (окна времени, распределение АС, метрики стабильности)",
        "flows": "GetSimIdService → SimulationManager",
        "affects": "Состав участников и запуск симуляций",
    },
    "Shovel": {
        "purpose": "Экскаватор с ТТХ и координатой",
        "flows": "QuarryDataService → SimDataSerializer",
        "affects": "Время цикла погрузки/производительность",
    },
    "Truck": {
        "purpose": "Самосвал с топливной моделью",
        "flows": "QuarryDataService → SimDataSerializer",
        "affects": "Скорости/топливо/ремонты/выработка",
    },
    "Unload": {
        "purpose": "Пункт разгрузки",
        "flows": "QuarryDataService → SimDataSerializer",
        "affects": "Пропускная способность разгрузки",
    },
    "FuelStation": {
        "purpose": "Заправка",
        "flows": "QuarryDataService → SimDataSerializer",
        "affects": "Время заправок/задержки",
    },
    "IdleArea": {
        "purpose": "Зоны ожидания (обед/смена/взрыв/ремонт)",
        "flows": "QuarryDataService → SimDataSerializer",
        "affects": "Стоянки/ограничения движения",
    },
    "Blasting": {
        "purpose": "Расписание взрывов с геозоной",
        "flows": "ScheduleDataService, SimDataSerializer",
        "affects": "Блокировки зон/окна времени",
    },
    "Trail": {
        "purpose": "Маршрут Shovel—Unload (raw_graph)",
        "flows": "QuarryDataService (segments, trucks)",
        "affects": "Геометрия/назначение маршрутов",
    },
    "TrailTruckAssociation": {
        "purpose": "M2M сценарий—маршрут—самосвал",
        "flows": "QuarryDataService",
        "affects": "Какие грузовики на каких трассах",
    },
    "RoadNet": {
        "purpose": "Дорожная сеть (GeoJSON)",
        "flows": "API /api/road-net, SimDataSerializer",
        "affects": "Топология дорог",
    },
    "MapOverlay": {
        "purpose": "Подложка карты (GeoJSON/цвет/якорь)",
        "flows": "API /api/map-overlay, QuarryDataService",
        "affects": "Отображение карты в UI",
    },
    "UploadedFile": {
        "purpose": "Файл в сторидже",
        "flows": "Связан с MapOverlay",
        "affects": "Жизненный цикл файлов",
    },
    "PlannedIdle": {
        "purpose": "Плановые простои техники (generic FK)",
        "flows": "ScheduleDataService, SimDataSerializer",
        "affects": "Недоступности техники во времени",
    },
    # Sim props/dataclasses
    "SimData": {
        "purpose": "Входная конфигурация симуляции",
        "flows": "В SimulationManager/симулятор",
        "affects": "Все аспекты моделирования",
    },
    "TruckProperties": {
        "purpose": "ТТХ самосвала",
        "flows": "В симуляцию",
        "affects": "Скорости/топливо/ремонты",
    },
    "ShovelProperties": {
        "purpose": "ТТХ экскаватора",
        "flows": "В симуляцию",
        "affects": "Цикл погрузки",
    },
    "UnlProperties": {
        "purpose": "ТТХ разгрузки",
        "flows": "В симуляцию",
        "affects": "Пропускная способность",
    },
    "FuelStationProperties": {
        "purpose": "Параметры заправки",
        "flows": "В симуляцию",
        "affects": "Скорость заправки/очереди",
    },
    "Route": {
        "purpose": "Маршрут (сегменты и привязки)",
        "flows": "В симуляцию",
        "affects": "Геометрия пути",
    },
    "PlannedTrip": {
        "purpose": "План рейса",
        "flows": "В симуляцию/планировщик",
        "affects": "Маршрутизация/очередность",
    },
    "ActualTrip": {
        "purpose": "Фактический рейс (телеметрия)",
        "flows": "В writer",
        "affects": "Экспорт результатов",
    },
    # Services
    "QuarryDataService": {
        "purpose": "Компоновка ответа /api/quarry-data",
        "flows": "DTO → API",
        "affects": "Полный срез карьеров",
    },
    "ObjectService": {
        "purpose": "Диспетчер create/update/delete по типам",
        "flows": "ORM запись/обновление",
        "affects": "Бизнес-логика сохранения",
    },
    "SimulationManager": {
        "purpose": "Сборка конфига и запуск симуляции",
        "flows": "Инициация симдвижка",
        "affects": "Успешность старта/пакеты",
    },
    "BatchWriter": {
        "purpose": "Запись батчей и событий",
        "flows": "Redis → API чтения",
        "affects": "Доступность результатов",
    },
    # Schemas
    "ObjectActionRequest": {
        "purpose": "Обёртка запроса create/update",
        "flows": "В ObjectService",
        "affects": "Диспетчинг по типам",
    },
}

# По умолчанию для неизвестных классов
DEFAULT_PURPOSE_BY_BUCKET = {
    "orm": "ORM модель домена",
    "forms": "Валидация/маппинг входных данных",
    "routes_dto": "DTO/валидатор роутов",
    "services": "Сервис/DAO бизнес-логики",
    "sim_serializer": "Сериализация входа в SimData",
    "sim_writer": "Запись результатов симуляции",
    "sim_manager": "Оркестрация запуска симуляции",
    "sim_props": "Датакласс симдвижка",
    "sim_states_events_behaviors": "Состояния/события/поведения симуляции",
    "planner": "Планировщик/сольвер/входные данные планирования",
    "calculations": "Расчётные блоки симуляции",
    "dxf": "Конвертер DXF → GeoJSON",
    "logger": "Логирование",
}

DEFAULT_FLOWS_BY_BUCKET = {
    "orm": "QuarryDataService/сервисы → API/сериализатор",
    "forms": "ObjectService → ORM",
    "routes_dto": "Маршруты FastAPI",
    "services": "DTO → роуты/API",
    "sim_serializer": "SimData → симдвижок",
    "sim_writer": "Redis/внешние потребители",
    "sim_manager": "Инициация симдвижка",
    "sim_props": "В симуляцию",
    "sim_states_events_behaviors": "Внутренний цикл симуляции",
    "planner": "Планировщик → симуляция",
    "calculations": "Симуляция",
    "dxf": "MapOverlay.geojson_data",
    "logger": "Логи",
}

DEFAULT_AFFECTS_BY_BUCKET = {
    "orm": "Состав и параметры предметных сущностей",
    "forms": "Корректность записи и постпроцессы",
    "routes_dto": "Формат/валидность входа/выхода",
    "services": "Агрегация/правила бизнес-логики",
    "sim_serializer": "Что попадёт в симуляцию",
    "sim_writer": "Доступность/формат результатов",
    "sim_manager": "Старт/конфигурация симуляции",
    "sim_props": "Динамика моделирования",
    "sim_states_events_behaviors": "Переходы состояний/ограничения",
    "planner": "Качество/очередность рейсов",
    "calculations": "Тайминги/ресурсы",
    "dxf": "Отрисовка подложек",
    "logger": "Диагностика",
}

def path_bucket(path: Path) -> Optional[str]:
    p = str(path).replace("\\", "/")
    for bucket, cfg in ROOT_HINTS.items():
        for sub in cfg["path_substr"]:
            if sub in p:
                return bucket
    return None

def read_classes(path: Path) -> List[Tuple[str, str, str, Optional[str]]]:
    """
    Returns list of tuples: (class_name, module_rel_path, bucket, docstring)
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return []
    try:
        node = ast.parse(text)
    except Exception:
        return []
    bucket = path_bucket(path)
    result = []
    for n in node.body:
        if isinstance(n, ast.ClassDef):
            name = n.name
            doc = ast.get_docstring(n) or ""
            result.append((name, str(path), bucket or "", doc))
    return result

def infer_fields(
    cls_name: str,
    module_path: str,
    bucket: str,
    doc: str,
) -> Dict[str, str]:
    # Defaults by bucket
    cfg = ROOT_HINTS.get(bucket, {})
    how_created = cfg.get("how_created", "")
    data_source = cfg.get("data_source", "")
    purpose = DEFAULT_PURPOSE_BY_BUCKET.get(bucket, "")
    flows = DEFAULT_FLOWS_BY_BUCKET.get(bucket, "")
    affects = DEFAULT_AFFECTS_BY_BUCKET.get(bucket, "")

    # Use docstring if meaningful
    if doc and len(doc.strip()) >= 8:
        # Shorten docstring for table
        d = " ".join(doc.strip().split())
        purpose = d[:140] + ("…" if len(d) > 140 else "")

    # Business overrides for known classes
    if cls_name in BUSINESS_OVERRIDES:
        ov = BUSINESS_OVERRIDES[cls_name]
        purpose = ov.get("purpose", purpose)
        flows = ov.get("flows", flows)
        affects = ov.get("affects", affects)

    # Fine-tune buckets
    if bucket == "orm":
        # ORM specifics
        # creation route known
        pass
    elif bucket == "forms":
        pass
    elif bucket == "routes_dto":
        pass
    elif bucket == "services":
        pass
    elif bucket == "sim_props":
        pass
    elif bucket == "sim_serializer":
        pass
    elif bucket == "sim_manager":
        pass
    elif bucket == "sim_writer":
        pass
    elif bucket == "sim_states_events_behaviors":
        pass
    elif bucket == "planner":
        pass
    elif bucket == "calculations":
        pass
    elif bucket == "dxf":
        pass
    elif bucket == "logger":
        pass

    return {
        "class": cls_name,
        "purpose": purpose or "-",
        "how": how_created or "-",
        "source": data_source or "-",
        "flows": flows or "-",
        "affects": affects or "-",
        "module": module_path,
    }

def print_table(title: str, rows: List[Dict[str, str]]):
    print(f"### {title}\n")
    print("| Класс | Назначение в бизнес-логике | Как создаётся | Источник данных | Потоки данных (куда передаётся) | На что влияет |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['class']} | {r['purpose']} | {r['how']} | {r['source']} | {r['flows']} | {r['affects']} |")
    print()

def table_to_md(title: str, rows: List[Dict[str, str]]) -> str:
    lines: List[str] = []
    lines.append(f"### {title}\n")
    lines.append("| Класс | Назначение в бизнес-логике | Как создаётся | Источник данных | Потоки данных (куда передаётся) | На что влияет |")
    lines.append("|---|---|---|---|---|---|")
    for r in rows:
        lines.append(f"| {r['class']} | {r['purpose']} | {r['how']} | {r['source']} | {r['flows']} | {r['affects']} |")
    lines.append("")
    return "\n".join(lines)

def flows_section_md() -> str:
    # Curated high-level flows for system analysis
    rows = [
        {
            "from": "UI/API (POST /api/object)",
            "to": "ObjectService → Generic/Schedule/Scenario services",
            "data": "JSON формы объекта/расписания",
            "trigger": "Пользователь создаёт/обновляет сущность",
        },
        {
            "from": "ObjectService",
            "to": "ORM (SQLAlchemy) / БД",
            "data": "Маппинг полей и m2m-связей",
            "trigger": "Валидация формы прошла успешно",
        },
        {
            "from": "UI/API (GET /api/quarry-data)",
            "to": "QuarryDataService",
            "data": "Запрос витрины",
            "trigger": "Открытие UI/обновление данных",
        },
        {
            "from": "QuarryDataService",
            "to": "API ответ (/api/quarry-data)",
            "data": "Собранные объекты, маршруты, оверлеи",
            "trigger": "Успешные выборки из БД",
        },
        {
            "from": "UI/API (POST /api/run-simulation)",
            "to": "GetSimIdService",
            "data": "SimulationRequestDTO",
            "trigger": "Пользователь запускает симуляцию",
        },
        {
            "from": "GetSimIdService",
            "to": "SimulationDAO (road_net, schedules)",
            "data": "Идентификаторы/фильтры → ORM",
            "trigger": "Подготовка входа",
        },
        {
            "from": "SimulationDAO + входные данные",
            "to": "SimDataSerializer",
            "data": "Комбинированный JSON",
            "trigger": "Сбор готов к сериализации",
        },
        {
            "from": "SimDataSerializer",
            "to": "SimulationManager",
            "data": "SimData (датаклассы)",
            "trigger": "Валидация сериализованных данных",
        },
        {
            "from": "SimulationManager",
            "to": "BatchWriter",
            "data": "Сводки/события/батчи",
            "trigger": "Итерации симуляции/батч-комплит",
        },
        {
            "from": "BatchWriter",
            "to": "Redis",
            "data": "meta, summary, events, batches",
            "trigger": "Буфер заполнен/таймер",
        },
        {
            "from": "API (/api/simulation/*)",
            "to": "Redis",
            "data": "Чтение ключей симуляции",
            "trigger": "UI запрашивает прогресс/итоги",
        },
        {
            "from": "UI/API (POST /api/file)",
            "to": "UploadedFile + ФС",
            "data": "Бинарный файл",
            "trigger": "Пользователь загружает файл",
        },
        {
            "from": "MapOverlaySchema.convert_dxf",
            "to": "MapOverlay.geojson_data",
            "data": "GeoJSON из DXF",
            "trigger": "Создание/обновление подложки",
        },
        {
            "from": "UI/API (GET /api/schedule-data-by-date-shift)",
            "to": "ScheduleDataService",
            "data": "date, quarry_id, type, shift",
            "trigger": "Фильтрация слоёв расписаний",
        },
    ]

    lines: List[str] = []
    lines.append("### Связи и граф потоков (высокоуровнево)\n")
    lines.append("| Откуда | Куда | Тип данных | Триггер/событие |")
    lines.append("|---|---|---|---|")
    for r in rows:
        lines.append(f"| {r['from']} | {r['to']} | {r['data']} | {r['trigger']} |")
    lines.append("")
    return "\n".join(lines)

def main():
    # Allow default to ./qsimmine12 if no arg provided
    if len(sys.argv) >= 2:
        root = Path(sys.argv[1]).resolve()
    else:
        root = (Path(__file__).parent / "qsimmine12").resolve()
        if not root.exists():
            print("Usage: python CursorParser.py <path-to-qsimmine12>")
            sys.exit(1)
    if not root.exists():
        print("Path not found:", root)
        sys.exit(1)

    py_files = [p for p in root.rglob("*.py") if "tests" not in str(p).replace("\\", "/")]

    classes = []
    for f in py_files:
        classes.extend(read_classes(f))

    # Split by buckets
    bucket_rows: Dict[str, List[Dict[str, str]]] = {}
    for cls_name, module_path, bucket, doc in classes:
        b = bucket or "other"
        row = infer_fields(cls_name, module_path, b, doc or "")
        bucket_rows.setdefault(b, []).append(row)

    # Select and print tables in the same grouping used in the report
    def sort_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
        return sorted(rows, key=lambda r: r["class"].lower())

    out_sections: List[str] = []
    if "orm" in bucket_rows:
        out_sections.append(table_to_md("ORM модели (SQLAlchemy)", sort_rows(bucket_rows["orm"])))
    if "forms" in bucket_rows:
        out_sections.append(table_to_md("Pydantic-схемы (формы API)", sort_rows(bucket_rows["forms"])))
    if "services" in bucket_rows:
        out_sections.append(table_to_md("Сервисы и DAO", sort_rows(bucket_rows["services"])))
    if "sim_props" in bucket_rows:
        out_sections.append(table_to_md("Симдвижок: входные датаклассы", sort_rows(bucket_rows["sim_props"])))
    if "sim_manager" in bucket_rows or "sim_writer" in bucket_rows:
        rows = bucket_rows.get("sim_manager", []) + bucket_rows.get("sim_writer", [])
        if rows:
            out_sections.append(table_to_md("Симдвижок: менеджер/вывод", sort_rows(rows)))
    if "sim_states_events_behaviors" in bucket_rows:
        out_sections.append(table_to_md("Симдвижок: состояния/события/поведения", sort_rows(bucket_rows["sim_states_events_behaviors"])))
    if "planner" in bucket_rows:
        out_sections.append(table_to_md("Планировщик и расчёты (планировщик отдельно)", sort_rows(bucket_rows["planner"])))
    if "calculations" in bucket_rows:
        out_sections.append(table_to_md("Планировщик и расчёты (расчётные блоки)", sort_rows(bucket_rows["calculations"])))
    if "routes_dto" in bucket_rows:
        out_sections.append(table_to_md("Pydantic DTO роутов", sort_rows(bucket_rows["routes_dto"])))
    if "dxf" in bucket_rows:
        out_sections.append(table_to_md("Прочее (DXF конвертер)", sort_rows(bucket_rows["dxf"])))
    if "logger" in bucket_rows:
        out_sections.append(table_to_md("Прочее (логирование)", sort_rows(bucket_rows["logger"])))

    # Any uncategorized classes
    other = [r for b, rows in bucket_rows.items() if b not in ROOT_HINTS for r in rows]
    if other:
        out_sections.append(table_to_md("Прочее (некатегоризированные)", sort_rows(other)))

    # Append flows section
    out_sections.append(flows_section_md())

    out_md = "\n".join(out_sections).strip() + "\n"

    # Write to Twin_Car_YYYY-MM-DD.md in project root
    out_name = f"Twin_Car_{date.today().isoformat()}.md"
    out_path = (Path(__file__).parent / out_name).resolve()
    out_path.write_text(out_md, encoding="utf-8")
    print(str(out_path))

if __name__ == "__main__":
    main()