
import json
import time
from pathlib import Path
from datetime import datetime, timezone

from schedule_fetcher import fetch_schedule_data
from fixtures_parser import extract_fixtures

from espn import (
    fetch_espn_data,
    get_standings,
    get_results,
    get_teams
)

from scorecard_fetcher import fetch_all_details

import scorecard_parser
import player_fetcher


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"

CACHE_DIR.mkdir(exist_ok=True)

# General data update interval
UPDATE_INTERVAL = 60

# Fixture checking interval
FIXTURE_CHECK_INTERVAL = 60

# Live scorecard refresh interval
LIVE_SCORECARD_INTERVAL = 30

# ------------------------------------------------------------
# TEST MODE
# ------------------------------------------------------------
# Set this to a match ID while testing.
#
# Example:
# TEST_MATCH_ID = "1510978"
#
# Set to None when you want to process all matches.
# ------------------------------------------------------------

TEST_MATCH_ID = "1510978"


# ============================================================
# CACHE FILES
# ============================================================

FIXTURES_CACHE = CACHE_DIR / "fixtures.json"
POINTS_CACHE = CACHE_DIR / "points.json"
TEAMS_CACHE = CACHE_DIR / "teams.json"
RESULTS_CACHE = CACHE_DIR / "results.json"
STATUS_CACHE = CACHE_DIR / "update_status.json"


# ============================================================
# TIME HELPERS
# ============================================================

def utc_now():
    return datetime.now(timezone.utc)


def utc_iso():
    return utc_now().isoformat()


# ============================================================
# FILE HELPERS
# ============================================================

def file_age_seconds(file_path):

    if not file_path.exists():
        return None

    modified = datetime.fromtimestamp(
        file_path.stat().st_mtime,
        timezone.utc
    )

    return (
        utc_now() - modified
    ).total_seconds()


def save_json(file_path, data):

    temp_file = file_path.with_suffix(".tmp")

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    temp_file.replace(file_path)


def load_json(file_path, default=None):

    if not file_path.exists():
        return default

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as e:

        print(
            f"WARNING: Could not read "
            f"{file_path.name}: {e}"
        )

        return default


# ============================================================
# DETERMINE MATCH STATE
# ============================================================

def get_match_state(match):

    if not isinstance(match, dict):
        return "unknown"

    # --------------------------------------------------------
    # Cancelled
    # --------------------------------------------------------

    if match.get("is_cancelled") is True:
        return "cancelled"

    state = str(
        match.get("state") or ""
    ).strip().lower()

    status = str(
        match.get("status") or ""
    ).strip().lower()

    status_text = str(
        match.get("status_text") or ""
    ).strip().lower()

    combined = (
        f"{state} "
        f"{status} "
        f"{status_text}"
    )

    # --------------------------------------------------------
    # Cancelled / abandoned
    # --------------------------------------------------------

    cancelled_words = [
        "cancelled",
        "canceled",
        "abandoned",
        "no result"
    ]

    for word in cancelled_words:

        if word in combined:
            return "cancelled"

    # --------------------------------------------------------
    # Live
    # --------------------------------------------------------

    live_words = [
        "live",
        "in progress",
        "inprogress",
        "playing",
        "innings break",
        "innings",
        "drinks"
    ]

    for word in live_words:

        if word in combined:
            return "live"

    # --------------------------------------------------------
    # Completed
    # --------------------------------------------------------

    completed_words = [
        "complete",
        "completed",
        "finished",
        "result",
        "won by",
        "tied"
    ]

    for word in completed_words:

        if word in combined:
            return "completed"

    # --------------------------------------------------------
    # Winner exists
    # --------------------------------------------------------

    if match.get("winner_team_id") is not None:
        return "completed"

    # --------------------------------------------------------
    # Score exists
    # --------------------------------------------------------

    teams = match.get(
        "teams",
        []
    )

    if isinstance(
        teams,
        list
    ):

        for team in teams:

            if not isinstance(
                team,
                dict
            ):
                continue

            score = team.get(
                "score"
            )

            if score not in (
                None,
                "",
                "-",
                "0"
            ):

                return "live"

    # --------------------------------------------------------
    # Otherwise upcoming
    # --------------------------------------------------------

    return "upcoming"


