#!/bin/bash
export PYTHONPATH=$(pwd)

ALEMBIC_INI=${ALEMBIC_INI:-"app/migrations/alembic.ini"}

# Настройки запуска FastAPI
APP_MODE=${APP_MODE:-dev}                          # prod или dev
APP_MODULE=${APP_MODULE:-"app:app"}          # пример: app.main:app
GUNICORN_CONF=${GUNICORN_CONF:-"./app/gunicorn.conf.py"}
UVICORN_HOST=${UVICORN_HOST:-"0.0.0.0"}
UVICORN_PORT=${UVICORN_PORT:-8000}

echo "=== Миграции ==="


if command -v alembic >/dev/null 2>&1; then
  if [ -f "$ALEMBIC_INI" ]; then
    echo "Найден alembic и конфиг: $ALEMBIC_INI"
    echo "alembic history"
    alembic -c "$ALEMBIC_INI" history || true
    echo "alembic upgrade head"
    alembic -c "$ALEMBIC_INI" upgrade head
    echo "alembic current"
    alembic -c "$ALEMBIC_INI" current || true
  else
    echo "alembic доступен, но файл конфигурации не найден по пути: $ALEMBIC_INI"
    if [ -d "./migrations" ] || [ -d "migrations" ]; then
      echo "В проекте найдена папка migrations. Рекомендуется либо переместить alembic.ini в $ALEMBIC_INI, либо создать симлинк."
    fi
  fi
  echo "Не найден 'alembic'. Пропускаю миграции."
fi

echo "=== Запуск приложения ==="
if [ "$APP_MODE" = "prod" ]; then
  echo "Запуск в режиме GUNICORN + Uvicorn workers (production)"
  if ! command -v gunicorn >/dev/null 2>&1; then
    echo "Ошибка: gunicorn не найден в PATH. Установите gunicorn и повторите."
    exit 2
  fi
  # Запуск gunicorn с UvicornWorker
  gunicorn -k uvicorn.workers.UvicornWorker "$APP_MODULE" -c "$GUNICORN_CONF"
else
  echo "Запуск в режиме Uvicorn (development)"
  if ! command -v uvicorn >/dev/null 2>&1; then
    echo "Ошибка: uvicorn не найден в PATH. Установите uvicorn и повторите."
    exit 2
  fi
  uvicorn "$APP_MODULE" --host "$UVICORN_HOST" --port "$UVICORN_PORT" --reload
fi
