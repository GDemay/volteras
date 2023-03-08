from ast import List
from typing import Any
from app.api.services.vehicle_data_service import VehicleDataService
from app.api.models.vehicle_data import VehicleModel
from sqlalchemy.ext.declarative import declarative_base
from app.core.database.models import Base, SortBy, VehicleDatabase
from datetime import datetime, timedelta
from tests.conftest import override_get_db, client


def test_root_endpoint():
    """
    Tests the root endpoint of the application by sending a GET request to it and checking if the response
    status code is 200 and the response JSON is as expected.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello World": "Hello World"}


def test_get_vehicle_data_by_id(test_db: None, add_vehicle_id: Any) -> None:
    # Send a GET request to the endpoint with vehicle ID 1
    response = client.get("/api/v1/vehicle_data/1/")

    # Check if the response status code is 200
    assert response.status_code == 200

    # Check if the response JSON matches the expected output
    expected_output = {
        "vehicle_id": "my_vehicle_id",
        "timestamp": "2032-01-01T00:00:00",
        "speed": 50,
        "elevation": 9545.0,
        "odometer": None,
        "soc": None,
        "shift_state": None,
    }
    assert response.json() == expected_output



def test_get_empty_vehicle_data(test_db: None) -> None:
    """
    GIVEN an empty database
    WHEN a GET request is sent to get the vehicle data
    THEN an empty list is returned
    """
    # Send a GET request to get the vehicle data
    response = client.get("/api/v1/vehicle_data/")

    # Ensure the response status code is 200 and an empty list is returned
    assert response.status_code == 200
    assert response.json() == []



def test_add_vehicle_data(test_db):
    # Send a POST request to add vehicle data to the API
    vehicle_data = {
        "vehicle_id": "my_vehicle_id",
        "timestamp": "2032-01-01T00:00:00",
        "speed": 50,
        "elevation": 55,
        "odometer": 676,
        "soc": 142,
        "shift_state": "blabla",
    }
    response = client.post(
        "/api/v1/vehicle_data/",
        json=vehicle_data,
    )

    # Assert that the response status code is 200
    assert response.status_code == 200

    # Assert that the response JSON matches the vehicle data sent
    assert response.json() == vehicle_data

    # Check that only one vehicle exists in the database with the given vehicle ID
    response = client.get(f"/api/v1/vehicle_data/?vehicle_id={vehicle_data['vehicle_id']}")

    # Assert that the response status code is 200
    assert response.status_code == 200

    # Assert that only one vehicle exists in the response JSON
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


def test_get_vehicle_data_with_limit(test_db: None, add_vehicle_id: None):
    """Test the get_vehicle_data function with a limit parameter."""
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))

    # Add 100 vehicles
    timestamp = datetime(2032, 1, 1, 0, 0, 0)
    for i in range(100):
        timestamp = timestamp + timedelta(days=1)
        vehicle = VehicleDatabase(
            vehicle_id="my_vehicle_id",
            timestamp=timestamp,
            speed=50 + i,
            elevation=9545 + i,
        )
        vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)

    # Get first 10 vehicles
    vehicles = vehicle_data_service.get_vehicle_data(vehicle_id="my_vehicle_id", limit=10)

    assert len(vehicles) == 10




def test_get_vehicle_data_with_invalid_vehicle_id(test_db) -> None:
    """
    Test that the get_vehicle_data method of VehicleDataService returns an empty list
    when an invalid vehicle_id is provided
    """
    vehicle_data_service = VehicleDataService(db=next(get_db()))

    # Add 10 vehicles with the same vehicle_id
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

    # Get vehicle data with an invalid vehicle_id
    vehicles: List[VehicleDatabase] = vehicle_data_service.get_vehicle_data(
        vehicle_id="INVALID_VEHICLE_ID",
    )

    assert len(vehicles) == 0


def test_get_vehicle_data_with_sort_by_asc(test_db, add_vehicle_id):
    # Create VehicleDataService object
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))

    # Create 3 vehicles with different timestamps
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

    # Convert VehicleModel objects to VehicleDatabase objects
    vehicles = [VehicleDatabase(**vehicle.dict()) for vehicle in [vehicle1, vehicle2, vehicle3]]

    # Add vehicles to the database
    vehicle_data_service.db.add_all(vehicles)

    # Commit the changes to the database
    vehicle_data_service.db.commit()

    # Get vehicles sorted by ascending timestamp
    vehicles = vehicle_data_service.get_vehicle_data(vehicle_id="BONJOUR", sort_by=SortBy.ASC)

    # Check that we have received all 3 vehicles
    assert len(vehicles) == 3

    # Check that the timestamps of the vehicles are sorted in ascending order
    assert vehicles[0].timestamp == datetime(2032, 1, 1, 0, 0)
    assert vehicles[1].timestamp == datetime(2032, 1, 2, 0, 0)
    assert vehicles[2].timestamp == datetime(2032, 1, 3, 0, 0)



def test_get_vehicle_data_with_sort_by_desc(test_db, add_vehicle_id):
    """
    Test function to check if vehicles are sorted in descending order of timestamp
    """
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
    vehicles_list = [VehicleDatabase(**vehicle.dict()) for vehicle in [vehicle1, vehicle2, vehicle3]]
    vehicle_data_service.db.add_all(vehicles_list)
    vehicle_data_service.db.commit()

    # Get vehicles sorted by descending timestamp
    vehicles = vehicle_data_service.get_vehicle_data(vehicle_id="BONJOUR", sort_by=SortBy.DESC)

    # Assertion tests
    assert len(vehicles) == 3
    assert vehicles[0].timestamp == datetime(2032, 1, 3, 0, 0)
    assert vehicles[1].timestamp == datetime(2032, 1, 2, 0, 0)
    assert vehicles[2].timestamp == datetime(2032, 1, 1, 0, 0)


def test_get_vehicle_data_with_sorting(test_db, add_vehicle_id):
    # Initialize the vehicle data service
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))

    # Add 5 vehicles with random speeds
    timestamp = datetime(2032, 1, 1, 0, 0, 0)
    for speed in [53, 54, 51, 52, 50]:
        timestamp += timedelta(days=1)
        vehicle = VehicleDatabase(
            vehicle_id="BONJOUR",
            timestamp=timestamp,
            speed=speed,
            elevation=9545 + speed,
        )
        vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)

    # Get all the vehicles sorted by speed in descending order
    vehicles: List[VehicleDatabase] = vehicle_data_service.get_vehicle_data(vehicle_id="BONJOUR", sort_by=SortBy.DESC)

    # Check the length of the returned vehicles
    assert len(vehicles) == 5

    # Check the order of the speeds of the returned vehicles
    assert vehicles[0].speed == 50
    assert vehicles[-1].speed == 53


def test_get_vehicle_data_with_invalid_vehicle_id(test_db, add_vehicle_id):
    # Create a vehicle data service object
    vehicle_data_service = VehicleDataService(db=next(override_get_db()))

    # Add 5 vehicles with random speeds
    vehicles = []
    timestamp = datetime(2032, 1, 1, 0, 0, 0)
    for i in [3, 1, 5, 2, 4]:
        timestamp = timestamp + timedelta(days=1)
        vehicle_data = VehicleModel(
            vehicle_id="BONJOUR",
            timestamp=timestamp,
            speed=50 + i,
            elevation=9545 + i,
        )
        vehicle = VehicleDatabase(**vehicle_data.dict())
        vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)
        vehicles.append(vehicle)

    # get all the vehicles with an invalid vehicle id
    invalid_vehicles = vehicle_data_service.get_vehicle_data(vehicle_id="INVALID", sort_by=SortBy.DESC)

    # Check if the invalid vehicle list is empty
    assert len(invalid_vehicles) == 0

