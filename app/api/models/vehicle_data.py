"""
This module defines the model for vehicle data.
"""

from typing import Optional

from pydantic import BaseModel


from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from datetime import datetime


class VehicleModel(BaseModel):
    vehicle_id: str
    timestamp: Optional[datetime] = None
    speed: Optional[float] = None
    odometer: Optional[float] = None
    elevation: Optional[float] = None
    soc: Optional[float] = None
    shift_state: Optional[str] = None

    class Config:
        orm_mode = True
