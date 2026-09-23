import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from database import (
    init_db,
    upsert_weather,
    get_all_weather,
    get_station_names,
    get_station_weather,
)

from weather_api import fetch_weather


# ==============================
# Streamlit 基本設定
# ==============================

st.set_page_config(
    page_title="Taiwan Weather Observation",
    page_icon="🌤️",
    layout="wide",
)


# ==============================
# 建立資料庫
# ==============================

init_db()


# ==============================
# 標題
# ==============================

st.title("🌤️ Taiwan Weather Observation")

st.caption(
    "中央氣象署 CWA O-A0003-001 × Python × SQLite × Streamlit"
)


# ==============================
# Sidebar
# ==============================

with st.sidebar:

    st.header("⚙️ 資料控制")

    st.write(
        "資料來源：中央氣象署 O-A0003-001"
    )

    st.write(
        "氣象觀測站－10分鐘綜觀氣象資料"
    )

    # 更新資料
    if st.button(
        "🔄 更新即時氣象資料",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "正在從中央氣象署取得資料..."
            ):

                rows = fetch_weather()

                upsert_weather(rows)

            st.success(
                f"更新完成，共 {len(rows)} 個測站。"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"更新失敗：{e}"
            )


# ==============================
# 從 SQLite 讀全部資料
# ==============================

rows = get_all_weather()


if not rows:

    st.warning(
        "資料庫目前沒有資料。"
    )

    st.info(
        "請先執行：python update_weather.py"
    )

    st.stop()


# ==============================
# 轉成 Pandas DataFrame
# ==============================

df = pd.DataFrame(
    [dict(row) for row in rows]
)


# ==============================
# 將時間轉成 datetime
# ==============================

df["obsTime"] = pd.to_datetime(
    df["obsTime"],
    errors="coerce"
)


# ==============================
# 只保留每個測站最新一筆
# ==============================

latest_df = (
    df
    .sort_values("obsTime")
    .groupby(
        "stationId",
        as_index=False
    )
    .tail(1)
)


# ==============================
# 縣市選擇
# ==============================

counties = sorted(
    latest_df["county"]
    .dropna()
    .unique()
    .tolist()
)


selected_county = st.selectbox(
    "📍 選擇縣市",
    ["全部"] + counties
)


# ==============================
# 篩選縣市
# ==============================

if selected_county == "全部":

    county_df = latest_df.copy()

else:

    county_df = latest_df[
        latest_df["county"]
        == selected_county
    ].copy()


# ==============================
# 測站選擇
# ==============================

station_names = sorted(
    county_df["stationName"]
    .dropna()
    .unique()
    .tolist()
)


selected_station = st.selectbox(
    "🌡️ 選擇氣象站",
    station_names
)


# ==============================
# 取得目前選擇測站
# ==============================

station_current = county_df[
    county_df["stationName"]
    == selected_station
]


if station_current.empty:

    st.error(
        "找不到此氣象站資料。"
    )

    st.stop()


current = station_current.iloc[0]


# ==============================
# 測站標題
# ==============================

st.subheader(
    f"📍 {selected_station}"
)


location_text = ""

if pd.notna(current["county"]):

    location_text += str(
        current["county"]
    )

if pd.notna(current["town"]):

    location_text += " " + str(
        current["town"]
    )


st.caption(
    f"{location_text} ｜ "
    f"測站代碼：{current['stationId']} ｜ "
    f"觀測時間：{current['obsTime']}"
)


# ==============================
# KPI 第一排
# ==============================

col1, col2, col3, col4 = st.columns(4)


# 氣溫
if pd.notna(current["temperature"]):

    col1.metric(
        "🌡️ 目前氣溫",
        f"{current['temperature']:.1f} °C"
    )

else:

    col1.metric(
        "🌡️ 目前氣溫",
        "N/A"
    )


# 今日最高
if pd.notna(current["dailyHigh"]):

    col2.metric(
        "🔥 今日最高溫",
        f"{current['dailyHigh']:.1f} °C"
    )

else:

    col2.metric(
        "🔥 今日最高溫",
        "N/A"
    )


# 今日最低
if pd.notna(current["dailyLow"]):

    col3.metric(
        "❄️ 今日最低溫",
        f"{current['dailyLow']:.1f} °C"
    )

else:

    col3.metric(
        "❄️ 今日最低溫",
        "N/A"
    )


# 濕度
if pd.notna(current["humidity"]):

    humidity_percent = (
        current["humidity"] * 100
        if current["humidity"] <= 1
        else current["humidity"]
    )

    col4.metric(
        "💧 相對濕度",
        f"{humidity_percent:.0f} %"
    )

else:

    col4.metric(
        "💧 相對濕度",
        "N/A"
    )


# ==============================
# KPI 第二排
# ==============================

col5, col6, col7, col8 = st.columns(4)


# 降雨量
if pd.notna(current["precipitation"]):

    col5.metric(
        "🌧️ 降雨量",
        f"{current['precipitation']:.1f} mm"
    )

else:

    col5.metric(
        "🌧️ 降雨量",
        "N/A"
    )


