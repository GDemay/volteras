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
from app.core.database.models import Base, SortBy, VehicleDatabase
from datetime import datetime, timedelta

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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
        vehicle_id="my_vehicle_id",
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
        "vehicle_id": "my_vehicle_id",
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


def test_get_vehicle_data_with_limit(test_db, add_vehicle_id):
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))

    # Add 100 vehicles
    timestamp = datetime(2032, 1, 1, 0, 0, 0)
    for i in range(100):
        timestamp = timestamp + timedelta(days=1)
        vehicle1 = VehicleModel(
            vehicle_id="my_vehicle_id",
            timestamp=timestamp,
            speed=50 + i,
            elevation=9545 + i,
        )
        vehicle = VehicleDatabase(**vehicle1.dict())
        vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)

    # get first 10 vehicles
    vehicles = vehicle_data_service.get_vehicle_data(vehicle_id="my_vehicle_id", limit=10)

    assert len(vehicles) == 10


def test_get_vehicle_data_with_valid_vehicle_id_initial_and_final_timestamp(test_db):
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))

    # Add 10 vehicles
    timestamp = datetime(2032, 1, 1, 0, 0, 0)
    for i in range(10):
        timestamp = timestamp + timedelta(days=1)
        vehicle1 = VehicleModel(
            vehicle_id="my_vehicle_id",
            timestamp=timestamp,
            speed=50 + i,
            elevation=9545 + i,
        )
        vehicle = VehicleDatabase(**vehicle1.dict())
        vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)

    initial_timestamp = datetime(2032, 1, 3, 0, 0, 0)
    final_timestamp = datetime(2032, 1, 7, 0, 0, 0)
    vehicles = vehicle_data_service.get_vehicle_data(
        vehicle_id="my_vehicle_id",
        initial_timestamp=initial_timestamp,
        final_timestamp=final_timestamp,
    )

    assert len(vehicles) == 5


def test_get_vehicle_data_with_invalid_vehicle_id(test_db):
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))

    # Add 10 vehicles
    timestamp = datetime(2032, 1, 1, 0, 0, 0)
    for i in range(10):
        timestamp = timestamp + timedelta(days=1)
        vehicle1 = VehicleModel(
            vehicle_id="BONJOUR",
            timestamp=timestamp,
            speed=50 + i,
            elevation=9545 + i,
        )
        vehicle = VehicleDatabase(**vehicle1.dict())
        vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)

    vehicles = vehicle_data_service.get_vehicle_data(
        vehicle_id="INVALID_VEHICLE_ID",
    )

    assert len(vehicles) == 0


def test_get_vehicle_data_with_sort_by_asc(test_db, add_vehicle_id):
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))

    # Add 3 vehicles with different timestamps
    vehicle1 = VehicleModel(
        vehicle_id="BONJOUR",
        timestamp="2032-01-03T00:00:00.000Z",
        speed=50,
        elevation=9545,
    )
    vehicle2 = VehicleModel(
        vehicle_id="BONJOUR",
        timestamp="2032-01-02T00:00:00.000Z",
        speed=60,
        elevation=9546,
    )
    vehicle3 = VehicleModel(
        vehicle_id="BONJOUR",
        timestamp="2032-01-01T00:00:00.000Z",
        speed=70,
        elevation=9547,
    )
    vehicles = [VehicleDatabase(**vehicle.dict()) for vehicle in [vehicle1, vehicle2, vehicle3]]
    vehicle_data_service.db.add_all(vehicles)
    vehicle_data_service.db.commit()

    # Get vehicles sorted by ascending timestamp
    vehicles = vehicle_data_service.get_vehicle_data(vehicle_id="BONJOUR", sort_by=SortBy.ASC)

    assert len(vehicles) == 3
    assert vehicles[0].timestamp == datetime(2032, 1, 1, 0, 0)
    assert vehicles[1].timestamp == datetime(2032, 1, 2, 0, 0)
    assert vehicles[2].timestamp == datetime(2032, 1, 3, 0, 0)


