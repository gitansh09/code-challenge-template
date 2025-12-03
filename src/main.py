# src/main.py
from datetime import date
from typing import Optional, List

from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session

from .database import SessionLocal, engine, Base
from .models import WeatherObservation, WeatherYearlyStats
from .schemas import (
    WeatherObservationOut,
    WeatherYearlyStatsOut,
)

# Ensure tables exist (for safety; create_db.py already does this)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Weather API",
    description="API for weather observations and yearly statistics",
    version="1.0.0",
)


def get_db():
    """Dependency for getting a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
