import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from app import create_app, get_db, get_redis
from app.models import Quarry


def redis_mock():
    """Создает мок-сессию базы данных"""
    with patch('app.routes.get_redis') as mock_get_db:
        mock_session = Mock()
        mock_get_db.return_value = mock_session
        yield mock_session


@pytest.fixture(scope="function")
def app():
    # Убедимся, что файл static/index.html существует / Иначе - генерим простой html
    # Это нужно для самого простого теста, который должен всегда проходить
    static_dir = Path("static")
    created_static_dir = False
    created_index = False
    try:
        if not static_dir.exists():
            static_dir.mkdir()
            created_static_dir = True

        index_file = static_dir / "index.html"
        if not index_file.exists():
            index_file.write_text("<html><body>Test Handbook</body></html>")
            created_index = True

        # C БД никак не взаимодействуем на тестах
        # Это заглушка, во избежание ошибок
        test_config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "postgresql+psycopg://test:test@localhost/test",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
        app = create_app(test_config)

        # --- REDIS MOCK ---
        mock_redis = Mock()
        mock_redis.exists.return_value = 0
        mock_redis.get.return_value = None
        mock_redis.hgetall.return_value = {}
        mock_redis.lrange.return_value = []
        mock_redis.keys.return_value = []
        mock_redis.scan_iter.return_value = iter([])  # <--- важно!

        app.dependency_overrides[get_redis] = lambda: mock_redis

        # --- DB MOCK ---
        mock_db = MagicMock()
        # Все вызовы .execute(select(...)) возвращают объект, у которого есть .scalar() -> None
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_db.execute.return_value = mock_result

        def override_get_db():
            yield mock_db


        app.dependency_overrides[get_db] = override_get_db
        app.state.mock_db = mock_db

        yield app
    finally:
        # Убираем временный файл/папку, если создали их для теста
        try:
            if created_index:
                (Path("static") / "index.html").unlink()
            # удаляем папку только если мы её создали и она пустая
            if created_static_dir:
                try:
                    Path("static").rmdir()
                except OSError:
                    # возможно папка не пуста — оставим как есть
                    pass
        except Exception:
            pass


@pytest.fixture(scope="function")
def client(app):
    """Создает тестовый клиент FastAPI"""
    return TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    """Создает мок-сессию базы данных"""
    with patch('app.routes.get_db') as mock_get_db:
        mock_session = Mock()
        mock_get_db.return_value = mock_session
        yield mock_session


@pytest.fixture(scope="function")
def init_database(db_session):
    """Создает тестовые данные в базе (mocked)"""
    quarry_data = {
        "name": "testquarry",
        "center_lat": 0.0,
        "center_lon": 0.0,
        "center_height": 0.0,
        "timezone": "Europe/Moscow",
        "shift_config": [
            {"begin_offset": 480, "end_offset": 1200},
            {"begin_offset": 1200, "end_offset": 1920}
        ],
        "work_break_duration": 10,
        "work_break_rate": 1,
        "lunch_break_offset": 360,
        "lunch_break_duration": 60
    }
    quarry = Mock(spec=Quarry, id=1, **quarry_data)

    return {
        'quarry': quarry
    }
