#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт-анализатор архитектуры проекта.
Сканирует код, извлекает компоненты и их связи, сохраняет в architecture.json.
"""

import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict


class ArchitectureParser:
    """Парсер архитектуры проекта."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.components: Dict[str, Dict] = {}
        self.relationships: List[Dict] = []
        self.layer_mapping = self._build_layer_mapping()
    
    def _build_layer_mapping(self) -> Dict[str, str]:
        """Определяет слой компонента на основе пути к файлу."""
        return {
            "models": "Модели данных",
            "services": "Сервисы",
            "routes": "API/Роуты",
            "forms": "Формы/Валидация",
            "sim_engine": "Движок симуляции",
            "sim_engine/core": "Ядро симуляции",
            "sim_engine/core/calculations": "Расчёты",
            "sim_engine/core/planner": "Планировщик",
            "sim_engine/core/simulations": "Симуляции",
            "sim_engine/infra": "Инфраструктура",
            "utils": "Утилиты",
            "consts": "Константы",
            "enums": "Перечисления",
        }
    
    def _get_layer(self, file_path: Path) -> str:
        """Определяет слой для файла."""
        rel_path = str(file_path.relative_to(self.project_root)).replace("\\", "/")
        
        # Проверяем точные совпадения
        if "app/models.py" in rel_path:
            return "Модели данных"
        elif "app/routes.py" in rel_path:
            return "API/Роуты"
        elif "app/forms.py" in rel_path:
            return "Формы/Валидация"
        elif "app/consts.py" in rel_path:
            return "Константы"
        elif "app/enums.py" in rel_path:
            return "Перечисления"
        elif "app/utils.py" in rel_path:
            return "Утилиты"
        elif "app/services/" in rel_path:
            return "Сервисы"
        elif "app/sim_engine/core/calculations/" in rel_path:
            return "Расчёты"
        elif "app/sim_engine/core/planner/" in rel_path:
            return "Планировщик"
        elif "app/sim_engine/core/simulations/" in rel_path:
            return "Симуляции"
        elif "app/sim_engine/core/" in rel_path:
            return "Ядро симуляции"
        elif "app/sim_engine/infra/" in rel_path:
            return "Инфраструктура"
        elif "app/sim_engine/" in rel_path:
            return "Движок симуляции"
        else:
            return "Прочее"
    
    def _get_component_id(self, name: str, file_path: Path, component_type: str) -> str:
        """Генерирует уникальный ID для компонента."""
        rel_path = str(file_path.relative_to(self.project_root)).replace("\\", "/")
        return f"{component_type}:{name}@{rel_path}"
    
    def _extract_imports(self, node: ast.AST) -> Set[str]:
        """Извлекает все импорты из AST узла."""
        imports = set()
        
        for item in ast.walk(node):
            if isinstance(item, ast.Import):
                for alias in item.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(item, ast.ImportFrom):
                if item.module:
                    imports.add(item.module.split('.')[0])
                    # Также добавляем импортированные имена
                    for alias in item.names:
                        imports.add(alias.name)
        
        return imports
    
    def _extract_function_calls(self, node: ast.AST) -> Set[str]:
        """Извлекает вызовы функций и методов из AST."""
        calls = set()
        
        for item in ast.walk(node):
            if isinstance(item, ast.Call):
                if isinstance(item.func, ast.Name):
                    calls.add(item.func.id)
                elif isinstance(item.func, ast.Attribute):
                    # Для методов получаем имя атрибута
                    calls.add(item.func.attr)
                    # Также получаем объект, у которого вызывается метод
                    if isinstance(item.func.value, ast.Name):
                        calls.add(item.func.value.id)
        
        return calls
    
    def _get_source_code(self, node: ast.AST, file_content: str) -> str:
        """Извлекает исходный код компонента из файла."""
        try:
            if not hasattr(node, 'lineno'):
                return ""
            start_line = node.lineno - 1
            # Используем end_lineno если доступен, иначе приблизительно
            if hasattr(node, 'end_lineno') and node.end_lineno:
                end_line = node.end_lineno
            else:
                # Если end_lineno нет, находим последнюю строку рекурсивно
                last_line = start_line + 1
                for child in ast.walk(node):
                    if hasattr(child, 'lineno') and child.lineno > last_line:
                        last_line = child.lineno
                end_line = last_line + 5  # Добавляем несколько строк для надёжности
            
            lines = file_content.split('\n')
            # Убеждаемся, что индексы в допустимых пределах
            start_line = max(0, start_line)
            end_line = min(len(lines), end_line)
            
            return '\n'.join(lines[start_line:end_line])
        except Exception as e:
            return f"# Ошибка извлечения кода: {e}"
    
    def _parse_file(self, file_path: Path):
        """Парсит Python файл и извлекает компоненты."""
        try:
            file_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {e}")
            return
        
        try:
            tree = ast.parse(file_content)
        except SyntaxError as e:
            print(f"Ошибка парсинга {file_path}: {e}")
            return
        
        layer = self._get_layer(file_path)
        rel_path = str(file_path.relative_to(self.project_root)).replace("\\", "/")
        
        # Извлекаем все импорты из файла
        file_imports = self._extract_imports(tree)
        
        # Множество для отслеживания функций, которые являются методами классов
        class_methods = set()
        
        # Сначала обрабатываем классы
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                component_id = self._get_component_id(node.name, file_path, "class")
                docstring = ast.get_docstring(node) or ""
                
                # Извлекаем методы класса
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                        # Помечаем функцию как метод класса
                        class_methods.add(item)
                
                # Анализируем использование внутри класса
                class_imports = self._extract_imports(node)
                class_calls = self._extract_function_calls(node)
                
                source_code = self._get_source_code(node, file_content)
                
                self.components[component_id] = {
                    "id": component_id,
                    "name": node.name,
                    "type": "class",
                    "layer": layer,
                    "file_path": rel_path,
                    "docstring": docstring,
                    "methods": methods,
                    "source_code": source_code,
                    "imports": list(class_imports),
                    "calls": list(class_calls),
                }
        
        # Затем обрабатываем функции верхнего уровня (не методы классов)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node not in class_methods:
                component_id = self._get_component_id(node.name, file_path, "function")
                docstring = ast.get_docstring(node) or ""
                
                func_imports = self._extract_imports(node)
                func_calls = self._extract_function_calls(node)
                source_code = self._get_source_code(node, file_content)
                
                self.components[component_id] = {
                    "id": component_id,
                    "name": node.name,
                    "type": "function",
                    "layer": layer,
                    "file_path": rel_path,
                    "docstring": docstring,
                    "source_code": source_code,
                    "imports": list(func_imports),
                    "calls": list(func_calls),
                }
    
    def _build_relationships(self):
        """Строит связи между компонентами на основе импортов и вызовов."""
        # Создаём индекс компонентов по именам для быстрого поиска
        name_to_components = defaultdict(list)
        for comp_id, comp in self.components.items():
            name_to_components[comp["name"]].append(comp_id)
            # Также индексируем по коротким именам из импортов
            for imp in comp.get("imports", []):
                # Убираем префикс app. если есть
                short_name = imp.replace("app.", "").split(".")[-1]
                name_to_components[short_name].append(comp_id)
        
        # Строим связи
        for comp_id, comp in self.components.items():
            # Связи через импорты
            for imp in comp.get("imports", []):
                # Ищем компоненты, которые могут быть импортированы
                potential_targets = set()
                
                # Прямое совпадение имени
                if imp in name_to_components:
                    potential_targets.update(name_to_components[imp])
                
                # Совпадение по последней части пути импорта
                imp_parts = imp.split(".")
                if len(imp_parts) > 1:
                    last_part = imp_parts[-1]
                    if last_part in name_to_components:
                        potential_targets.update(name_to_components[last_part])
                
                # Создаём связи
                for target_id in potential_targets:
                    if target_id != comp_id:
                        rel_id = f"{comp_id}->{target_id}"
                        # Проверяем, не создали ли мы уже эту связь
                        if not any(r["id"] == rel_id for r in self.relationships):
                            self.relationships.append({
                                "id": rel_id,
                                "source": comp_id,
                                "target": target_id,
                                "type": "imports",
                                "description": f"Импортирует {self.components[target_id]['name']}"
                            })
            
            # Связи через вызовы функций
            for call in comp.get("calls", []):
                if call in name_to_components:
                    for target_id in name_to_components[call]:
                        if target_id != comp_id:
                            rel_id = f"{comp_id}->{target_id}"
                            if not any(r["id"] == rel_id for r in self.relationships):
                                self.relationships.append({
                                    "id": rel_id,
                                    "source": comp_id,
                                    "target": target_id,
                                    "type": "calls",
                                    "description": f"Вызывает {self.components[target_id]['name']}"
                                })
    
    def parse(self) -> Dict:
        """Главный метод парсинга проекта."""
        print(f"Сканирование проекта: {self.project_root}")
        
        # Находим все Python файлы
        python_files = list(self.project_root.rglob("*.py"))
        # Исключаем тестовые файлы и миграции
        python_files = [
            f for f in python_files 
            if "test" not in str(f).lower() 
            and "migration" not in str(f).lower()
            and "__pycache__" not in str(f)
        ]
        
        print(f"Найдено {len(python_files)} Python файлов")
        
        # Парсим каждый файл
        for file_path in python_files:
            self._parse_file(file_path)
        
        print(f"Найдено {len(self.components)} компонентов")
        
        # Строим связи
        self._build_relationships()
        print(f"Найдено {len(self.relationships)} связей")
        
        # Формируем итоговую структуру
        return {
            "metadata": {
                "project_root": str(self.project_root),
                "total_components": len(self.components),
                "total_relationships": len(self.relationships),
            },
            "components": list(self.components.values()),
            "relationships": self.relationships,
        }
    
    def save(self, output_path: Path):
        """Сохраняет результат в JSON файл."""
        data = self.parse()
        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Результат сохранён в {output_path}")


def main():
    """Точка входа."""
    if len(sys.argv) >= 2:
        project_root = Path(sys.argv[1]).resolve()
    else:
        # По умолчанию используем папку qsimmine12
        project_root = (Path(__file__).parent / "qsimmine12").resolve()
    
    if not project_root.exists():
        print(f"Ошибка: путь не найден: {project_root}")
        sys.exit(1)
    
    output_file = Path(__file__).parent / "architecture.json"
    
    parser = ArchitectureParser(project_root)
    parser.save(output_file)
    
    print(f"\nГотово! Файл architecture.json создан.")
    print(f"Откройте viewer.html в браузере для просмотра архитектуры.")


if __name__ == "__main__":
    main()

