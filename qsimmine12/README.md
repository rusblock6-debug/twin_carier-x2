# QSimMine12

## Sim Engine
### Работа с тестовым скриптом
>python -m app.sim_engine.tests.run_simulate  

Скрипт берет за основу набор входящих данных из input_sim_data.json  
Далее запускается движок симуляции и формирование итоговых данных. Телеметрия выгружается в файл telemetry.csv  
Расположение скрипта и всех сопутствующих файлов qsimmine12/app/sim_engine/tests/

## Тесты
### Запуск тестов
>pytest

