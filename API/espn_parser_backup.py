import json

DATA_FILE = "espn_data.json"


# ==========================================
# LOAD ESPN DATA
# ==========================================

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ==========================================
# GET CONTENT SECTION
# ==========================================

def get_content():
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

def get_standings():

    content = get_content()

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

            "played": int(team["matchesPlayed"]),
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

def get_results():

    content = get_content()

    matches = content.get("recentResults", [])

    results = []

    for match in matches:

        teams = match.get("teams", [])

        match_teams = []

        for team_data in teams:

            team = team_data["team"]

            match_teams.append({
                "team_id": team["id"],
                "name": team["longName"],
                "short_name": team["name"],
                "abbreviation": team["abbreviation"],

                "score": team_data.get("score"),
                "score_info": team_data.get("scoreInfo"),

                "logo": team.get("imageUrl")
            })

        results.append({

            "match_id": match["id"],
            "object_id": match["objectId"],

            "title": match["title"],

            "date": match["startDate"],
            "time": match["startTime"],

            "status": match["status"],
            "status_text": match["statusText"],

            "winner_team_id": match.get("winnerTeamId"),

            "venue": match.get("ground", {}).get("longName"),

            "teams": match_teams
        })

    return results


# ==========================================
# GET TEAMS
# ==========================================

def get_teams():

    content = get_content()

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

            "logo": info.get("imageUrl")
        })

    return teams


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("\n================================")
    print("NPL STANDINGS")
    print("================================")

    for team in get_standings():

        print(
            f"{team['rank']}. "
            f"{team['team']} | "
            f"P: {team['played']} | "
            f"W: {team['won']} | "
            f"L: {team['lost']} | "
            f"Pts: {team['points']} | "
            f"NRR: {team['nrr']}"
        )


    print("\n================================")
    print("NPL MATCH RESULTS")
    print("================================")

    for match in get_results():

        teams = match["teams"]

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


    print("\n================================")
    print("NPL TEAMS")
    print("================================")

    for team in get_teams():

        print(
            f"{team['team_id']} | "
            f"{team['name']} | "
            f"{team['abbreviation']}"
        )
