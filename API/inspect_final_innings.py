import json
from pathlib import Path

FILE = Path(__file__).parent / "scorecard_1510977_raw.json"

with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

details = data["details"]

print("=" * 70)
print("FINAL DELIVERY OF EACH INNINGS")
print("=" * 70)

innings = {}

for detail in details:
    period = detail.get("period")

    if period not in innings:
        innings[period] = detail
    else:
        # Keep the latest delivery
        if detail.get("sequence", 0) > innings[period].get("sequence", 0):
            innings[period] = detail

for period in sorted(innings):

    detail = innings[period]

    print()
    print("-" * 70)
    print("INNINGS:", period)
    print("DETAIL ID:", detail.get("id"))
    print("SEQUENCE:", detail.get("sequence"))
    print("SHORT TEXT:", detail.get("shortText"))
    print("HOME SCORE:", detail.get("homeScore"))
    print("AWAY SCORE:", detail.get("awayScore"))
    print("SCORE VALUE:", detail.get("scoreValue"))

    print()
    print("INNINGS OBJECT:")
    print(detail.get("innings"))

    print()
    print("OVER OBJECT:")
    print(detail.get("over"))

print()
print("=" * 70)