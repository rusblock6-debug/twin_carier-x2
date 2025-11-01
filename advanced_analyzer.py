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
# 8. Главный запуск
# ==============================
if __name__ == "__main__":
    # УКАЖИ СВОЙ ПУТЬ ЗДЕСЬ (используй raw-строку или /)
    project_path = r"C:\Сторонние\Цифровой двойник - документация\qsimmine12"

    if not os.path.isdir(project_path):
        print("Папка не найдена! Проверь путь.")
        exit(1)

    print("Запуск анализа проекта...")
    all_data = analyze_project(project_path)

    # --- 1. Полные метаданные ---
    with open("project_metadata_full.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    # --- 2. Граф вызовов (JSON + DOT) ---
    call_graph = build_call_graph(all_data)
    with open("call_graph.json", "w", encoding="utf-8") as f:
        json.dump(call_graph, f, indent=2, ensure_ascii=False)

    dot_content = generate_dot_graph(call_graph)
    with open("call_graph.dot", "w", encoding="utf-8") as f:
        f.write(dot_content)

    # --- 3. Markdown-документация ---
    md_content = generate_markdown(all_data)
    with open("project_analysis.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    # --- 4. Зависимости модулей ---
    mod_deps = module_dependencies(all_data)
    with open("module_dependencies.json", "w", encoding="utf-8") as f:
        json.dump(mod_deps, f, indent=2, ensure_ascii=False)

    # --- Статистика ---
    total_files = len([d for d in all_data if "error" not in d])
    total_funcs = sum(len(d["functions"]) for d in all_data if "functions" in d)

    print("\nГОТОВО!")
    print(f"  • Файлов обработано: {total_files}")
    print(f"  • Функций найдено: {total_funcs}")
    print("\n  Выходные файлы:")
    print("    - project_metadata_full.json")
    print("    - call_graph.json")
    print("    - call_graph.dot   ← открой в Graphviz или VS Code")
    print("    - project_analysis.md")
    print("    - module_dependencies.json")
    print("\n  Для PNG: dot -Tpng call_graph.dot -o call_graph.png")