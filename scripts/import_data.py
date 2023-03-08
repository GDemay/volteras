import csv
import os
from datetime import datetime
from pathlib import Path
import sys
from typing import List
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.api.models.vehicle_data import VehicleModel
from app.api.services.vehicle_data_service import VehicleDataService
from app.core.database import SessionLocal
from app.core.database.models import VehicleDatabase


def import_data(csv_file_path: str) -> None:
    """
    Import vehicle data from a CSV file and add it to the database.

    Args:
        csv_file_path: The path to the CSV file containing the vehicle data.

    Returns:
        None.
    """
    # Create a database session and a vehicle data service
    db = SessionLocal()
    vehicle_data_service = VehicleDataService(db=db)

    # Get the basename of the CSV file (without the extension) to use as the vehicle ID
    basename = os.path.basename(os.path.splitext(csv_file_path)[0])

    # Open the CSV file and read its contents
    with open(csv_file_path, "r") as csv_file:
        reader = csv.DictReader(csv_file)

        # Parse each row of the CSV file into a VehicleModel object and add it to the database
        for row in reader:
            vehicle = VehicleModel(
                vehicle_id=basename,
                timestamp=None
                if row["timestamp"] == "NULL"
                else datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S.%f"),
                speed=None if row["speed"] == "NULL" else float(row["speed"]),
                odometer=None if row["odometer"] == "NULL" else float(row["odometer"]),
                soc=None if row["soc"] == "NULL" else int(row["soc"]),
                elevation=None if row["elevation"] == "NULL" else float(row["elevation"]),
                shift_state=None if row["shift_state"] == "NULL" else row["shift_state"],
            )
            vehicle_db = VehicleDatabase(**vehicle.dict())
            vehicle_data_service.add_vehicle_data(vehicle_database=vehicle_db)

    # Print a success message
    print(f"Data imported successfully for {basename}")


def drop_data() -> None:
    """
    Drop all vehicle data from the database.

    Returns:
        None.
    """
    # Create a database session and delete all VehicleDatabase objects
    db = SessionLocal()
    db.query(VehicleDatabase).delete()
    db.commit()
    db.close()

    # Print a success message
    print("Data dropped successfully!")


if __name__ == "__main__":
    # Get a list of all CSV files in the 'data' directory
    directory = "data"
    csv_files: List[str] = [
        file
        for file in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, file)) and file.endswith(".csv")
    ]

    # Drop all existing data from the database
    # Comment if you don't want to drop the data
    drop_data()

    # Import the data from each CSV file into the database
    for csv_file in csv_files:
        import_data(f"{directory}/{csv_file}")
