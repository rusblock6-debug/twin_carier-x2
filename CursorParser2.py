import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import date


# Bucket hints reused from CursorParser but extended here
ROOT_HINTS = {
    "orm": {"path_substr": ["app/models.py"]},
    "forms": {"path_substr": ["app/forms.py"]},
    "routes_dto": {"path_substr": ["app/routes.py"]},
    "services": {"path_substr": ["app/services/"]},
    "sim_serializer": {"path_substr": ["app/sim_engine/serializer.py"]},
    "sim_writer": {"path_substr": ["app/sim_engine/writer.py"]},
    "sim_manager": {"path_substr": ["app/sim_engine/simulation_manager.py"]},
    "sim_props": {"path_substr": ["app/sim_engine/core/props.py"]},
    "sim_states_events_behaviors": {
        "path_substr": [
            "app/sim_engine/states.py",
            "app/sim_engine/events.py",
            "app/sim_engine/core/behaviors/",
        ]
    },
    "planner": {"path_substr": ["app/sim_engine/core/planner/"]},
    "calculations": {"path_substr": ["app/sim_engine/core/calculations/"]},
    "dxf": {"path_substr": ["app/dxf_converter.py"]},
    "logger": {"path_substr": ["app/sim_engine/infra/logger/"]},
}


# Defaults per bucket for extended columns
CREATION_MODE = {
    "orm": "вручную (UI/API)",
    "forms": "автоматически (код при CRUD)",
    "routes_dto": "автоматически (иниц. роутером)",
    "services": "автоматически (код сервиса)",
    "sim_serializer": "автоматически (при запуске симуляции)",
    "sim_writer": "автоматически (цикл симуляции)",
    "sim_manager": "автоматически (ручной триггер запуска)",
    "sim_props": "автоматически (сериализатор)",
    "sim_states_events_behaviors": "автоматически (движок)",
    "planner": "автоматически (планировщик)",
    "calculations": "автоматически (движок)",
    "dxf": "автоматически (конвертация по действию пользователя)",
    "logger": "автоматически",
}

DATA_SOURCE = {
    "orm": "БД / пользовательский ввод",
    "forms": "HTTP JSON",
    "routes_dto": "HTTP запрос/ответ",
    "services": "БД/Redis/конфиг",
    "sim_serializer": "Комбинация API+БД",
    "sim_writer": "События симуляции",
    "sim_manager": "Запрос запуска/конфиг",
    "sim_props": "SimData (из API+БД)",
    "sim_states_events_behaviors": "Внутреннее состояние движка",
    "planner": "InputPlanningData/SimData",
    "calculations": "ТТХ/события",
    "dxf": "Файлы DXF/GeoJSON",
    "logger": "Сообщения/события",
}

FLOWS = {
    "orm": "Сервисы → API/витрины → сериализатор",
    "forms": "ObjectService → ORM",
    "routes_dto": "Роуты FastAPI",
    "services": "DTO → API",
    "sim_serializer": "SimData → Симулятор",
    "sim_writer": "Redis → API чтения",
    "sim_manager": "Оркестрация запуска",
    "sim_props": "Внутрь симуляции",
    "sim_states_events_behaviors": "Цикл симуляции",
    "planner": "План → симуляция",
    "calculations": "Расчёт в симуляции",
    "dxf": "GeoJSON в MapOverlay",
    "logger": "Файлы/консоль",
}

AFFECTS = {
    "orm": "Состав и параметры домена",
    "forms": "Качество/консистентность записи",
    "routes_dto": "Контракты API",
    "services": "Агрегация/правила",
    "sim_serializer": "Что попадёт в симуляцию",
    "sim_writer": "Доступность результатов",
    "sim_manager": "Успешность запуска",
    "sim_props": "Динамика моделирования",
    "sim_states_events_behaviors": "Переходы и ограничения",
    "planner": "Распределение/эффективность",
    "calculations": "Тайминги/ресурсы",
    "dxf": "Визуализация",
    "logger": "Диагностика",
}

# Extended: KPIs, NFRs, Events/SLAs, Flow triggers
KPIS = {
    "orm": "наполнение справочников, полнота данных",
    "services": "SLA ответа API, корректность витрины",
    "routes_dto": "валидность контрактов",
    "sim_manager": "время старта, стабильность батчей",
    "sim_writer": "пропускная способность записи, задержка до Redis",
    "sim_props": "точность входных параметров",
    "sim_serializer": "валидность/полнота входа",
    "planner": "качество плана (очередность), время решения",
    "calculations": "точность таймингов, производительность",
}

NFRS = {
    "orm": "объёмы записей, индексы, время коммита",
    "services": "латентность, пиковая нагрузка на БД",
    "sim_manager": "время инициализации, масштабирование процессов",
    "sim_writer": "скорость записи в Redis, объём батчей",
    "sim_serializer": "время сериализации",
    "planner": "время решения, ограничение памяти",
    "calculations": "CPU-интенсивность",
}

EVENTS = {
    "orm": "CRUD события (create/update/delete)",
    "services": "запросы API, построение витрины",
    "sim_manager": "запуск симуляции, завершение батча",
    "sim_writer": "события записи, ротация батчей",
    "sim_props": "обеды/пересменки/взрывы/простои (через SimData)",
    "sim_states_events_behaviors": "переходы состояний, аварии, топливо",
}

