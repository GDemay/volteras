"""
This module defines the sorting utility.
"""

from sqlalchemy.sql import asc, desc


def get_order_by(field: str, order: str) -> str:
    if order == "asc":
        return asc(field)
    elif order == "desc":
        return desc(field)
    else:
        raise ValueError("Invalid sort order")
