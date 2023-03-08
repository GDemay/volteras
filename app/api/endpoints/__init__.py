"""
This module initializes the API endpoints.
"""

from .vehicle_data import router as vehicle_data_router


__all__ = [
    "vehicle_data_router",
]
