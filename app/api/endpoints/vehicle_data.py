"""
This module defines the API endpoints for vehicle data.
"""

from enum import Enum
from fastapi import APIRouter, HTTPException, Query, Response
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.responses import JSONResponse

from app.api.models.vehicle_data import VehicleModel
from app.api.services.exporter_service import ExporterService
from app.api.services.vehicle_data_service import VehicleDataService
from app.core.database.models import VehicleDatabase, SortBy, ExportFormat
from app.core.database import SessionLocal, get_db
from fastapi import Depends

router = APIRouter()


@router.get("/api/v1/vehicle_data/", response_model=List[VehicleModel])
async def get_vehicle_data(
    export_format: Optional[ExportFormat] = Query(None, alias="export-format"),
    vehicle_id: str = "f212b271-f033-444c-a445-560511f95e9c",
    db: Session = Depends(get_db),
    initial_timestamp: Optional[datetime] = Query(None, alias="initial-timestamp"),
    final_timestamp: Optional[datetime] = Query(None, alias="final-timestamp"),
    sort_by: Optional[SortBy] = Query(None, alias="sort-by"),
    limit: Optional[int] = Query(3, alias="limit"),
    skip: Optional[int] = Query(None, alias="skip"),
):
    """
    Get vehicle data filtered by query parameters and optionally export the data in the specified format.

    Args:
        export_format: The format in which to export the data.
        vehicle_id: The ID of the vehicle to retrieve data for.
        db: The database session.
        initial_timestamp: The initial timestamp to filter by.
        final_timestamp: The final timestamp to filter by.
        sort_by: The field to sort the data by.
        limit: The maximum number of records to return.
        skip: The number of records to skip.

    Returns:
        If an export format is specified, returns a response with the exported data. Otherwise, returns a list of VehicleModel objects.
    """
    # Initialize vehicle data service
    vehicle_data_service = VehicleDataService(db=db)

    # Get vehicle data filtered by query parameters
    vehicle_data = vehicle_data_service.get_vehicle_data(
        vehicle_id=vehicle_id,
        initial_timestamp=initial_timestamp,
        final_timestamp=final_timestamp,
        sort_by=sort_by,
        limit=limit,
        skip=skip,
    )

    # Export the data in the specified format if requested
    if export_format:
        # Export the data in the specified format
        exported_data = ExporterService.export(vehicle_data, export_format)

        # Set the media type and headers for the response
        media_type = "text/csv" if export_format == ExportFormat.CSV else "application/json"
        response = JSONResponse(
        content=exported_data,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=vehicle_data.{export_format.value.lower()}",
        },
        )

        return response

    # Return the data as a list of VehicleModel objects if no export format is requested
    else:
        return vehicle_data


@router.get("/api/v1/vehicle_data/{id}/", response_model=VehicleModel)
async def get_vehicle_data_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a particular vehicle data by ID.
    """
    vehicle_data_service = VehicleDataService(db=db)
    vehicle_data = vehicle_data_service.get_vehicle_data_by_id(id=id)
    if vehicle_data is None:
        raise HTTPException(status_code=404, detail=f"Vehicle data with id {id} not found")
    return vehicle_data


# Add new vehicle
@router.post("/api/v1/vehicle_data/", response_model=VehicleModel)
async def add_vehicle_data(vehicle: VehicleModel, db: Session = Depends(get_db)):
    """
    Adds a new vehicle data.
    """
    vehicle_data_service = VehicleDataService(db=db)
    # Transform a VehicleModel into a VehicleDatabase
    vehicle = VehicleDatabase(**vehicle.dict())
    vehicle = vehicle_data_service.add_vehicle_data(vehicle_database=vehicle)
    return vehicle