# ============================================================
# GET SCORECARD MATCH ID
# ============================================================

def get_scorecard_match_id(match):

    possible_keys = [
        "object_id",
        "objectId",
        "event_id",
        "eventId",
        "match_id",
        "matchId",
        "id"
    ]

    for key in possible_keys:

        value = match.get(
            key
        )

        if value is not None:

            return str(value)

    return None


# ============================================================
# SCORECARD CACHE FILE
# ============================================================

def get_scorecard_cache_file(match_id):

    return (
        CACHE_DIR
        / f"scorecard_{match_id}.json"
    )


# ============================================================
# RAW SCORECARD FILE
# ============================================================

def get_raw_scorecard_file(match_id):

    return (
        BASE_DIR
        / f"scorecard_{match_id}_raw.json"
    )


# ============================================================
# UPDATE SCORECARD
# ============================================================

def update_scorecard(match_id):

    print()
    print("=" * 70)
    print("UPDATING SCORECARD")
    print("=" * 70)

    print(
        "MATCH ID:",
        match_id
    )

    try:

        # ====================================================
        # STEP 1
        # FETCH RAW SCORECARD
        # ====================================================

        print()
        print("=" * 70)
        print("STEP 1: FETCHING RAW SCORECARD")
        print("=" * 70)

        raw_data = fetch_all_details(
            match_id,
            save_file=True
        )

        if not raw_data:

            print(
                "ERROR: Scorecard fetch "
                "returned no data."
            )

            return False

        # ----------------------------------------------------
        # Check failed details
        # ----------------------------------------------------

        failed_details = raw_data.get(
            "failed_details",
            0
        )

        if failed_details > 0:

            print()
            print(
                "ERROR: Some scorecard "
                "details failed to download."
            )

            print(
                "Failed details:",
                failed_details
            )

            return False

        total_details = raw_data.get(
            "total_details",
            0
        )

        fetched_details = raw_data.get(
            "fetched_details",
            0
        )

        print()
        print(
            "Expected details:",
            total_details
        )

        print(
            "Fetched details:",
            fetched_details
        )

        print(
            "Failed details:",
            failed_details
        )

        # ====================================================
        # STEP 2
        # BUILD PLAYER DATABASE
        # ====================================================

        print()
        print("=" * 70)
        print("STEP 2: BUILDING PLAYER DATABASE")
        print("=" * 70)

        player_data = (
            player_fetcher
            .build_player_database(
                match_id,
                save_file=True
            )
        )

        if not player_data:

            print()
            print(
                "ERROR: Player database "
                "could not be built."
            )

            return False

        player_count = player_data.get(
            "player_count",
            0
        )

        player_failures = player_data.get(
            "failed",
            0
        )

        print()
        print(
            "Players found:",
            player_count
        )

        print(
            "Players failed:",
            player_failures
        )

        if player_count == 0:

            print()
            print(
                "ERROR: Player database "
                "contains no players."
            )

            return False

        # ====================================================
        # STEP 3
        # LOAD SCORECARD
        # ====================================================

        print()
        print("=" * 70)
        print("STEP 3: LOADING SCORECARD")
        print("=" * 70)

        raw_file = (
            get_raw_scorecard_file(
                match_id
            )
        )

        scorecard_parser.RAW_FILE = (
            raw_file
        )

        deliveries = (
            scorecard_parser.load_scorecard()
        )

        if not deliveries:

            print()
            print(
                "ERROR: No scorecard "
                "deliveries found."
            )

            return False

        print()
        print(
            "Loaded",
            len(deliveries),
            "scorecard details."
        )

        # ====================================================
        # STEP 4
        # LOAD PLAYER DATABASE
        # ====================================================

        print()
        print("=" * 70)
        print("STEP 4: LOADING PLAYER DATABASE")
        print("=" * 70)

        player_file = (
            BASE_DIR
            / f"players_{match_id}.json"
        )

        scorecard_parser.PLAYER_FILE = (
            player_file
        )

        players = (
            scorecard_parser.load_players()
        )

        if not players:

            print()
            print(
                "ERROR: No players found "
                "after building player database."
            )

            return False

        print()
        print(
            "Loaded",
            len(players),
            "players."
        )

        # ====================================================
        # STEP 5
        # GROUP AND PARSE INNINGS
        # ====================================================

        print()
        print("=" * 70)
        print("STEP 5: GROUPING AND PARSING INNINGS")
        print("=" * 70)

        # ----------------------------------------------------
        # Group all deliveries by innings
        # ----------------------------------------------------

        innings_groups = (
            scorecard_parser.group_innings(
                deliveries
            )
        )

        if not innings_groups:

            print()
            print(
                "ERROR: Could not identify "
                "any innings."
            )

            return False

        print()
        print(
            "Innings groups found:",
            len(innings_groups)
        )

        # ----------------------------------------------------
        # Parse each innings separately
        # ----------------------------------------------------

        innings = []

        for innings_number in sorted(
            innings_groups.keys()
        ):

            innings_deliveries = (
                innings_groups[
                    innings_number
                ]
            )

            print()
            print(
                "Parsing innings",
                innings_number,
                "| Details:",
                len(innings_deliveries)
            )

            parsed = (
                scorecard_parser.parse_innings(
                    innings_deliveries,
                    players
                )
            )

            if parsed is None:

                print()
                print(
                    "ERROR: Failed to parse "
                    "innings",
                    innings_number
                )

                return False

            innings.append(parsed)

        print()
        print(
            "Parsed innings:",
            len(innings)
        )

        # ----------------------------------------------------
        # Validate innings count
        # ----------------------------------------------------

        if len(innings) != len(innings_groups):

            print()
            print(
                "ERROR: Parsed innings count "
                "does not match grouped innings count."
            )

            return False

        # ====================================================
        # STEP 6
        # BUILD FINAL SCORECARD CACHE
        # ====================================================

        print()
        print("=" * 70)
        print("STEP 6: SAVING SCORECARD CACHE")
        print("=" * 70)

        scorecard_data = {

            "success":
                True,

            "series_id":
                raw_data.get(
                    "series_id",
                    "1510976"
                ),

            "match_id":
                match_id,

            "raw_details":
                raw_data.get(
                    "total_details",
                    len(deliveries)
                ),

            "fetched_details":
                raw_data.get(
                    "fetched_details",
                    len(deliveries)
                ),

            "failed_details":
                raw_data.get(
                    "failed_details",
                    0
                ),

            "player_count":
                len(players),

            "player_database_failed":
                player_failures,

            "innings_count":
                len(innings),

            "updated_at":
                utc_iso(),

            "innings":
                innings
        }

        cache_file = (
            get_scorecard_cache_file(
                match_id
            )
        )

        save_json(
            cache_file,
            scorecard_data
        )

        print()
        print(
            "Scorecard cache updated:"
        )

        print(
            cache_file
        )

        # ====================================================
        # COMPLETE
        # ====================================================

        print()
        print("=" * 70)
        print("SCORECARD UPDATE COMPLETE")
        print("=" * 70)

        print(
            "Match ID        :",
            match_id
        )

        print(
            "Players         :",
            len(players)
        )

        print(
            "Deliveries      :",
            len(deliveries)
        )

        print(
            "Innings         :",
            len(innings)
        )

        print(
            "Player failures :",
            player_failures
        )

        return True

    except Exception as e:

        print()
        print("=" * 70)
        print("ERROR UPDATING SCORECARD")
        print("=" * 70)

        print(
            type(e).__name__,
            ":",
            e
        )

        return False

