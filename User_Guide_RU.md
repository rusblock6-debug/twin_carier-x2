# Руководство пользователя - Карьерный Симулятор

## Содержание
1. [Введение](#введение)
2. [Установка и настройка](#установка-и-настройка) 
3. [Быстрый старт](#быстрый-старт)
4. [Конфигурация системы](#конфигурация-системы)
5. [Запуск симуляции](#запуск-симуляции)
6. [Анализ результатов](#анализ-результатов)
7. [Расширенные возможности](#расширенные-возможности)
8. [Интеграция](#интеграция)
9. [Мониторинг](#мониторинг)
10. [Устранение неполадок](#устранение-неполадок)
11. [Часто задаваемые вопросы](#часто-задаваемые-вопросы)
12. [Поддержка](#поддержка)

## Введение

### 1.1 О системе
Карьерный симулятор - это комплексная система цифрового двойника для моделирования работы горнодобывающего предприятия. Система позволяет:

- Оптимизировать логистические потоки
- Прогнозировать производительность
- Анализировать надежность работы
- Тестировать различные сценарии

### 1.2 Ключевые возможности
- **Реальное время**: Моделирование с точностью до секунды
- **Физическая достоверность**: Учет реальных характеристик техники
- **Оптимизация**: Автоматическое планирование маршрутов
- **Аналитика**: Детальная статистика и отчетность
- **Масштабируемость**: Поддержка крупных карьеров

## Установка и настройка

### 2.1 Системные требования
- **ОС**: Linux Ubuntu 20.04+, Windows Server 2019+
- **Память**: 16 ГБ RAM (рекомендуется 32 ГБ)
- **Процессор**: 8+ ядер
- **Диск**: 50 ГБ свободного места
- **Сеть**: 1 Гбит/с

### 2.2 Установка зависимостей

#### Базовая установка
```bash
# Клонирование репозитория
git clone https://github.com/your-company/quarry-simulator.git
cd quarry-simulator

# Установка Python зависимостей
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -U pip setuptools wheel
pip install -r requirements.txt
```

#### Установка оптимизаторов
```bash
# Установка OR-Tools (Google)
pip install ortools

# Установка HiGHS solver
pip install highspy

# Установка PuLP
pip install pulp
```

#### Настройка базы данных
```bash
# Установка PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Создание базы данных
sudo -u postgres createdb quarry_db
sudo -u postgres createuser simulator_user

# Настройка прав доступа
sudo -u postgres psql -c "ALTER USER simulator_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE quarry_db TO simulator_user;"
```

### 2.3 Конфигурация окружения

#### Основной .env файл
```env
# База данных
DATABASE_URL=postgresql://simulator_user:secure_password@localhost:5432/quarry_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Настройки симуляции
SIMULATION_TIME_LIMIT=300
MAX_CONCURRENT_SIMULATIONS=5
DEFAULT_SOLVER=CP-SAT

# Логирование
LOG_LEVEL=INFO
LOG_FILE=/var/log/quarry-simulator/app.log
LOG_ROTATION=50MB
LOG_RETENTION=10

# Производительность
WORKER_PROCESSES=4
MEMORY_LIMIT_MB=4096
CPU_LIMIT=80

# Безопасность
SECRET_KEY=your-secret-key-here
JWT_EXPIRE_MINUTES=60
CORS_ORIGINS=*
```

#### Дополнительные настройки
```env
# Кэширование
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# Мониторинг
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Внешние интеграции
WEATHER_API_KEY=your-weather-api-key
GIS_SERVICE_URL=https://gis.example.com/api
ERP_INTEGRATION=false
```

## Конфигурация системы

### Основные параметры симуляции
```python
# Пример конфигурации в коде
config = {
    "mode": "auto",           # Режим работы: auto/manual
    "solver": "CP-SAT",       # Алгоритм оптимизации
    "time_limit": 300,        # Лимит времени решения (сек)
    "workers": 16,            # Количество потоков
    "msg": True,              # Логирование процесса
    
    # Настройки надежности
    "reliability_calc_enabled": True,
    "rel_process_num": 4,
    "rel_init_runs_num": 10,
    "rel_max_runs_num": 100
}
```

### Параметры оборудования

#### Самосвалы
```json
{
    "body_capacity": 120,           # Грузоподъемность (тонн)
    "fuel_capacity": 200,           # Емкость топливного бака (л)
    "fuel_consumption": 205,        # Удельный расход топлива (г/кВт·ч)
    "speed_loaded": 18,             # Скорость груженого (км/ч)
    "speed_empty": 35               # Скорость порожнего (км/ч)
}
```

#### Экскаваторы
```json
{
    "bucket_volume": 4,             # Объем ковша (м³)
    "bucket_fill_speed": 0.25,      # Скорость наполнения ковша
    "arm_turn_speed": 0.8           # Скорость поворота стрелы
}
```

## Запуск симуляции

### 1. Подготовка входных данных
```python
from app.sim_engine.simulation_manager import SimulationManager

# Пример входных данных
input_data = {
    "start_time": "2025-09-19T01:00:00.000Z",
    "end_time": "2025-09-19T08:00:00.000Z",
    "quarry": {
        "name": "Карьер 1",
        "shovel_list": [...],
        "truck_list": [...],
        "unload_list": [...],
        "fuel_station_list": [...]
    }
}
```

### 2. Запуск симуляции
```python
# Создание менеджера симуляции
manager = SimulationManager(
    raw_data=input_data,
    options={
        'mode': 'auto',
        'reliability_calc_enabled': True
    }
)

# Запуск симуляции
result = manager.run()
```

### 3. Многопроцессорный режим
```python
# Запуск с использованием многопроцессорности
manager = SimulationManager(
    raw_data=input_data,
    options=config,
    use_multiprocessing=True
)
```

## Анализ результатов

### Основные метрики
```python
# Анализ результатов
summary = result["summary"]
print(f"Количество рейсов: {summary['trips']}")
print(f"Общий объем: {summary['volume']} тонн")
print(f"Общий вес: {summary['weight']} тонн")

# Почасовые данные
for hour_data in summary["chart_volume_data"]:
    print(f"Час {hour_data['time']}: {hour_data['value']} тонн")
```

### Телеметрия оборудования
```python
# Фильтрация телеметрии
truck_telemetry = [
    point for point in result["telemetry"] 
    if point["object_type"] == "truck"
]

# Анализ состояния техники
for event in result["events"]:
    print(f"Событие: {event['event_name']}")
    print(f"Время: {event['time']}")
    print(f"Объект: {event['object_name']}")
```

## Расширенные возможности

### Надежность системы
```python
# Расчет показателей надежности
from app.sim_engine.reliability import calc_reliability

reliability_data = calc_reliability(
    simulation_results=multiple_runs,
    metric='weight',
    alpha=0.05
)

print(f"Надежность системы: {reliability_data['reliability']}")
print(f"Доверительный интервал: {reliability_data['confidence_interval']}")
```

### Пользовательские алгоритмы
```python
# Использование различных алгоритмов оптимизации
config = {
    "solver": "CP-SAT",  # или "MILP", "GREEDY"
    "time_limit": 600,
    "workers": 32
}
```

### Интеграция с внешними системами
```python
# Экспорт результатов в CSV
import pandas as pd

df = pd.DataFrame(result["summary"]["trips_table"])
df.to_csv("simulation_results.csv", index=False)

# Экспорт телеметрии
telemetry_df = pd.DataFrame(result["telemetry"])
telemetry_df.to_json("telemetry.json", orient="records")
```

## Устранение неполадок

### Common Issues
1. **Нехватка памяти**: Уменьшите количество параллельных процессов
2. **Долгое время выполнения**: Увеличьте time_limit или используйте более простой алгоритм
3. **Ошибки валидации**: Проверьте входные данные на полноту

### Логирование
```python
# Настройка логирования
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simulation")
```

## Поддержка

Для получения дополнительной помощи обращайтесь:
- Документация: `README.md`
- Примеры: `app/sim_engine/tests/`
- Исходный код: `app/sim_engine/`

---
*Последнее обновление: 2025-11-11*