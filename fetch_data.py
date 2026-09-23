import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

# Mock data generation since CWA API key is not provided
def fetch_mock_weather_data():
    regions = ["北部地區", "中部地區", "南部地區", "東部地區"]
    today = datetime.now()
    
    data = []
    for region in regions:
        # Base temperatures
        if region == "北部地區":
            base_min, base_max = 20, 26
        elif region == "中部地區":
            base_min, base_max = 22, 28
        elif region == "南部地區":
            base_min, base_max = 24, 30
        else: # 東部地區
            base_min, base_max = 21, 27
            
        for i in range(7):
            date_str = (today + timedelta(days=i)).strftime("%Y-%m-%d")
            # add some random fluctuation
            mint = base_min + random.randint(-2, 2)
            maxt = base_max + random.randint(-2, 2)
            if maxt <= mint:
                maxt = mint + 2
            
            data.append({
                "regionName": region,
                "dataDate": date_str,
                "mint": mint,
                "maxt": maxt
            })
            
    return data

def save_to_db(data):
    # Connect to SQLite database (will create it if it doesn't exist)
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TemperatureForecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regionName TEXT,
            dataDate TEXT,
            mint REAL,
            maxt REAL,
            UNIQUE(regionName, dataDate)
        )
    ''')
    
    # Insert data
    for item in data:
        cursor.execute('''
            INSERT OR REPLACE INTO TemperatureForecasts (regionName, dataDate, mint, maxt)
            VALUES (?, ?, ?, ?)
        ''', (item['regionName'], item['dataDate'], item['mint'], item['maxt']))
        
    conn.commit()
    conn.close()
    print("Data saved to database successfully.")

if __name__ == "__main__":
    weather_data = fetch_mock_weather_data()
    save_to_db(weather_data)
    
    # Preview using pandas
    conn = sqlite3.connect('data.db')
    df = pd.read_sql_query("SELECT * FROM TemperatureForecasts LIMIT 5", conn)
    print("Data Preview:")
    print(df)
    conn.close()
