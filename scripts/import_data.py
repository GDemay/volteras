import os
import sys
from pathlib import Path

# Add the parent directory of the current script to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import csv
from datetime import datetime
from app.core.database import SessionLocal
from app.core.database.models import VehicleDatabase
from app.api.models.vehicle_data import VehicleModel
from app.api.services.vehicle_data_service import VehicleDataService


def import_data(csv_file_path):
    db = SessionLocal()
    vehicle_data_service = VehicleDataService(db=db)
    basename = os.path.basename(os.path.splitext(csv_file_path)[0])
    with open(csv_file_path, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        vehicles = []
        for row in reader:
            # Parse the CSV row into a VehicleData object
            # Add id to the VehicleData object
            # TODO Handle if a vehicle
            vehicle = VehicleModel(
                vehicle_id=basename,
                timestamp=None
                if row["timestamp"] == "NULL"
                else datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S.%f"),
                speed=None if row["speed"] == "NULL" else float(row["speed"]),
                odometer=None if row["odometer"] == "NULL" else float(row["odometer"]),
                soc=None if row["soc"] == "NULL" else int(row["soc"]),
                elevation=None
                if row["elevation"] == "NULL"
                else float(row["elevation"]),
                shift_state=None
                if row["shift_state"] == "NULL"
                else row["shift_state"],
            )

            vehicle = VehicleDatabase(**vehicle.dict())
            vehicle = vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)

    print(f"Data imported successfully! for {basename}")


def drop_data():
    db = SessionLocal()
    db.query(VehicleDatabase).delete()
    db.commit()
    db.close()
    print("Data dropped successfully!")


if __name__ == "__main__":
    # Get all files from the data directory

    directory = "data"
    csv_files = [
        file
        for file in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, file)) and file.endswith(".csv")
    ]
    drop_data()
    for csv_file in csv_files:
        import_data(f"{directory}/{csv_file}")
