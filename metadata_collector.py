import ast
import os
import json
from typing import List, Dict, Any

class FunctionVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.functions: List[Dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # === Аргументы ===
        args = []
        # Добавляем self для методов
        if node.args.args and node.args.args[0].arg == 'self':
            args.append('self')
            args.extend([arg.arg for arg in node.args.args[1:]])
        else:
            args.extend([arg.arg for arg in node.args.args])

        # === Возвращаемый тип (аннотация) ===
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)

        # === Docstring ===
        docstring = ast.get_docstring(node)

        # === Простые return (по желанию) ===
        returns = []
        for n in ast.walk(node):
            if isinstance(n, ast.Return) and n.value:
                try:
                    returns.append(ast.unparse(n.value))
                except:
                    returns.append("<complex>")

        self.functions.append({
            "file_path": self.file_path,
            "function_name": node.name,
            "arguments": args,
            "return_type": return_type,
            "returns": returns[:3],  # первые 3
            "docstring": docstring,
            "line_start": node.lineno,
            "line_end": node.end_lineno
        })
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)  # обрабатываем как обычную

def analyze_file(file_path: str) -> List[Dict[str, Any]]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
    except Exception as e:
        print(f"Ошибка: {file_path} — {e}")
        return []

    visitor = FunctionVisitor(file_path)
    visitor.visit(tree)
    return visitor.functions

def analyze_project(root_dir: str) -> List[Dict[str, Any]]:
    all_funcs = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                path = os.path.join(subdir, file)
                print(f"→ {path}")
                funcs = analyze_file(path)
                all_funcs.extend(funcs)
    return all_funcs

if __name__ == "__main__":
    project_path = "qsimmine12"
    if not os.path.isdir(project_path):
        print("Папка не найдена!")
    else:
        data = analyze_project(project_path)
        with open("project_metadata_full.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nГОТОВО! Найдено функций: {len(data)}")
        print("Файл: project_metadata_full.json")