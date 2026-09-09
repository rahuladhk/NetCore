import requests
import json


# ============================================================
# CONFIGURATION
# ============================================================

MATCH_ID = "1510977"


URL = (
    "http://core.espnuk.org/v2/sports/cricket/"
    "leagues/1510976/"
    f"events/{MATCH_ID}/competitions/{MATCH_ID}/"
    "details"
)


# ============================================================
# TEST REQUEST
# ============================================================

print()
print("=" * 70)
print("TESTING ESPN SCORECARD API")
print("=" * 70)

print()
print("MATCH ID:", MATCH_ID)

print()
print("URL:")
print(URL)


try:

    response = requests.get(
        URL,
        timeout=30
    )

    print()
    print("HTTP STATUS:", response.status_code)

    print()
    print("RESPONSE SIZE:", len(response.text), "characters")

    print()
    print("FIRST 500 CHARACTERS:")
    print(response.text[:500])


    # ========================================================
    # SUCCESS
    # ========================================================

    if response.status_code == 200:

        data = response.json()

        print()
        print("=" * 70)
        print("SUCCESS")
        print("=" * 70)

        print()
        print("TOP LEVEL KEYS:")

        if isinstance(data, dict):

            print(list(data.keys()))

        else:

            print(type(data).__name__)


        # ----------------------------------------------------
        # Save response
        # ----------------------------------------------------

        with open(
            "scorecard_1510977.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )


        print()
        print("Saved to:")
        print("scorecard_1510977.json")


    else:

        print()
        print("=" * 70)
        print("API REQUEST FAILED")
        print("=" * 70)


except Exception as e:

    print()
    print("=" * 70)
    print("ERROR")
    print("=" * 70)

    print()
    print(e)
