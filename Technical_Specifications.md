# Технические спецификации карьерного симулятора

## Содержание
1. [API системы](#api-системы)
2. [Форматы данных](#форматы-данных)
3. [Алгоритмы оптимизации](#алгоритмы-оптимизации)
4. [Модели надежности](#модели-надежности)
5. [Протоколы связи](#протоколы-связи)
6. [Схемы БД](#схемы-бд)

## API системы

### 1.1 REST API

#### Основные эндпоинты
```python
# Запуск симуляции
POST /api/v1/simulations
{
    "config": {...},
    "scenario": {...}
}

# Получение результатов
GET /api/v1/simulations/{id}

# Управление симуляцией
DELETE /api/v1/simulations/{id}
PUT /api/v1/simulations/{id}/pause
PUT /api/v1/simulations/{id}/resume

# Мониторинг
GET /api/v1/simulations/{id}/telemetry
GET /api/v1/simulations/{id}/events
```

### 1.2 WebSocket API
```python
# Подключение
wss://{host}/api/v1/ws/simulations/{id}

# Сообщения
{
    "type": "telemetry|event|status",
    "data": {...},
    "timestamp": "ISO-8601"
}
```

## Форматы данных

### 2.1 Входные данные
```json
{
    "version": "2.0.0",
    "metadata": {...},
    "scenario": {
        "time": {...},
        "quarry": {...},
        "equipment": {
            "trucks": [...],
            "shovels": [...],
            "unloads": [...]
        },
        "road_network": {...},
        "constraints": {...}
    }
}
```

### 2.2 Выходные данные
```json
{
    "status": "completed|failed|running",
    "execution_time": 123.45,
    "summary": {...},
    "telemetry": [...],
    "events": [...],
    "metrics": {...},
    "optimization_report": {...}
}
```

## Алгоритмы оптимизации

### 3.1 CP-SAT
```python
# Пример конфигурации
cp_model = CpModel()

# Переменные
x = {}
for i in trucks:
    for j in shovels:
        for z in unloads:
            x[(i,j,z)] = cp_model.NewBoolVar(f'x_{i}_{j}_{z}')

# Ограничения
for i in trucks:
    cp_model.Add(sum(x[(i,j,z)] for j in shovels for z in unloads) <= max_trips)

# Целевая функция
cp_model.Maximize(sum(
    x[(i,j,z)] * value_matrix[(i,j,z)] 
    for i,j,z in product(trucks, shovels, unloads)
))
```

### 3.2 MILP
```python
# Создание модели
model = LpProblem("QuarryOptimization", LpMaximize)

# Переменные
x = LpVariable.dicts(
    "route", 
    product(trucks, shovels, unloads), 
    0, 1, LpBinary
)

# Ограничения
for i in trucks:
    model += lpSum(x[(i,j,z)] for j in shovels for z in unloads) <= max_trips[i]

# Решение
solver = HiGHS_CMD(timeLimit=300)
model.solve(solver)
```

## Модели надежности

### 4.1 Статистические методы
```python
def monte_carlo_simulation(runs):
    results = []
    for _ in range(runs):
        result = run_simulation()
        results.append(result['summary']['weight'])
    return {
        'mean': np.mean(results),
        'std': np.std(results),
        'ci': stats.norm.interval(0.95, loc=np.mean(results), scale=np.std(results)/np.sqrt(len(results)))
    }
```

### 4.2 Анализ чувствительности
```python
def sensitivity_analysis(base_config, params):
    results = {}
    for param, values in params.items():
        param_results = []
        for value in values:
            config = base_config.copy()
            config[param] = value
            result = run_simulation(config)
            param_results.append(result['metric'])
        results[param] = param_results
    return results
```

## Протоколы связи

### 5.1 Внутрисистемные
- gRPC для межсервисного взаимодействия
- Protocol Buffers для сериализации
- ZeroMQ для потоковой передачи данных

### 5.2 Внешние интеграции
- REST API для управления
- WebSocket для реального времени
- MQTT для IoT устройств

## Схемы БД

### 6.1 Основные таблицы
```sql
CREATE TABLE simulations (
    id SERIAL PRIMARY KEY,
    config JSONB NOT NULL,
    scenario JSONB NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE TABLE telemetry (
    simulation_id INTEGER REFERENCES simulations(id),
    timestamp TIMESTAMPTZ,
    object_id VARCHAR(50),
    object_type VARCHAR(20),
    data JSONB,
    PRIMARY KEY (simulation_id, timestamp, object_id)
);
```

### 6.2 Индексы
```sql
CREATE INDEX idx_simulations_status ON simulations(status);
CREATE INDEX idx_telemetry_simulation ON telemetry(simulation_id);
CREATE INDEX idx_telemetry_object ON telemetry(object_id);
```

## Заключение

Данный документ содержит полные технические спецификации системы, включая API, форматы данных, алгоритмы и схемы баз данных. Для получения дополнительной информации обратитесь к другим разделам документации.