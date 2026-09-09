import json
from pathlib import Path
from playwright.sync_api import sync_playwright


# ==========================================
# CONFIGURATION
# ==========================================

ESPN_URL = (
    "https://www.espncricinfo.com/series/"
    "nepal-premier-league-2025-26-1510976"
)

DATA_FILE = Path(__file__).parent / "espn_data.json"


# ==========================================
# FETCH ESPN PAGE
# ==========================================

def fetch_espn_data():

    print("Connecting to ESPNcricinfo...")
    print(ESPN_URL)

    with sync_playwright() as p:

        browser = None
        page = None

        try:

            # ----------------------------------
            # START BROWSER
            # ----------------------------------

            browser = p.webkit.launch(
                headless=True
            )

            page = browser.new_page()

            # ----------------------------------
            # OPEN ESPN PAGE
            # ----------------------------------

            response = page.goto(
                ESPN_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            if response:

                print(
                    f"HTTP Status: {response.status}"
                )

            print("Page loaded.")

            # ----------------------------------
            # WAIT FOR PAGE TO FINISH LOADING
            # ----------------------------------

            page.wait_for_timeout(5000)

            print(
                "Searching for __NEXT_DATA__..."
            )

            # ----------------------------------
            # FIND NEXT DATA SCRIPT
            # ----------------------------------

            script = page.locator(
                'script#__NEXT_DATA__'
            )

            if script.count() == 0:

                print(
                    "ERROR: __NEXT_DATA__ was not found."
                )

                return None

            # ----------------------------------
            # READ JSON
            # ----------------------------------

            json_text = script.text_content()

            if not json_text:

                print(
                    "ERROR: __NEXT_DATA__ is empty."
                )

                return None

            # ----------------------------------
            # CONVERT JSON TEXT TO PYTHON DATA
            # ----------------------------------

            data = json.loads(
                json_text
            )

            print(
                "SUCCESS: ESPN data extracted."
            )

            # ----------------------------------
            # SAVE DATA
            # ----------------------------------

            with open(
                DATA_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            print(
                f"Saved data to: {DATA_FILE}"
            )

            return data

        # ======================================
        # ERROR HANDLING
        # ======================================

        except Exception as e:

            print()
            print(
                "ERROR FETCHING ESPN SERIES DATA:"
            )

            print(e)

            return None

        # ======================================
        # CLEANUP
        # ======================================

        finally:

            # Close page first.
            try:

                if page:

                    page.close()

            except Exception:

                pass

            # Close browser second.
            try:

                if browser:

                    browser.close()

            except Exception:

                pass


# ==========================================
# LOAD DATA
# ==========================================

def load_data():

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ==========================================
# GET CONTENT
# ==========================================

def get_content(data=None):

    if data is None:

        data = load_data()

    return (
        data["props"]
        ["appPageProps"]
        ["data"]
        ["content"]
    )


# ==========================================
# GET POINTS TABLE
# ==========================================

def get_standings(data=None):

    content = get_content(data)

    team_stats = (
        content["standings"]
        ["groups"][0]
        ["teamStats"]
    )

    standings = []

    for team in team_stats:

        info = team["teamInfo"]

        standings.append({

            "rank": team["rank"],

            "team_id": info["id"],

            "team": info["longName"],

            "short_name": info["name"],

            "abbreviation": info["abbreviation"],

            "played": int(
                team["matchesPlayed"]
            ),

            "won": team["matchesWon"],

            "lost": team["matchesLost"],

            "tied": team["matchesTied"],

            "drawn": team["matchesDrawn"],

            "no_result": team["matchesNoResult"],

            "points": team["points"],

            "nrr": team["nrr"],

            "for": team["for"],

            "against": team["against"],

            "logo": info.get("imageUrl")
        })

    return standings


# ==========================================
# GET MATCH RESULTS
# ==========================================

def get_results(data=None):

    content = get_content(data)

    matches = content.get(
        "recentResults",
        []
    )

    results = []

    for match in matches:

        teams = match.get(
            "teams",
            []
        )

        match_teams = []

        for team_data in teams:

            team = team_data["team"]

            match_teams.append({

                "team_id": team["id"],

                "name": team["longName"],

                "short_name": team["name"],

                "abbreviation": team["abbreviation"],

                "score": team_data.get(
                    "score"
                ),

                "score_info": team_data.get(
                    "scoreInfo"
                ),

                "logo": team.get(
                    "imageUrl"
                )
            })

        results.append({

            "match_id": match["id"],

            "object_id": match["objectId"],

            "title": match["title"],

            "date": match["startDate"],

            "time": match["startTime"],

            "status": match["status"],

            "status_text": match["statusText"],

            "winner_team_id": match.get(
                "winnerTeamId"
            ),

            "venue": (
                match.get("ground", {})
                .get("longName")
            ),

            "teams": match_teams
        })

    return results


# ==========================================
# GET TEAMS
# ==========================================

def get_teams(data=None):

    content = get_content(data)

    team_stats = (
        content["standings"]
        ["groups"][0]
        ["teamStats"]
    )

    teams = []

    for team_data in team_stats:

        info = team_data["teamInfo"]

        teams.append({

            "team_id": info["id"],

            "name": info["longName"],

            "short_name": info["name"],

            "abbreviation": info["abbreviation"],

            "slug": info["slug"],

            "logo": info.get(
                "imageUrl"
            )
        })

    return teams


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print()
    print("================================")
    print("FETCHING ESPN DATA")
    print("================================")

    # --------------------------------------
    # FETCH ESPN DATA
    # --------------------------------------

    data = fetch_espn_data()

    if data is None:

        print()
        print(
            "Could not fetch ESPN data."
        )

        print(
            "The existing espn_data.json "
            "was NOT modified."
        )

        raise SystemExit(1)

    # ======================================
    # NPL STANDINGS
    # ======================================

    print()
    print("================================")
    print("NPL STANDINGS")
    print("================================")

    for team in get_standings(data):

        print(

            f"{team['rank']}. "

            f"{team['team']} | "

            f"P: {team['played']} | "

            f"W: {team['won']} | "

            f"L: {team['lost']} | "

            f"Pts: {team['points']} | "

            f"NRR: {team['nrr']}"

        )

    # ======================================
    # NPL MATCH RESULTS
    # ======================================

    print()
    print("================================")
    print("NPL MATCH RESULTS")
    print("================================")

    for match in get_results(data):

        teams = match["teams"]

        if len(teams) >= 2:

            print(

                f"{match['match_id']} | "

                f"{match['title']} | "

                f"{match['date'][:10]} | "

                f"{teams[0]['short_name']} "

                f"vs "

                f"{teams[1]['short_name']} | "

                f"{teams[0]['score']} - "

                f"{teams[1]['score']} | "

                f"{match['status_text']}"

            )

    # ======================================
    # NPL TEAMS
    # ======================================

    print()
    print("================================")
    print("NPL TEAMS")
    print("================================")

    for team in get_teams(data):

        print(

            f"{team['team_id']} | "

            f"{team['name']} | "

            f"{team['abbreviation']}"

        )