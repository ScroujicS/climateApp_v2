import csv
import os
import requests
from datetime import datetime
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = "86f62b6444e867fd4b6b9a009b62e3c5"
CSV_FILE_PATH = "mock_climate_data.csv"

CITIES = [
    "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Нижний Новгород",
"Казань", "Челябинск", "Омск", "Ростов-на-Дону", "Уфа",
"Волгоград", "Красноярск", "Саратов", "Тюмень", "Тольятти",
"Ижевск", "Барнаул", "Хабаровск", "Владивосток", "Калининград"
]

CSV_FIELDS = ["city", "timestamp", "temperature", "feels_like", "pressure", "humidity", "wind_speed", "weather_description"]

def get_climate_data(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": f"{city},RU",
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        climate_info = {
            "city": data["name"],
            "timestamp": datetime.utcfromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "weather_description": data["weather"][0]["description"]
        }
        return climate_info
    else:
        logger.warning(f"Error retrieving data for {city}: {response.status_code}")
        return None

def update_csv_with_weather_data():
    logger.info("Starting CSV weather data update...")

    # Загрузка текущих данных, если CSV существует
    existing_rows = []
    if os.path.isfile(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            existing_rows = list(reader)

    new_rows = []
    for city in CITIES:
        data = get_climate_data(city)
        if data:
            new_rows.append(data)

    # Объединяем старые и новые, при желании — добавить фильтр дубликатов
    combined_rows = existing_rows + new_rows

    try:
        with open(CSV_FILE_PATH, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(combined_rows)
        logger.info(f"CSV file '{CSV_FILE_PATH}' updated with total {len(combined_rows)} records.")
    except Exception as e:
        logger.error(f"Failed to update CSV file: {e}")

def start_scheduler(interval_hours=1):
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_csv_with_weather_data, 'interval', hours=interval_hours)
    scheduler.start()
    logger.info(f"Scheduler started: обновление данных каждые {interval_hours} час(ов)")

    try:
        # Чтобы планировщик работал пока программа не остановлена
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped.")

if __name__ == "__main__":
    start_scheduler()