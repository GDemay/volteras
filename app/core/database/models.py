"""
This module defines the database models.
"""

import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class VehicleDatabase(Base):
    __tablename__ = "vehicle_data"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, index=True)
    speed = Column(Float, nullable=True)
    odometer = Column(Float, nullable=True)
    soc = Column(Float, nullable=True)
    elevation = Column(Float, nullable=True)
    shift_state = Column(String, nullable=True)


class SortBy(str, Enum):
    ASC = "ASC"
    DESC = "DESC"
