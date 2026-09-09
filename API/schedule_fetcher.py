import json
from pathlib import Path

from playwright.sync_api import sync_playwright


# ============================================================
# CONFIGURATION
# ============================================================

ESPN_SCHEDULE_URL = (
    "https://www.espncricinfo.com/series/"
    "nepal-premier-league-2025-26-1510976/"
    "match-schedule-fixtures-and-results"
)

DATA_FILE = Path(__file__).parent / "schedule_data.json"


# ============================================================
# FETCH ESPN SCHEDULE PAGE
# ============================================================

def fetch_schedule_data():
    print()
    print("=" * 70)
    print("FETCHING NPL SCHEDULE FROM ESPNCRICINFO")
    print("=" * 70)

    print()
    print("URL:")
    print(ESPN_SCHEDULE_URL)

    with sync_playwright() as p:

        browser = p.webkit.launch(headless=True)

        page = browser.new_page()

        try:

            response = page.goto(
                ESPN_SCHEDULE_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            if response:
                print()
                print("HTTP STATUS:", response.status)

            print("Page loaded.")

            # Give ESPN time to finish loading the page
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
            print("SUCCESS: ESPN schedule data extracted.")

            # ------------------------------------------------
            # Check that the expected schedule structure exists
            # ------------------------------------------------

            try:

                matches = (
                    data["props"]
                    ["appPageProps"]
                    ["data"]
                    ["content"]
                    ["matches"]
                )

            except (KeyError, TypeError):

                print()
                print("ERROR: Expected 'matches' data was not found.")

                return None

            print("Matches found:", len(matches))

            # ------------------------------------------------
            # Save JSON
            # ------------------------------------------------

            with open(DATA_FILE, "w", encoding="utf-8") as f:

                json.dump(
                    data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            print()
            print("Saved schedule data to:")

            print(DATA_FILE)

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

    data = fetch_schedule_data()

    print()

    if data is None:

        print("=" * 70)
        print("SCHEDULE FETCH FAILED")
        print("=" * 70)

    else:

        print("=" * 70)
        print("SCHEDULE FETCH COMPLETED")
        print("=" * 70)
