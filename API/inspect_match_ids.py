import json


# ============================================================
# LOAD SCHEDULE DATA
# ============================================================

with open("schedule_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# ============================================================
# GET MATCHES
# ============================================================

matches = (
    data["props"]
    ["appPageProps"]
    ["data"]
    ["content"]
    ["matches"]
)


# ============================================================
# FIND MATCH 123228
# ============================================================

for match in matches:

    if str(match.get("id")) == "123228":

        print()
        print("=" * 70)
        print("MATCH FOUND")
        print("=" * 70)

        print()

        # Print all simple ID-like fields
        for key, value in match.items():

            key_lower = key.lower()

            if (
                "id" in key_lower
                or "slug" in key_lower
                or "event" in key_lower
            ):

                if not isinstance(value, (dict, list)):

                    print(f"{key}: {value}")

        print()
        print("=" * 70)
        print("SERIES INFORMATION")
        print("=" * 70)

        series = match.get("series")

        if isinstance(series, dict):

            for key, value in series.items():

                if not isinstance(value, (dict, list)):

                    print(f"{key}: {value}")

        print()
        print("=" * 70)
        print("FULL MATCH OBJECT")
        print("=" * 70)

        print()

        print(json.dumps(
            match,
            indent=2,
            ensure_ascii=False
        ))

        break

else:

    print("Match 123228 was not found.")
