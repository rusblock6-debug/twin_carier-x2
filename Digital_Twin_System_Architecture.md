# Digital Twin System Architecture - Карьерный Симулятор

## Содержание
1. [Введение](#введение)
2. [Архитектурные принципы](#архитектурные-принципы)
3. [Компоненты системы](#компоненты-системы)
4. [Потоки данных](#потоки-данных) 
5. [Масштабируемость](#масштабируемость)
6. [Безопасность](#безопасность)
7. [Интеграции](#интеграции)
8. [Мониторинг](#мониторинг)
9. [Развертывание](#развертывание)
10. [Оптимизация](#оптимизация)

## Введение

### 1.1 Обзор системы
Цифровой двойник карьерной техники представляет собой комплексную систему моделирования работы карьера, включая:

- Экскаваторы и погрузочное оборудование
- Самосвалы и транспортные системы
- Пункты разгрузки и складирования
- Заправочные станции и инфраструктура
- Дорожная сеть и логистические маршруты

### 1.2 Основные возможности
- Реальное время моделирования с точностью до секунды
- Физически достоверные расчеты движения техники
- Учет характеристик материалов (плотность, влажность)
- Моделирование отказов и ремонтов оборудования
- Оптимизация логистических потоков

### 1.3 Технологический стек
- **Ядро**: Python 3.13 (асинхронное программирование)
- **Оптимизация**: OR-Tools (Google), PuLP, HiGHS
- **Базы данных**: PostgreSQL (транзакционные данные), Redis (кеш)
- **Визуализация**: Three.js, WebGL
- **API**: FastAPI (REST), WebSockets (реальное время)

## Архитектурные принципы

### 2.1 Модульность
Система построена по принципу микросервисов с четким разделением ответственности:

- Сервис расчета движения (TruckService)
- Сервис погрузки (ShovelService) 
- Сервис разгрузки (UnloadService)
- Сервис топливной логистики (FuelService)
- Сервис планирования (PlannerService)

### 2.2 Событийная модель
Основана на дискретно-событийном подходе с использованием:

- Очереди событий (PriorityQueue)
- Таймлайн-менеджер (TimeKeeper)
- Обработчики событий (EventHandlers)
- Логгер изменений состояния (StateLogger)

### 2.3 Потоковая обработка
- Потоки данных в реальном времени (Kafka)
- Оконные агрегации (1 мин, 5 мин, 1 час)
- Комплексные метрики производительности

## Компоненты системы

### 3.1 Ядро симуляции (Simulation Core)

#### 3.1.1 Simulation Manager
Полный контроль над жизненным циклом симуляции:

```python
class SimulationManager:
    def __init__(self, config):
        self.env = QSimEnvironment(config)
        self.planner = Planner()
        self.validator = DataValidator()
        self.writer = ResultWriter()
        
    def run(self):
        self._validate_inputs()
        self._setup_environment()
        self._run_events_loop()
        self._generate_reports()
```

#### 3.1.2 Планировщик маршрутов
Поддерживаемые алгоритмы:

1. **CP-SAT (Constraint Programming)**
   - Оптимальное решение для средних задач
   - Поддержка временных ограничений
   - Пример конфигурации:
   ```python
   config = {
       "solver": "CP-SAT",
       "time_limit": 300,
       "workers": 16,
       "precision": 0.01
   }
   ```

2. **MILP (Mixed Integer Linear Programming)**
   - Линейные модели с целочисленными переменными
   - Использует HiGHS solver
   - Особенности:
     - Формализация ограничений
     - Целевые функции
     - Параметризация

3. **Жадный алгоритм (Greedy)**
   - Быстрое приближенное решение
   - Эвристики:
     - Ближайший экскаватор
     - Минимальное время простоя
     - Балансировка нагрузки

### 3.2 Модели данных

#### 3.2.1 Основные сущности
```python
class SimData:
    """Контейнер всех данных симуляции"""
    trucks: Dict[int, Truck]          # Самосвалы
    shovels: Dict[int, Shovel]        # Экскаваторы
    unloads: Dict[int, Unload]        # Пункты разгрузки
    fuel_stations: Dict[int, FuelStation]  # Заправочные станции
    idle_areas: IdleAreas             # Зоны простоя
    road_net: RoadNetwork             # Дорожная сеть
    weather: WeatherConditions       # Метеоусловия
    material: MaterialProperties     # Свойства материалов
```

#### 3.2.2 Параметры оборудования

##### Самосвалы
```python
class TruckSpecs(BaseModel):
    body_capacity: float            # Грузоподъемность (тонн)
    engine_power: float             # Мощность двигателя (кВт)
    fuel_consumption: float         # Удельный расход (г/кВт·ч)
    speed_loaded: float             # Скорость груженого (км/ч)
    speed_empty: float              # Скорость порожнего (км/ч)
    fuel_capacity: float            # Емкость бака (л)
    tire_wear_rate: float          # Коэффициент износа шин
    maintenance_interval: int      # Интервал ТО (часы)
```

##### Экскаваторы
```python
class ShovelSpecs(BaseModel):
    bucket_volume: float           # Объем ковша (м³)
    digging_force: float           # Усилие копания (кН)
    swing_speed: float             # Скорость поворота (рад/с)
    hydraulic_pressure: float      # Давление в гидросистеме (бар)
    engine_hours: int             # Наработка (часы)
    wear_factors: Dict[str, float] # Коэффициенты износа
```

### 3.3 Расчетные модули

#### 3.3.1 Движение техники
```python
def calculate_motion(truck: Truck, route: Route, loaded: bool):
    """Расчет времени движения по маршруту"""
    total_time = 0.0
    for segment in route.segments:
        segment_time = segment.length / truck.speed(loaded)
        segment_time *= terrain_factor(segment.terrain)
        segment_time *= slope_factor(segment.slope)
        segment_time *= load_factor(truck.load)
        total_time += segment_time
    return total_time
```

#### 3.3.2 Погрузка/разгрузка
```python
class LoadingCalculator:
    def __init__(self, shovel: Shovel, truck: Truck):
        self.shovel = shovel
        self.truck = truck
        
    def calculate(self):
        cycles = self.truck.capacity / self.shovel.bucket_volume
        cycle_time = (
            self.shovel.dig_time 
            + self.shovel.swing_time 
            + self.shovel.dump_time
        )
        return cycles * cycle_time
```

### 3.4 Система надежности

#### Методы оценки
1. Монте-Карло моделирование
2. Бутстрап-анализ
3. Доверительные интервалы
4. Анализ чувствительности

```python
def reliability_analysis(results: List[SimResult]):
    stats = {
        'mean': np.mean(results),
        'std': np.std(results),
        'ci': stats.norm.interval(0.95, loc=mean, scale=std),
        'sensitivity': calculate_sensitivity(results)
    }
    return stats
```

## Потоки данных

### 4.1 Основные потоки
1. Телеметрия оборудования → Агрегатор → Хранилище
2. Команды управления ← Планировщик ← Оптимизатор
3. Логи событий → Анализатор → Дашборды

### 4.2 Форматы данных
- **Телеметрия**: Protocol Buffers (бинарный)
- **Команды**: JSON (REST API)
- **События**: Apache Avro (Kafka)

## Масштабируемость

### 5.1 Горизонтальное масштабирование
- Шардирование по карьерам
- Балансировка нагрузки
- Геораспределение

### 5.2 Производительность
- 10,000 объектов в реальном времени
- Задержка < 100 мс
- Пропускная способность 1 ГБ/с

## Безопасность

### 6.1 Контроль доступа
- RBAC (ролевая модель)
- OAuth 2.0 / OpenID Connect
- Аудит действий

### 6.2 Защита данных
- Шифрование TLS 1.3
- Маскирование PII
- WAF защита

## Интеграции

### 7.1 Внешние системы
- ERP (SAP, Oracle)
- MES системы
- GIS платформы
- Погодные сервисы

## Мониторинг

### 8.1 Метрики
- Prometheus + Grafana
- Кастомные дашборды
- Оповещения

## Развертывание

### 9.1 Топологии
- Standalone
- Кластер Kubernetes
- Гибридное облако

## Оптимизация

### 10.1 Методы
- Профилирование кода
- JIT компиляция
- Векторизация вычислений

[Вернуться к содержанию](#содержание)

## Архитектурные компоненты

### 1. Ядро симуляции (Simulation Engine)

#### 1.1 Simulation Manager
- **Назначение**: Управление запуском симуляции в ручном/автоматическом режиме
- **Ключевые функции**:
  - Валидация входных данных
  - Управление многопроцессорными вычислениями
  - Интеграция с планировщиком маршрутов
  - Обработка результатов симуляции

#### 1.2 Планировщик маршрутов (Planner)
- **Поддерживаемые алгоритмы**:
  - CP-SAT (Constraint Programming)
  - MILP (Mixed Integer Linear Programming)
  - Жадный алгоритм (Greedy)
- **Функциональность**:
  - Оптимизация распределения самосвалов
  - Расчет временных параметров рейсов
  - Учет ограничений оборудования

### 2. Модели данных

#### 2.1 Основные сущности
```python
class SimData:
    """Контейнер всех данных симуляции"""
    trucks: Dict[int, Truck]          # Самосвалы
    shovels: Dict[int, Shovel]        # Экскаваторы
    unloads: Dict[int, Unload]        # Пункты разгрузки
    fuel_stations: Dict[int, FuelStation]  # Заправочные станции
    idle_areas: IdleAreas             # Зоны простоя
    road_net: RoadNetwork             # Дорожная сеть
```

#### 2.2 Параметры оборудования
- **Самосвалы**: грузоподъемность, расход топлива, скорость
- **Экскаваторы**: объем ковша, скорость работы
- **Пункты разгрузки**: тип разгрузки, пропускная способность

### 3. Расчетные модули

#### 3.1 Временные расчеты
```python
# Время погрузки
T_load[i,j] = ShovelCalc.calculate_load_cycles(shovel, truck)

# Время движения
T_haul[i,j,z] = TruckCalc.calculate_time_motion_by_edges(route, truck, loaded=True)
T_return[i,z,j] = TruckCalc.calculate_time_motion_by_edges(route, truck, loaded=False)

# Время разгрузки  
T_unload[i,z] = UnloadCalc.unload_calculation_by_norm(unload, truck)
```

#### 3.2 Надежность системы (Reliability)
- Статистический анализ результатов многократных симуляций
- Расчет доверительных интервалов
- Оценка стабильности работы системы

### 4. Визуализация и отчетность

#### 4.1 Телеметрия в реальном времени
- Позиционирование оборудования
- Состояние техники (работа, простой, ремонт)
- Очереди на погрузку/разгрузку

#### 4.2 Отчеты производительности
- Количество рейсов
- Объем перевезенного материала
- Почасовые показатели работы

### 5. Конфигурация системы

#### 5.1 Настройки симуляции
```python
SIM_CONFIG = {
    "solver": "CP-SAT",              # Алгоритм оптимизации
    "time_limit": 300,               # Лимит времени решения
    "workers": 16,                   # Количество потоков
    "reliability_calc_enabled": True,# Включение расчета надежности
    "msg": True                      # Логирование процесса
}
```

#### 5.2 Физические константы
```python
# Коэффициенты сопротивления материалов
koef_soprotivleniya = {
    PayloadType.GRAVEL: 1.0,   # Щебень
    PayloadType.SAND: 1.1,     # Песок
    PayloadType.CLAY: 1.4,     # Глина
    PayloadType.WET_ORE: 1.5   # Влажная руда
}

# Плотность материалов
density_by_material = {
    PayloadType.SAND: 1.6,      # песок
    PayloadType.CLAY: 1.9,      # глина  
    PayloadType.GRAVEL: 1.5,    # щебень
    PayloadType.WET_ORE: 2.7    # влажная руда
}
```