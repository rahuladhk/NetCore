import json
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

CORS(app)


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).parent

CACHE_DIR = BASE_DIR / "cache"

SCORECARD_CACHE_DIR = (
    CACHE_DIR / "scorecards"
)


# ============================================================
# CACHE FILES
# ============================================================

FIXTURES_CACHE = (
    CACHE_DIR / "fixtures.json"
)

POINTS_CACHE = (
    CACHE_DIR / "points_table.json"
)

TEAMS_CACHE = (
    CACHE_DIR / "teams.json"
)

RESULTS_CACHE = (
    CACHE_DIR / "results.json"
)

STATUS_CACHE = (
    CACHE_DIR / "update_status.json"
)


# ============================================================
# READ JSON CACHE
# ============================================================

def read_json(file_path):

    if not file_path.exists():

        return None

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as e:

        print(
            f"Cache read error "
            f"{file_path}: {e}"
        )

        return None


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({

        "name": "NPL T20 API",

        "status": "online",

        "architecture":
            "cache-based",

        "message":
            "API is serving cached NPL data"
    })


# ============================================================
# FIXTURES
# ============================================================

@app.route("/api/fixtures")
def fixtures():

    data = read_json(
        FIXTURES_CACHE
    )

    if data is None:

        return jsonify({

            "success": False,

            "error":
                "Fixtures cache is not available"
        }), 503

    return jsonify({

        "success": True,

        "count": len(data)
            if isinstance(data, list)
            else 0,

        "fixtures": data
    })


# ============================================================
# POINTS TABLE
# ============================================================

@app.route("/api/points-table")
def points_table():

    data = read_json(
        POINTS_CACHE
    )

    if data is None:

        return jsonify({

            "success": False,

            "error":
                "Points table cache is not available"
        }), 503

    return jsonify({

        "success": True,

        "count": len(data)
            if isinstance(data, list)
            else 0,

        "standings": data
    })


# ============================================================
# TEAMS
# ============================================================

@app.route("/api/teams")
def teams():

    data = read_json(
        TEAMS_CACHE
    )

    if data is None:

        return jsonify({

            "success": False,

            "error":
                "Teams cache is not available"
        }), 503

    return jsonify({

        "success": True,

        "count": len(data)
            if isinstance(data, list)
            else 0,

        "teams": data
    })


# ============================================================
# RESULTS
# ============================================================

@app.route("/api/results")
def results():

    data = read_json(
        RESULTS_CACHE
    )

    if data is None:

        return jsonify({

            "success": False,

            "error":
                "Results cache is not available"
        }), 503

    return jsonify({

        "success": True,

        "count": len(data)
            if isinstance(data, list)
            else 0,

        "results": data
    })


# ============================================================
# SCORECARD
# ============================================================

@app.route(
    "/api/scorecard/<match_id>"
)
def scorecard(match_id):

    cache_file = (
        SCORECARD_CACHE_DIR
        / f"{match_id}.json"
    )

    data = read_json(
        cache_file
    )

    if data is None:

        return jsonify({

            "success": False,

            "match_id": match_id,

            "error":
                "Scorecard is not available in cache"
        }), 404

    return jsonify(data)


# ============================================================
# UPDATE STATUS
# ============================================================

@app.route("/api/status")
def status():

    data = read_json(
        STATUS_CACHE
    )

    if data is None:

        return jsonify({

            "success": False,

            "error":
                "Updater status is not available"
        }), 503

    return jsonify({

        "success": True,

        "status": data
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health")
def health():

    fixtures_exists = (
        FIXTURES_CACHE.exists()
    )

    points_exists = (
        POINTS_CACHE.exists()
    )

    teams_exists = (
        TEAMS_CACHE.exists()
    )

    results_exists = (
        RESULTS_CACHE.exists()
    )

    return jsonify({

        "success": True,

        "api": "online",

        "cache": {

            "fixtures": fixtures_exists,

            "points_table": points_exists,

            "teams": teams_exists,

            "results": results_exists
        }
    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )