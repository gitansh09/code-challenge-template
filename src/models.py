# src/models.py
from sqlalchemy import (
    Column, Integer, String, Date, UniqueConstraint, Float
)
from .database import Base

class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String, nullable=False, index=True)  # from filename
    date = Column(Date, nullable=False, index=True)

    # Raw values from file (missing -> NULL)
    max_temp_tenth_c = Column(Integer, nullable=True)
    min_temp_tenth_c = Column(Integer, nullable=True)
    precip_tenth_mm = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("station_id", "date", name="uq_station_date"),
    )


class WeatherYearlyStats(Base):
    __tablename__ = "weather_yearly_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)

    # Converted values:
    # - avg_* in degrees Celsius
    # - total_precip in centimeters
    avg_max_temp_c = Column(Float, nullable=True)
    avg_min_temp_c = Column(Float, nullable=True)
    total_precip_cm = Column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint("station_id", "year", name="uq_station_year"),
    )
