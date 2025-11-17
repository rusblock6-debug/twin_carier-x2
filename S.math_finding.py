#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S.math_finding.py
=================

Поиск и документация всех математических формул в проекте.
Скрипт рекурсивно сканирует указанный каталог (по умолчанию `qsimmine12`),
отыскивает математические выражения в Python-файлах и сохраняет результат
в Markdown-таблицу `S.Формулы.md`.
"""

from __future__ import annotations

import argparse
import ast
import itertools
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


MATH_FUNC_NAMES: Set[str] = {
    "abs", "acos", "asin", "atan", "atan2", "ceil", "copysign", "cos", "cosh",
    "degrees", "exp", "floor", "fmod", "frexp", "fsum", "gamma", "hypot",
    "isfinite", "isinf", "isnan", "ldexp", "lgamma", "log", "log10", "log1p",
    "log2", "modf", "pow", "radians", "sin", "sinh", "sqrt", "tan", "tanh",
    "trunc", "sum", "min", "max", "mean", "median", "variance", "stdev"
}

OPERATOR_NAMES: Dict[type, str] = {
    ast.Add: "сложение",
    ast.Sub: "вычитание",
    ast.Mult: "умножение",
    ast.Div: "деление",
    ast.FloorDiv: "целочисленное деление",
    ast.Mod: "остаток",
    ast.Pow: "степень",
    ast.MatMult: "матричное умножение",
    ast.BitOr: "побитовое ИЛИ",
    ast.BitAnd: "побитовое И",
    ast.BitXor: "побитовое XOR",
    ast.LShift: "сдвиг влево",
    ast.RShift: "сдвиг вправо",
}


def iter_py_files(root: Path) -> Iterable[Path]:
    """Возвращает python-файлы, исключая служебные каталоги."""
    skip_parts = {"__pycache__", ".git", ".hg", ".svn", ".mypy_cache", ".pytest_cache", "venv", ".venv", "env"}
    for path in root.rglob("*.py"):
        if any(part in skip_parts for part in path.parts):
            continue
        yield path


def is_math_expression(node: ast.AST) -> bool:
    """Эвристика: содержит ли выражение математические операции."""
    if isinstance(node, (ast.BinOp, ast.UnaryOp, ast.AugAssign)):
        return True
    if isinstance(node, ast.Call):
        func_name = get_call_name(node)
        if func_name and any(func_name.endswith(name) for name in MATH_FUNC_NAMES):
            return True
        return any(is_math_expression(arg) for arg in node.args)
    if isinstance(node, ast.Compare):
        return any(isinstance(op, (ast.Lt, ast.Gt, ast.LtE, ast.GtE)) for op in node.ops)
    if isinstance(node, (ast.IfExp, ast.DictComp, ast.ListComp, ast.GeneratorExp, ast.SetComp)):
        return True
    return False


def get_call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return f"{get_attribute_full_name(node.func)}"
    return ""


def get_attribute_full_name(node: ast.Attribute) -> str:
    value = node.value
    if isinstance(value, ast.Name):
        return f"{value.id}.{node.attr}"
    if isinstance(value, ast.Attribute):
        return f"{get_attribute_full_name(value)}.{node.attr}"
    return node.attr


def collect_dependencies(node: ast.AST) -> Set[str]:
    """Собирает имена переменных, задействованных в выражении."""
    names: Set[str] = set()

    class NameCollector(ast.NodeVisitor):
        def visit_Name(self, name_node: ast.Name) -> None:
            if isinstance(name_node.ctx, ast.Load):
                names.add(name_node.id)
            self.generic_visit(name_node)

    NameCollector().visit(node)
    return names


def collect_operator_labels(node: ast.AST) -> Set[str]:
    """Возвращает множество задействованных операторов (в словесном виде)."""
    labels: Set[str] = set()

    class OperatorCollector(ast.NodeVisitor):
        def visit_BinOp(self, bin_node: ast.BinOp) -> None:
            labels.add(OPERATOR_NAMES.get(type(bin_node.op), type(bin_node.op).__name__))
            self.generic_visit(bin_node)

        def visit_UnaryOp(self, unary_node: ast.UnaryOp) -> None:
            op_type = type(unary_node.op)
            labels.add({
                ast.UAdd: "унарное +",
                ast.USub: "унарное -",
                ast.Not: "логическое не",
                ast.Invert: "битовое НЕ",
            }.get(op_type, op_type.__name__))
            self.generic_visit(unary_node)

    OperatorCollector().visit(node)
    return labels


def extract_source_segment(source: str, node: ast.AST) -> str:
    """Возвращает исходный код для узла (с запасом)."""
    segment = ast.get_source_segment(source, node)
    if segment:
        return segment.strip()
    # fallback: взять строку по номеру
    if hasattr(node, "lineno"):
        lines = source.splitlines()
        idx = node.lineno - 1
        return lines[idx].strip() if 0 <= idx < len(lines) else ""
    return ""


@dataclass
class FormulaRecord:
    formula: str
    explanation: str
    location: str
    action: str
    dependencies: str


class FormulaVisitor(ast.NodeVisitor):
    """Обходит AST файла и собирает формулы."""

    def __init__(self, file_path: Path, source: str):
        self.file_path = file_path
        self.source = source
        self.records: List[FormulaRecord] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        if is_math_expression(node.value):
            for target in node.targets:
                target_text = ast.unparse(target).strip()
                expr_text = extract_source_segment(self.source, node.value)
                formula = f"{target_text} = {expr_text}"
                self._add_record(node, formula, f"Присваивает {target_text} результат выражения.")
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value and is_math_expression(node.value):
            target_text = ast.unparse(node.target).strip()
            expr_text = extract_source_segment(self.source, node.value)
            formula = f"{target_text} = {expr_text}"
            self._add_record(node, formula, f"Присваивает {target_text} результат выражения с аннотацией.")
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if is_math_expression(node.value):
            op_name = OPERATOR_NAMES.get(type(node.op), type(node.op).__name__)
            op_symbol = self._operator_symbol(node.op)
            target_text = ast.unparse(node.target).strip()
            expr_text = extract_source_segment(self.source, node.value)
            formula = f"{target_text} {op_symbol}= {expr_text}"
            self._add_record(node, formula, f"Обновляет {target_text} через {op_name}.")
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        if node.value and is_math_expression(node.value):
            expr_text = extract_source_segment(self.source, node.value)
            self._add_record(node, f"return {expr_text}", "Возвращает результат вычисления.")
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Call) and is_math_expression(node.value):
            expr_text = extract_source_segment(self.source, node.value)
            self._add_record(node, expr_text, "Вычисляет выражение без сохранения результата.")
        self.generic_visit(node)

    def _add_record(self, node: ast.AST, formula_text: str, action: str) -> None:
        dependencies = sorted(collect_dependencies(node))
        operators = sorted(collect_operator_labels(node))
        operators_text = ", ".join(operators) if operators else "функции и литералы"
        deps_text = ", ".join(dependencies) if dependencies else "—"
        explanation = f"Операции: {operators_text}. Операнды: {deps_text}."

        location = f"{self.file_path.as_posix()}:{getattr(node, 'lineno', '?')}"
        record = FormulaRecord(
            formula=formula_text,
            explanation=explanation,
            location=location,
            action=action,
            dependencies=deps_text
        )
        self.records.append(record)

    @staticmethod
    def _operator_symbol(op: ast.AST) -> str:
        return {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.Mod: "%",
            ast.Pow: "**",
            ast.FloorDiv: "//",
            ast.MatMult: "@",
            ast.BitOr: "|",
            ast.BitAnd: "&",
            ast.BitXor: "^",
            ast.LShift: "<<",
            ast.RShift: ">>",
        }.get(type(op), "?")


class MathFormulaExtractor:
    """Высокоуровневый интерфейс для поиска формул в проекте."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.formulas: List[FormulaRecord] = []

    def scan(self) -> List[FormulaRecord]:
        """Сканирует все Python-файлы и заполняет список формул."""
        self.formulas.clear()
        print(f"[scan] Сканирую каталоги, корень: {self.project_root}")
        for py_file in iter_py_files(self.project_root):
            try:
                source = py_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                print(f"[warn] Пропуск (кодировка): {py_file}")
                continue
            except Exception as exc:
                print(f"[warn] Ошибка чтения {py_file}: {exc}")
                continue

            try:
                tree = ast.parse(source)
            except SyntaxError as exc:
                print(f"[warn] Невозможно распарсить {py_file}: {exc}")
                continue

            try:
                relative_path = py_file.relative_to(self.project_root.parent)
            except ValueError:
                try:
                    relative_path = py_file.relative_to(self.project_root)
                except ValueError:
                    relative_path = py_file

            visitor = FormulaVisitor(relative_path, source)
            visitor.visit(tree)
            if visitor.records:
                print(f"[info] {py_file}: найдено {len(visitor.records)} формул")
            self.formulas.extend(visitor.records)

        self.formulas.sort(key=lambda rec: rec.location)
        print(f"[done] Всего формул: {len(self.formulas)}")
        return self.formulas

    def to_markdown(self, output_path: Path) -> None:
        """Сохраняет найденные формулы в Markdown-таблицу."""
        if not self.formulas:
            self.scan()

        header = textwrap.dedent(
            """\
            # Сводка математических формул проекта

            | № | Формула | Пояснение (из чего состоит) | Местоположение | Что делает | Зависимости |
            |---|---------|----------------------------|----------------|------------|-------------|
            """
        )
        rows = [header]
        for idx, record in enumerate(self.formulas, 1):
            rows.append(
                f"| {idx} | `{record.formula.replace('|', '\\|')}` | "
                f"{record.explanation.replace('|', '\\|')} | "
                f"{record.location.replace('|', '\\|')} | "
                f"{record.action.replace('|', '\\|')} | "
                f"{record.dependencies.replace('|', '\\|')} |"
            )

        stats = textwrap.dedent(
            f"""
            ---

            **Всего формул:** {len(self.formulas)}
            *Отчёт сформирован автоматически скриптом `S.math_finding.py`.*
            """
        )
        rows.append(stats)

        output_path.write_text("\n".join(rows), encoding="utf-8")
        print(f"[save] Отчёт сохранён: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Поиск математических формул в проекте.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).parent / "qsimmine12",
        help="Корень проекта для сканирования (по умолчанию ./qsimmine12)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "S.Формулы.md",
        help="Путь к Markdown-файлу с результатами"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.root.resolve()
    if not project_root.exists():
        raise SystemExit(f"Каталог {project_root} не существует.")

    extractor = MathFormulaExtractor(project_root)
    extractor.scan()
    extractor.to_markdown(args.output.resolve())


if __name__ == "__main__":
    main()

