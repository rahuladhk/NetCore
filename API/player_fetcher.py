import json
import requests
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

SERIES_ID = "1510976"

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0"
})


# ============================================================
# LOAD RAW SCORECARD
# ============================================================

def load_raw_scorecard(match_id):

    file_path = (
        Path(__file__).parent
        / f"scorecard_{match_id}_raw.json"
    )

    if not file_path.exists():

        print(
            f"Raw scorecard not found: "
            f"{file_path}"
        )

        return None

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# EXTRACT PLAYER REFERENCES
# ============================================================

def extract_player_refs(details):

    player_refs = {}

    for detail in details:

        # ----------------------------------------------------
        # Athletes involved
        # ----------------------------------------------------

        athletes = detail.get(
            "athletesInvolved",
            []
        )

        for athlete in athletes:

            ref = athlete.get(
                "$ref"
            )

            if ref and not ref.endswith("/athletes/0"):
                player_refs[ref] = True

        # ----------------------------------------------------
        # Bowler
        # ----------------------------------------------------

        bowler = detail.get(
            "bowler"
        )

        if isinstance(
            bowler,
            dict
        ):

            athlete = bowler.get(
                "athlete"
            )

            if isinstance(
                athlete,
                dict
            ):

                ref = athlete.get(
                    "$ref"
                )

                if (
                    ref
                    and not ref.endswith(
                        "/athletes/0"
                    )
                ):

                    player_refs[ref] = True

        # ----------------------------------------------------
        # Other bowler
        # ----------------------------------------------------

        other_bowler = detail.get(
            "otherBowler"
        )

        if isinstance(
            other_bowler,
            dict
        ):

            athlete = other_bowler.get(
                "athlete"
            )

            if isinstance(
                athlete,
                dict
            ):

                ref = athlete.get(
                    "$ref"
                )

                if (
                    ref
                    and not ref.endswith(
                        "/athletes/0"
                    )
                ):

                    player_refs[ref] = True

        # ----------------------------------------------------
        # Batsman
        # ----------------------------------------------------

        batsman = detail.get(
            "batsman"
        )

        if isinstance(
            batsman,
            dict
        ):

            athlete = batsman.get(
                "athlete"
            )

            if isinstance(
                athlete,
                dict
            ):

                ref = athlete.get(
                    "$ref"
                )

                if (
                    ref
                    and not ref.endswith(
                        "/athletes/0"
                    )
                ):

                    player_refs[ref] = True

        # ----------------------------------------------------
        # Other batsman
        # ----------------------------------------------------

        other_batsman = detail.get(
            "otherBatsman"
        )

        if isinstance(
            other_batsman,
            dict
        ):

            athlete = other_batsman.get(
                "athlete"
            )

            if isinstance(
                athlete,
                dict
            ):

                ref = athlete.get(
                    "$ref"
                )

                if (
                    ref
                    and not ref.endswith(
                        "/athletes/0"
                    )
                ):

                    player_refs[ref] = True

    return list(
        player_refs.keys()
    )


# ============================================================
# FETCH PLAYER
# ============================================================

def fetch_player(ref):

    try:

        response = session.get(
            ref,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        print()
        print(
            "FAILED PLAYER REQUEST"
        )

        print(
            "Reference:",
            ref
        )

        print(
            "Error:",
            e
        )

        return None


# ============================================================
# CLEAN PLAYER DATA
# ============================================================

def clean_player(data):

    if not data:
        return None

    player_id = data.get(
        "id"
    )

    if not player_id:
        return None

    position = data.get(
        "position",
        {}
    )

    if not isinstance(
        position,
        dict
    ):
        position = {}

    return {

        "player_id":
            str(player_id),

        "name":
            data.get(
                "displayName"
            ),

        "full_name":
            data.get(
                "fullName"
            ),

        "short_name":
            data.get(
                "shortName"
            ),

        "first_name":
            data.get(
                "firstName"
            ),

        "last_name":
            data.get(
                "lastName"
            ),

        "batting_name":
            data.get(
                "battingName"
            ),

        "fielding_name":
            data.get(
                "fieldingName"
            ),

        "position":
            position.get(
                "name"
            ),

        "position_abbreviation":
            position.get(
                "abbreviation"
            ),

        "country":
            data.get(
                "country"
            ),

        "active":
            data.get(
                "active"
            ),

        "gender":
            data.get(
                "gender"
            ),

        "date_of_birth":
            data.get(
                "dateOfBirth"
            ),

        "headshot":
            data.get(
                "headshot"
            ),

        "flag":
            data.get(
                "flag"
            )
    }


# ============================================================
# BUILD PLAYER DATABASE
# ============================================================

def build_player_database(
    match_id,
    save_file=True
):

    print()
    print("=" * 70)
    print("PLAYER DATABASE BUILDER")
    print("=" * 70)

    print(
        "Match ID:",
        match_id
    )

    # --------------------------------------------------------
    # Load raw scorecard
    # --------------------------------------------------------

    raw_data = load_raw_scorecard(
        match_id
    )

    if not raw_data:

        print(
            "Could not load raw scorecard."
        )

        return None

    details = raw_data.get(
        "details",
        []
    )

    print(
        "Raw deliveries:",
        len(details)
    )

    # --------------------------------------------------------
    # Extract references
    # --------------------------------------------------------

    print()
    print(
        "Extracting player references..."
    )

    refs = extract_player_refs(
        details
    )

    print(
        "Player references:",
        len(refs)
    )

    # --------------------------------------------------------
    # Fetch players
    # --------------------------------------------------------

    players = {}

    failed = 0

    failed_refs = []

    for index, ref in enumerate(
        refs,
        start=1
    ):

        print(
            f"Fetching player "
            f"{index}/{len(refs)}..."
        )

        data = fetch_player(
            ref
        )

        player = clean_player(
            data
        )

        if player:

            players[
                player["player_id"]
            ] = player

        else:

            failed += 1

            failed_refs.append(
                ref
            )

            print()
            print(
                "FAILED PLAYER REFERENCE:"
            )

            print(
                ref
            )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    output = {

        "series_id":
            SERIES_ID,

        "match_id":
            str(match_id),

        "player_count":
            len(players),

        "failed":
            failed,

        "failed_refs":
            failed_refs,

        "players":
            players

    }

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    if save_file:

        file_path = (
            Path(__file__).parent
            / f"players_{match_id}.json"
        )

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                output,
                f,
                indent=2,
                ensure_ascii=False
            )

        print()
        print(
            "Saved player database to:"
        )

        print(
            file_path
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PLAYER DATABASE COMPLETE")
    print("=" * 70)

    print(
        "Players found :",
        len(players)
    )

    print(
        "Players failed:",
        failed
    )

    # --------------------------------------------------------
    # SHOW FAILED REFERENCES
    # --------------------------------------------------------

    if failed_refs:

        print()
        print("=" * 70)
        print("FAILED PLAYER REFERENCES")
        print("=" * 70)

        for failed_ref in failed_refs:

            print()
            print(
                failed_ref
            )

    else:

        print()
        print(
            "SUCCESS: "
            "ALL PLAYER REFERENCES "
            "WERE RESOLVED."
        )

    return output


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    build_player_database(
        "1510977"
    )