import streamlit as st
import pandas as pd
import sqlite3
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title="Taiwan Weather Dashboard", layout="wide")

st.title("Taiwan Weather Forecast Dashboard")
st.markdown("### 從氣象資料到互動式天氣預報應用")

# Read data from database
@st.cache_data
def load_data():
    conn = sqlite3.connect('data.db')
    df = pd.read_sql_query("SELECT * FROM TemperatureForecasts", conn)
    conn.close()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

if df.empty:
    st.warning("No data available. Please run `fetch_data.py` first.")
    st.stop()

# Sidebar for region selection
st.sidebar.header("Settings")
regions = df['regionName'].unique().tolist()
selected_region = st.sidebar.selectbox("Select Region", regions)

# Filter data for selected region
region_df = df[df['regionName'] == selected_region].copy()
region_df = region_df.sort_values(by='dataDate')

# Layout using columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Temperature Forecast for {selected_region}")
    # Draw line chart
    chart_data = region_df.set_index('dataDate')[['mint', 'maxt']]
    chart_data.columns = ['MinT', 'MaxT']
    st.line_chart(chart_data)
    
with col2:
    st.subheader("Data Table")
    # Display Data Table
    table_data = region_df[['dataDate', 'mint', 'maxt']].copy()
    table_data.columns = ['Date', 'MinT', 'MaxT']
    st.dataframe(table_data, hide_index=True)

# Advanced: Map Visualization
st.markdown("---")
st.subheader("Interactive Taiwan Map by Date")

dates = df['dataDate'].unique().tolist()
dates.sort()
selected_date = st.selectbox("Select Date for Map", dates)

date_df = df[df['dataDate'] == selected_date]

# Coordinates for regions (approximate)
region_coords = {
    "北部地區": [25.0330, 121.5654],
    "中部地區": [24.1477, 120.6736],
    "南部地區": [22.9999, 120.2269],
    "東部地區": [23.9751, 121.6044]
}

# Create a map centered around Taiwan
m = folium.Map(location=[23.6978, 120.9605], zoom_start=7)

for index, row in date_df.iterrows():
    region = row['regionName']
    if region in region_coords:
        mint = row['mint']
        maxt = row['maxt']
        
        # Determine color based on MaxT
        if maxt >= 30:
            color = 'red'
        elif maxt >= 25:
            color = 'orange'
        else:
            color = 'green'
            
        popup_html = f"<b>{region}</b><br>Min: {mint}°C<br>Max: {maxt}°C"
        
        folium.Marker(
            location=region_coords[region],
            popup=popup_html,
            tooltip=region,
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)

folium_static(m)
