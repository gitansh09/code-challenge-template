# src/schemas.py
from datetime import date
from typing import Optional, List
from pydantic import BaseModel


class WeatherObservationOut(BaseModel):
    station_id: str
    date: date
    max_temp_c: Optional[float]
    min_temp_c: Optional[float]
    precip_cm: Optional[float]

    class Config:
        orm_mode = True


class WeatherYearlyStatsOut(BaseModel):
    station_id: str
    year: int
    avg_max_temp_c: Optional[float]
    avg_min_temp_c: Optional[float]
    total_precip_cm: Optional[float]

    class Config:
        orm_mode = True


class PaginatedWeatherResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: List[WeatherObservationOut]


class PaginatedStatsResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: List[WeatherYearlyStatsOut]
