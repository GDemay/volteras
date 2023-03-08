"""
This module defines the main application.
"""

import os

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.api.endpoints import vehicle_data_router
from app.core.database import SessionLocal, engine
from app.core.database.models import Base


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

@app.get("/")
async def read_root():
    return {"Hello World": "Hello World"}
