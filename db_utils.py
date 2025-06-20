# db_utils.py
from sqlalchemy import create_engine
import pandas as pd

DB_USER = "root"
DB_PASSWORD = "ТВОЙ_ПАРОЛЬ"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "climate_db"

def get_engine():
    url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)

def load_climate_data():
    engine = get_engine()
    query = "SELECT city, temperature, humidity, pressure, timestamp FROM climate_data"
    df = pd.read_sql(query, con=engine)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df