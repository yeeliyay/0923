from database import (
    init_db,
    upsert_weather,
)

from weather_api import (
    fetch_weather,
)


def main():

    init_db()

    rows = fetch_weather()

    upsert_weather(rows)

    print(
        f"完成：已寫入/更新 {len(rows)} 個氣象站資料。"
    )

    counties = sorted(
        {
            r["county"]
            for r in rows
            if r["county"]
        }
    )

    print(
        "縣市：",
        "、".join(counties)
    )


if __name__ == "__main__":
    main()