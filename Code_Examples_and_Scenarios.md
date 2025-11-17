# Примеры кода и сценарии использования

## Содержание
1. [Базовые примеры](#базовые-примеры)
2. [Продвинутые сценарии](#продвинутые-сценарии)
3. [Интеграционные примеры](#интеграционные-примеры)
4. [Тестирование](#тестирование)
5. [Оптимизация производительности](#оптимизация-производительности)

## Базовые примеры

### 1.1 Простая симуляция
```python
from app.sim_engine.simulation_manager import SimulationManager
from app.sim_engine.core.props import SimData

# Создание простого сценария
basic_config = {
    "mode": "auto",
    "solver": "CP-SAT",
    "time_limit": 60,
    "workers": 4
}

# Запуск симуляции
manager = SimulationManager(
    raw_data=example_data,
    options=basic_config
)
result = manager.run()

print(f"Результат: {result['status']}")
print(f"Время выполнения: {result['execution_time']} сек")
```

### 1.2 Анализ результатов
```python
def analyze_simulation_result(result):
    """Детальный анализ результатов симуляции"""
    
    summary = result['summary']
    metrics = {
        'total_trips': summary['trips'],
        'total_volume': summary['volume'],
        'total_weight': summary['weight'],
        'fuel_consumption': summary.get('fuel_consumption', 0),
        'equipment_utilization': summary.get('utilization', {})
    }
    
    # Анализ телеметрии
    telemetry = result['telemetry']
    truck_movements = [
        point for point in telemetry 
        if point['object_type'] == 'truck' 
        and point['data'].get('speed', 0) > 0
    ]
    
    # Расчет KPI
    kpis = {
        'avg_trip_time': calculate_avg_trip_time(result),
        'truck_utilization': calculate_utilization(result, 'truck'),
        'shovel_utilization': calculate_utilization(result, 'shovel'),
        'unload_utilization': calculate_utilization(result, 'unload')
    }
    
    return {
        'metrics': metrics,
        'kpis': kpis,
        'telemetry_stats': {
            'total_points': len(telemetry),
            'truck_movements': len(truck_movements),
            'update_frequency': calculate_update_frequency(telemetry)
        }
    }
```

## Продвинутые сценарии

### 2.1 Многовариантное моделирование
```python
import concurrent.futures
from typing import List, Dict

def run_multiple_scenarios(scenarios: List[Dict], max_workers: int = 4):
    """Запуск нескольких сценариев параллельно"""
    
    results = {}
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Подготовка задач
        future_to_scenario = {
            executor.submit(run_single_scenario, scenario): scenario 
            for scenario in scenarios
        }
        
        # Обработка результатов
        for future in concurrent.futures.as_completed(future_to_scenario):
            scenario = future_to_scenario[future]
            try:
                result = future.result()
                results[scenario['name']] = result
            except Exception as e:
                results[scenario['name']] = {'error': str(e)}
    
    return results

def run_single_scenario(scenario: Dict):
    """Запуск одного сценария"""
    manager = SimulationManager(
        raw_data=scenario['data'],
        options=scenario['config']
    )
    return manager.run()
```

### 2.2 Анализ чувствительности
```python
import numpy as np
import pandas as pd
from scipy import stats

def sensitivity_analysis(base_config, parameters, num_runs=100):
    """Анализ чувствительности по ключевым параметрам"""
    
    results = []
    
    for param_name, param_values in parameters.items():
        param_results = []
        
        for value in param_values:
            # Модификация конфигурации
            config = base_config.copy()
            config[param_name] = value
            
            # Многократный запуск
            run_results = []
            for _ in range(num_runs):
                result = run_simulation_with_config(config)
                run_results.append(result['summary']['weight'])
            
            # Статистика
            param_results.append({
                'parameter': param_name,
                'value': value,
                'mean': np.mean(run_results),
                'std': np.std(run_results),
                'ci': stats.norm.interval(0.95, loc=np.mean(run_results), scale=np.std(run_results))
            })
        
        results.extend(param_results)
    
    return pd.DataFrame(results)
```

## Интеграционные примеры

### 3.1 Интеграция с внешними системами
```python
import requests
import json
from datetime import datetime

class ExternalIntegration:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def send_simulation_results(self, result):
        """Отправка результатов во внешнюю систему"""
        
        payload = {
            'timestamp': datetime.utcnow().isoformat(),
            'simulation_id': result.get('simulation_id'),
            'status': result['status'],
            'metrics': result['summary'],
            'execution_time': result['execution_time']
        }
        
        try:
            response = self.session.post(
                f'{self.api_url}/api/simulation-results',
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка отправки результатов: {e}")
            return None
    
    def get_equipment_data(self, equipment_ids):
        """Получение данных об оборудовании"""
        
        try:
            response = self.session.get(
                f'{self.api_url}/api/equipment',
                params={'ids': ','.join(map(str, equipment_ids))},
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка получения данных оборудования: {e}")
            return None
```

### 3.2 Реализация WebSocket клиента
```python
import websocket
import json
import threading
from queue import Queue

class SimulationWebSocketClient:
    def __init__(self, url, simulation_id):
        self.url = f"{url}/ws/simulations/{simulation_id}"
        self.ws = None
        self.message_queue = Queue()
        self.running = False
        
    def on_message(self, ws, message):
        """Обработка входящих сообщений"""
        try:
            data = json.loads(message)
            self.message_queue.put(data)
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования сообщения: {e}")
    
    def on_error(self, ws, error):
        print(f"WebSocket ошибка: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket соединение закрыто")
        self.running = False
    
    def on_open(self, ws):
        print("WebSocket соединение установлено")
        self.running = True
        
    def connect(self):
        """Установка соединения"""
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        
        # Запуск в отдельном потоке
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.daemon = True
        self.thread.start()
    
    def get_messages(self):
        """Получение сообщений из очереди"""
        messages = []
        while not self.message_queue.empty():
            messages.append(self.message_queue.get())
        return messages
    
    def close(self):
        """Закрытие соединения"""
        if self.ws:
            self.ws.close()
        self.running = False
```

## Тестирование

### 4.1 Модульные тесты
```python
import pytest
from unittest.mock import Mock, patch
from app.sim_engine.simulation_manager import SimulationManager
from app.sim_engine.core.props import SimData

class TestSimulationManager:
    @pytest.fixture
    def mock_sim_data(self):
        return {
            "trucks": {"1": {"id": 1, "name": "Test Truck"}},
            "shovels": {"1": {"id": 1, "name": "Test Shovel"}},
            "unloads": {"1": {"id": 1, "name": "Test Unload"}}
        }
    
    def test_manager_initialization(self, mock_sim_data):
        """Тест инициализации менеджера"""
        manager = SimulationManager(
            raw_data=mock_sim_data,
            options={"mode": "auto"}
        )
        
        assert manager is not None
        assert hasattr(manager, 'simdata')
        assert hasattr(manager, 'config')
    
    @patch('app.sim_engine.simulation_manager.SimulationManager._process_simulation')
    def test_run_simulation(self, mock_process, mock_sim_data):
        """Тест запуска симуляции"""
        mock_process.return_value = {"status": "completed"}
        
        manager = SimulationManager(
            raw_data=mock_sim_data,
            options={"mode": "auto"}
        )
        
        result = manager.run()
        assert result["status"] == "completed"
        mock_process.assert_called_once()
```

### 4.2 Интеграционные тесты
```python
@pytest.mark.integration
class TestIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.test_data = load_test_data('integration_scenario.json')
    
    def test_full_simulation_flow(self):
        """Полный тест потока симуляции"""
        
        # Подготовка
        manager = SimulationManager(
            raw_data=self.test_data,
            options={
                "mode": "auto",
                "time_limit": 30,
                "workers": 2
            }
        )
        
        # Выполнение
        result = manager.run()
        
        # Проверки
        assert result["status"] == "completed"
        assert "summary" in result
        assert "telemetry" in result
        assert "events" in result
        
        summary = result["summary"]
        assert summary["trips"] > 0
        assert summary["volume"] > 0
        assert summary["weight"] > 0
```

## Оптимизация производительности

### 5.1 Профилирование кода
```python
import cProfile
import pstats
import io

def profile_simulation():
    """Профилирование производительности симуляции"""
    
    pr = cProfile.Profile()
    pr.enable()
    
    # Запуск симуляции
    result = run_simulation()
    
    pr.disable()
    
    # Анализ результатов
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    
    print("Результаты профилирования:")
    print(s.getvalue())
    
    return result

def optimize_memory_usage(config):
    """Оптимизация использования памяти"""
    
    # Настройка для уменьшения использования памяти
    optimized_config = {
        **config,
        "memory_optimization": True,
        "telemetry_interval": 300,  # Реже телеметрия
        "max_telemetry_points": 10000,
        "compression": True
    }
    
    return optimized_config
```

### 5.2 Параллельная обработка
```python
from multiprocessing import Pool, cpu_count
import numpy as np

def parallel_monte_carlo(num_simulations, config, num_processes=None):
    """Параллельное выполнение множества симуляций"""
    
    if num_processes is None:
        num_processes = cpu_count()
    
    # Подготовка аргументов
    args = [(config.copy(), i) for i in range(num_simulations)]
    
    with Pool(num_processes) as pool:
        results = pool.starmap(run_single_simulation, args)
    
    return analyze_parallel_results(results)

def run_single_simulation(config, run_id):
    """Запуск одной симуляции с уникальным seed"""
    config = config.copy()
    config['seed'] = run_id  # Уникальный seed для каждой симуляции
    return run_simulation(config)
```

## Заключение

Данные примеры охватывают широкий спектр сценариев использования системы - от базовых запусков до продвинутых интеграций и оптимизации производительности. Используйте эти примеры как основу для разработки собственных решений.