# ============================================================
# UPDATE GENERAL DATA
# ============================================================

def update_general_data():

    print()
    print("=" * 70)
    print("UPDATING GENERAL NPL DATA")
    print("=" * 70)

    try:

        # ====================================================
        # SCHEDULE
        # ====================================================

        print()
        print("Fetching schedule...")

        schedule_data = (
            fetch_schedule_data()
        )

        if schedule_data:

            fixtures = (
                extract_fixtures(
                    schedule_data
                )
            )

            save_json(
                FIXTURES_CACHE,
                fixtures
            )

            print(
                f"Fixtures saved: "
                f"{len(fixtures)} matches"
            )

        # ====================================================
        # ESPN SERIES DATA
        # ====================================================

        print()
        print(
            "Fetching ESPN series data..."
        )

        espn_data = (
            fetch_espn_data()
        )

        if not espn_data:

            print(
                "WARNING: ESPN series data "
                "was not returned."
            )

            return

        # ====================================================
        # STANDINGS
        # ====================================================

        try:

            standings = (
                get_standings(
                    espn_data
                )
            )

            save_json(
                POINTS_CACHE,
                standings
            )

            print(
                f"Points table saved: "
                f"{len(standings)} teams"
            )

        except Exception as e:

            print(
                "WARNING: Could not update "
                "points table:"
            )

            print(e)

        # ====================================================
        # RESULTS
        # ====================================================

        try:

            results = (
                get_results(
                    espn_data
                )
            )

            save_json(
                RESULTS_CACHE,
                results
            )

            print(
                f"Results saved: "
                f"{len(results)} matches"
            )

        except Exception as e:

            print(
                "WARNING: Could not update "
                "results:"
            )

            print(e)

        # ====================================================
        # TEAMS
        # ====================================================

        try:

            teams = (
                get_teams(
                    espn_data
                )
            )

            save_json(
                TEAMS_CACHE,
                teams
            )

            print(
                f"Teams saved: "
                f"{len(teams)} teams"
            )

        except Exception as e:

            print(
                "WARNING: Could not update "
                "teams:"
            )

            print(e)

    except Exception as e:

        print()
        print(
            "ERROR UPDATING GENERAL DATA:"
        )

        print(e)


