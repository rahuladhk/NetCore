import json
from pathlib import Path


DATA_FILE = Path(__file__).parent / "scorecard_1510977_raw.json"


with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


details = data["details"]


print("=" * 70)
print("SCORECARD STRUCTURE INSPECTION")
print("=" * 70)

print()
print("TOTAL DETAILS:", len(details))


# ============================================================
# FIRST DELIVERY
# ============================================================

first = details[0]

print()
print("=" * 70)
print("FIRST DELIVERY")
print("=" * 70)

print()

for key, value in first.items():

    print(f"{key}:")
    print(f"    {value}")
    print()


# ============================================================
# INNINGS
# ============================================================

print("=" * 70)
print("INNINGS STRUCTURE")
print("=" * 70)

for i, detail in enumerate(details):

    innings = detail.get("innings")

    if innings:

        print()
        print(f"Delivery {i + 1}")
        print("Innings:")

        print(innings)

        break


# ============================================================
# WICKETS
# ============================================================

print()
print("=" * 70)
print("WICKET DELIVERIES")
print("=" * 70)

wickets_found = 0

for detail in details:

    dismissal = detail.get("dismissal", {})

    if dismissal.get("dismissal") is True:

        wickets_found += 1

        print()
        print("DETAIL ID:", detail.get("id"))
        print("TEXT:", detail.get("text"))
        print("SHORT TEXT:", detail.get("shortText"))
        print("DISMISSAL:")
        print(dismissal)

        if wickets_found >= 5:
            break


print()
print("WICKET DELIVERIES SHOWN:", wickets_found)


# ============================================================
# BATSMAN STRUCTURE
# ============================================================

print()
print("=" * 70)
print("BATSMAN STRUCTURE")
print("=" * 70)

for detail in details:

    batsman = detail.get("batsman")

    if batsman:

        print()
        print(batsman)

        break


# ============================================================
# BOWLER STRUCTURE
# ============================================================

print()
print("=" * 70)
print("BOWLER STRUCTURE")
print("=" * 70)

for detail in details:

    bowler = detail.get("bowler")

    if bowler:

        print()
        print(bowler)

        break


# ============================================================
# OVER STRUCTURE
# ============================================================

print()
print("=" * 70)
print("OVER STRUCTURE")
print("=" * 70)

for detail in details:

    over = detail.get("over")

    if over:

        print()
        print(over)

        break


# ============================================================
# EXTRAS / PLAY TYPES
# ============================================================

print()
print("=" * 70)
print("PLAY TYPES")
print("=" * 70)

play_types = {}

for detail in details:

    play_type = detail.get("playType")

    if isinstance(play_type, dict):

        description = play_type.get(
            "description",
            "unknown"
        )

        play_types[description] = (
            play_types.get(description, 0) + 1
        )


for name, count in sorted(play_types.items()):

    print(f"{name}: {count}")


print()
print("=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)
