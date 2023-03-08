"""
This module defines the service for vehicle data.
"""

from typing import List, Optional
from pydantic import ValidationError

from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

# from app.api.models.vehicle_data import VehicleData
from app.core.database.models import SortBy, VehicleDatabase
from sqlalchemy import asc, desc
from datetime import datetime


from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session



class VehicleDataService:
    def __init__(self, db: Session):
        self.db = db

    def get_vehicle_data(
        self,
        vehicle_id: str = None,
        initial_timestamp: Optional[datetime] = None,
        final_timestamp: Optional[datetime] = None,
        sort_by: Optional[SortBy] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[VehicleDatabase]:
        """
        Get vehicle data based on the specified filters.
        """
        query = self.db.query(VehicleDatabase).filter(VehicleDatabase.vehicle_id == vehicle_id)

        if initial_timestamp:
            query = query.filter(VehicleDatabase.timestamp >= initial_timestamp)

        if final_timestamp:
            query = query.filter(VehicleDatabase.timestamp <= final_timestamp)

        if sort_by:
            sort_field = VehicleDatabase.timestamp.asc() if sort_by == SortBy.ASC else VehicleDatabase.timestamp.desc()
            query = query.order_by(sort_field)

        query = query.offset(skip).limit(limit)

        vehicles = query.all()
        return vehicles

    def get_vehicle_data_by_id(self, id: int) -> Optional[VehicleDatabase]:
        """
        Get vehicle data by ID.
        """
        vehicle = self.db.query(VehicleDatabase).filter_by(id=id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail=f"Vehicle data with id {id} not found.")
        return vehicle

    def add_vehicle_data(self, vehicle_database: VehicleDatabase) -> VehicleDatabase:
        """
        Add vehicle data to the database.
        """
        try:
            self.db.add(vehicle_database)
            self.db.commit()
            self.db.refresh(vehicle_database)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self.db.close()

        return vehicle_database