def test_get_vehicle_data_with_sort_by_desc(test_db, add_vehicle_id):
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))

    # Add 3 vehicles with different timestamps
    vehicle1 = VehicleModel(
        vehicle_id="BONJOUR",
        timestamp="2032-01-03T00:00:00.000Z",
        speed=50,
        elevation=9545,
    )
    vehicle2 = VehicleModel(
        vehicle_id="BONJOUR",
        timestamp="2032-01-02T00:00:00.000Z",
        speed=60,
        elevation=9546,
    )
    vehicle3 = VehicleModel(
        vehicle_id="BONJOUR",
        timestamp="2032-01-01T00:00:00.000Z",
        speed=70,
        elevation=9547,
    )
    vehicles = [VehicleDatabase(**vehicle.dict()) for vehicle in [vehicle1, vehicle2, vehicle3]]
    vehicle_data_service.db.add_all(vehicles)
    vehicle_data_service.db.commit()

    # Get vehicles sorted by descending timestamp
    vehicles = vehicle_data_service.get_vehicle_data(vehicle_id="BONJOUR", sort_by=SortBy.DESC)

    assert len(vehicles) == 3
    assert vehicles[0].timestamp == datetime(2032, 1, 3, 0, 0)
    assert vehicles[1].timestamp == datetime(2032, 1, 2, 0, 0)
    assert vehicles[2].timestamp == datetime(2032, 1, 1, 0, 0)


def test_get_vehicle_data_with_offset(test_db, add_vehicle_id):
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))

    # Add 100 vehicles
    timestamp = datetime(2032, 1, 1, 0, 0, 0)
    for i in range(100):
        timestamp = timestamp + timedelta(days=1)
        vehicle1 = VehicleModel(
            vehicle_id="BONJOUR",
            timestamp=timestamp,
            speed=50 + i,
            elevation=9545 + i,
        )
        vehicle = VehicleDatabase(**vehicle1.dict())
        vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)

    # get 10 vehicles starting from the 10th vehicle
    vehicles = vehicle_data_service.get_vehicle_data(vehicle_id="BONJOUR", limit=10, offset=10)

    assert len(vehicles) == 10
    assert vehicles[0].speed == 50
    assert vehicles[-1].speed == 59


def test_get_vehicle_data_with_sorting(test_db, add_vehicle_id):
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))

    # Add 5 vehicles with random speeds
    timestamp = datetime(2032, 1, 1, 0, 0, 0)
    for i in [3, 1, 5, 2, 4]:
        timestamp = timestamp + timedelta(days=1)
        vehicle1 = VehicleModel(
            vehicle_id="BONJOUR",
            timestamp=timestamp,
            speed=50 + i,
            elevation=9545 + i,
        )
        vehicle = VehicleDatabase(**vehicle1.dict())
        vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)

    # get all the vehicles sorted by speed in descending order
    vehicles = vehicle_data_service.get_vehicle_data(vehicle_id="BONJOUR", sort_by=SortBy.DESC)

    assert len(vehicles) == 5
    assert vehicles[0].speed == 54
    assert vehicles[-1].speed == 53


def test_get_vehicle_data_with_invalid_vehicle_id(test_db, add_vehicle_id):
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))

    # Add 5 vehicles with random speeds
    timestamp = datetime(2032, 1, 1, 0, 0, 0)
    for i in [3, 1, 5, 2, 4]:
        timestamp = timestamp + timedelta(days=1)
        vehicle1 = VehicleModel(
            vehicle_id="BONJOUR",
            timestamp=timestamp,
            speed=50 + i,
            elevation=9545 + i,
        )
        vehicle = VehicleDatabase(**vehicle1.dict())
        vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)

    # get all the vehicles with an invalid vehicle id
    vehicles = vehicle_data_service.get_vehicle_data(vehicle_id="INVALID", sort_by=SortBy.DESC)

    assert len(vehicles) == 0
