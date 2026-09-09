
import json


# ============================================================
# CONFIGURATION
# ============================================================

MATCH_ID = "1510978"

RAW_FILE = f"scorecard_{MATCH_ID}_raw.json"
PLAYER_FILE = f"players_{MATCH_ID}.json"
OUTPUT_FILE = f"scorecard_{MATCH_ID}.json"


# ============================================================
# LOAD DATA
# ============================================================

def load_scorecard():

    print("=" * 80)
    print("SCORECARD PARSER")
    print("=" * 80)

    print("\nLoading raw scorecard...")

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    details = data.get("details", [])

    print(f"Deliveries : {len(details)}")

    return details


def load_players():

    try:

        with open(PLAYER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        players = data.get("players", {})

        print(f"Players    : {len(players)}")

        return players

    except FileNotFoundError:

        print("Player file not found.")

        return {}


# ============================================================
# PLAYER FUNCTIONS
# ============================================================

def get_player_id(athlete):

    if not athlete:
        return None

    ref = athlete.get("$ref")

    if not ref:
        return None

    if "/athletes/" not in ref:
        return None

    player_id = ref.split("/athletes/")[-1].rstrip("/")

    if player_id == "0":
        return None

    return player_id


def get_player_name(player_id, players):

    if not player_id:
        return None

    player = players.get(str(player_id))

    if not player:
        return None

    return (
        player.get("name")
        or player.get("full_name")
        or player.get("short_name")
    )


# ============================================================
# GROUP DELIVERIES INTO INNINGS
# ============================================================

def group_innings(deliveries):

    innings = {}

    for detail in deliveries:

        # ----------------------------------------------------
        # ESPN provides the actual innings/period here.
        #
        # Example:
        # period = 1 -> 1st innings
        # period = 2 -> 2nd innings
        # ----------------------------------------------------

        period = detail.get("period")

        if period is None:

            innings_info = detail.get("innings") or {}

            period = innings_info.get("number")

        if period is None:
            continue

        if period not in innings:
            innings[period] = []

        innings[period].append(detail)

    return innings


# ============================================================
# BATTER STATISTICS
# ============================================================

def parse_batters(deliveries, players):

    batters = {}

    for detail in deliveries:

        batsman = detail.get("batsman") or {}

        athlete = batsman.get("athlete") or {}

        player_id = get_player_id(athlete)

        if not player_id:
            continue

        if player_id not in batters:

            batters[player_id] = {
                "player_id": player_id,
                "name": get_player_name(
                    player_id,
                    players
                ),
                "runs": 0,
                "balls": 0,
                "fours": 0,
                "sixes": 0
            }

        # ESPN gives cumulative statistics.
        batters[player_id]["runs"] = batsman.get(
            "totalRuns",
            batters[player_id]["runs"]
        )

        batters[player_id]["balls"] = batsman.get(
            "faced",
            batters[player_id]["balls"]
        )

        batters[player_id]["fours"] = batsman.get(
            "fours",
            batters[player_id]["fours"]
        )

        batters[player_id]["sixes"] = batsman.get(
            "sixes",
            batters[player_id]["sixes"]
        )

    return list(batters.values())


# ============================================================
# BOWLER STATISTICS
# ============================================================

def parse_bowlers(deliveries, players):

    bowlers = {}

    for detail in deliveries:

        bowler = detail.get("bowler") or {}

        athlete = bowler.get("athlete") or {}

        player_id = get_player_id(athlete)

        if not player_id:
            continue

        if player_id not in bowlers:

            bowlers[player_id] = {
                "player_id": player_id,
                "name": get_player_name(
                    player_id,
                    players
                ),
                "overs": 0,
                "balls": 0,
                "maidens": 0,
                "runs": 0,
                "wickets": 0
            }

        # ESPN gives cumulative bowling statistics.

        bowlers[player_id]["overs"] = bowler.get(
            "overs",
            bowlers[player_id]["overs"]
        )

        bowlers[player_id]["balls"] = bowler.get(
            "balls",
            bowlers[player_id]["balls"]
        )

        bowlers[player_id]["maidens"] = bowler.get(
            "maidens",
            bowlers[player_id]["maidens"]
        )

        bowlers[player_id]["runs"] = bowler.get(
            "conceded",
            bowlers[player_id]["runs"]
        )

        bowlers[player_id]["wickets"] = bowler.get(
            "wickets",
            bowlers[player_id]["wickets"]
        )

    return list(bowlers.values())


# ============================================================
# WICKET EVENTS
# ============================================================

def parse_wickets(deliveries, players):

    wicket_events = []

    for detail in deliveries:

        dismissal = detail.get("dismissal") or {}

        dismissal_type = dismissal.get("type")

        # Normal delivery
        if not dismissal_type:
            continue

        # ----------------------------------------------------
        # Batsman
        # ----------------------------------------------------

        batsman = detail.get("batsman") or {}

        batsman_id = get_player_id(
            batsman.get("athlete")
        )

        # ----------------------------------------------------
        # Bowler
        # ----------------------------------------------------

        bowler = detail.get("bowler") or {}

        bowler_id = get_player_id(
            bowler.get("athlete")
        )

        # ----------------------------------------------------
        # Wicket
        # ----------------------------------------------------

        wicket = {

            "delivery_id": detail.get("id"),

            "sequence": detail.get("sequence"),

            "over": (
                detail.get("over") or {}
            ).get("number"),

            "ball": (
                detail.get("over") or {}
            ).get("ball"),

            "batsman_id": batsman_id,

            "batsman": get_player_name(
                batsman_id,
                players
            ),

            "dismissal_type": dismissal_type,

            "bowler_id": bowler_id,

            "bowler": get_player_name(
                bowler_id,
                players
            ),

            "text": detail.get("text"),

            "short_text": detail.get("shortText")
        }

        # ----------------------------------------------------
        # Fielder
        # ----------------------------------------------------

        fielder = dismissal.get("fielder") or {}

        fielder_id = get_player_id(fielder)

        if fielder_id:

            wicket["fielder_id"] = fielder_id

            wicket["fielder"] = get_player_name(
                fielder_id,
                players
            )

        # ----------------------------------------------------
        # Keeper
        # ----------------------------------------------------

        keeper = dismissal.get("keeper") or {}

        keeper_id = get_player_id(keeper)

        if keeper_id:

            wicket["keeper_id"] = keeper_id

            wicket["keeper"] = get_player_name(
                keeper_id,
                players
            )

        wicket_events.append(wicket)

    return wicket_events


# ============================================================
# EXTRAS
# ============================================================

def parse_extras(deliveries):

    if not deliveries:
        return {
            "wides": 0,
            "no_balls": 0,
            "byes": 0,
            "leg_byes": 0,
            "total": 0
        }

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # ESPN's innings extras are cumulative.
    #
    # Therefore we DO NOT add the values from every delivery.
    #
    # We take the values from the final delivery.
    # --------------------------------------------------------

    deliveries = sorted(
        deliveries,
        key=lambda x: x.get("sequence", 0)
    )

    final_detail = deliveries[-1]

    innings = final_detail.get("innings") or {}

    wides = innings.get("wides", 0) or 0
    no_balls = innings.get("noBalls", 0) or 0
    byes = innings.get("byes", 0) or 0
    leg_byes = innings.get("legByes", 0) or 0

    total = (
        wides
        + no_balls
        + byes
        + leg_byes
    )

    return {

        "wides": wides,

        "no_balls": no_balls,

        "byes": byes,

        "leg_byes": leg_byes,

        "total": total
    }


# ============================================================
# PARSE ONE INNINGS
# ============================================================

def parse_innings(deliveries, players):

    if not deliveries:
        return None

    # --------------------------------------------------------
    # Sort deliveries
    # --------------------------------------------------------

    deliveries = sorted(
        deliveries,
        key=lambda x: x.get("sequence", 0)
    )

    # --------------------------------------------------------
    # Final delivery contains cumulative innings statistics
    # --------------------------------------------------------

    final_detail = deliveries[-1]

    innings_info = final_detail.get("innings") or {}

    # --------------------------------------------------------
    # Innings number
    # --------------------------------------------------------

    innings_number = final_detail.get("period")

    if innings_number is None:

        innings_number = innings_info.get(
            "number"
        )

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    score = innings_info.get(
        "runs",
        0
    )

    # --------------------------------------------------------
    # Wickets
    # --------------------------------------------------------

    wicket_count = innings_info.get(
        "wickets",
        0
    )

    # --------------------------------------------------------
    # Balls
    # --------------------------------------------------------

    balls = innings_info.get(
        "balls",
        0
    )

    # --------------------------------------------------------
    # Overs
    # --------------------------------------------------------

    over_info = final_detail.get("over") or {}

    actual_overs = over_info.get(
        "overs",
        0
    )

    # --------------------------------------------------------
    # Batters
    # --------------------------------------------------------

    batters = parse_batters(
        deliveries,
        players
    )

    # --------------------------------------------------------
    # Bowlers
    # --------------------------------------------------------

    bowlers = parse_bowlers(
        deliveries,
        players
    )

    # --------------------------------------------------------
    # Wickets
    # --------------------------------------------------------

    wicket_events = parse_wickets(
        deliveries,
        players
    )

    # --------------------------------------------------------
    # Extras
    # --------------------------------------------------------

    extras = parse_extras(
        deliveries
    )

    # ========================================================
    # BATTING TOTALS
    # ========================================================

    batter_runs = sum(
        batter.get("runs", 0) or 0
        for batter in batters
    )

    batter_balls = sum(
        batter.get("balls", 0) or 0
        for batter in batters
    )

    fours = sum(
        batter.get("fours", 0) or 0
        for batter in batters
    )

    sixes = sum(
        batter.get("sixes", 0) or 0
        for batter in batters
    )

    # ========================================================
    # BOWLING TOTALS
    # ========================================================

    bowler_balls = sum(
        bowler.get("balls", 0) or 0
        for bowler in bowlers
    )

    bowler_runs = sum(
        bowler.get("runs", 0) or 0
        for bowler in bowlers
    )

    bowler_wickets = sum(
        bowler.get("wickets", 0) or 0
        for bowler in bowlers
    )

    # ========================================================
    # RESULT
    # ========================================================

    return {

        "innings": innings_number,

        "score": score,

        "wickets": wicket_count,

        "overs": actual_overs,

        "balls": balls,

        "extras": extras,

        "batting_summary": {

            "runs": batter_runs,

            "balls": batter_balls,

            "fours": fours,

            "sixes": sixes
        },

        "bowling_summary": {

            "balls": bowler_balls,

            "runs": bowler_runs,

            "wickets": bowler_wickets
        },

        "batters": batters,

        "bowlers": bowlers,

        "wicket_events": wicket_events
    }


# ============================================================
# MAIN PARSER
# ============================================================

def main():

    deliveries = load_scorecard()

    players = load_players()

    if not deliveries:

        print("\nERROR: No scorecard details found.")

        return

    if not players:

        print("\nERROR: No players found.")

        return

    # --------------------------------------------------------
    # GROUP INTO INNINGS
    # --------------------------------------------------------

    innings_groups = group_innings(
        deliveries
    )

    print(
        f"\nInnings groups found: "
        f"{len(innings_groups)}"
    )

    for number, group in innings_groups.items():

        print(
            f"  Innings {number}: "
            f"{len(group)} deliveries"
        )

    # --------------------------------------------------------
    # Parse innings
    # --------------------------------------------------------

    parsed_innings = []

    for innings_number in sorted(
        innings_groups.keys()
    ):

        print(
            f"\nParsing innings {innings_number}..."
        )

        innings_deliveries = innings_groups[
            innings_number
        ]

        innings = parse_innings(
            innings_deliveries,
            players
        )

        if innings is None:
            continue

        parsed_innings.append(
            innings
        )

        print(
            f"Score: "
            f"{innings['score']}/"
            f"{innings['wickets']}"
        )

        print(
            f"Overs: "
            f"{innings['overs']}"
        )

        print(
            f"Balls: "
            f"{innings['balls']}"
        )

        print(
            f"Batters: "
            f"{len(innings['batters'])}"
        )

        print(
            f"Bowlers: "
            f"{len(innings['bowlers'])}"
        )

        print(
            f"Wickets: "
            f"{len(innings['wicket_events'])}"
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    print("\n" + "=" * 80)
    print("VALIDATION")
    print("=" * 80)

    for innings in parsed_innings:

        print(
            f"\nInnings {innings['innings']}"
        )

        print(
            f"Score: "
            f"{innings['score']}/"
            f"{innings['wickets']}"
        )

        # ----------------------------------------------------
        # Batting + extras
        # ----------------------------------------------------

        batter_runs = innings[
            "batting_summary"
        ]["runs"]

        extras_total = innings[
            "extras"
        ]["total"]

        calculated_score = (
            batter_runs
            + extras_total
        )

        print(
            f"Batter runs + extras: "
            f"{batter_runs} + "
            f"{extras_total} = "
            f"{calculated_score}"
        )

        if calculated_score == innings["score"]:

            print(
                "Score validation: PASS"
            )

        else:

            print(
                "Score validation: CHECK"
            )

        # ----------------------------------------------------
        # Wickets
        # ----------------------------------------------------

        wicket_events = len(
            innings["wicket_events"]
        )

        wicket_count = innings[
            "wickets"
        ]

        print(
            f"Wicket count: "
            f"{wicket_count}"
        )

        print(
            f"Wicket events: "
            f"{wicket_events}"
        )

        if wicket_count == wicket_events:

            print(
                "Wicket validation: PASS"
            )

        else:

            print(
                "Wicket validation: CHECK"
            )

        # ----------------------------------------------------
        # Bowler wickets
        # ----------------------------------------------------

        bowler_wickets = innings[
            "bowling_summary"
        ]["wickets"]

        print(
            f"Bowler wickets: "
            f"{bowler_wickets}"
        )

        if bowler_wickets == wicket_count:

            print(
                "Bowler wicket validation: PASS"
            )

        else:

            print(
                "Bowler wicket validation: CHECK"
            )

    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    output = {

        "series_id": "1510976",

        "match_id": MATCH_ID,

        "innings_count": len(
            parsed_innings
        ),

        "innings": parsed_innings
    }

    # --------------------------------------------------------
    # SAVE JSON
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    # ========================================================
    # COMPLETE
    # ========================================================

    print("\n" + "=" * 80)
    print("SCORECARD PARSING COMPLETE")
    print("=" * 80)

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    print(
        f"Innings parsed: "
        f"{len(parsed_innings)}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
