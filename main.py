import os
import ast
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- КОНФИГУРАЦИЯ: Укажите путь к вашему проекту ---
PROJECT_PATH = "qsimmine12"
APP_PATH = os.path.join(PROJECT_PATH, "app")
SIM_ENGINE_PATH = os.path.join(APP_PATH, "sim_engine")
CORE_PATH = os.path.join(SIM_ENGINE_PATH, "core")
# ----------------------------------------------------

app = FastAPI(
    title="Comprehensive Digital Twin Analyzer",
    description="Полный анализатор кодовой базы проекта qsimmine12. Охватывает все компоненты от БД до UI.",
    version="3.0.0"
)

# --- Вспомогательные функции для анализа кода ---

def analyze_python_file(filepath: str) -> Dict[str, Any]:
    """Анализирует один .py файл и извлекает классы, функции и докстринги."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        
        info = {"file": filepath, "classes": [], "functions": [], "imports": []}
        
        for node in ast.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    info["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                info["imports"].append(f"from {module}")
            elif isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "docstring": ast.get_docstring(node) or "Нет описания",
                    "methods": [{"name": n.name, "docstring": ast.get_docstring(n) or "Нет описания"} for n in node.body if isinstance(n, ast.FunctionDef)]
                }
                info["classes"].append(class_info)
            elif isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "docstring": ast.get_docstring(node) or "Нет описания",
                    "arguments": [arg.arg for arg in node.args.args]
                }
                info["functions"].append(func_info)
        return info
    except Exception as e:
        return {"file": filepath, "error": f"Ошибка парсинга: {str(e)}"}

def list_python_files(directory: str) -> List[str]:
    """Возвращает список .py файлов в директории, исключая __init__.py."""
    if not os.path.isdir(directory):
        return []
    return [f for f in os.listdir(directory) if f.endswith('.py') and f != '__init__.py']

def list_directory_contents(directory: str) -> List[str]:
    """Возвращает список всех файлов и папок в директории."""
    if not os.path.isdir(directory):
        return []
    return sorted(os.listdir(directory))

# --- Модели данных для API ---
class ComponentAnalysis(BaseModel):
    name: str
    path: str
    analysis: Dict[str, Any]

# --- ЭНДПОИНТЫ ДЛЯ АНАЛИЗА ПРОЕКТА ---

# --- Project Overview ---
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Comprehensive Analyzer is working. Go to /docs to explore the entire project."}

@app.get("/project/structure", tags=["Project Overview"])
async def get_project_structure():
    """Возвращает высокоуровневую структуру папок и ключевых файлов проекта."""
    if not os.path.isdir(PROJECT_PATH):
        raise HTTPException(status_code=404, detail=f"Папка проекта '{PROJECT_PATH}' не найдена.")
    
    structure = {
        "project_name": PROJECT_PATH,
        "key_directories": {
            "sim_engine": SIM_ENGINE_PATH,
            "core": CORE_PATH,
            "planner": os.path.join(CORE_PATH, "planner"),
            "calculations": os.path.join(CORE_PATH, "calculations"),
            "simulations": os.path.join(SIM_ENGINE_PATH, "simulations"),
            "services": os.path.join(APP_PATH, "services"),
            "migrations": os.path.join(APP_PATH, "migrations"),
        },
        "key_files": {
            "simulation_manager": os.path.join(SIM_ENGINE_PATH, "simulation_manager.py"),
            "planner": os.path.join(SIM_ENGINE_PATH, "planner.py"),
            "simulate": os.path.join(SIM_ENGINE_PATH, "simulate.py"),
            "props": os.path.join(CORE_PATH, "props.py"),
            "states": os.path.join(SIM_ENGINE_PATH, "states.py"),
            "enums": os.path.join(APP_PATH, "enums.py"),
            "models": os.path.join(APP_PATH, "models.py"),
            "routes": os.path.join(APP_PATH, "routes.py"),
            "shift": os.path.join(APP_PATH, "shift.py"),
        }
    }
    return structure

# --- Core Simulation Logic ---
@app.get("/core/calculations", tags=["Core"], response_model=List[ComponentAnalysis])
async def get_calculations():
    """Анализирует все файлы с расчетами в папке core/calculations."""
    calc_dir = os.path.join(CORE_PATH, "calculations")
    files = list_python_files(calc_dir)
    results = []
    for file_name in files:
        file_path = os.path.join(calc_dir, file_name)
        results.append(ComponentAnalysis(name=file_name, path=file_path, analysis=analyze_python_file(file_path)))
    return results

@app.get("/core/props", tags=["Core"])
async def get_props():
    """Анализирует файл props.py, чтобы показать все сущности и их поля."""
    props_file = os.path.join(CORE_PATH, "props.py")
    return {"file": props_file, "analysis": analyze_python_file(props_file)}

@app.get("/core/geometry", tags=["Core"])
async def get_geometry():
    """Анализирует файл geometry.py для понимания работы с графами и геометрией."""
    geometry_file = os.path.join(CORE_PATH, "geometry.py")
    return {"file": geometry_file, "analysis": analyze_python_file(geometry_file)}

# --- Planner ---
@app.get("/planners/solvers", tags=["Planner"], response_model=List[ComponentAnalysis])
async def get_planner_solvers():
    """Анализирует все файлы солверов в папке planner/solvers."""
    solvers_dir = os.path.join(CORE_PATH, "planner", "solvers")
    files = list_python_files(solvers_dir)
    results = []
    for file_name in files:
        file_path = os.path.join(solvers_dir, file_name)
        results.append(ComponentAnalysis(name=file_name, path=file_path, analysis=analyze_python_file(file_path)))
    return results

# --- Simulation Execution ---
@app.get("/simulation/manager", tags=["Simulation"])
async def get_simulation_manager_details():
    """Анализирует simulation_manager.py для понимания точки входа в симуляцию."""
    manager_file = os.path.join(SIM_ENGINE_PATH, "simulation_manager.py")
    return {"file": manager_file, "analysis": analyze_python_file(manager_file)}

@app.get("/simulation/simulate_script", tags=["Simulation"])
async def get_simulate_script_details():
    """Анализирует simulate.py, основной скрипт запуска симуляции."""
    simulate_file = os.path.join(SIM_ENGINE_PATH, "simulate.py")
    return {"file": simulate_file, "analysis": analyze_python_file(simulate_file)}

@app.get("/simulation/states", tags=["Simulation"])
async def get_simulation_states():
    """Анализирует файл states.py для понимания всех возможных состояний системы."""
    states_file = os.path.join(SIM_ENGINE_PATH, "states.py")
    return {"file": states_file, "analysis": analyze_python_file(states_file)}

# --- Database & Models ---
@app.get("/database/models", tags=["Database & Models"])
async def get_database_models():
    """Анализирует models.py, чтобы показать все таблицы, поля и связи в базе данных."""
    models_file = os.path.join(APP_PATH, "models.py")
    return {"file": models_file, "analysis": analyze_python_file(models_file)}

@app.get("/database/migrations", tags=["Database & Models"])
async def get_database_migrations():
    """Показывает список всех миграций базы данных."""
    migrations_dir = os.path.join(APP_PATH, "migrations", "versions")
    return {"directory": migrations_dir, "contents": list_directory_contents(migrations_dir)}

# --- Business Logic Services ---
@app.get("/services/all", tags=["Services"], response_model=List[ComponentAnalysis])
async def get_all_services():
    """Анализирует все файлы в папке services, где находится бизнес-логика."""
    services_dir = os.path.join(APP_PATH, "services")
    files = list_python_files(services_dir)
    results = []
    for file_name in files:
        file_path = os.path.join(services_dir, file_name)
        results.append(ComponentAnalysis(name=file_name, path=file_path, analysis=analyze_python_file(file_path)))
    return results

# --- Web API & UI ---
@app.get("/web/routes", tags=["Web API & UI"])
async def get_web_routes():
    """Анализирует routes.py, чтобы понять все эндпоинты веб-интерфейса."""
    routes_file = os.path.join(APP_PATH, "routes.py")
    return {"file": routes_file, "analysis": analyze_python_file(routes_file)}

@app.get("/web/forms", tags=["Web API & UI"])
async def get_web_forms():
    """Анализирует forms.py, чтобы понять все формы для ввода данных."""
    forms_file = os.path.join(APP_PATH, "forms.py")
    return {"file": forms_file, "analysis": analyze_python_file(forms_file)}

# --- Scheduling & Time ---
@app.get("/schedule/shifts", tags=["Scheduling & Time"])
async def get_schedule_shifts():
    """Анализирует shift.py, отвечающий за логику смен и расписаний."""
    shift_file = os.path.join(APP_PATH, "shift.py")
    return {"file": shift_file, "analysis": analyze_python_file(shift_file)}

# --- Geometry & Geography ---
@app.get("/geometry/road_network", tags=["Geometry & Geography"])
async def get_road_network():
    """Анализирует road_net.py для понимания логики дорожной сети."""
    road_net_file = os.path.join(APP_PATH, "road_net.py")
    return {"file": road_net_file, "analysis": analyze_python_file(road_net_file)}

@app.get("/geometry/geo_utils", tags=["Geometry & Geography"])
async def get_geo_utilities():
    """Анализирует geo_utils.py для понимания утилит для работы с геоданными."""
    geo_utils_file = os.path.join(APP_PATH, "geo_utils.py")
    return {"file": geo_utils_file, "analysis": analyze_python_file(geo_utils_file)}

# --- Configuration & Enums ---
@app.get("/config/enums", tags=["Configuration & Enums"])
async def get_enums():
    """Анализирует enums.py, чтобы увидеть все перечисления и константы в системе."""
    enums_file = os.path.join(APP_PATH, "enums.py")
    return {"file": enums_file, "analysis": analyze_python_file(enums_file)}

# --- Manual Analysis ---
@app.get("/analyze/file", tags=["Manual Analysis"])
async def analyze_any_file(filepath: str):
    """
    Позволяет проанализировать любой .py файл в проекте, указав его относительный путь.
    Пример: qsimmine12/app/sim_engine/simulation_manager.py
    """
    if not filepath.startswith(PROJECT_PATH):
        raise HTTPException(status_code=400, detail="Путь должен быть внутри папки проекта.")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Файл не найден.")
    if not filepath.endswith('.py'):
        raise HTTPException(status_code=400, detail="Можно анализировать только .py файлы.")
    return analyze_python_file(filepath)
