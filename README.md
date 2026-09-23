# Taiwan Weather Forecast

依照課程海報流程完成的 Python 專案：

**CWA API → JSON → 資料整理 → SQLite → SQL 查詢 → Streamlit → 折線圖 → Folium 地圖**

資料來源使用中央氣象署「一般天氣預報－七天天氣預報」資料集 `F-C0032-003`。

---

## 1. 專案檔案

```text
taiwan_weather_forecast/
├─ app.py                 # Streamlit Web App
├─ weather_api.py         # CWA API / JSON 解析
├─ database.py            # SQLite 建表、寫入、查詢
├─ update_weather.py      # 手動更新 CWA 資料
├─ inspect_db.py          # 查看 SQLite 內容
├─ requirements.txt
├─ .env.example
├─ .gitignore
└─ README.md
```

執行後會自動建立：

```text
data.db
```

---

## 2. 建立環境

Windows PowerShell / CMD：

```bash
cd taiwan_weather_forecast
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 3. 取得中央氣象署 API Key

1. 到中央氣象署 Open Data 平台註冊/登入。
2. 取得授權碼（API Key）。
3. 將 `.env.example` 複製成 `.env`。
4. 編輯 `.env`：

```env
CWA_API_KEY=你的授權碼
```

不要把 `.env` 上傳到 GitHub。

---

## 4. API 資料取得

本專案使用：

```text
資料集：F-C0032-003
一般天氣預報－七天天氣預報
```

Python 核心概念：

```python
response = requests.get(
    "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-003",
    params={
        "Authorization": API_KEY,
        "format": "JSON"
    }
)

data = response.json()
```

`weather_api.py` 會從 JSON 中抓出：

- 地區 `regionName`
- 日期 `dataDate`
- 最低溫 `MinT`
- 最高溫 `MaxT`

---

## 5. 建立 SQLite 資料庫

不用自己先建檔，第一次執行會建立 `data.db`。

資料表：

```sql
CREATE TABLE IF NOT EXISTS TemperatureForecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regionName TEXT NOT NULL,
    dataDate TEXT NOT NULL,
    min REAL NOT NULL,
    max REAL NOT NULL,
    UNIQUE(regionName, dataDate)
);
```

使用 `IF NOT EXISTS`，所以重複執行不會出現：

```text
sqlite3.OperationalError: table ... already exists
```

---

## 6. 取得資料並寫入 SQLite

```bash
python update_weather.py
```

成功時會看到類似：

```text
完成：已寫入/更新 49 筆預報資料。
地區：北部地區、中部地區、南部地區...
```

---

## 7. 查看 SQLite 資料

```bash
python inspect_db.py
```

也可以在 Python 中：

```python
import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM TemperatureForecasts")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
```

若遇到：

```text
sqlite3.OperationalError: no such table
```

通常是：
- 開到了不同資料夾中的 `data.db`
- 尚未執行建表程式

本專案用 `Path(__file__).with_name("data.db")` 固定 DB 路徑，可避免這類問題。

---

## 8. SQL 查詢

查出所有地區：

```sql
SELECT DISTINCT regionName
FROM TemperatureForecasts
ORDER BY regionName;
```

查某個地區：

```sql
SELECT dataDate, min, max
FROM TemperatureForecasts
WHERE regionName = '中部地區'
ORDER BY dataDate;
```

---

## 9. 啟動 Streamlit

```bash
streamlit run app.py
```

瀏覽器會開啟：

```text
http://localhost:8501
```

功能包括：

- 地區下拉選單
- 一週最高/最低溫折線圖
- 一週資料表
- SQLite 查詢
- 更新 CWA API 資料
- Folium 互動式台灣地圖

---

## 10. 溫度顏色概念

地圖標記依一週平均溫度分級：

- `< 20°C`：藍
- `20–25°C`：綠
- `25–30°C`：橘
- `> 30°C`：紅

---

## 11. GitHub

```bash
git init
git add .
git commit -m "Initial Taiwan weather forecast project"
git branch -M main
git remote add origin 你的GitHubRepository網址
git push -u origin main
```

`.gitignore` 已排除：

- `.env`
- `data.db`
- 虛擬環境
- Python cache

避免把 API Key 上傳。

---

## 12. 對照海報 24 個步驟

1. 課程介紹 → 完成專案目標
2. 台灣天氣與生活 → 天氣預報應用
3. CWA Open Data → 使用官方資料
4. API 資料取得 → `requests`
5. JSON 結構解析 → `response.json()`
6. 提取最高/最低氣溫 → MinT / MaxT
7. 資料整理 → Python dict / Pandas
8. 建立 SQLite → `data.db`
9. 資料庫設計 → `TemperatureForecasts`
10. SQL 查詢 → `SELECT`
11. Streamlit 入門 → `app.py`
12. 從 DB 讀資料 → SQLite + Pandas
13. 地區下拉選單 → `st.selectbox`
14. 折線圖 → `st.line_chart`
15. 資料表 → `st.dataframe`
16. Web App 整合 → Dashboard
17. 台灣地圖視覺化 → Folium
18. 選日期/互動 → 可再擴充日期選擇
19. 完整成果 → Taiwan Weather Dashboard
20. 程式碼品質 → 模組化
21. GitHub → 指令已附
22. 延伸應用 → LINE Bot / 旅遊 / 農業
23. 回顧 → API、JSON、SQLite、Streamlit
24. 下一步 → AI / 多 API / Real World

---

## 13. 建議下一階段

完成基本版後可再加入：

- 降雨機率
- 天氣現象
- 22 縣市地圖
- 日期下拉選單
- 自動排程更新 SQLite
- LINE Bot
- AI 文字天氣摘要
