import json
from pathlib import Path


DATA_FILE = Path(__file__).parent / "schedule_data.json"


def load_schedule_data():
    """Load the ESPN schedule JSON file."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_matches(data=None):
    """Return the raw match list from ESPN data."""
    if data is None:
        data = load_schedule_data()

    return (
        data["props"]
        ["appPageProps"]
        ["data"]
        ["content"]
        ["matches"]
    )


def extract_fixtures(data=None):
    """
    Convert ESPN match data into a clean structure
    suitable for our NPL API.
    """

    matches = get_matches(data)

    fixtures = []

    for match in matches:

        teams = []

        for team_data in match.get("teams", []):

            team = team_data.get("team", {})

            teams.append({
                "team_id": team.get("id"),
                "name": team.get("longName"),
                "short_name": team.get("name"),
                "abbreviation": team.get("abbreviation"),
                "logo": team.get("imageUrl"),
                "score": team_data.get("score"),
                "score_info": team_data.get("scoreInfo"),
                "is_home": team_data.get("isHome", False),
                "points": team_data.get("points", 0)
            })

        ground = match.get("ground") or {}

        fixture = {
            "match_id": match.get("id"),
            "object_id": match.get("objectId"),
            "slug": match.get("slug"),

            "title": match.get("title"),

            "date": match.get("startDate"),
            "time": match.get("startTime"),

            "stage": match.get("stage"),
            "state": match.get("state"),

            "status": match.get("status"),
            "status_text": match.get("statusText"),

            "winner_team_id": match.get("winnerTeamId"),

            "toss_winner_team_id": match.get("tossWinnerTeamId"),
            "toss_winner_choice": match.get("tossWinnerChoice"),

            "venue": ground.get("longName"),
            "venue_short": ground.get("smallName"),
            "city": ground.get("town", {}).get("name"),

            "format": match.get("format"),

            "is_cancelled": match.get("isCancelled", False),

            "has_commentary": match.get("hasCommentary", False),
            "has_scorecard": match.get("hasScorecard", False),

            "teams": teams
        }

        fixtures.append(fixture)

    return fixtures


if __name__ == "__main__":

    fixtures = extract_fixtures()

    print()
    print("=" * 100)
    print("NPL FIXTURES / RESULTS")
    print("=" * 100)

    print("TOTAL MATCHES:", len(fixtures))
    print()

    for match in fixtures:

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
