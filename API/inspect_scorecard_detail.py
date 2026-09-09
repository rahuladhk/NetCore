import requests
import json

SERIES_ID = "1510976"
MATCH_ID = "1510977"

DETAIL_IDS = [
    "110",
    "120",
    "130",
    "140",
    "150"
]

BASE_URL = (
    f"http://core.espnuk.org/v2/sports/cricket/"
    f"leagues/{SERIES_ID}/"
    f"events/{MATCH_ID}/"
    f"competitions/{MATCH_ID}/"
    f"details"
)

for detail_id in DETAIL_IDS:

    url = f"{BASE_URL}/{detail_id}"

    print()
    print("=" * 80)
    print("DETAIL ID:", detail_id)
    print("=" * 80)

    try:
        response = requests.get(
            url,
            timeout=30
        )

        print("HTTP STATUS:", response.status_code)

        if response.status_code != 200:
            print("FAILED")
            continue

        data = response.json()

        print()
        print("PERIOD:", data.get("period"))
        print("PERIOD TEXT:", data.get("periodText"))
        print("SEQUENCE:", data.get("sequence"))
        print("OVER:", data.get("over"))

        print()
        print("PLAY TYPE:")
        print(json.dumps(
            data.get("playType"),
            indent=2
        ))

        print()
        print("SHORT TEXT:")
        print(data.get("shortText"))

        print()
        print("HOME SCORE:", data.get("homeScore"))
        print("AWAY SCORE:", data.get("awayScore"))
        print("SCORE VALUE:", data.get("scoreValue"))
        print("BOUNDARY:", data.get("boundary"))

        print()
        print("BATSMAN:")
        print(json.dumps(
            data.get("batsman"),
            indent=2
        )[:1000])

        print()
        print("BOWLER:")
        print(json.dumps(
            data.get("bowler"),
            indent=2
        )[:1000])

        print()
        print("DISMISSAL:")
        print(json.dumps(
            data.get("dismissal"),
            indent=2
        )[:1000])

    except Exception as e:
        print("ERROR:", e)

print()
print("=" * 80)
print("TEST COMPLETED")
print("=" * 80)
