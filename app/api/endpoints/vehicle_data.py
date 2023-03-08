"""
This module defines the API endpoints for vehicle data.
"""

from enum import Enum
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.models.vehicle_data import VehicleModel
from app.api.services.vehicle_data_service import VehicleDataService
from app.core.database.models import VehicleDatabase, SortBy
from app.core.utils.pagination import paginate
from app.core.database import SessionLocal, get_db
from fastapi import Depends

router = APIRouter()


@router.get("/api/v1/vehicle_data/", response_model=List[VehicleModel])
async def get_vehicle_data(
    vehicle_id: str = "f212b271-f033-444c-a445-560511f95e9c",
    db: Session = Depends(get_db),
    initial_timestamp: Optional[datetime] = Query(None, alias="initial-timestamp"),
    final_timestamp: Optional[datetime] = Query(None, alias="final-timestamp"),
    sort_by: Optional[SortBy] = Query(None, alias="sort-by"),
    limit: Optional[int] = Query(3, alias="limit"),
    skip: Optional[int] = Query(None, alias="skip"),
    offset: Optional[int] = Query(None, alias="offset"),
):
    vehicle_data_service = VehicleDataService(db=db)
    vehicle_data = vehicle_data_service.get_vehicle_data(
        vehicle_id=vehicle_id,
        initial_timestamp=initial_timestamp,
        final_timestamp=final_timestamp,
        sort_by=sort_by,
        limit=limit,
        skip=skip,
        offset=offset,
    )
    return vehicle_data


@router.get("/api/v1/vehicle_data/{id}/", response_model=VehicleModel)
async def get_vehicle_data_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a particular vehicle data by ID.
    """
    vehicle_data_service = VehicleDataService(db=db)
    vehicle_data = vehicle_data_service.get_vehicle_data_by_id(id=id)
    if vehicle_data is None:
        raise HTTPException(
            status_code=404, detail=f"Vehicle data with id {id} not found"
        )
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
