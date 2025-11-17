# Руководство по оптимизации и отладке

## Содержание
1. [Профилирование производительности](#профилирование-производительности)
2. [Оптимизация алгоритмов](#оптимизация-алгоритмов)
3. [Управление памятью](#управление-памятью)
4. [Отладка симуляции](#отладка-симуляции)
5. [Мониторинг в реальном времени](#мониторинг-в-реальном-времени)
6. [Устранение узких мест](#устранение-узких-мест)

## Профилирование производительности

### 1.1 Инструменты профилирования

#### cProfile
```python
import cProfile
import pstats

def profile_simulation():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Код для профилирования
    result = run_simulation()
    
    profiler.disable()
    
    # Анализ результатов
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Топ-20 функций
    
    return result
```

#### line_profiler
```python
# Установка: pip install line_profiler
# Декоратор для профилирования строк
@profile
def critical_function():
    # Код для детального профилирования
    pass
```

### 1.2 Метрики производительности
- **Время выполнения**: Общее время симуляции
- **Использование CPU**: Загрузка процессора
- **Использование памяти**: Пиковое потребление RAM
- **I/O операции**: Дисковые и сетевые операции

## Оптимизация алгоритмов

### 2.1 Оптимизация планировщика

#### Кэширование результатов
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def calculate_route_time(truck_id, shovel_id, unload_id, loaded):
    """Кэширование расчетов времени маршрута"""
    # Сложные расчеты
    return calculated_time
```

#### Векторизация вычислений
```python
import numpy as np

def vectorized_calculations(trucks, shovels, unloads):
    """Векторизованные расчеты вместо циклов"""
    
    # Создание матриц параметров
    truck_params = np.array([truck.speed for truck in trucks])
    shovel_params = np.array([shovel.rate for shovel in shovels])
    
    # Векторизованные операции
    result_matrix = np.outer(truck_params, shovel_params)
    
    return result_matrix
```

### 2.2 Параллельные вычисления

#### Multiprocessing
```python
from multiprocessing import Pool
from itertools import product

def parallel_route_calculation(trucks, shovels, unloads):
    """Параллельный расчет всех маршрутов"""
    
    # Подготовка аргументов
    args = list(product(trucks, shovels, unloads))
    
    with Pool() as pool:
        results = pool.starmap(calculate_single_route, args)
    
    return dict(zip(args, results))
```

## Управление памятью

### 3.1 Оптимизация структур данных

#### Использование массивов вместо списков
```python
import array

# Более эффективное хранение числовых данных
positions = array.array('d', [])  # double precision
speeds = array.array('f', [])     # float
```

#### Слабое ссылочное поле
```python
import weakref

class LargeDataHolder:
    def __init__(self, data):
        self._data = data
        self._cache = weakref.WeakValueDictionary()
```

### 3.2 Сборка мусора
```python
import gc

def optimize_memory():
    """Оптимизация использования памяти"""
    
    # Принудительная сборка мусора
    gc.collect()
    
    # Настройка порогов сборки
    gc.set_threshold(700, 10, 10)
    
    # Отслеживание объектов
    gc.set_debug(gc.DEBUG_STATS)
```

## Отладка симуляции

### 4.1 Логирование

#### Структурированное логирование
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self):
        self.logger = logging.getLogger('simulation')
        self.logger.setLevel(logging.DEBUG)
        
        # JSON форматтер
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}'
        )
        
        handler = logging.FileHandler('simulation.log')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_event(self, event_type, data):
        """Логирование структурированных событий"""
        log_data = {
            "event": event_type,
            "data": data,
            "simulation_time": datetime.utcnow().isoformat()
        }
        self.logger.info(json.dumps(log_data))
```

### 4.2 Трассировка выполнения

#### Декоратор трассировки
```python
def trace_execution(func):
    """Декоратор для трассировки выполнения функций"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        print(f"{func.__name__} executed in {execution_time:.4f}s")
        return result
    
    return wrapper
```

## Мониторинг в реальном времени

### 5.1 Метрики Prometheus
```python
from prometheus_client import Counter, Gauge, Histogram

# Счетчики событий
SIMULATION_START = Counter('simulation_start', 'Number of simulations started')
TRUCK_MOVEMENT = Counter('truck_movement', 'Truck movement events')
FUEL_CONSUMPTION = Counter('fuel_consumption', 'Total fuel consumed')

# Измерители значений
CPU_USAGE = Gauge('cpu_usage', 'Current CPU usage')
MEMORY_USAGE = Gauge('memory_usage', 'Current memory usage')

# Гистограммы времени
EXECUTION_TIME = Histogram('execution_time', 'Time spent in operations')
```

### 5.2 Дашборды Grafana

#### Конфигурация дашборда
```json
{
  "dashboard": {
    "title": "Simulation Monitoring",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(cpu_usage[5m])",
            "legendFormat": "CPU Usage"
          }
        ]
      }
    ]
  }
}
```

## Устранение узких мест

### 6.1 Анализ производительности

#### Выявление медленных функций
```python
import time
import inspect

def performance_analysis():
    """Автоматический анализ производительности"""
    
    slow_functions = []
    
    # Обход всех функций модуля
    for name, func in inspect.getmembers(sys.modules[__name__], inspect.isfunction):
        start_time = time.time()
        
        # Тестовый запуск
        try:
            test_result = func()
            execution_time = time.time() - start_time
            
            if execution_time > 1.0:  # Порог медленной функции
                slow_functions.append({
                    'name': name,
                    'time': execution_time,
                    'source': inspect.getsource(func)
                })
                
        except Exception as e:
            print(f"Ошибка тестирования {name}: {e}")
    
    return slow_functions
```

### 6.2 Оптимизация базы данных

#### Индексация и запросы
```sql
-- Создание индексов для часто используемых запросов
CREATE INDEX idx_telemetry_timestamp ON telemetry(timestamp);
CREATE INDEX idx_telemetry_object_type ON telemetry(object_type);

-- Оптимизация запросов
EXPLAIN ANALYZE SELECT * FROM telemetry 
WHERE timestamp > NOW() - INTERVAL '1 hour'
AND object_type = 'truck';
```
