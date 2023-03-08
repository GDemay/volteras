import csv
import io
import json
from typing import List, Union

from app.api.models.vehicle_data import VehicleModel
from app.core.database.models import ExportFormat
from fastapi.encoders import jsonable_encoder


class ExporterService:
    """
    Utility class for exporting vehicle data to CSV or JSON format.
    """

    @staticmethod
    def export(vehicle_data: List[VehicleModel], export_format: ExportFormat) -> Union[str, bytes]:
        """
        Export vehicle data in the specified format (CSV or JSON).

        Args:
            vehicle_data: A list of VehicleModel objects.
            export_format: The export format ("csv" or "json").

        Returns:
            The vehicle data in the specified format as a string or bytes object, depending on the Python version.
        """
        if export_format == ExportFormat.CSV:
            # Export the data as CSV
            csv_data = ExporterService._export_csv(vehicle_data)
            return csv_data
        elif export_format == ExportFormat.JSON:
            # Export the data as JSON
            json_data = ExporterService._export_json(vehicle_data)
            return json_data
        else:
            # Invalid export format
            raise ValueError(f"Invalid export format: {export_format}")

    @staticmethod
    def _export_csv(vehicle_data: List[VehicleModel]) -> Union[str, bytes]:
        """
        Export vehicle data as CSV.

        Args:
            vehicle_data: A list of VehicleModel objects.

        Returns:
            The vehicle data as a CSV string or bytes object, depending on the Python version.
        """
        json_data = jsonable_encoder(vehicle_data)

        # Create a CSV file-like object in memory
        csv_file = io.StringIO()

        # Create a CSV writer object
        csv_writer = csv.writer(csv_file, lineterminator='\n')

        # Write the CSV header row
        csv_writer.writerow(["vehicle_id", "timestamp", "speed", "odometer", "elevation", "soc", "shift_state"])

        # Write each data row to the CSV file
        for row in json_data:
            csv_writer.writerow([row["vehicle_id"], row["timestamp"], row["speed"], row["odometer"], row["elevation"], row["soc"], row["shift_state"]])

        # Get the CSV data as a string
        csv_data = csv_file.getvalue()

        # Print the CSV data
        print(csv_data)
        return csv_data

    @staticmethod
    def _export_json(vehicle_data: List[VehicleModel]) -> str:
        """
        Export vehicle data as JSON.

        Args:
            vehicle_data: A list of VehicleModel objects.

        Returns:
            The vehicle data as a JSON string.
        """
        # Convert the VehicleModel objects to a list of dictionaries
        json_data = jsonable_encoder(vehicle_data)

        return json_data
