import sqlite3
from pathlib import Path
from typing import Iterable


DB_PATH = Path(__file__).with_name(
    "data.db"
)


def get_connection():

    conn = sqlite3.connect(
        DB_PATH
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    with get_connection() as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS WeatherObservations (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                stationName TEXT,

                stationId TEXT,

                obsTime TEXT,

                county TEXT,

                town TEXT,

                latitude REAL,

                longitude REAL,

                weather TEXT,

                temperature REAL,

                humidity REAL,

                pressure REAL,

                windDirection REAL,

                windSpeed REAL,

                precipitation REAL,

                uvIndex REAL,

                dailyHigh REAL,

                dailyLow REAL,

                UNIQUE(stationId, obsTime)

            )
            """
        )

        conn.commit()


def upsert_weather(rows: Iterable[dict]):

    sql = """
        INSERT INTO WeatherObservations (

            stationName,
            stationId,
            obsTime,
            county,
            town,
            latitude,
            longitude,
            weather,
            temperature,
            humidity,
            pressure,
            windDirection,
            windSpeed,
            precipitation,
            uvIndex,
            dailyHigh,
            dailyLow

        )

        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?
        )

        ON CONFLICT(stationId, obsTime)

        DO UPDATE SET

            stationName = excluded.stationName,
            county = excluded.county,
            town = excluded.town,
            latitude = excluded.latitude,
            longitude = excluded.longitude,
            weather = excluded.weather,
            temperature = excluded.temperature,
            humidity = excluded.humidity,
            pressure = excluded.pressure,
            windDirection = excluded.windDirection,
            windSpeed = excluded.windSpeed,
            precipitation = excluded.precipitation,
            uvIndex = excluded.uvIndex,
            dailyHigh = excluded.dailyHigh,
            dailyLow = excluded.dailyLow
    """

    values = []

    for r in rows:

        values.append(
            (
                r["stationName"],
                r["stationId"],
                r["obsTime"],
                r["county"],
                r["town"],
                r["latitude"],
                r["longitude"],
                r["weather"],
                r["temperature"],
                r["humidity"],
                r["pressure"],
                r["windDirection"],
                r["windSpeed"],
                r["precipitation"],
                r["uvIndex"],
                r["dailyHigh"],
                r["dailyLow"],
            )
        )

    with get_connection() as conn:

        conn.executemany(
            sql,
            values
        )

        conn.commit()


def get_all_weather():

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT *
            FROM WeatherObservations
            ORDER BY county, stationName
            """
        ).fetchall()

    return rows


def get_station_names():

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT DISTINCT stationName
            FROM WeatherObservations
            ORDER BY stationName
            """
        ).fetchall()

    return [
        row["stationName"]
        for row in rows
    ]


def get_station_weather(station_name):

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT *
            FROM WeatherObservations
            WHERE stationName = ?
            ORDER BY obsTime DESC
            """,
            (station_name,),
        ).fetchall()

    return rows