# ============================================================
# UPDATE MATCH SCORECARDS
# ============================================================

def update_match_scorecards(fixtures):

    if not fixtures:

        print(
            "No fixtures available."
        )

        return

    print()
    print("=" * 70)
    print("CHECKING MATCH SCORECARDS")
    print("=" * 70)

    updated = 0
    live_updated = 0
    skipped = 0
    ignored = 0
    failed = 0

    # ========================================================
    # LOOP THROUGH FIXTURES
    # ========================================================

    for match in fixtures:

        if not isinstance(
            match,
            dict
        ):

            continue

        # ----------------------------------------------------
        # Get scorecard ID
        # ----------------------------------------------------

        match_id = (
            get_scorecard_match_id(
                match
            )
        )

        if not match_id:

            print()
            print(
                "WARNING: Could not "
                "determine match ID."
            )

            continue

        # ----------------------------------------------------
        # TEST MODE
        # ----------------------------------------------------

        if (
            TEST_MATCH_ID is not None
            and match_id != str(
                TEST_MATCH_ID
            )
        ):

            ignored += 1

            continue

        # ----------------------------------------------------
        # Match state
        # ----------------------------------------------------

        state = (
            get_match_state(
                match
            )
        )

        title = match.get(
            "title",
            f"Match {match_id}"
        )

        cache_file = (
            get_scorecard_cache_file(
                match_id
            )
        )

        print()
        print(
            f"{title} | "
            f"ID: {match_id} | "
            f"STATE: {state.upper()}"
        )

        # ====================================================
        # CANCELLED
        # ====================================================

        if state == "cancelled":

            print(
                "  → Cancelled. Skipping."
            )

            skipped += 1

            continue

        # ====================================================
        # UPCOMING
        # ====================================================

        if state == "upcoming":

            print(
                "  → Upcoming. "
                "No scorecard request."
            )

            skipped += 1

            continue

        # ====================================================
        # COMPLETED
        # ====================================================

        if state == "completed":

            if cache_file.exists():

                print(
                    "  → Completed and cached. "
                    "Skipping permanently."
                )

                skipped += 1

            else:

                print(
                    "  → Completed but no cache. "
                    "Fetching scorecard once."
                )

                success = (
                    update_scorecard(
                        match_id
                    )
                )

                if success:

                    updated += 1

                else:

                    failed += 1

            continue

        # ====================================================
        # LIVE
        # ====================================================

        if state == "live":

            age = (
                file_age_seconds(
                    cache_file
                )
            )

            if age is None:

                print(
                    "  → Live with no cache. "
                    "Fetching now."
                )

                success = (
                    update_scorecard(
                        match_id
                    )
                )

                if success:

                    updated += 1
                    live_updated += 1

                else:

                    failed += 1

            elif age >= LIVE_SCORECARD_INTERVAL:

                print(
                    f"  → Live cache is "
                    f"{age:.1f}s old. "
                    f"Refreshing."
                )

                success = (
                    update_scorecard(
                        match_id
                    )
                )

                if success:

                    updated += 1
                    live_updated += 1

                else:

                    failed += 1

            else:

                print(
                    f"  → Live cache is "
                    f"{age:.1f}s old. "
                    f"Waiting for next refresh."
                )

                skipped += 1

            continue

        # ====================================================
        # UNKNOWN
        # ====================================================

        print(
            "  → Unknown state. Skipping."
        )

        skipped += 1

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("SCORECARD UPDATE SUMMARY")
    print("=" * 70)

    if TEST_MATCH_ID is not None:

        print(
            "TEST MODE MATCH       :",
            TEST_MATCH_ID
        )

    else:

        print(
            "TEST MODE             : DISABLED"
        )

    print(
        "Scorecards updated    :",
        updated
    )

    print(
        "Live scorecards updated:",
        live_updated
    )

    print(
        "Scorecards skipped    :",
        skipped
    )

    print(
        "Scorecards ignored    :",
        ignored
    )

    print(
        "Scorecards failed     :",
        failed
    )

    return {

        "updated":
            updated,

        "live_updated":
            live_updated,

        "skipped":
            skipped,

        "ignored":
            ignored,

        "failed":
            failed
    }