TRIGGERS = {
    "orm": "действия пользователя/интеграции",
    "services": "вызовы роутов",
    "sim_manager": "POST /api/run-simulation",
    "sim_writer": "накопление событий/таймер",
    "dxf": "загрузка файла/конверсия",
}


def path_bucket(path: Path) -> Optional[str]:
    p = str(path).replace("\\", "/")
    for bucket, cfg in ROOT_HINTS.items():
        for sub in cfg["path_substr"]:
            if sub in p:
                return bucket
    return None


def read_classes(path: Path) -> List[Tuple[str, str, str, Optional[str]]]:
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


def infer_row(
    cls_name: str,
    module_path: str,
    bucket: str,
    doc: str,
) -> Dict[str, str]:
    # Purpose from docstring if present
    purpose = " ".join((doc or "").split())
    if not purpose:
        purpose = {
            "orm": "ORM модель домена",
            "forms": "Валидация/маппинг входных данных",
            "routes_dto": "DTO/валидатор роутов",
            "services": "Сервис/DAO бизнес-логики",
            "sim_serializer": "Сериализация входа в SimData",
            "sim_writer": "Запись результатов симуляции",
            "sim_manager": "Оркестрация запуска симуляции",
            "sim_props": "Датакласс симдвижка",
            "sim_states_events_behaviors": "Состояния/события/поведения",
            "planner": "Планировщик/сольвер/входные данные",
            "calculations": "Расчётные блоки",
            "dxf": "Конвертер DXF → GeoJSON",
            "logger": "Логирование",
        }.get(bucket, "Класс приложения")

    how_created = CREATION_MODE.get(bucket, "-")
    source = DATA_SOURCE.get(bucket, "-")
    flows = FLOWS.get(bucket, "-")
    affects = AFFECTS.get(bucket, "-")
    kpis = KPIS.get(bucket, "-")
    nfrs = NFRS.get(bucket, "-")
    events = EVENTS.get(bucket, "-")
    trigger = TRIGGERS.get(bucket, "-")

    return {
        "class": cls_name,
        "purpose": purpose,
        "how": how_created,
        "source": source,
        "flows": flows,
        "affects": affects,
        "relations": f"{events}; триггер: {trigger}",
        "kpis": kpis,
        "nfrs": nfrs,
        "events": events,
        "module": module_path,
    }


def md_table(rows: List[Dict[str, str]]) -> str:
    lines: List[str] = []
    lines.append("### Полный каталог классов (с потоками/KPI/NFR/событиями)\n")
    lines.append("| Класс | Назначение | Как создаётся | Источник | Потоки | На что влияет | Связи/триггеры | KPI/метрики | Нефункциональные | События/расписания |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        lines.append(
            f"| {r['class']} | {r['purpose']} | {r['how']} | {r['source']} | {r['flows']} | {r['affects']} | {r['relations']} | {r['kpis']} | {r['nfrs']} | {r['events']} |"
        )
    lines.append("")
    return "\n".join(lines)


def html_page(md: str) -> str:
    # Very light HTML wrapper with pre-converted markdown-like table kept as is
    style = (
        "body{font-family:Segoe UI,Roboto,Arial,sans-serif;margin:24px;line-height:1.55;}"
        "table{border-collapse:collapse;width:100%;margin:16px 0;}"
        "th,td{border:1px solid #ddd;padding:8px 10px;vertical-align:top;}"
        "th{background:#f6f8fa;text-align:left;}"
        "h1,h2,h3{line-height:1.25;}"
    )
    # Wrap markdown directly; consumers often view table HTML-friendly
    return (
        "<!doctype html><html lang=\"ru\"><head><meta charset=\"utf-8\">"
        f"<style>{style}</style><title>Классы и потоки</title></head><body>"
        f"<h1>Каталог классов и потоков</h1>\n<pre style=\"white-space:normal\">{md}</pre>"
        "</body></html>"
    )


def main():
    # Resolve root path: arg or ./qsimmine12
    if len(sys.argv) >= 2:
        root = Path(sys.argv[1]).resolve()
    else:
        root = (Path(__file__).parent / "qsimmine12").resolve()
    if not root.exists():
        print("Path not found:", root)
        sys.exit(1)

    py_files = [p for p in root.rglob("*.py") if "tests" not in str(p).replace("\\", "/")]

    classes: List[Tuple[str, str, str, Optional[str]]] = []
    for f in py_files:
        classes.extend(read_classes(f))

    rows: List[Dict[str, str]] = []
    for cls_name, module_path, bucket, doc in classes:
        bucket_key = bucket or "other"
        row = infer_row(cls_name, module_path, bucket_key, doc or "")
        rows.append(row)

    # Sort by class name for stability
    rows.sort(key=lambda r: (r["class"].lower(), r["module"]))

    md = md_table(rows)
    today = date.today().isoformat()
    base = f"Twin_Car_Flows_{today}"
    out_md = (Path(__file__).parent / f"{base}.md").resolve()
    out_html = (Path(__file__).parent / f"{base}.html").resolve()

    out_md.write_text(md + "\n", encoding="utf-8")
    out_html.write_text(html_page(md), encoding="utf-8")

    # Print paths for convenience
    print(str(out_md))
    print(str(out_html))


if __name__ == "__main__":
    main()


