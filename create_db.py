# create_db.py
from src.database import Base, engine
from src.models import WeatherObservation, WeatherYearlyStats

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database and tables created successfully.")