# ============================================================
# UPDATE STATUS
# ============================================================

def update_status(
    status="running",
    message=""
):

    data = {

        "status":
            status,

        "message":
            message,

        "updated_at":
            utc_iso()
    }

    save_json(
        STATUS_CACHE,
        data
    )


# ============================================================
# RUN ONE UPDATE
# ============================================================

def run_update():

    print()
    print("=" * 80)
    print("NPL T20 BACKGROUND UPDATER")
    print("=" * 80)

    print(
        "Time:",
        utc_iso()
    )

    try:

        # ----------------------------------------------------
        # General data
        # ----------------------------------------------------

        update_status(
            "running",
            "Updating general data"
        )

        update_general_data()

        # ----------------------------------------------------
        # Load fixtures from cache
        # ----------------------------------------------------

        fixtures = (
            load_json(
                FIXTURES_CACHE,
                []
            )
        )

        # ----------------------------------------------------
        # Scorecards
        # ----------------------------------------------------

        update_status(
            "running",
            "Checking match scorecards"
        )

        update_match_scorecards(
            fixtures
        )

        # ----------------------------------------------------
        # Complete
        # ----------------------------------------------------

        update_status(
            "idle",
            "Update completed successfully"
        )

        print()
        print("=" * 80)
        print("UPDATE COMPLETED")
        print("=" * 80)

    except Exception as e:

        print()
        print("=" * 80)
        print("UPDATE FAILED")
        print("=" * 80)

        print(
            type(e).__name__,
            ":",
            e
        )

        update_status(
            "error",
            str(e)
        )


# ============================================================
# MAIN LOOP
# ============================================================

def main():

    print()
    print("=" * 80)
    print("NPL T20 BACKGROUND UPDATER STARTED")
    print("=" * 80)

    print()
    print(
        "General update interval       :",
        UPDATE_INTERVAL
    )

    print(
        "Fixture check interval        :",
        FIXTURE_CHECK_INTERVAL
    )

    print(
        "Live scorecard interval       :",
        LIVE_SCORECARD_INTERVAL
    )

    print()

    if TEST_MATCH_ID is not None:

        print(
            "TEST MODE MATCH               :",
            TEST_MATCH_ID
        )

        print(
            "Only this match will be "
            "processed in STEP 3."
        )

    else:

        print(
            "TEST MODE                     : DISABLED"
        )

        print(
            "All required scorecards "
            "will be processed normally."
        )

    print()
    print(
        "Press CTRL+C to stop."
    )

    print()

    update_status(
        "starting",
        "Background updater starting"
    )

    last_general_update = 0

    try:

        while True:

            current_time = (
                time.time()
            )

            if (
                current_time
                - last_general_update
                >= UPDATE_INTERVAL
            ):

                run_update()

                last_general_update = (
                    current_time
                )

            time.sleep(5)

    except KeyboardInterrupt:

        print()
        print("=" * 80)
        print("UPDATER STOPPED")
        print("=" * 80)

        update_status(
            "stopped",
            "Updater stopped by user"
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()
