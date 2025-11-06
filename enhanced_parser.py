#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import os
import json
import re
from typing import List, Dict, Set, Optional
from collections import defaultdict

class UltimateProjectAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path: str, project_root: str):
        self.file_path = file_path
        self.project_root = project_root
        self.relative_path = os.path.relpath(file_path, project_root)
        self.module_name = self.relative_path.replace(os.sep, ".").replace(".py", "")
        self.functions = []
        self.classes = []
        self.imports = []
        self.current_function = None
        self.class_stack = []
        self.current_calls = []
        self.current_data_flow = []
        self.unresolved_calls: Set[str] = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append({'type': 'import', 'name': alias.name, 'alias': alias.asname})
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                self.imports.append({'type': 'from', 'module': node.module, 'name': alias.name, 'alias': alias.asname})
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        class_info = {
            "name": node.name,
            "bases": [self._unparse(b) for b in node.bases],
            "file_path": self.file_path,
            "line_start": node.lineno,
            "methods": []
        }
        self.classes.append(class_info)
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.current_calls = []
        self.current_data_flow = []
        self.generic_visit(node)
        self._process_function(node)
        self.current_function = None

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def _process_function(self, node):
        args_full = []
        defaults = node.args.defaults if node.args.defaults else []
        for i, arg in enumerate(node.args.args):
            arg_info = {"name": arg.arg}
            if arg.annotation:
                arg_info["type"] = self._unparse(arg.annotation)
            def_idx = i - (len(node.args.args) - len(defaults))
            if def_idx >= 0:
                arg_info["default"] = self._unparse(defaults[def_idx]) if defaults[def_idx] else None
            args_full.append(arg_info)
        return_type = self._unparse(node.returns) if node.returns else None
        returns = [self._unparse(stmt.value) for stmt in node.body if isinstance(stmt, ast.Return) and stmt.value]
        docstring = ast.get_docstring(node)
        kpi_mentions = self._extract_kpi_from_docstring(docstring) if docstring else []
        decorators = [self._unparse(d) for d in node.decorator_list]
        current_class = self.class_stack[-1] if self.class_stack else None
        func_data = {
            "file_path": self.file_path,
            "module": self.module_name,
            "class_name": current_class,
            "function_name": node.name,
            "arguments": args_full,
            "return_type": return_type,
            "returns": returns,
            "docstring": docstring,
            "decorators": decorators,
            "calls": self.current_calls,
            "data_flow": self.current_data_flow,
            "kpi": kpi_mentions,
            "line_start": node.lineno,
            "line_end": getattr(node, "end_lineno", node.lineno)
        }
        self.functions.append(func_data)
        if current_class:
            for cls in self.classes:
                if cls["name"] == current_class:
                    cls["methods"].append(func_data)

    def visit_Call(self, node):
        if self.current_function:
            call_info = self._resolve_call_precise(node)
            if call_info:
                self.current_calls.append(call_info["called"])
                self.current_data_flow.append(call_info)
            elif isinstance(node.func, (ast.Name, ast.Attribute)):
                self.unresolved_calls.add(self._unparse(node.func))
        self.generic_visit(node)

    def _resolve_call_precise(self, node):
        if isinstance(node.func, ast.Name):
            return {"called": node.func.id, "args": [self._unparse(a) for a in node.args]}
        elif isinstance(node.func, ast.Attribute):
            full_attr_chain = self._get_full_attr_chain(node.func)
            if full_attr_chain:
                return {"called": ".".join(full_attr_chain), "args": [self._unparse(a) for a in node.args]}
        return None

    def _unparse(self, node: Optional[ast.AST]) -> str:
        if node is None:
            return ""
        try:
            return ast.unparse(node)
        except Exception:
            return str(node)

    def _get_full_attr_chain(self, node: ast.Attribute) -> List[str]:
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return list(reversed(parts))

    def _extract_kpi_from_docstring(self, docstring: str) -> List[str]:
        kpi_keywords = ["payload", "capacity", "speed", "cycle", "downtime", "throughput", "time", "utilization", "productivity"]
        found = [k for k in kpi_keywords if k in docstring.lower()]
        return found