# 風速
if pd.notna(current["windSpeed"]):

    col6.metric(
        "💨 風速",
        f"{current['windSpeed']:.1f} m/s"
    )

else:

    col6.metric(
        "💨 風速",
        "N/A"
    )


# 氣壓
if pd.notna(current["pressure"]):

    col7.metric(
        "🔵 氣壓",
        f"{current['pressure']:.1f} hPa"
    )

else:

    col7.metric(
        "🔵 氣壓",
        "N/A"
    )


# UV
if pd.notna(current["uvIndex"]):

    col8.metric(
        "☀️ UV 指數",
        f"{current['uvIndex']:.1f}"
    )

else:

    col8.metric(
        "☀️ UV 指數",
        "N/A"
    )


st.divider()


# ==============================
# 台灣即時氣溫地圖
# ==============================

st.subheader(
    "🗺️ 台灣即時氣溫地圖"
)


# 台灣中心
weather_map = folium.Map(
    location=[
        23.7,
        121.0
    ],
    zoom_start=7
)


# ==============================
# Marker 顏色
# ==============================

def get_marker_color(temp):

    if pd.isna(temp):
        return "gray"

    if temp < 15:
        return "blue"

    elif temp < 20:
        return "lightblue"

    elif temp < 25:
        return "green"

    elif temp < 30:
        return "orange"

    else:
        return "red"


# ==============================
# 將測站加入地圖
# ==============================

for _, row in county_df.iterrows():

    lat = row["latitude"]
    lon = row["longitude"]

    if pd.isna(lat) or pd.isna(lon):
        continue

    temp = row["temperature"]

    marker_color = get_marker_color(
        temp
    )

    popup_text = f"""
    <b>{row['stationName']}</b><br>
    縣市：{row['county']}<br>
    鄉鎮：{row['town']}<br>
    氣溫：{temp if pd.notna(temp) else 'N/A'} °C<br>
    濕度：{row['humidity'] if pd.notna(row['humidity']) else 'N/A'}<br>
    降雨：{row['precipitation'] if pd.notna(row['precipitation']) else 'N/A'} mm<br>
    風速：{row['windSpeed'] if pd.notna(row['windSpeed']) else 'N/A'} m/s
    """

    folium.Marker(
        location=[
            lat,
            lon
        ],
        tooltip=(
            f"{row['stationName']} "
            f"{temp if pd.notna(temp) else ''}°C"
        ),
        popup=folium.Popup(
            popup_text,
            max_width=300
        ),
        icon=folium.Icon(
            color=marker_color,
            icon="cloud"
        ),
    ).add_to(
        weather_map
    )


# ==============================
# 顯示地圖
# ==============================

st_folium(
    weather_map,
    width=None,
    height=550
)


# ==============================
# 顏色說明
# ==============================

st.caption(
    "🔵 <15°C ｜ "
    "🟦 15–20°C ｜ "
    "🟢 20–25°C ｜ "
    "🟠 25–30°C ｜ "
    "🔴 >30°C"
)


st.divider()


# ==============================
# 縣市氣溫圖
# ==============================

st.subheader(
    f"📊 {selected_county} 氣象站即時氣溫"
)


temperature_df = (
    county_df[
        [
            "stationName",
            "temperature"
        ]
    ]
    .dropna()
    .sort_values(
        "temperature",
        ascending=False
    )
)


temperature_chart = (
    temperature_df
    .set_index(
        "stationName"
    )
)


st.bar_chart(
    temperature_chart,
    height=400
)


# ==============================
# 測站詳細資料
# ==============================

st.subheader(
    "📋 測站詳細資料"
)


display_df = county_df.copy()


display_df = display_df.rename(
    columns={
        "stationName": "測站名稱",
        "stationId": "測站代碼",
        "obsTime": "觀測時間",
        "county": "縣市",
        "town": "鄉鎮",
        "temperature": "氣溫 (°C)",
        "humidity": "相對濕度",
        "pressure": "氣壓 (hPa)",
        "windSpeed": "風速 (m/s)",
        "windDirection": "風向",
        "precipitation": "降雨量 (mm)",
        "dailyHigh": "今日最高溫",
        "dailyLow": "今日最低溫",
    }
)


columns_to_show = [
    "測站名稱",
    "測站代碼",
    "縣市",
    "鄉鎮",
    "氣溫 (°C)",
    "今日最高溫",
    "今日最低溫",
    "相對濕度",
    "降雨量 (mm)",
    "風速 (m/s)",
    "氣壓 (hPa)",
    "觀測時間",
]


available_columns = [
    column
    for column in columns_to_show
    if column in display_df.columns
]


st.dataframe(
    display_df[
        available_columns
    ],
    use_container_width=True,
    hide_index=True
)


# ==============================
# SQL 查詢展示
# ==============================

with st.expander(
    "🗄️ 查看 SQL 查詢範例"
):

    st.code(
        f"""
SELECT
    stationName,
    county,
    town,
    temperature,
    humidity,
    precipitation,
    windSpeed,
    obsTime

FROM WeatherObservations

WHERE stationName = '{selected_station}'

ORDER BY obsTime DESC;
""",
        language="sql"
    )