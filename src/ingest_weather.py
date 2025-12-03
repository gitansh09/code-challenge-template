# src/ingest_weather.py
import logging
import os
from datetime import datetime
from pathlib import Path

from sqlalchemy.exc import IntegrityError

from .database import SessionLocal
from .models import WeatherObservation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Assuming wx_data is in the repo root alongside src/
WX_DATA_DIR = Path(__file__).resolve().parents[1] / "wx_data"


def parse_int(value: str):
    """Convert string to int, treating -9999 as missing (None)."""
    iv = int(value)
    return None if iv == -9999 else iv


def parse_date(yyyymmdd: str):
    return datetime.strptime(yyyymmdd, "%Y%m%d").date()


def ingest_weather_data():
    start_time = datetime.now()
    logging.info("Starting weather data ingestion...")
    logging.info(f"Reading files from: {WX_DATA_DIR}")

    session = SessionLocal()
    total_inserted = 0

    try:
        for file_path in WX_DATA_DIR.glob("*.txt"):
            station_id = file_path.stem  # filename without extension
            logging.info(f"Processing file: {file_path.name} (station {station_id})")
            with file_path.open("r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split()
                    if len(parts) != 4:
                        logging.warning(f"Skipping malformed line in {file_path.name}: {line}")
                        continue

                    date_str, max_t, min_t, precip = parts

                    obs = WeatherObservation(
                        station_id=station_id,
                        date=parse_date(date_str),
                        max_temp_tenth_c=parse_int(max_t),
                        min_temp_tenth_c=parse_int(min_t),
                        precip_tenth_mm=parse_int(precip),
                    )

                    session.add(obs)
                    try:
                        session.commit()
                        total_inserted += 1
                    except IntegrityError:
                        # Duplicate (station_id, date) – ignore and rollback
                        session.rollback()

        end_time = datetime.now()
        logging.info(
            f"Finished ingestion. Inserted {total_inserted} records. "
            f"Duration: {end_time - start_time}"
        )
    finally:
        session.close()


if __name__ == "__main__":
    ingest_weather_data()
