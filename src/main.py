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

# Ensure tables exist (for safety)
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


@app.get("/api/weather", response_model=dict)
def get_weather(
    station_id: Optional[str] = Query(None),
    date_eq: Optional[date] = Query(None, alias="date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Get weather observations.

    Query params:
    - station_id: filter by station ID
    - date: filter by exact date (YYYY-MM-DD)
    - page, page_size: pagination
    """

    query = db.query(WeatherObservation)

    if station_id:
        query = query.filter(WeatherObservation.station_id == station_id)

    if date_eq:
        query = query.filter(WeatherObservation.date == date_eq)

    total = query.count()

    offset = (page - 1) * page_size
    rows = query.order_by(
        WeatherObservation.station_id,
        WeatherObservation.date
    ).offset(offset).limit(page_size).all()

    items: List[WeatherObservationOut] = []
    for r in rows:
        items.append(
            WeatherObservationOut(
                station_id=r.station_id,
                date=r.date,
                max_temp_c=r.max_temp_tenth_c / 10.0 if r.max_temp_tenth_c is not None else None,
                min_temp_c=r.min_temp_tenth_c / 10.0 if r.min_temp_tenth_c is not None else None,
                precip_cm=r.precip_tenth_mm / 100.0 if r.precip_tenth_mm is not None else None,
            )
        )

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": [item.dict() for item in items],
    }


@app.get("/api/weather/stats", response_model=dict)
def get_weather_stats(
    station_id: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Get yearly weather statistics.

    Query params:
    - station_id: filter by station ID
    - year: filter by year (e.g., 1990)
    - page, page_size: pagination
    """

    query = db.query(WeatherYearlyStats)

    if station_id:
        query = query.filter(WeatherYearlyStats.station_id == station_id)

    if year:
        query = query.filter(WeatherYearlyStats.year == year)

    total = query.count()
    offset = (page - 1) * page_size

    rows = query.order_by(
        WeatherYearlyStats.station_id,
        WeatherYearlyStats.year
    ).offset(offset).limit(page_size).all()

    items: List[WeatherYearlyStatsOut] = [
        WeatherYearlyStatsOut.from_orm(r) for r in rows
    ]

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": [item.dict() for item in items],
    }
