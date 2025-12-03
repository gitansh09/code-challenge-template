# src/compute_stats.py
import logging
from datetime import datetime

from sqlalchemy import func, cast, Integer

from .database import SessionLocal
from .models import WeatherObservation, WeatherYearlyStats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def compute_yearly_stats():
    start_time = datetime.now()
    logging.info("Starting yearly stats computation...")

    session = SessionLocal()
    try:
        # For SQLite: extract year using strftime, then cast to integer
        year_expr = cast(func.strftime("%Y", WeatherObservation.date), Integer)

        query = (
            session.query(
                WeatherObservation.station_id.label("station_id"),
                year_expr.label("year"),
                # Tenths of °C -> divide by 10.0
                (func.avg(WeatherObservation.max_temp_tenth_c) / 10.0).label("avg_max_temp_c"),
                (func.avg(WeatherObservation.min_temp_tenth_c) / 10.0).label("avg_min_temp_c"),
                # Tenths of mm -> divide by 100.0 to get cm
                (func.sum(WeatherObservation.precip_tenth_mm) / 100.0).label("total_precip_cm"),
            )
            .group_by(WeatherObservation.station_id, year_expr)
        )

        rows = query.all()
        logging.info(f"Calculated stats for {len(rows)} (station, year) combinations")

        upserts = 0
        for r in rows:
            existing = (
                session.query(WeatherYearlyStats)
                .filter_by(station_id=r.station_id, year=r.year)
                .one_or_none()
            )

            if existing:
                existing.avg_max_temp_c = r.avg_max_temp_c
                existing.avg_min_temp_c = r.avg_min_temp_c
                existing.total_precip_cm = r.total_precip_cm
            else:
                stats = WeatherYearlyStats(
                    station_id=r.station_id,
                    year=r.year,
                    avg_max_temp_c=r.avg_max_temp_c,
                    avg_min_temp_c=r.avg_min_temp_c,
                    total_precip_cm=r.total_precip_cm,
                )
                session.add(stats)

            upserts += 1

        session.commit()

        end_time = datetime.now()
        logging.info(
            f"Finished computing yearly stats. Upserted {upserts} rows. "
            f"Duration: {end_time - start_time}"
        )
    finally:
        session.close()


if __name__ == "__main__":
    compute_yearly_stats()
