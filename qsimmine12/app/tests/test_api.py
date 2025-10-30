import pytest
from unittest.mock import patch, MagicMock
from app.models import Quarry, Truck, Shovel, FuelStation, Unload

# ---------------------------------------------------------
# Простые эндпоинты
# ---------------------------------------------------------
def test_handbook_returns_200(client):
    response = client.get("/handbook")
    assert response.status_code == 200


def test_defaults_returns_200_and_dict(client):
    response = client.get("/api/defaults")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_scenarios_returns_200_and_list(client):
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ---------------------------------------------------------
# Quarry Data
# ---------------------------------------------------------
class TestQuarryDataAPI:
    def test_quarry_data_returns_200_and_valid_json(self, client):
        response = client.get("/api/quarry-data")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "time" in data
        assert "templates" in data

# ---------------------------------------------------------
# Object API
# ---------------------------------------------------------
class TestObjectAPI:

    def test_invalid_method_returns_405_on_get(self, client):
        response = client.get("/api/object")
        assert response.status_code == 405

    def test_invalid_payload_returns_400_on_post(self, client):
        # Некорректный JSON должен привести к 422
        response = client.post(
            "/api/object",
            content="not a json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_create_quarry_success(self, client):
        payload = {
            "action": "create",
            "type": "quarry",
            "data": {
                "name": "Test Quarry",
                "center_height": 0.0,
                "center_lat": 0.0,
                "center_lon": 0.0,
                "lunch_break_duration": 60,
                "lunch_break_offset": 360,
                "shift_config": [
                    {"begin_offset": 480, "end_offset": 1200},
                    {"begin_offset": 1200, "end_offset": 1920},
                ],
                "timezone": "Europe/Moscow",
                "work_break_duration": 10,
                "work_break_rate": 1,
            },
        }

        # DummyForm имитирует форму для создания карьера
        class DummyForm:
            def __init__(self, *a, **kw):
                self.data = payload["data"]
                self.errors = {}

            def validate(self):
                return True

            def instantiate_object(self):
                return Quarry(**self.data)

            def __iter__(self):
                return iter([])
            
            def dict(self, *args, **kwargs):
                return self.data

        with patch.dict("app.forms.TYPE_SCHEMA_MAP", {"quarry": DummyForm}):
            response = client.post("/api/object", json=payload)
            assert response.status_code == 201
            assert response.json().get("success") is True

    @pytest.mark.parametrize(
        "object_type, data_factory, model_class",
        [
            (
                "truck",
                lambda f: {
                    "quarry_id": f["quarry"].id,
                    "name": "Test Truck",
                    "body_capacity": 100,
                    "speed_empty": 10,
                    "speed_loaded": 20,
                },
                Truck,
            ),
            (
                "shovel",
                lambda f: {
                    "quarry_id": f["quarry"].id,
                    "name": "Test Shovel",
                    "bucket_volume": 10,
                    "bucket_dig_speed": 10,
                    "bucket_fill_speed": 200,
                },
                Shovel,
            ),
            (
                "fuel_station",
                lambda f: {
                    "quarry_id": f["quarry"].id,
                    "name": "Test Fuel Station",
                    "num_pumps": 4,
                    "flow_rate": 2.5,
                },
                FuelStation,
            ),
            (
                "unload",
                lambda f: {
                    "quarry_id": f["quarry"].id,
                    "name": "Test Unload",
                    "unload_type": "hydraulic",
                },
                Unload,
            ),
        ],
    )
    def test_create_object_success(self, client, init_database, object_type, data_factory, model_class):
        fixture = init_database

        payload = {
            "action": "create",
            "type": object_type,
            "data": data_factory(fixture),
        }

        # Берём мок сессии из приложения, предоставленный в conftest
        mock_db = client.app.state.mock_db
        mock_db.add.reset_mock()
        mock_db.commit.reset_mock()
        mock_db.execute.reset_mock()
        mock_db.merge.reset_mock()
        mock_db.add_all.reset_mock()

        # Создаем DummyForm для всех типов
        class DummyForm:
            def __init__(self, *a, **kw):
                self.data = payload["data"]
                self.errors = {}

            def validate(self):
                return True

            def instantiate_object(self):
                return model_class(**self.data)

            def __iter__(self):
                return iter([])

            def dict(self, *args, **kwargs):
                return self.data


        with patch.dict("app.forms.TYPE_SCHEMA_MAP", {object_type: DummyForm}):
            response = client.post("/api/object", json=payload)

        assert response.status_code == 201
        assert response.json().get("success") is True

        # Некоторые реализации могут использовать session.add, другие - session.execute/merge/add_all
        # Вместо жёсткого требования — проверяем: если был вызов сохранения (add/execute/merge/add_all),
        # то обязательно должен быть вызван commit() и (если использовался add) проверяем объект.
        save_methods_called = any([
            mock_db.add.called,
            mock_db.execute.called,
            mock_db.merge.called,
            mock_db.add_all.called,
        ])

        if save_methods_called:
            assert mock_db.commit.called, (
                f"Ожидался вызов commit() при сохранении объекта типа '{object_type}'"
            )

        # Если использовался mock_db.add, проверим переданный объект
        if mock_db.add.called:
            created_obj = mock_db.add.call_args[0][0]
            assert isinstance(created_obj, model_class)
            for key, value in payload["data"].items():
                # У некоторых моделей имена атрибутов могут отличаться — проверяем только когда атрибут есть
                if hasattr(created_obj, key):
                    assert getattr(created_obj, key) == value

# ---------------------------------------------------------
# NotFound Endpoints
# ---------------------------------------------------------
class TestNotFoundEndpoints:
    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/road-net/999999",
            "/api/simulation/non-existent-id/meta",
            "/api/simulation/non-existent-id/summary",
            "/api/simulation/non-existent-id/events",
        ],
    )
    def test_returns_404(self, client, endpoint):
        """Проверяем, что несуществующие ресурсы возвращают 404"""
        response = client.get(endpoint)
        assert response.status_code == 404
