import json
from pathlib import Path

FILE = Path(__file__).parent / "scorecard_1510977.json"


def load_scorecard():
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_innings(innings):

    print()
    print("=" * 80)
    print(f"INNINGS {innings['number']}")
    print("=" * 80)

    total_runs = innings["total_runs"]
    wickets = innings["wickets"]
    balls = innings["balls"]

    extras = innings["extras"]

    total_extras = (
        extras["wides"]
        + extras["no_balls"]
        + extras["byes"]
        + extras["leg_byes"]
    )

    # --------------------------------------------------
    # BATTERS
    # --------------------------------------------------

    total_batter_runs = sum(
        batter["runs"]
        for batter in innings["batters"]
    )

    total_batter_balls = sum(
        batter["balls"]
        for batter in innings["batters"]
    )

    total_fours = sum(
        batter["fours"]
        for batter in innings["batters"]
    )

    total_sixes = sum(
        batter["sixes"]
        for batter in innings["batters"]
    )

    # --------------------------------------------------
    # BOWLERS
    # --------------------------------------------------

    total_bowler_balls = sum(
        bowler["balls"]
        for bowler in innings["bowlers"]
    )

    total_bowler_runs = sum(
        bowler["runs"]
        for bowler in innings["bowlers"]
    )

    total_bowler_wickets = sum(
        bowler["wickets"]
        for bowler in innings["bowlers"]
    )

    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------

    print()
    print("INNINGS SUMMARY")
    print("-" * 80)

    print(f"Score              : {total_runs}/{wickets}")
    print(f"Balls              : {balls}")
    print(f"Overs              : {innings['overs']}")

    print()
    print("EXTRAS")
    print("-" * 80)

    print(f"Wides              : {extras['wides']}")
    print(f"No-balls           : {extras['no_balls']}")
    print(f"Byes               : {extras['byes']}")
    print(f"Leg-byes           : {extras['leg_byes']}")
    print(f"Total extras       : {total_extras}")

    print()
    print("BATTER TOTALS")
    print("-" * 80)

    print(f"Batters            : {len(innings['batters'])}")
    print(f"Runs               : {total_batter_runs}")
    print(f"Balls faced        : {total_batter_balls}")
    print(f"Fours              : {total_fours}")
    print(f"Sixes              : {total_sixes}")

    print()
    print("BOWLER TOTALS")
    print("-" * 80)

    print(f"Bowlers            : {len(innings['bowlers'])}")
    print(f"Bowler balls       : {total_bowler_balls}")
    print(f"Bowler runs        : {total_bowler_runs}")
    print(f"Bowler wickets     : {total_bowler_wickets}")

    # --------------------------------------------------
    # VALIDATION TESTS
    # --------------------------------------------------

    print()
    print("VALIDATION")
    print("-" * 80)

    # 1. Batter runs + extras
    calculated_score = total_batter_runs + total_extras

    print(
        f"Batters + Extras   : "
        f"{total_batter_runs} + {total_extras} "
        f"= {calculated_score}"
    )

    print(
        f"Official score     : {total_runs}"
    )

    if calculated_score == total_runs:
        print("✓ RUN TOTAL: PASS")
    else:
        print(
            "✗ RUN TOTAL: FAIL "
            f"(difference: {total_runs - calculated_score})"
        )

    # 2. Wickets
    wicket_list_count = len(
        innings["wickets_list"]
    )

    print()
    print(
        f"Wicket list        : {wicket_list_count}"
    )

    print(
        f"Innings wickets    : {wickets}"
    )

    if wicket_list_count == wickets:
        print("✓ WICKET TOTAL: PASS")
    else:
        print("✗ WICKET TOTAL: FAIL")

    # 3. Bowler balls
    print()
    print(
        f"Bowler balls       : {total_bowler_balls}"
    )

    print(
        f"Innings balls      : {balls}"
    )

    if total_bowler_balls == balls:
        print("✓ BOWLER BALLS: PASS")
    else:
        print("✗ BOWLER BALLS: FAIL")

    # 4. Bowler wickets
    print()
    print(
        f"Bowler wickets     : {total_bowler_wickets}"
    )

    print(
        f"Innings wickets    : {wickets}"
    )

    if total_bowler_wickets == wickets:
        print("✓ BOWLER WICKETS: PASS")
    else:
        print(
            "NOTE: Bowler wickets do not "
            "necessarily equal total wickets "
            "because run-outs and some other "
            "dismissals are not credited to bowlers."
        )

    # 5. Bowler runs
    print()
    print(
        f"Bowler runs        : {total_bowler_runs}"
    )

    print(
        f"Innings score      : {total_runs}"
    )

    print(
        "NOTE: Bowler conceded runs can differ "
        "from innings score because byes and "
        "leg-byes are not charged to the bowler."
    )


def main():

    data = load_scorecard()

    print()
    print("=" * 80)
    print("NPL SCORECARD VALIDATION")
    print("=" * 80)

    print(f"Match ID: {data['match_id']}")
    print(f"Innings : {len(data['innings'])}")

    for innings in data["innings"]:
        validate_innings(innings)

    print()
    print("=" * 80)
    print("VALIDATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
