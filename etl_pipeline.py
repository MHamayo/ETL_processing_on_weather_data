import requests
import pandas as pd
import sqlite3
import yaml
import logging

# Set up logging
logging.basicConfig(filename='logs/etl.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def extract_data(api_url, api_key, city):
    """Extract weather data from OpenWeatherMap API"""
    params = {'q': city, 'appid': api_key, 'units': 'metric'}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        logging.info("Data extraction successful")
        return response.json()
    else:
        logging.error("Failed to extract data")
        return None

def transform_data(data):
    """Transform JSON data into a DataFrame"""
    weather_info = {
        'city': data['name'],
        'temperature': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'weather': data['weather'][0]['description'],
        'wind_speed': data['wind']['speed']
    }
    df = pd.DataFrame([weather_info])
    logging.info("Data transformation completed")
    return df

def load_data(df, db_name, table_name):
    """Load data into SQLite database"""
    conn = sqlite3.connect(db_name)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    logging.info("Data loaded into database")

if __name__ == "__main__":
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    
    api_url = config['api_url']
    api_key = config['api_key']
    city = config['city']
    db_name = config['database']['name']
    table_name = config['database']['table']
    
    raw_data = extract_data(api_url, api_key, city)
    if raw_data:
        transformed_data = transform_data(raw_data)
        load_data(transformed_data, db_name, table_name)
