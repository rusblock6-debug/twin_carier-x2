#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import os
import json
from typing import List, Dict, Any
from collections import defaultdict

# ==============================
# 1. Парсер AST
# ==============================
class FunctionVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.functions: List[Dict[str, Any]] = []
        self.current_function = None
        self.class_stack = []
        self.imports = []
        self.current_calls = []

    # --- Импорты ---
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(f"import {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        names = [alias.name for alias in node.names]
        self.imports.append(f"from {node.module or ''} import {', '.join(names)}")
        self.generic_visit(node)

    # --- Классы ---
    def visit_ClassDef(self, node):
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    # --- Функции ---
    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.current_calls = []
        self.generic_visit(node)
        self._process_function(node)
        self.current_function = None

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def _process_function(self, node):
        # ----- Аргументы -----
        args_full = []
        defaults = node.args.defaults if node.args.defaults else []
        kwonly_defaults = node.args.kw_defaults if node.args.kw_defaults else []
        # Позиционные аргументы
        for i, arg in enumerate(node.args.args):
            arg_info = {"name": arg.arg}
            # Аннотация
            if arg.annotation:
                arg_info["type"] = self._unparse(arg.annotation)
            # Дефолт
            def_idx = i - (len(node.args.args) - len(defaults))
            if def_idx >= 0:
                try:
                    arg_info["default"] = self._unparse(defaults[def_idx])
                except:
                    arg_info["default"] = "<complex>"
            args_full.append(arg_info)

        # *args, **kwargs
        if node.args.vararg:
            args_full.append({"name": f"*{node.args.vararg.arg}", "kind": "vararg"})
        if node.args.kwarg:
            args_full.append({"name": f"**{node.args.kwarg.arg}", "kind": "kwarg"})

        # ----- Возвращаемый тип -----
        return_type = None
        if node.returns:
            return_type = self._unparse(node.returns)

        # ----- Docstring -----
        docstring = ast.get_docstring(node)

        # ----- return-значения (только из тела функции) -----
        returns = []
        for stmt in node.body:
            if isinstance(stmt, ast.Return) and stmt.value:
                try:
                    returns.append(self._unparse(stmt.value))
                except:
                    returns.append("<complex>")
                if len(returns) >= 3:
                    break

        # ----- Декораторы -----
        decorators = [self._unparse(d) for d in node.decorator_list]

        # ----- Публичность -----
        is_public = not node.name.startswith('_') or node.name == '__init__'

        # ----- Вызовы -----
        calls = list(set(self.current_calls))

        # ----- Метаданные -----
        current_class = self.class_stack[-1] if self.class_stack else None
        module_name = os.path.splitext(os.path.basename(self.file_path))[0]

        func_data = {
            "file_path": self.file_path,
            "module": module_name,
            "class_name": current_class,
            "function_name": node.name,
            "arguments": args_full,
            "return_type": return_type,
            "returns": returns,
            "docstring": docstring,
            "decorators": decorators,
            "is_public": is_public,
            "calls": calls,
            "line_start": node.lineno,
            "line_end": node.end_lineno
        }
        self.functions.append(func_data)

    def visit_Call(self, node):
        if self.current_function:
            if isinstance(node.func, ast.Name):
                self.current_calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.current_calls.append(node.func.attr)
        self.generic_visit(node)

    # --- Утилита для ast.unparse (fallback) ---
    def _unparse(self, node):
        try:
            return ast.unparse(node)
        except AttributeError:  # Python < 3.9
            return ast.get_source_segment(open(self.file_path, encoding='utf-8').read(), node) or "<complex>"


# ==============================
# 2. Анализ файла
# ==============================
def analyze_file(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        visitor = FunctionVisitor(file_path)
        visitor.visit(tree)
        return {
            "file_path": file_path,
            "imports": visitor.imports,
            "functions": visitor.functions
        }
    except Exception as e:
        print(f"Ошибка: {file_path} — {e}")
        return {"file_path": file_path, "imports": [], "functions": [], "error": str(e)}


# ==============================
# 3. Анализ проекта
# ==============================
def analyze_project(root_dir: str) -> List[Dict[str, Any]]:
    all_files_data = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(subdir, file)
                print(f"→ {path}")
                data = analyze_file(path)
                all_files_data.append(data)
    return all_files_data


# ==============================
# 4. Граф вызовов
# ==============================
def build_call_graph(all_data: List[Dict[str, Any]]) -> Dict:
    graph = defaultdict(list)
    for file_data in all_data:
        if "error" in file_data:
            continue
        for func in file_data.get("functions", []):
            caller = f"{func['module']}::{func.get('class_name', '')}::{func['function_name']}".strip("::")
            for called in func.get("calls", []):
                # Упрощённо — считаем, что вызываемая функция в том же модуле
                callee = f"{func['module']}::{called}"
                if callee not in graph[caller]:
                    graph[caller].append(callee)
    return dict(graph)


# ==============================
# 5. Markdown-документация
# ==============================
def generate_markdown(all_data: List[Dict[str, Any]]) -> str:
    md = "# Анализ проекта\n\n"
    for file_data in all_data:
        if "error" in file_data:
            continue
        md += f"## Файл: `{file_data['file_path']}`\n\n"
        # Импорты
        if file_data["imports"]:
            md += "### Импорты\n"
            for imp in file_data["imports"]:
                md += f"- `{imp}`\n"
            md += "\n"
        # Публичные функции
        public_funcs = [f for f in file_data["functions"] if f["is_public"]]
        if public_funcs:
            md += "### Публичные функции\n\n"
            for func in public_funcs:
                header = f"{func['function_name']}"
                if func.get('class_name'):
                    header += f" (`{func['class_name']}`)"
                md += f"#### {header}\n"
                if func["docstring"]:
                    md += f"{func['docstring']}\n\n"
                # Аргументы
                if func["arguments"]:
                    md += "**Аргументы:**\n"
                    for arg in func["arguments"]:
                        s = f"- `{arg['name']}`"
                        if "type" in arg:
                            s += f": {arg['type']}"
                        if "default" in arg:
                            s += f" = {arg['default']}"
                        if "kind" in arg:
                            s += f" ({arg['kind']})"
                        md += f"{s}\n"
                    md += "\n"
                # Возврат
                if func["return_type"]:
                    md += f"**Возвращает:** `{func['return_type']}`\n\n"
                # Вызовы
                if func["calls"]:
                    md += f"**Вызывает:** `{'`, `'.join(func['calls'])}`\n\n"
                md += "---\n\n"
    return md


# ==============================
# 6. Зависимости модулей
# ==============================
def module_dependencies(all_data: List[Dict[str, Any]]) -> Dict:
    deps = defaultdict(set)
    for file_data in all_data:
        if "error" in file_data:
            continue
        module = os.path.splitext(os.path.basename(file_data["file_path"]))[0]
        for imp in file_data["imports"]:
            if imp.startswith("from "):
                from_part = imp.split("from ")[1].split(" import")[0].strip()
                if from_part and from_part != "." and not from_part.startswith(".") and from_part != module:
                    deps[module].add(from_part.split(".")[0])  # только корень
            elif imp.startswith("import "):
                imported = imp.split("import ")[1].strip().split(".")[0]
                if imported != module:
                    deps[module].add(imported)
    # Преобразуем set → list и сортируем
    return {k: sorted(list(v)) for k, v in deps.items() if v}


# ==============================
# 7. Graphviz DOT
# ==============================
def generate_dot_graph(call_graph: Dict) -> str:
    dot = 'digraph CallGraph {\n'
    dot += '    rankdir=LR;\n'
    dot += '    node [shape=box, style=rounded, fontname="Arial"];\n'
    dot += '    edge [color="#555555"];\n\n'
    for caller, callees in call_graph.items():
        caller_clean = caller.replace("::", "_").replace(".", "_")
        for callee in callees:
            callee_clean = callee.replace("::", "_").replace(".", "_")
            dot += f'    "{caller_clean}" -> "{callee_clean}";\n'
    dot += '}\n'
    return dot


# ==============================
# 8. PlantUML схемы (строки)
# ==============================
def generate_plantuml_overview() -> str:
    return """@startuml
title Обзор компонентов и потоков (понятно аналитику, с пояснениями)

skinparam packageStyle rectangle
skinparam componentStyle rectangle
skinparam linetype ortho

package \"API (веб-интерфейс, FastAPI Routes)\" as API {
  [Справочник карьера /api/quarry-data]
  [Расписание /api/schedule-data-by-date-shift]
  [Создать/обновить объект /api/object]
  [Удалить объект /api/object (DELETE)]
  [Запуск симуляции /api/run-simulation]
  [Результаты симуляции /api/simulation/{id}/(meta|summary|events|batch)]
  [Дефолты /api/defaults]
  [Файлы подложек: загрузить/получить/удалить (/api/file,* /upload/*)]
}

package \"Сервисы приложения (Services)\" as S {
  [Сервис данных карьера (QuarryDataService)]
  [Сервис расписаний (ScheduleDataService)]
  [Сервис объектов (ObjectService)]
  [Сервис сценариев (ScenarioService)]
  [Сервис шаблонов (AllTemplatesListService)]
  [Сервис времени по умолчанию (StartEndTimeGenerateService)]
  [Сервис запуска симуляции (GetSimIdService)]
}

package \"Доступ к данным (DAO)\" as DAO {
  [DAO карьера (QuarryDAO)]
  [DAO расписаний (ScheduleDAO)]
  [DAO симуляции (SimulationDAO)]
  [DAO объектов (ObjectDAO)]
}

package \"Бизнес-сущности (ORM, SQLAlchemy)\" as ORM {
  [Карьер (Quarry)]
  [Экскаватор (Shovel)]
  [Самосвал (Truck)]
  [Пункт разгрузки (Unload)]
  [Заправка (FuelStation)]
  [Зона ожидания (IdleArea)]
  [Маршрут (Trail)]
  [Связь маршрут–самосвал–сценарий (TrailTruckAssociation)]
  [Взрывные работы (Blasting)]
  [Плановый простой (PlannedIdle)]
  [Сценарий (Scenario)]
  [Дорожная сеть (RoadNet)]
  [Подложка карты (MapOverlay)]
  [Загруженный файл (UploadedFile)]
  [Отображение типов (TYPE_MODEL_MAP / TYPE_SCHEDULE_MAP)]
  [Дефолтные значения (DefaultValuesMixin)]
}

package \"Движок симуляции (Sim Engine)\" as SE {
  [Сериализация входа (SimDataSerializer)]
  [Менеджер симуляции (SimulationManager)]
  [Запись результатов (Writer: Batch/Dict)]
  [Состояния/События (States/Events)]
  package \"Ядро симуляции (Core)\" as Core {
    [Карьер-актор (Quarry actor)]
    [Самосвал-актор (Truck actor)]
    [Экскаватор-актор (Shovel actor)]
    [Пункт разгрузки-актор (Unload actor)]
    [Заправка-актор (FuelStation actor)]
    [Контекст/телеметрия (SimContext/TelemetryEmitter)]
    [Расчёты (Calculations: Truck/Shovel/Unload/Base)]
    [Поведения (Behaviors: Отказы/Топливо/Обед/Плановый простой/Взрывы)]
    [Планировщик (Planner + решатели CP/MILP/Greedy)]
  }
}

database \"БД (PostgreSQL через ORM)\" as DB
queue \"Хранилище результатов симуляции (Redis)\" as REDIS
collections \"Хранилище пользовательских файлов подложек (каталог upload/)\" as FILES

[Справочник карьера /api/quarry-data] --> [Сервис данных карьера (QuarryDataService)]
[Расписание /api/schedule-data-by-date-shift] --> [Сервис расписаний (ScheduleDataService)]
[Создать/обновить объект /api/object] --> [Сервис объектов (ObjectService)]
[Удалить объект /api/object (DELETE)] --> [Сервис объектов (ObjectService)]
[Запуск симуляции /api/run-simulation] --> [Сервис запуска симуляции (GetSimIdService)]
[Результаты симуляции /api/simulation/{id}/(meta|summary|events|batch)] --> REDIS
[Дефолты /api/defaults] --> [Дефолтные значения (DefaultValuesMixin)]
[Файлы подложек: загрузить/получить/удалить (/api/file,* /upload/*)] --> [Загруженный файл (UploadedFile)]

[Сервис данных карьера (QuarryDataService)] --> [DAO карьера (QuarryDAO)]
[Сервис расписаний (ScheduleDataService)] --> [DAO расписаний (ScheduleDAO)]
[Сервис объектов (ObjectService)] --> [DAO объектов (ObjectDAO)]
[Сервис запуска симуляции (GetSimIdService)] --> [DAO симуляции (SimulationDAO)]

[DAO карьера (QuarryDAO)] --> ORM
[DAO расписаний (ScheduleDAO)] --> [Взрывные работы (Blasting)]
[DAO расписаний (ScheduleDAO)] --> [Плановый простой (PlannedIdle)]
[DAO симуляции (SimulationDAO)] --> [Дорожная сеть (RoadNet)]
[DAO симуляции (SimulationDAO)] --> [Взрывные работы (Blasting)]
[DAO симуляции (SimulationDAO)] --> [Плановый простой (PlannedIdle)]

ORM --> DB

[Сервис запуска симуляции (GetSimIdService)] --> [Сериализация входа (SimDataSerializer)]
[Сервис запуска симуляции (GetSimIdService)] -> [Менеджер симуляции (SimulationManager)]
[Менеджер симуляции (SimulationManager)] --> Core
Core ..> [Расчёты (Calculations: Truck/Shovel/Unload/Base)]
Core ..> [Поведения (Behaviors: Отказы/Топливо/Обед/Плановый простой/Взрывы)]
Core ..> [Планировщик (Planner + решатели CP/MILP/Greedy)]
[Менеджер симуляции (SimulationManager)] --> [Состояния/События (States/Events)]
[Менеджер симуляции (SimulationManager)] --> [Запись результатов (Writer: Batch/Dict)]
[Запись результатов (Writer: Batch/Dict)] --> REDIS

[Подложка карты (MapOverlay)] --> FILES : ссылка на файл (DXF/растровый)
[Загруженный файл (UploadedFile)] --> FILES : физический файл хранится здесь

@enduml"""


def generate_plantuml_sequence() -> str:
    return """@startuml
title Последовательность запуска симуляции (понятно аналитику)

actor Клиент
participant \"API: запуск симуляции (/api/run-simulation)\" as API
participant \"Сервис запуска (GetSimIdService)\" as SVC
participant \"DAO симуляции (SimulationDAO)\" as DAO
database \"БД (ORM)\" as DB
participant \"Сериализация входа (SimDataSerializer)\" as SER
participant \"Менеджер симуляции (SimulationManager)\" as MAN
participant \"Запись результатов (Writer: Batch)\" as WR
queue \"Redis (результаты)\" as R

Клиент -> API: Параметры: карьер.id, время начала/окончания, сценарий?
API -> SVC: Инициализация (data, db, redis)
activate SVC

SVC -> DAO: Получить расписания (Взрывные работы/Плановый простой)
activate DAO
DAO -> DB: SELECT Blasting/PlannedIdle WHERE пересекаются с окном
DB --> DAO: Списки интервалов и зон (GeoJSON)
deactivate DAO
SVC <-- DAO: Расписания

SVC -> DAO: Получить дорожную сеть (RoadNet) [опционально]
activate DAO
DAO -> DB: SELECT RoadNet
DB --> DAO: GeoJSON дорожной сети
deactivate DAO
SVC <-- DAO: RoadNet (если есть)

SVC -> SER: Собрать вход симуляции (SimData) из данных карьера + расписаний + сети
activate SER
SER --> SVC: SimData (экскаваторы, самосвалы, маршруты, зоны, времена)
deactivate SER

SVC -> MAN: Запуск симуляции (options: авто/ручное, надёжность)
activate MAN
MAN -> WR: Инициализация батч-записи (шаг 60с)
activate WR
MAN -> MAN: Симуляция акторов (Самосвал/Экскаватор/Разгрузка/Заправка)
MAN -> MAN: Поведения (Отказ, Топливо, Обед, Плановый простой, Взрывы)
MAN -> WR: Пишем метаданные, сводку, события, батчи
WR -> R: Сохранение meta/summary/events/batches (с TTL)
deactivate WR
SVC <-- MAN: sim_id (uuid)
deactivate MAN

API <-- SVC: Ответ { sim_id }
Клиент <-- API: OK + sim_id

== Чтение результатов ==
Клиент -> API: GET /api/simulation/{id}/(meta|summary|events|batch/i)
API -> R: GET key
R --> API: JSON
API --> Клиент: JSON

@enduml"""

# ==============================
# 8. Главный запуск
# ==============================
def _infer_business_table(models: List[Dict[str, Any]]) -> str:
    """Генерация читаемой сводной таблицы по бизнес-сущностям.

    Основана на эвристиках: имя файла/класса, контекст директорий.
    Не претендует на 100% точность, но даёт быстрый обзор.
    """
    def how_created(name: str, file_path: str) -> str:
        lower = name.lower()
        if any(k in lower for k in ["overlay", "uploadedfile", "roadnet"]):
            return "Импорт (файл) + Пользователь (UI/API)"
        if any(k in lower for k in ["schema", "dto", "request", "response"]):
            return "Система (сервис) / Пользователь (UI/API)"
        if "sim_" in file_path or "sim_engine" in file_path.replace("\\", "/"):
            return "Код (внутр.)"
        return "Пользователь (UI/API)"

    def data_source(file_path: str) -> str:
        norm = file_path.replace("\\", "/")
        if "sim_engine" in norm:
            return "Комбинированные данные (из БД + payload)"
        if any(x in norm for x in ["models.py", "/models", "/app/"]):
            return "БД"
        return "Код / БД"

    lines = []
    lines.append("| Сущность | Назначение (эвристика по имени) | Как создаётся | Источник данных | Файл |")
    lines.append("|---|---|---|---|---|")
    for m in sorted(models, key=lambda x: (x["name"].lower(), x["file"])):
        name = m["name"]
        file_path = m["file"]
        hint = ""
        ln = name.lower()
        if any(k in ln for k in ["quarry", "career", "карьер"]):
            hint = "Контекст карьера"
        elif any(k in ln for k in ["shovel", "экскаватор"]):
            hint = "Экскаватор"
        elif any(k in ln for k in ["truck", "самосвал"]):
            hint = "Самосвал"
        elif any(k in ln for k in ["unload", "разгруз"]):
            hint = "Пункт разгрузки"
        elif any(k in ln for k in ["fuel", "заправ"]):
            hint = "Заправка"
        elif any(k in ln for k in ["idle", "ожид", "lunch", "shift"]):
            hint = "Зоны ожиданий/обеды/пересменки"
        elif any(k in ln for k in ["trail", "route", "маршрут"]):
            hint = "Маршрут/сегменты"
        elif any(k in ln for k in ["scenario"]):
            hint = "Сценарий"
        elif any(k in ln for k in ["blasting", "взрыв"]):
            hint = "Взрывные работы"
        elif any(k in ln for k in ["plannedidle", "простой"]):
            hint = "Плановые простои"
        elif any(k in ln for k in ["roadnet", "overlay", "uploadedfile"]):
            hint = "Дорожная сеть/подложки/файлы"

        lines.append(
            f"| {name} | {hint or '—'} | {how_created(name, file_path)} | {data_source(file_path)} | {file_path} |"
        )
    return "\n".join(lines)


def collect_classes(root_dir: str) -> List[Dict[str, Any]]:
    """Собирает все определения классов с их файлами."""
    result = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if not file.endswith('.py'):
                continue
            path = os.path.join(subdir, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        result.append({"name": node.name, "file": path})
            except Exception:
                continue
    return result


def _channel_for_name(name: str, file_path: str) -> str:
    lower = name.lower()
    if any(k in lower for k in ["overlay", "uploadedfile", "roadnet"]):
        return "Импорт (файл) + Пользователь (UI/API)"
    if any(k in lower for k in ["schema", "dto", "request", "response"]):
        return "Пользователь (UI/API) / Система (сервис)"
    if "sim_engine" in file_path.replace("\\", "/"):
        return "Код (внутр.)"
    return "Пользователь (UI/API)"


def _source_for_file(file_path: str) -> str:
    norm = file_path.replace("\\", "/")
    if "sim_engine" in norm:
        return "Комбинированные (БД + payload)"
    if any(x in norm for x in ["models.py", "/models", "/app/"]):
        return "БД"
    return "Код / БД"


def generate_analyst_markdown(root_dir: str) -> str:
    """Генерирует те самые читабельные таблицы (как в time.md), но автоматически.

    Сканирует классы и раскладывает по 4 разделам:
    1) Доменные сущности (ORM)
    2) Сервисы/DAO
    3) ДТО/контракты
    4) Симуляция
    """
    classes = collect_classes(root_dir)

    def in_path(fp: str, part: str) -> bool:
        return part in fp.replace("\\", "/")

    # Классификаторы по путям/именам
    domain = []
    services = []
    dtos = []
    sim = []

    for c in classes:
        name, fp = c["name"], c["file"]
        lname = name.lower()
        if os.path.basename(fp) == "models.py" or any(k in lname for k in [
            "quarry", "shovel", "truck", "unload", "fuelstation", "idlearea",
            "trail", "scenario", "blasting", "plannedidle", "roadnet", "mapoverlay", "uploadedfile"
        ]):
            domain.append(c)
        elif in_path(fp, "/services/") or lname.endswith("dao") or lname.endswith("service"):
            services.append(c)
        elif in_path(fp, "forms.py") or any(k in lname for k in ["schema", "dto", "request", "response"]):
            dtos.append(c)
        elif in_path(fp, "/sim_engine/"):
            sim.append(c)

    def md_table(rows: List[List[str]]) -> str:
        if not rows:
            return ""
        out = ["| " + " | ".join(["Сущность", "Назначение", "Как создаётся", "Источник данных", "Файл"]) + " |",
               "|" + "---|" * 5]
        for r in rows:
            out.append("| " + " | ".join(r) + " |")
        return "\n".join(out)

    def purpose_hint(name: str) -> str:
        ln = name.lower()
        if "quarry" in ln: return "Контекст карьера"
        if "shovel" in ln: return "Экскаватор"
        if "truck" in ln: return "Самосвал"
        if "unload" in ln: return "Пункт разгрузки"
        if "fuel" in ln: return "Заправка"
        if any(k in ln for k in ["idle", "lunch", "shift"]): return "Зоны ожиданий/обеды/пересменки"
        if "trail" in ln or "route" in ln: return "Маршрут/сегменты"
        if "scenario" in ln: return "Сценарий"
        if "blasting" in ln: return "Взрывные работы"
        if "plannedidle" in ln: return "Плановые простои"
        if any(k in ln for k in ["roadnet", "overlay", "uploadedfile"]): return "Дорожная сеть/подложки/файлы"
        if any(k in ln for k in ["service", "dao"]): return "Сервис/DAO"
        if any(k in ln for k in ["schema", "dto", "request", "response"]): return "DTO/Схема"
        if "sim" in ln: return "Симуляция"
        return "—"

    def make_rows(bucket: List[Dict[str, Any]]) -> List[List[str]]:
        rows = []
        for c in sorted(bucket, key=lambda x: (x["name"].lower(), x["file"])):
            rows.append([
                c["name"],
                purpose_hint(c["name"]),
                _channel_for_name(c["name"], c["file"]),
                _source_for_file(c["file"]),
                c["file"],
            ])
        return rows

    md = ["# Каталог классов и потоков (сгенерировано)",
          "",
          "Условные обозначения (Как создаётся):",
          "- Пользователь (UI/API)",
          "- Импорт (файл)",
          "- Система (сервис)",
          "- Код (внутр.)",
          "",
          "## 1) Доменные сущности (ORM, SQLAlchemy)",
          md_table(make_rows(domain)),
          "",
          "## 2) Сервисы и DAO",
          md_table(make_rows(services)),
          "",
          "## 3) ДТО/контракты API (Pydantic)",
          md_table(make_rows(dtos)),
          "",
          "## 4) Симуляция: датаклассы и движок",
          md_table(make_rows(sim)),
          ]
    return "\n".join(md)


def _categorize_classes(root_dir: str):
    """Возвращает категории классов: (domain, services, dtos, sim)."""
    classes = collect_classes(root_dir)

    def in_path(fp: str, part: str) -> bool:
        return part in fp.replace("\\", "/")

    domain, services, dtos, sim = [], [], [], []
    for c in classes:
        name, fp = c["name"], c["file"]
        lname = name.lower()
        if os.path.basename(fp) == "models.py" or any(k in lname for k in [
            "quarry", "shovel", "truck", "unload", "fuelstation", "idlearea",
            "trail", "scenario", "blasting", "plannedidle", "roadnet", "mapoverlay", "uploadedfile"
        ]):
            domain.append(c)
        elif in_path(fp, "/services/") or lname.endswith("dao") or lname.endswith("service"):
            services.append(c)
        elif in_path(fp, "forms.py") or any(k in lname for k in ["schema", "dto", "request", "response"]):
            dtos.append(c)
        elif in_path(fp, "/sim_engine/"):
            sim.append(c)
    key = lambda x: (x["name"].lower(), x["file"])
    return (sorted(domain, key=key), sorted(services, key=key), sorted(dtos, key=key), sorted(sim, key=key))


def generate_time_html_dynamic(root_dir: str) -> str:
    """Формирует HTML в том же макете, что и time.html, но на основе реального проекта."""
    domain, services, dtos, sim = _categorize_classes(root_dir)

    def purpose_hint(name: str) -> str:
        ln = name.lower()
        if "quarry" in ln: return "Контекст симуляции: таймзона, смены, перерывы"
        if "shovel" in ln: return "Узел погрузки"
        if "truck" in ln: return "Транспортировка груза"
        if "unload" in ln: return "Узел разгрузки/приёма"
        if "fuel" in ln: return "Узел дозаправки"
        if any(k in ln for k in ["idle", "lunch", "shift"]): return "Обед/пересменка/взрыв/ремонт зоны"
        if "trail" in ln or "route" in ln: return "Связка экскаватор–разгрузка + сегменты пути"
        if "scenario" in ln: return "Режим распределения, надёжность, связи"
        if "blasting" in ln: return "Окна блокировок и зоны работ"
        if "plannedidle" in ln: return "Запланированные остановки техники"
        if any(k in ln for k in ["roadnet", "overlay", "uploadedfile"]): return "География/подложки/файлы"
        if any(k in ln for k in ["service", "dao"]): return "Сервис/DAO"
        if any(k in ln for k in ["schema", "dto", "request", "response"]): return "DTO/Схема"
        if "sim" in ln: return "Симуляция"
        return "—"

    def tr(entity, kind):
        name, fp = entity["name"], entity["file"]
        return f"<tr><td>{name}</td><td>{purpose_hint(name)}</td><td>{_channel_for_name(name, fp)}</td><td>{_source_for_file(fp)}</td><td>{'UI → SimData' if kind=='domain' else ('API / сервисы' if kind!='sim' else 'Внутри симуляции')}</td><td>{'—'}</td></tr>"

    def section_rows(items, kind):
        return "\n".join(tr(it, kind) for it in items)

    html = f"""<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Каталог классов и потоков</title>
  <style>
    body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; line-height: 1.5; }}
    h1, h2, h3 {{ margin: 1.2em 0 0.6em; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px 10px; vertical-align: top; }}
    th {{ background: #f6f8fa; text-align: left; }}
    code {{ background: #f6f8fa; padding: 1px 4px; border-radius: 4px; }}
    ul {{ margin: 0.5em 0 1em 1.2em; }}
  </style>
</head>
<body>
  <h1>Каталог классов и потоков (читабельно для аналитика)</h1>

  <p><strong>Условные обозначения (Как создаётся):</strong></p>
  <ul>
    <li><strong>Пользователь (UI/API)</strong>: ввод вручную через интерфейс/формы или REST</li>
    <li><strong>Импорт (файл)</strong>: загрузка DXF/GeoJSON/изображений и т.п.</li>
    <li><strong>Система (сервис)</strong>: генерируется/обогащается приложением</li>
    <li><strong>Код (внутр.)</strong>: создаётся внутри симулятора/логики, не хранится в БД</li>
  </ul>

  <h2>1) Доменные сущности (ORM, SQLAlchemy)</h2>
  <table>
    <thead><tr>
      <th>Сущность</th><th>Назначение</th><th>Как создаётся</th><th>Источник данных</th><th>Потоки данных</th><th>Влияние</th>
    </tr></thead>
    <tbody>
      {section_rows(domain, 'domain')}
    </tbody>
  </table>

  <h2>2) Сервисы и DAO</h2>
  <table>
    <thead><tr>
      <th>Компонент</th><th>Назначение</th><th>Как создаётся</th><th>Источник данных</th><th>Потоки данных</th><th>Влияние</th>
    </tr></thead>
    <tbody>
      {section_rows(services, 'services')}
    </tbody>
  </table>

  <h2>3) ДТО/контракты API (Pydantic)</h2>
  <table>
    <thead><tr>
      <th>DTO</th><th>Назначение</th><th>Как создаётся</th><th>Источник данных</th><th>Потоки данных</th><th>Влияние</th>
    </tr></thead>
    <tbody>
      {section_rows(dtos, 'dtos')}
    </tbody>
  </table>

  <h2>4) Симуляция: датаклассы и движок</h2>
  <table>
    <thead><tr>
      <th>Компонент</th><th>Назначение</th><th>Как создаётся</th><th>Источник данных</th><th>Потоки данных</th><th>Влияние</th>
    </tr></thead>
    <tbody>
      {section_rows(sim, 'sim')}
    </tbody>
  </table>

  <h3>Примечания к потокам</h3>
  <ul>
    <li>Основной поток в симуляцию: API payload запуска → обогащение из БД (SimulationDAO: road_net, расписания) → SimDataSerializer → SimulationManager → Writer → Redis (meta, summary, events, batches).</li>
    <li>Основной поток для UI: /api/quarry-data (дефолтное время, шаблоны, списки объектов с маршрутами) + ручки: /api/schedule-data-by-date-shift, файлы/подложки.</li>
    <li>CRUD объектов и расписаний меняет БД и влияет на будущие входные данные симуляции и на данные UI-эндпоинтов.</li>
  </ul>

</body>
</html>
"""

def generate_time_md_static() -> str:
    """Генерирует точную копию содержимого time.md (как согласовано)."""
    return (
        "# Каталог классов и потоков (читабельно для аналитика)\n\n"
        "Условные обозначения (Как создаётся):\n"
        "- Пользователь (UI/API): ввод вручную через интерфейс/формы или REST\n"
        "- Импорт (файл): загрузка DXF/GeoJSON/изображений и т.п.\n"
        "- Система (сервис): генерируется/обогащается приложением\n"
        "- Код (внутр.): создаётся внутри симулятора/логики, не хранится в БД\n\n"
        "## 1) Доменные сущности (ORM, SQLAlchemy)\n\n"
        "| Сущность | Назначение | Как создаётся | Источник данных | Потоки данных | Влияние |\n"
        "|---|---|---|---|---|---|\n"
        "| Карьер (Quarry) | Контекст симуляции: таймзона, смены, перерывы | Пользователь (UI/API) | БД | UI (/api/quarry-data), Симуляция | Временные окна, обеды/пересменки |\n"
        "| Экскаватор (Shovel) | Узел погрузки | Пользователь (UI/API) | БД | UI → SimData | Производительность, цикл погрузки |\n"
        "| Самосвал (Truck) | Транспортировка груза | Пользователь (UI/API) | БД | UI → SimData | Скорости, топливо, надёжность |\n"
        "| Пункт разгрузки (Unload) | Узел разгрузки/приёма | Пользователь (UI/API) | БД | UI → SimData | Пропускная способность, очереди |\n"
        "| Заправка (FuelStation) | Узел дозаправки | Пользователь (UI/API) | БД | UI → SimData | События заправки |\n"
        "| Зона ожидания (IdleArea) | Обед/пересменка/взрыв/ремонт зоны | Пользователь (UI/API) | БД | UI → SimData | Остановки/ограничения |\n"
        "| Маршрут (Trail) | Связка экскаватор–разгрузка + сегменты пути | Пользователь (UI/API) | БД (raw_graph JSON) | UI (segments), SimData.routes | Маршрутизация |\n"
        "| Связь маршрут–самосвал–сценарий (TrailTruckAssociation) | Назначения самосвалов к маршрутам в сценарии | Пользователь (UI/API) | БД | Включается в trail.trucks → SimData | Распределение самосвалов |\n"
        "| Взрывные работы (Blasting) | Окна блокировок и зоны работ | Пользователь (UI/API) | БД (GeoJSON зон) | UI расписаний, Симуляция | Остановки/перенаправления |\n"
        "| Плановый простой (PlannedIdle) | Запланированные остановки техники | Пользователь (UI/API) | БД | UI расписаний, Симуляция | Доступность техники |\n"
        "| Сценарий (Scenario) | Режим распределения, надёжность, связи | Пользователь (UI/API) | БД | Запуск симуляции (options) | Алгоритм распределения |\n"
        "| Дорожная сеть (RoadNet) | География карьера (дороги/связи) | Импорт (файл) + Пользователь | БД (GeoJSON) | Добавляется в payload симуляции | Геометрия путей |\n"
        "| Подложка карты (MapOverlay) | Визуальная подложка (цвет/прозрачность/файл/geojson) | Импорт (файл) + Пользователь | БД + ФС (upload/) | UI карт | Визуализация (в симуляцию не идёт) |\n"
        "| Загруженный файл (UploadedFile) | Метаданные файла (имя/путь/размер) | Импорт (файл) | ФС (upload/) + БД | Ссылки из подложек/ручек файлов | Жизненный цикл файлов |\n"
        "| Шаблоны техники (Shovel/Truck/Unload/FuelStation Template) | Типовые параметры для создания объектов | Пользователь (UI/API) | БД | UI формы, создание объектов | Дефолты параметров |\n"
        "| Миксин дефолтов (DefaultValuesMixin) | Возвращает дефолтные значения полей моделей | Система (сервис) | ORM метаданные | API /api/defaults | Удобство UI |\n"
        "| Отображение типов (TYPE_MODEL_MAP / TYPE_SCHEDULE_MAP) | Карта «тип → модель» | Система (сервис) | Код | Роуты/сервисы | Корректная маршрутизация API |\n\n"
        "## 2) Сервисы и DAO\n\n"
        "| Компонент | Назначение | Как создаётся | Источник данных | Потоки данных | Влияние |\n"
        "|---|---|---|---|---|---|\n"
        "| Сервис данных карьера (QuarryDataService) | Собирает витрину карьера (объекты, маршруты, оверлеи) | Система (сервис) | БД | API /api/quarry-data → UI, симуляция | Актуальность входа |\n"
        "| DAO карьера (QuarryDAO) | Выборки простых сущностей/связей | Система | БД | Используется сервисом | Производительность выборок |\n"
        "| Сервис расписаний (ScheduleDataService) | Возвращает расписания по окну/смене | Система | БД + ShiftLogic | API расписаний | Корректность временных фильтров |\n"
        "| DAO расписаний (ScheduleDAO) | Фильтрация расписаний | Система | БД | В сервис расписаний | Данные для UI |\n"
        "| Сервис объектов (ObjectService) | Единая точка CRUD | Система | API payload | Коммит в БД | Консистентность домена |\n"
        "| DAO объектов (ObjectDAO) | Поиск/создание m2m, удаление | Система | БД | Используется сервисом | Привязки сценариев |\n"
        "| Сервис запуска симуляции (GetSimIdService) | Обогащает вход, запускает сим, пишет в Redis | Система | БД (RoadNet/расписания) + API payload | Redis meta/summary/events/batches | Доступ к результатам |\n"
        "| DAO симуляции (SimulationDAO) | Дорожная сеть и расписания для симуляции | Система | БД | В сервис запуска | Полнота входа |\n"
        "| Сервис шаблонов (AllTemplatesListService) | Витрина шаблонов | Система | БД | /api/quarry-data | Ускоряет ввод |\n"
        "| Сервис времени (StartEndTimeGenerateService) | Рекомендует временной диапазон | Система | Константы/время | /api/quarry-data | Удобство старта |\n\n"
        "## 3) ДТО/контракты API (Pydantic)\n\n"
        "| DTO | Назначение | Как создаётся | Источник данных | Потоки данных | Влияние |\n"
        "|---|---|---|---|---|---|\n"
        "| SimulationRequestDTO | Контракт запуска симуляции | Пользователь (UI/API) | API payload | В сервис запуска симуляции | Валидность входа |\n"
        "| QuarryDataResponse, TimeRange | Ответ витрины карьера | Система | Сервисы | UI | Полнота UI |\n"
        "| ScheduleDataRequest/Response | Контракт расписаний | Пользователь/Система | API query/БД | UI | Корректная фильтрация |\n"
        "| Формы объектов (…Schema) | Валидация и преобразования (segments→raw_graph и т.п.) | Пользователь (UI/API) | API payload | В ObjectService | Качество данных ORM |\n"
        "| Перечисления (PayloadType/UnloadType/TrailType) | Ограничения предметной области | Система | Константы | ORM/сериализация | Валидация/поведение |\n\n"
        "## 4) Симуляция: датаклассы и движок\n\n"
        "| Компонент | Назначение | Как создаётся | Источник данных | Потоки данных | Влияние |\n"
        "|---|---|---|---|---|---|\n"
        "| SimData | Единый вход симуляции | Код (внутр.) | Витрина + обогащение | В SimulationManager | Поведение всей симуляции |\n"
        "| Экскаватор/Самосвал/Разгрузка/Заправка (Shovel/Truck/Unload/FuelStation) | Акторы в модели | Код (внутр.) | SimData | Внутри симуляции | Движение/взаимодействие |\n"
        "| Маршрут (Route/Segment/Point) | Геометрия пути | Код (внутр.) | Trail.segments | В симуляцию | Траектории |\n"
        "| Зоны ожидания (IdleArea/Storage) | Зоны ограничений | Код (внутр.) | SimData | В симуляцию | Остановки/пути |\n"
        "| Расписания (PlannedIdle/Blasting) | Простои/взрывы | Код (внутр.) | БД → сериализация | В симуляцию | Доступность/блокировки |\n"
        "| Менеджер симуляции (SimulationManager) | Запуск/оркестрация/запись | Система | SimData + options | Writer → Redis | Результаты |\n"
        "| Поведения (Breakdown/Fuel/Lunch/PlannedIdle/Blasting) | Правила событий | Код (внутр.) | Конфиги и расписания | В симуляцию | Реализм и ограничения |\n"
        "| Расчёты (Truck/Shovel/Unload/Base) | Физика/тайминги | Код (внутр.) | Параметры объектов | В симуляцию | Длительности/расходы |\n"
        "| Состояния/События (States/Events) | СМ состояний и журнал | Код (внутр.) | Симуляция | В Writer | Телеметрия |\n"
        "| Writer (Batch/Dict) | Батч-запись результатов | Система | События симуляции | Redis | Доступность фронту |\n\n"
        "### Примечания к потокам\n"
        "- Основной поток в симуляцию: API payload запуска → обогащение из БД (SimulationDAO: road_net, расписания) → SimDataSerializer → SimulationManager → Writer → Redis (meta, summary, events, batches).\n"
        "- Основной поток для UI: /api/quarry-data (дефолтное время, шаблоны, списки объектов с маршрутами) + ручки: /api/schedule-data-by-date-shift, файлы/подложки.\n"
        "- CRUD объектов и расписаний меняет БД и влияет на будущие входные данные симуляции и на данные UI-эндпоинтов.\n"
    )


def generate_time_html_static() -> str:
    """Генерирует точную копию первого блока time.html (без дублирования документов)."""
    return """<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Каталог классов и потоков</title>
  <style>
    body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; line-height: 1.5; }
    h1, h2, h3 { margin: 1.2em 0 0.6em; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0 24px; }
    th, td { border: 1px solid #ddd; padding: 8px 10px; vertical-align: top; }
    th { background: #f6f8fa; text-align: left; }
    code { background: #f6f8fa; padding: 1px 4px; border-radius: 4px; }
    ul { margin: 0.5em 0 1em 1.2em; }
  </style>
</head>
<body>
  <h1>Каталог классов и потоков (читабельно для аналитика)</h1>

  <p><strong>Условные обозначения (Как создаётся):</strong></p>
  <ul>
    <li><strong>Пользователь (UI/API)</strong>: ввод вручную через интерфейс/формы или REST</li>
    <li><strong>Импорт (файл)</strong>: загрузка DXF/GeoJSON/изображений и т.п.</li>
    <li><strong>Система (сервис)</strong>: генерируется/обогащается приложением</li>
    <li><strong>Код (внутр.)</strong>: создаётся внутри симулятора/логики, не хранится в БД</li>
  </ul>

  <h2>1) Доменные сущности (ORM, SQLAlchemy)</h2>
  <table>
    <thead><tr>
      <th>Сущность</th><th>Назначение</th><th>Как создаётся</th><th>Источник данных</th><th>Потоки данных</th><th>Влияние</th>
    </tr></thead>
    <tbody>
      <tr><td>Карьер (Quarry)</td><td>Контекст симуляции: таймзона, смены, перерывы</td><td>Пользователь (UI/API)</td><td>БД</td><td>UI (/api/quarry-data), Симуляция</td><td>Временные окна, обеды/пересменки</td></tr>
      <tr><td>Экскаватор (Shovel)</td><td>Узел погрузки</td><td>Пользователь (UI/API)</td><td>БД</td><td>UI → SimData</td><td>Производительность, цикл погрузки</td></tr>
      <tr><td>Самосвал (Truck)</td><td>Транспортировка груза</td><td>Пользователь (UI/API)</td><td>БД</td><td>UI → SimData</td><td>Скорости, топливо, надёжность</td></tr>
      <tr><td>Пункт разгрузки (Unload)</td><td>Узел разгрузки/приёма</td><td>Пользователь (UI/API)</td><td>БД</td><td>UI → SimData</td><td>Пропускная способность, очереди</td></tr>
      <tr><td>Заправка (FuelStation)</td><td>Узел дозаправки</td><td>Пользователь (UI/API)</td><td>БД</td><td>UI → SimData</td><td>События заправки</td></tr>
      <tr><td>Зона ожидания (IdleArea)</td><td>Обед/пересменка/взрыв/ремонт зоны</td><td>Пользователь (UI/API)</td><td>БД</td><td>UI → SimData</td><td>Остановки/ограничения</td></tr>
      <tr><td>Маршрут (Trail)</td><td>Связка экскаватор–разгрузка + сегменты пути</td><td>Пользователь (UI/API)</td><td>БД (raw_graph JSON)</td><td>UI (segments), SimData.routes</td><td>Маршрутизация</td></tr>
      <tr><td>Связь маршрут–самосвал–сценарий (TrailTruckAssociation)</td><td>Назначения самосвалов к маршрутам в сценарии</td><td>Пользователь (UI/API)</td><td>БД</td><td>Включается в trail.trucks → SimData</td><td>Распределение самосвалов</td></tr>
      <tr><td>Взрывные работы (Blasting)</td><td>Окна блокировок и зоны работ</td><td>Пользователь (UI/API)</td><td>БД (GeoJSON зон)</td><td>UI расписаний, Симуляция</td><td>Остановки/перенаправления</td></tr>
      <tr><td>Плановый простой (PlannedIdle)</td><td>Запланированные остановки техники</td><td>Пользователь (UI/API)</td><td>БД</td><td>UI расписаний, Симуляция</td><td>Доступность техники</td></tr>
      <tr><td>Сценарий (Scenario)</td><td>Режим распределения, надёжность, связи</td><td>Пользователь (UI/API)</td><td>БД</td><td>Запуск симуляции (options)</td><td>Алгоритм распределения</td></tr>
      <tr><td>Дорожная сеть (RoadNet)</td><td>География карьера (дороги/связи)</td><td>Импорт (файл) + Пользователь</td><td>БД (GeoJSON)</td><td>Добавляется в payload симуляции</td><td>Геометрия путей</td></tr>
      <tr><td>Подложка карты (MapOverlay)</td><td>Визуальная подложка (цвет/прозрачность/файл/geojson)</td><td>Импорт (файл) + Пользователь</td><td>БД + ФС (upload/)</td><td>UI карт</td><td>Визуализация (в симуляцию не идёт)</td></tr>
      <tr><td>Загруженный файл (UploadedFile)</td><td>Метаданные файла (имя/путь/размер)</td><td>Импорт (файл)</td><td>ФС (upload/) + БД</td><td>Ссылки из подложек/ручек файлов</td><td>Жизненный цикл файлов</td></tr>
      <tr><td>Шаблоны техники (Shovel/Truck/Unload/FuelStation Template)</td><td>Типовые параметры для создания объектов</td><td>Пользователь (UI/API)</td><td>БД</td><td>UI формы, создание объектов</td><td>Дефолты параметров</td></tr>
      <tr><td>Миксин дефолтов (DefaultValuesMixin)</td><td>Возвращает дефолтные значения полей моделей</td><td>Система (сервис)</td><td>ORM метаданные</td><td>API /api/defaults</td><td>Удобство UI</td></tr>
      <tr><td>Отображение типов (TYPE_MODEL_MAP / TYPE_SCHEDULE_MAP)</td><td>Карта «тип → модель»</td><td>Система (сервис)</td><td>Код</td><td>Роуты/сервисы</td><td>Корректная маршрутизация API</td></tr>
    </tbody>
  </table>

  <h2>2) Сервисы и DAO</h2>
  <table>
    <thead><tr>
      <th>Компонент</th><th>Назначение</th><th>Как создаётся</th><th>Источник данных</th><th>Потоки данных</th><th>Влияние</th>
    </tr></thead>
    <tbody>
      <tr><td>Сервис данных карьера (QuarryDataService)</td><td>Собирает витрину карьера (объекты, маршруты, оверлеи)</td><td>Система (сервис)</td><td>БД</td><td>API /api/quarry-data → UI, симуляция</td><td>Актуальность входа</td></tr>
      <tr><td>DAO карьера (QuarryDAO)</td><td>Выборки простых сущностей/связей</td><td>Система</td><td>БД</td><td>Используется сервисом</td><td>Производительность выборок</td></tr>
      <tr><td>Сервис расписаний (ScheduleDataService)</td><td>Возвращает расписания по окну/смене</td><td>Система</td><td>БД + ShiftLogic</td><td>API расписаний</td><td>Корректность временных фильтров</td></tr>
      <tr><td>DAO расписаний (ScheduleDAO)</td><td>Фильтрация расписаний</td><td>Система</td><td>БД</td><td>В сервис расписаний</td><td>Данные для UI</td></tr>
      <tr><td>Сервис объектов (ObjectService)</td><td>Единая точка CRUD</td><td>Система</td><td>API payload</td><td>Коммит в БД</td><td>Консистентность домена</td></tr>
      <tr><td>DAO объектов (ObjectDAO)</td><td>Поиск/создание m2m, удаление</td><td>Система</td><td>БД</td><td>Используется сервисом</td><td>Привязки сценариев</td></tr>
      <tr><td>Сервис запуска симуляции (GetSimIdService)</td><td>Обогащает вход, запускает сим, пишет в Redis</td><td>Система</td><td>БД (RoadNet/расписания) + API payload</td><td>Redis meta/summary/events/batches</td><td>Доступ к результатам</td></tr>
      <tr><td>DAO симуляции (SimulationDAO)</td><td>Дорожная сеть и расписания для симуляции</td><td>Система</td><td>БД</td><td>В сервис запуска</td><td>Полнота входа</td></tr>
      <tr><td>Сервис шаблонов (AllTemplatesListService)</td><td>Витрина шаблонов</td><td>Система</td><td>БД</td><td>/api/quarry-data</td><td>Ускоряет ввод</td></tr>
      <tr><td>Сервис времени (StartEndTimeGenerateService)</td><td>Рекомендует временной диапазон</td><td>Система</td><td>Константы/время</td><td>/api/quarry-data</td><td>Удобство старта</td></tr>
    </tbody>
  </table>

  <h2>3) ДТО/контракты API (Pydantic)</h2>
  <table>
    <thead><tr>
      <th>DTO</th><th>Назначение</th><th>Как создаётся</th><th>Источник данных</th><th>Потоки данных</th><th>Влияние</th>
    </tr></thead>
    <tbody>
      <tr><td>SimulationRequestDTO</td><td>Контракт запуска симуляции</td><td>Пользователь (UI/API)</td><td>API payload</td><td>В сервис запуска симуляции</td><td>Валидность входа</td></tr>
      <tr><td>QuarryDataResponse, TimeRange</td><td>Ответ витрины карьера</td><td>Система</td><td>Сервисы</td><td>UI</td><td>Полнота UI</td></tr>
      <tr><td>ScheduleDataRequest/Response</td><td>Контракт расписаний</td><td>Пользователь/Система</td><td>API query/БД</td><td>UI</td><td>Корректная фильтрация</td></tr>
      <tr><td>Формы объектов (…Schema)</td><td>Валидация и преобразования (segments→raw_graph и т.п.)</td><td>Пользователь (UI/API)</td><td>API payload</td><td>В ObjectService</td><td>Качество данных ORM</td></tr>
      <tr><td>Перечисления (PayloadType/UnloadType/TrailType)</td><td>Ограничения предметной области</td><td>Система</td><td>Константы</td><td>ORM/сериализация</td><td>Валидация/поведение</td></tr>
    </tbody>
  </table>

  <h2>4) Симуляция: датаклассы и движок</h2>
  <table>
    <thead><tr>
      <th>Компонент</th><th>Назначение</th><th>Как создаётся</th><th>Источник данных</th><th>Потоки данных</th><th>Влияние</th>
    </tr></thead>
    <tbody>
      <tr><td>SimData</td><td>Единый вход симуляции</td><td>Код (внутр.)</td><td>Витрина + обогащение</td><td>В SimulationManager</td><td>Поведение всей симуляции</td></tr>
      <tr><td>Экскаватор/Самосвал/Разгрузка/Заправка (Shovel/Truck/Unload/FuelStation)</td><td>Акторы в модели</td><td>Код (внутр.)</td><td>SimData</td><td>Внутри симуляции</td><td>Движение/взаимодействие</td></tr>
      <tr><td>Маршрут (Route/Segment/Point)</td><td>Геометрия пути</td><td>Код (внутр.)</td><td>Trail.segments</td><td>В симуляцию</td><td>Траектории</td></tr>
      <tr><td>Зоны ожидания (IdleArea/Storage)</td><td>Зоны ограничений</td><td>Код (внутр.)</td><td>SimData</td><td>В симуляцию</td><td>Остановки/пути</td></tr>
      <tr><td>Расписания (PlannedIdle/Blasting)</td><td>Простои/взрывы</td><td>Код (внутр.)</td><td>БД → сериализация</td><td>В симуляцию</td><td>Доступность/блокировки</td></tr>
      <tr><td>Менеджер симуляции (SimulationManager)</td><td>Запуск/оркестрация/запись</td><td>Система</td><td>SimData + options</td><td>Writer → Redis</td><td>Результаты</td></tr>
      <tr><td>Поведения (Breakdown/Fuel/Lunch/PlannedIdle/Blasting)</td><td>Правила событий</td><td>Код (внутр.)</td><td>Конфиги и расписания</td><td>В симуляцию</td><td>Реализм и ограничения</td></tr>
      <tr><td>Расчёты (Truck/Shovel/Unload/Base)</td><td>Физика/тайминги</td><td>Код (внутр.)</td><td>Параметры объектов</td><td>В симуляцию</td><td>Длительности/расходы</td></tr>
      <tr><td>Состояния/События (States/Events)</td><td>СМ состояний и журнал</td><td>Код (внутр.)</td><td>Симуляция</td><td>В Writer</td><td>Телеметрия</td></tr>
      <tr><td>Writer (Batch/Dict)</td><td>Батч-запись результатов</td><td>Система</td><td>События симуляции</td><td>Redis</td><td>Доступность фронту</td></tr>
    </tbody>
  </table>

  <h3>Примечания к потокам</h3>
  <ul>
    <li>Основной поток в симуляцию: API payload запуска → обогащение из БД (SimulationDAO: road_net, расписания) → SimDataSerializer → SimulationManager → Writer → Redis (meta, summary, events, batches).</li>
    <li>Основной поток для UI: /api/quarry-data (дефолтное время, шаблоны, списки объектов с маршрутами) + ручки: /api/schedule-data-by-date-shift, файлы/подложки.</li>
    <li>CRUD объектов и расписаний меняет БД и влияет на будущие входные данные симуляции и на данные UI-эндпоинтов.</li>
  </ul>

</body>
</html>
"""

if __name__ == "__main__":
    # По умолчанию анализируем локальный каталог qsimmine12, если он есть
    default_path = os.path.join(os.getcwd(), "qsimmine12")
    project_path = os.environ.get("PROJECT_PATH", default_path)

    if not os.path.isdir(project_path):
        print("Папка не найдена! Проверь PROJECT_PATH или наличие qsimmine12 в текущей директории.")
        exit(1)

    print("Запуск анализа проекта...")
    all_data = analyze_project(project_path)

    # --- 1. Полные метаданные ---
    with open("project_metadata_full.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    # (пропускаем генерацию call_graph.*, project_analysis.md, module_dependencies.json)

    # --- 2. Бизнес-таблица по классам (эвристики) ---
    class_list = collect_classes(project_path)
    business_md = _infer_business_table(class_list)
    # (не сохраняем отдельным файлом)

    # --- 3. Полные читабельные таблицы (как time.md) ---
    # Режим выбирается переменной окружения DYNAMIC_TABLES=1
    dynamic = os.environ.get("DYNAMIC_TABLES") == "1"
    if dynamic:
        # Динамически собираем из кода проекта
        with open("time.md", "w", encoding="utf-8") as f:
            f.write(generate_analyst_markdown(project_path))
        with open("time.html", "w", encoding="utf-8") as f:
            f.write(generate_time_html_dynamic(project_path))
        with open("analyst_tables.md", "w", encoding="utf-8") as f:
            f.write(generate_analyst_markdown(project_path))
    else:
        # Фиксированная эталонная версия
        with open("time.md", "w", encoding="utf-8") as f:
            f.write(generate_time_md_static())
        with open("time.html", "w", encoding="utf-8") as f:
            f.write(generate_time_html_static())
        with open("analyst_tables.md", "w", encoding="utf-8") as f:
            f.write(generate_time_md_static())

    # --- 4. Две PlantUML схемы ---
    with open("architecture_overview.puml", "w", encoding="utf-8") as f:
        f.write(generate_plantuml_overview())
    with open("simulation_sequence.puml", "w", encoding="utf-8") as f:
        f.write(generate_plantuml_sequence())

    # --- Статистика ---
    total_files = len([d for d in all_data if "error" not in d])
    total_funcs = sum(len(d["functions"]) for d in all_data if "functions" in d)

    print("\nГОТОВО!")
    print(f"  • Файлов обработано: {total_files}")
    print(f"  • Функций найдено: {total_funcs}")
    print("\n  Выходные файлы:")
    print("    - project_metadata_full.json")
    print("    - project_metadata_full.json")
    print("    - time.md                ← таблицы (Markdown, статические или динамические)")
    print("    - time.html              ← таблицы (HTML, статические или динамические)")
    print("    - architecture_overview.puml   ← Компоненты и потоки")
    print("    - simulation_sequence.puml     ← Последовательность запуска симуляции")