def analyze_project_for_business_table(root_dir: str) -> List[Dict]:
    print("Сбор бизнес-данных из проекта...")
    index = {"functions": defaultdict(list), "classes": defaultdict(list), "imports": defaultdict(list)}
    
    # Сканируем проект
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(subdir, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    tree = ast.parse(content)
                    analyzer = UltimateProjectAnalyzer(path, root_dir)
                    analyzer.visit(tree)
                    module_name = analyzer.module_name
                    for func in analyzer.functions:
                        full_name = ".".join(filter(None, [module_name, func['class_name'], func['function_name']]))
                        index["functions"][full_name].append(func)
                    for cls in analyzer.classes:
                        full_name = f"{module_name}.{cls['name']}"
                        index["classes"][full_name].append(cls)
                    index["imports"][module_name] = analyzer.imports
                except Exception as e:
                    print(f"Ошибка при индексации {path}: {e}")

    # Формируем бизнес-таблицу
    entity_map = {
        'quarry': 'Карьер', 'truck': 'Самосвал', 'shovel': 'Экскаватор', 'unload': 'Пункт Разгрузки',
        'scenario': 'Сценарий', 'idlearea': 'Зона простоя', 'fuelstation': 'Заправка',
        'blast': 'Взрывные работы'
    }
    entities_table = []
    processed_entities = set()
    for cls_full, cls_data_list in index["classes"].items():
        if not cls_data_list:
            continue
        cls_data = cls_data_list[0]
        cls_name = cls_data["name"]
        # Пропускаем вспомогательные классы
        if any(suffix in cls_name.lower() for suffix in ['mixin', 'template', 'args', 'base']):
            continue
        business_entity_name = None
        for key, name in entity_map.items():
            if key in cls_name.lower() and name not in processed_entities:
                business_entity_name = name
                break
        if not business_entity_name or business_entity_name not in entity_map.values():
            continue

        entity_row = {
            "Сущность": f"{business_entity_name} (Backend: {cls_name})",
            "Зачем нужна": _assess_business_purpose(cls_name),
            "Создание": _detect_creation_method_precise(cls_name, index),
            "Откуда пришло": _detect_source_precise(cls_name, index),
            "Куда уходит": _detect_flow_precise(cls_name, index),
            "Влияние": _detect_influence_precise(cls_name, index),
        }
        entities_table.append(entity_row)
        processed_entities.add(business_entity_name)
    
    return entities_table

def _assess_business_purpose(cls_name: str) -> str:
    purposes = {
        "Quarry": "Центральный объект. Определяет настройки карьера (местоположение, смены, часовой пояс).",
        "Truck": "Основной транспорт. Перевозит породу от экскаватора к пункту разгрузки.",
        "Shovel": "Ключевое оборудование. Загружает самосвалы, определяет темп цикла.",
        "Unload": "Точка разгрузки. Завершает цикл транспортировки.",
        "Scenario": "Конфигурация симуляции. Задаёт параметры для моделирования.",
        "IdleArea": "Зона для простоев техники (ремонт, смены).",
        "FuelStation": "Заправка. Управляет топливными операциями.",
        "Blasting": "Взрывные работы. Блокирует зоны, влияет на простои."
    }
    return purposes.get(cls_name, "Вспомогательный объект системы.")

def _detect_creation_method_precise(cls_name: str, index: Dict) -> str:
    creators = set()
    for func_full, func_list in index["functions"].items():
        for func in func_list:
            for call in func.get("calls", []):
                if call == cls_name or call.endswith(f".{cls_name}"):
                    module = func_full.split('.')[0]
                    if "routes" in module or "api" in module:
                        creators.add("Вручную через API/форму")
                    if "object_service" in module:
                        creators.add("Автоматически через сервисный слой")
                    if "forms" in module or "schema" in func["module"]:
                        creators.add(f"Вручную через форму {cls_name}Schema")
                    if "migrations" in module:
                        creators.add("Автоматически через миграции БД")
            if func["class_name"] == cls_name and func["function_name"] == "__init__":
                for arg in func["arguments"]:
                    if "template" in arg["name"].lower():
                        creators.add("Вручную из шаблона")
                    if "schedule" in arg["name"].lower():
                        creators.add("Автоматически по расписанию")
    return ", ".join(creators) or "Вручную через форму"

def _detect_source_precise(cls_name: str, index: Dict) -> str:
    sources = set()
    for func_full, func_list in index["functions"].items():
        for func in func_list:
            if func['class_name'] == cls_name and func['function_name'] == '__init__':
                for arg in func["arguments"]:
                    if arg['name'] != 'self':
                        arg_type = arg.get("type", arg["name"]).lower()
                        if "schema" in arg_type:
                            sources.add(f"Форма {cls_name}Schema")
                        elif "template" in arg_type:
                            sources.add("Шаблон")
                        elif "quarry" in arg_type:
                            sources.add("Настройки карьера")
                        elif "schedule" in arg_type:
                            sources.add("Расписание")
                        else:
                            sources.add("Пользователь/база данных")
    return ", ".join(sources) or "Пользователь/база данных"

def _detect_flow_precise(cls_name: str, index: Dict) -> str:
    flows = []
    for func_full, func_data_list in index["functions"].items():
        for func in func_data_list:
            for call_info in func.get("data_flow", []):
                if call_info and cls_name in str(call_info.get("args", [])):
                    caller_module = func['module']
                    if "sim_engine" in caller_module:
                        flows.append("Используется в SimEngine (симуляция)")
                    elif "routes" in caller_module or "api" in caller_module:
                        flows.append("Передаётся во фронтенд через API")
                    elif "scenario_service" in caller_module:
                        flows.append("Передаётся в сценарии моделирования")
                    else:
                        flows.append(f"Передаётся в {caller_module}")
            if func["class_name"] == cls_name:
                for ret in func["returns"]:
                    if "telemetry" in ret.lower():
                        flows.append("Логируется в телеметрию")
    if cls_name == "Quarry":
        flows.append("Фильтр для всех объектов (quarry_id)")
    elif cls_name == "Scenario":
        flows.append("Управляет симуляцией")
    return "; ".join(set(flows)) or "Сохраняется в базу данных"

def _detect_influence_precise(cls_name: str, index: Dict) -> str:
    influences = []
    if cls_name == "Quarry":
        influences.append("Центральная сущность. Все объекты привязаны через quarry_id.")
    elif cls_name == "Truck":
        influences.append("Влияет на Экскаватор (загрузка) и Пункт разгрузки (разгрузка) через цикл.")
    elif cls_name == "Shovel":
        influences.append("Определяет скорость загрузки самосвалов, влияет на время цикла.")
    elif cls_name == "Unload":
        influences.append("Завершает цикл, влияет на простои через взрывные работы.")
    elif cls_name == "IdleArea":
        influences.append("Управляет простоями техники (ремонт, смены).")
    elif cls_name == "FuelStation":
        influences.append("Влияет на простои и затраты на топливо.")
    elif cls_name == "Blasting":
        influences.append("Блокирует зоны, вызывает простои.")
    elif cls_name == "Scenario":
        influences.append("Определяет параметры всей симуляции.")
    for func_full, func_list in index["functions"].items():
        for func in func_list:
            if "quarry_id" in str(func) and cls_name in str(func):
                influences.append("Связывает объекты через quarry_id.")
    return "; ".join(set(influences)) or "Локальное влияние внутри модуля"

def _collect_kpi_precise(cls_name: str, index: Dict) -> str:
    kpis = set()
    kpi_keywords = ["payload", "capacity", "speed", "cycle", "downtime", "throughput", "time", "utilization", "productivity"]
    for func_full, func_data_list in index["functions"].items():
        for func in func_data_list:
            if func['class_name'] == cls_name:
                for arg in func["arguments"]:
                    if any(k in arg["name"].lower() for k in kpi_keywords):
                        kpis.add(f"{arg['name'].title()} ({arg['name']})")
                for ret in func["returns"]:
                    if isinstance(ret, str):
                        keys = re.findall(r"'(\w*?_(?:time|speed|payload|capacity|utilization|productivity))'", ret)
                        kpis.update([f"{k.title()} ({k})" for k in keys])
                if "telemetry" in str(func["returns"]).lower():
                    keys = re.findall(r"'(\w*?_(?:time|speed|payload|capacity|utilization|productivity))'", str(func["returns"]))
                    kpis.update([f"{k.title()} ({k})" for k in keys])
    # Добавляем типичные KPI для карьера
    if cls_name == "Quarry":
        kpis.update(["Производительность (tonnage_per_hour)", "Общая эффективность (utilization)"])
    elif cls_name == "Truck":
        kpis.update(["Грузоподъёмность (body_capacity)", "Скорость (speed)", "Время цикла (cycle_time)", "Расход топлива (fuel_consumption)", "Простои (downtime)"])
    elif cls_name == "Shovel":
        kpis.update(["Объём ковша (bucket_volume)", "Время загрузки (dig_time)", "Производительность (shovel_productivity)"])
    elif cls_name == "Unload":
        kpis.update(["Время разгрузки (unload_time)", "Простои от взрывов (blast_downtime)"])
    elif cls_name == "IdleArea":
        kpis.update(["Время простоев (idle_time)", "Использование зон (area_utilization)"])
    elif cls_name == "FuelStation":
        kpis.update(["Расход топлива (fuel_rate)", "Время заправки (refuel_time)"])
    elif cls_name == "Blasting":
        kpis.update(["Время взрыва (blast_duration)", "Простои от взрывов (blast_downtime)"])
    elif cls_name == "Scenario":
        kpis.update(["Производительность (scenario_productivity)", "Эффективность (scenario_efficiency)", "Простои (scenario_downtime)"])
    return ", ".join(sorted(list(kpis))) or "Не определены"

def generate_business_table(entities: List[Dict]) -> str:
    headers = [
        "Сущность", "Зачем нужна",
        "Создание", "Откуда пришло",
        "Куда уходит", "Влияние"
    ]
    lines = ["| " + " | ".join(headers) + " |",
             "| " + " | ".join(["---"] * len(headers)) + " |"]
    for e in entities:
        lines.append("| " + " | ".join(str(e[h]) for h in headers) + " |")
    return "\n".join(lines)

if __name__ == "__main__":
    project_path = r"D:\Work\twin_carier_x2\qsimmine12"
    if not os.path.isdir(project_path):
        print(f"Ошибка: Проект не найден по пути {project_path}")
        exit(1)
    print("Запуск бизнес-анализатора...")
    entities_data = analyze_project_for_business_table(project_path)
    table_md = generate_business_table(entities_data)
    with open("business_table.md", "w", encoding="utf-8") as f:
        f.write(table_md)
    with open("business_data.json", "w", encoding="utf-8") as f:
        json.dump(entities_data, f, ensure_ascii=False, indent=2)
    print("\nГОТОВО!")
    print(f" • Сущностей обработано: {len(entities_data)}")
    print(" • Выходные файлы: business_table.md, business_data.json")