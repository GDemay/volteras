from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from app.api.endpoints.vehicle_data import add_vehicle_data
from main import app
from app.core.database import SessionLocal, engine
from app.api.services.vehicle_data_service import VehicleDataService
from app.api.models.vehicle_data import VehicleModel
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
from sqlalchemy.ext.declarative import declarative_base
from app.core.database import SessionLocal, get_db
from app.core.database.models import Base, VehicleDatabase

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


# @pytest.fixture()
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def add_vehicle_id(test_db):
    # Create a vehicle in the database
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))
    vehicle1 = VehicleModel(
        vehicle_id="BONJOUR",
        timestamp="2032-01-01T00:00:00.000Z",
        speed=50,
        elevation=9545,
    )
    vehicle = VehicleDatabase(**vehicle1.dict())
    return vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)


def test_hello_world(test_db):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello World": "Hello World"}


def test_get_vehicle_data_by_id(test_db, add_vehicle_id):
    response = client.get("/api/v1/vehicle_data/1/")
    assert response.status_code == 200
    assert response.json() == {
        "vehicle_id": "BONJOUR",
        "timestamp": "2032-01-01T00:00:00",
        "speed": 50,
        "elevation": 9545.0,
        "odometer": None,
        "soc": None,
        "shift_state": None,
    }


def test_check_empty_db(test_db):
    response = client.get("/api/v1/vehicle_data/")
    assert response.status_code == 200
    assert response.json() == []


def test_add_vehicle_data(test_db):
    response = client.post(
        "/api/v1/vehicle_data/",
        json={
            "vehicle_id": "my_vehicle_id",
            "timestamp": "2032-01-01T00:00:00",
            "speed": 50,
            "elevation": 55,
            "odometer": 676,
            "soc": 142,
            "shift_state": "blabla",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "vehicle_id": "my_vehicle_id",
        "timestamp": "2032-01-01T00:00:00",
        "speed": 50,
        "elevation": 55,
        "odometer": 676,
        "soc": 142,
        "shift_state": "blabla",
    }

    # Check that only one vehicle exists in the database
    response = client.get(f"/api/v1/vehicle_data/?vehicle_id=my_vehicle_id")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_vehicle_data(test_db):
    response = client.get("/api/v1/vehicle_data/")
    assert response.status_code == 200

    vehicle_data_service = VehicleDataService(db=next(override_get_db()))
    # Transform a VehicleModel into a VehicleDatabase

    # Create a vehicleModel object
    vehicle_id = "aa"
    vehicle1 = VehicleModel(
        vehicle_id=vehicle_id,
        timestamp="2022-01-01T00:00:00.000Z",
        speed=50,
        elevation=None,
    )

    vehicle = VehicleDatabase(**vehicle1.dict())
    vehicle = vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)

    # Add the vehicle to the database
    response = client.get(f"/api/v1/vehicle_data/?vehicle_id={vehicle_id}")
    assert response.status_code == 200

    # Assert that the response contains the added vehicle
    data = response.json()
    assert len(data) == 1
    assert data[0]["vehicle_id"] == vehicle_id
    assert data[0]["timestamp"] == "2022-01-01T00:00:00"
    assert data[0]["speed"] == 50
    assert data[0]["elevation"] is None
