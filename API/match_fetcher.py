import json
from pathlib import Path

from playwright.sync_api import sync_playwright

# ============================================================
# CONFIGURATION
# ============================================================

# ESPN objectId for the match
MATCH_ID = "1510977"

ESPN_MATCH_URL = (
    "https://www.espncricinfo.com/series/"
    "nepal-premier-league-2025-26-1510976/"
    f"match/{MATCH_ID}/"
    "janakpur-bolts-npl-vs-kathmandu-gorkhas-npl-1st-match"
)

DATA_FILE = Path(__file__).parent / f"match_{MATCH_ID}_data.json"

# ============================================================
# FETCH MATCH DATA
# ============================================================

def fetch_match_data():

    print()
    print("=" * 70)
    print("FETCHING NPL MATCH DATA")
    print("=" * 70)

    print()
    print("Match ID:", MATCH_ID)
    print("URL:")
    print(ESPN_MATCH_URL)

    with sync_playwright() as p:

        browser = p.webkit.launch(headless=True)

        page = browser.new_page()

        try:

            response = page.goto(
                ESPN_MATCH_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            if response:
                print()
                print("HTTP STATUS:", response.status)

            print("Page loaded.")

            # Give ESPN time to finish loading
            page.wait_for_timeout(5000)

            print("Searching for __NEXT_DATA__...")

            script = page.locator("script#__NEXT_DATA__")

            if script.count() == 0:

                print()
                print("ERROR: __NEXT_DATA__ was not found.")

                html = page.content()

                print("Page size:", len(html), "characters")

                return None

            json_text = script.text_content()

            if not json_text:

                print()
                print("ERROR: __NEXT_DATA__ is empty.")

                return None

            data = json.loads(json_text)

            print()
            print("SUCCESS: Match data extracted.")

            # ------------------------------------------------
            # Save raw match data
            # ------------------------------------------------

            with open(DATA_FILE, "w", encoding="utf-8") as f:

                json.dump(
                    data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            print()
            print("Saved match data to:")
            print(DATA_FILE)

            # ------------------------------------------------
            # Display basic structure
            # ------------------------------------------------

            print()
            print("=" * 70)
            print("TOP LEVEL KEYS")
            print("=" * 70)

            print(list(data.keys()))

            props = data.get("props", {})

            print()
            print("PROPS KEYS:")
            print(list(props.keys()))

            app_page_props = props.get("appPageProps", {})

            print()
            print("APP PAGE PROPS KEYS:")
            print(list(app_page_props.keys()))

            page_data = app_page_props.get("data", {})

            print()
            print("DATA KEYS:")
            print(list(page_data.keys()))

            content = page_data.get("content", {})

            print()
            print("CONTENT TYPE:")
            print(type(content).__name__)

            if isinstance(content, dict):

                print()
                print("CONTENT KEYS:")
                print(list(content.keys()))

            return data

        except Exception as e:

            print()
            print("ERROR:", e)

            return None

        finally:

            browser.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    data = fetch_match_data()

    print()

    if data is None:

        print("=" * 70)
        print("MATCH FETCH FAILED")
        print("=" * 70)

    else:

        print("=" * 70)
        print("MATCH FETCH COMPLETED")
        print("=" * 70)
