"""
This module defines the main application.
"""

import os

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.api.endpoints import vehicle_data_router
from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.core.database.models import Base
from app.core.utils.exceptions import ResourceNotFoundException


app = FastAPI()

app.include_router(vehicle_data_router)


@app.on_event("startup")
async def startup():
    # Initialize database connection
    Base.metadata.create_all(bind=engine)


@app.on_event("shutdown")
async def shutdown():
    # Close database connection
    SessionLocal.close_all()


@app.exception_handler(ResourceNotFoundException)
async def resource_not_found_exception_handler(request, exc):
    return HTTPException(status_code=404, detail=str(exc))


@app.get("/")
async def read_root():
    return {"Hello World": "Hello World"}
