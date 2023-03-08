"""
This module defines the pagination utility.
"""

from typing import List

from sqlalchemy.orm import Query

from app.api.models.vehicle_data import VehicleModel


def paginate(query: Query, page: int, page_size: int) -> List[VehicleModel]:
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size).all()
