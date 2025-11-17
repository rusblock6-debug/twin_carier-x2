# Бизнес-процессы и метрики карьерного симулятора

## Основные бизнес-процессы

### 1.1 Управление техникой
```python
# Классы из проекта (app/sim_engine/core/props.py)
class TruckProperties:
    payload: float      # Грузоподъемность в тоннах
    speed_empty: float  # Скорость порожнего (км/ч)
    speed_loaded: float # Скорость груженого (км/ч)
    fuel_consumption: float # Расход топлива (л/ч)

class ShovelProperties:
    bucket_volume: float  # Объем ковша (м³)
    fill_factor: float    # Коэффициент наполнения (0.0-1.0)
    dig_cycles: int       # Циклов копания в час
```

| Процесс | Описание | Ключевые параметры |
|---------|----------|-------------------|
| Планирование маршрутов | Оптимизация логистики | `speed_empty`, `speed_loaded`, `road_network` |
| Управление топливом | Контроль заправок | `fuel_consumption`, `fuel_stations` |
| Координация работы | Управление техникой | `shift_schedule`, `idle_areas` |

## Ключевые метрики

### 2.1 Производительность
```python
# Реализация расчетов (app/sim_engine/core/calculations/)
def calculate_total_volume(trucks: list) -> float:
    """Общий объем перевезенного материала"""
    return sum(truck.payload * truck.trips for truck in trucks)

def calculate_utilization(working_time: float, total_time: float) -> float:
    """Коэффициент использования оборудования"""
    return working_time / total_time
```

| Метрика | Формула | Источник данных |
|---------|---------|----------------|
| Объем перевезенного материала | $$V = \sum (payload_i \cdot trips_i)$$ | `TruckProperties.payload`, `.trips` |
| Количество рейсов | $$N = \sum trips_i$$ | `TruckProperties.trips` |
| Использование экскаватора | $$\eta = \frac{T_{work}}{T_{total}}$$ | `ShovelProperties.working_time` |

### 2.2 Эффективность логистики
```python
# Расчет расстояний (app/sim_engine/core/geometry.py)
def calculate_avg_speed(trips: list) -> float:
    """Средняя скорость транспорта"""
    total_distance = sum(haversine_km(t.start, t.end) for t in trips)
    total_time = sum(t.duration for t in trips)
    return total_distance / total_time if total_time > 0 else 0
```

| Метрика | Формула | Источник данных |
|---------|---------|----------------|
| Средняя скорость | $$v_{avg} = \frac{\sum distance_i}{\sum time_i}$$ | `TripData.distance`, `.duration` |
| Эффективность маршрута | $$\eta = \frac{d_{opt}}{d_{act}} \cdot 100\%$$ | `Route.optimal_distance`, `.actual_distance` |

### 2.3 Надежность оборудования
```python
# Расчет надежности (app/sim_engine/reliability.py)
def calculate_availability(mtbf: float, mttr: float) -> float:
    """Доступность оборудования"""
    return mtbf / (mtbf + mttr) * 100 if mtbf + mttr > 0 else 100
```

| Метрика | Формула | Источник данных |
|---------|---------|----------------|
| MTBF | $$MTBF = \frac{T_{work}}{N_{fail}}$$ | `maintenance_log.operating_hours`, `.failures` |
| Доступность | $$A = \frac{MTBF}{MTBF + MTTR} \cdot 100\%$$ | `telemetry.mtbf`, `.mttr` |

## Входы/выходы процессов

### Входные данные:
- Параметры техники (`TruckProperties`, `ShovelProperties`)
- Карта карьера и дорожная сеть
- Графики работ и расписания

### Выходные данные:
- Телеметрия и показатели работы
- Отчеты производительности
- Рекомендации по оптимизации

## Интеграции

### Внутренние системы:
- Модуль мониторинга оборудования
- База данных карьера
- Система расчета надежности

### Внешние системы:
- Погодные сервисы (учет условий работы)
- ERP-системы (синхронизация планов)
- GIS-платформы (актуальные карты)