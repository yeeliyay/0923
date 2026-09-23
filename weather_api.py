import os
import ssl
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from dotenv import load_dotenv


load_dotenv()


DATASET_ID = "O-A0003-001"
API_URL = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{DATASET_ID}"


class SSLAdapter(HTTPAdapter):
    """
    Python 3.13 / 3.14 相容用 SSL Adapter。
    保留 HTTPS 驗證，只關閉 VERIFY_X509_STRICT。
    """

    def init_poolmanager(
        self,
        connections,
        maxsize,
        block=False,
        **pool_kwargs
    ):
        context = ssl.create_default_context()

        if hasattr(ssl, "VERIFY_X509_STRICT"):
            context.verify_flags &= ~ssl.VERIFY_X509_STRICT

        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=context,
            **pool_kwargs,
        )


def _safe_float(value):
    """
    將 CWA API 的值安全轉成 float。

    -99、-999、None 等視為無效資料。
    """

    try:
        value = float(value)

        if value <= -90:
            return None

        return value

    except (TypeError, ValueError):
        return None


def _get_wgs84_coordinates(geo_info: dict):
    """
    從 GeoInfo 中找 WGS84 經緯度。
    """

    coordinates = geo_info.get("Coordinates", [])

    if isinstance(coordinates, dict):
        coordinates = [coordinates]

    for coord in coordinates:

        if coord.get("CoordinateName") == "WGS84":

            lat = _safe_float(
                coord.get("StationLatitude")
            )

            lon = _safe_float(
                coord.get("StationLongitude")
            )

            return lat, lon

    # 找不到 WGS84 時，退回第一組座標
    if coordinates:

        coord = coordinates[0]

        lat = _safe_float(
            coord.get("StationLatitude")
        )

        lon = _safe_float(
            coord.get("StationLongitude")
        )

        return lat, lon

    return None, None


def fetch_weather(api_key: str | None = None) -> list[dict]:
    """
    從中央氣象署 O-A0003-001
    取得即時氣象觀測資料。
    """

    api_key = api_key or os.getenv("CWA_API_KEY")

    if not api_key:
        raise RuntimeError(
            "找不到 CWA_API_KEY。\n"
            "請確認 .env 中有：\n"
            "CWA_API_KEY=你的授權碼"
        )

    session = requests.Session()

    session.mount(
        "https://",
        SSLAdapter(),
    )

    response = session.get(
        API_URL,
        params={
            "Authorization": api_key,
            "format": "JSON",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if str(data.get("success", "true")).lower() != "true":

        raise RuntimeError(
            f"CWA API 回傳失敗：{data}"
        )

    stations = (
        data
        .get("records", {})
        .get("Station", [])
    )

    if not stations:
        raise RuntimeError(
            "API 有成功回傳，但找不到 records -> Station。"
        )

    rows = []

    for station in stations:

        station_name = station.get("StationName")

        station_id = station.get("StationId")

        obs_time = (
            station
            .get("ObsTime", {})
            .get("DateTime")
        )

        geo_info = station.get(
            "GeoInfo",
            {}
        )

        county = geo_info.get(
            "CountyName"
        )

        town = geo_info.get(
            "TownName"
        )

        latitude, longitude = (
            _get_wgs84_coordinates(
                geo_info
            )
        )

        weather_element = station.get(
            "WeatherElement",
            {}
        )

        weather = weather_element.get(
            "Weather"
        )

        temperature = _safe_float(
            weather_element.get(
                "AirTemperature"
            )
        )

        humidity = _safe_float(
            weather_element.get(
                "RelativeHumidity"
            )
        )

        pressure = _safe_float(
            weather_element.get(
                "AirPressure"
            )
        )

        wind_direction = _safe_float(
            weather_element.get(
                "WindDirection"
            )
        )

        wind_speed = _safe_float(
            weather_element.get(
                "WindSpeed"
            )
        )

        precipitation = _safe_float(
            weather_element
            .get("Now", {})
            .get("Precipitation")
        )

        uv_index = _safe_float(
            weather_element.get(
                "UVIndex"
            )
        )

        daily_extreme = weather_element.get(
            "DailyExtreme",
            {}
        )

        daily_high = _safe_float(
            daily_extreme
            .get("DailyHigh", {})
            .get("TemperatureInfo", {})
            .get("AirTemperature")
        )

        daily_low = _safe_float(
            daily_extreme
            .get("DailyLow", {})
            .get("TemperatureInfo", {})
            .get("AirTemperature")
        )

        # 沒有氣溫資料的站先略過
        if temperature is None:
            continue

        rows.append(
            {
                "stationName": station_name,
                "stationId": station_id,
                "obsTime": obs_time,
                "county": county,
                "town": town,
                "latitude": latitude,
                "longitude": longitude,
                "weather": weather,
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure,
                "windDirection": wind_direction,
                "windSpeed": wind_speed,
                "precipitation": precipitation,
                "uvIndex": uv_index,
                "dailyHigh": daily_high,
                "dailyLow": daily_low,
            }
        )

    if not rows:

        raise RuntimeError(
            "API 有資料，但沒有成功解析任何氣象站。"
        )

    return rows