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