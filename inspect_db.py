from database import init_db, get_connection


def main():
    init_db()
    with get_connection() as conn:
        print("資料表：")
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        for t in tables:
            print(" -", t["name"])

        print("\nTemperatureForecasts 內容：")
        rows = conn.execute(
            """
            SELECT id, regionName, dataDate, min, max
            FROM TemperatureForecasts
            ORDER BY dataDate, regionName
            """
        ).fetchall()

        if not rows:
            print("(目前沒有資料，先執行 python update_weather.py)")
        else:
            for row in rows:
                print(dict(row))


if __name__ == "__main__":
    main()
