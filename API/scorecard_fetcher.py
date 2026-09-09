import json
import time
from pathlib import Path

import requests


# ============================================================
# CONFIGURATION
# ============================================================

SERIES_ID = "1510976"

MAX_RETRIES = 5
RETRY_DELAY = 2


# ============================================================
# SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0"
})


# ============================================================
# BUILD BASE URL
# ============================================================

def get_base_url(match_id):

    return (
        f"http://core.espnuk.org/v2/sports/cricket/"
        f"leagues/{SERIES_ID}/events/{match_id}/"
        f"competitions/{match_id}/details"
    )


# ============================================================
# FETCH SCORECARD INDEX PAGE
# ============================================================

def fetch_index_page(
    match_id,
    page_number=1
):

    base_url = get_base_url(
        match_id
    )

    url = base_url

    if page_number > 1:

        url = (
            f"{base_url}"
            f"?page={page_number}"
        )

    print()
    print(
        f"Fetching index page "
        f"{page_number}..."
    )

    print(url)

    response = session.get(
        url,
        timeout=30
    )

    print(
        "HTTP STATUS:",
        response.status_code
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# FETCH INDIVIDUAL DETAIL WITH RETRIES
# ============================================================

def fetch_detail(detail_url):

    detail_id = (
        detail_url
        .rstrip("/")
        .split("/")[-1]
    )

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            response = session.get(
                detail_url,
                timeout=30
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:

            print(
                f"  Attempt "
                f"{attempt}/{MAX_RETRIES} "
                f"failed for {detail_id}: {e}"
            )

            if attempt < MAX_RETRIES:

                print(
                    f"  Waiting "
                    f"{RETRY_DELAY} seconds "
                    f"before retry..."
                )

                time.sleep(
                    RETRY_DELAY
                )

    print(
        f"  FAILED permanently: "
        f"{detail_id}"
    )

    return None


# ============================================================
# FETCH ALL DETAILS
# ============================================================

def fetch_all_details(
    match_id,
    save_file=True
):

    print()
    print("=" * 70)
    print("ESPN NPL SCORECARD FETCHER")
    print("=" * 70)

    print()
    print(
        "SERIES ID:",
        SERIES_ID
    )

    print(
        "MATCH ID:",
        match_id
    )

    # --------------------------------------------------------
    # FIRST PAGE
    # --------------------------------------------------------

    first_page = fetch_index_page(
        match_id,
        1
    )

    total_details = first_page.get(
        "count",
        0
    )

    page_count = first_page.get(
        "pageCount",
        1
    )

    print()
    print(
        "TOTAL DETAILS:",
        total_details
    )

    print(
        "PAGE COUNT:",
        page_count
    )

    # --------------------------------------------------------
    # COLLECT ALL DETAIL REFERENCES
    # --------------------------------------------------------

    detail_refs = []

    for page_number in range(
        1,
        page_count + 1
    ):

        if page_number == 1:

            page_data = first_page

        else:

            page_data = fetch_index_page(
                match_id,
                page_number
            )

        items = page_data.get(
            "items",
            []
        )

        print(
            f"Page {page_number}: "
            f"{len(items)} "
            f"detail references"
        )

        for item in items:

            detail_url = item.get(
                "$ref"
            )

            if detail_url:

                detail_refs.append(
                    detail_url
                )

    print()
    print("=" * 70)
    print("DETAIL REFERENCES COLLECTED")
    print("=" * 70)

    print(
        "TOTAL REFERENCES:",
        len(detail_refs)
    )

    # --------------------------------------------------------
    # FETCH EVERY DETAIL
    # --------------------------------------------------------

    details = []

    failed_refs = []

    for index, detail_url in enumerate(
        detail_refs,
        start=1
    ):

        detail_id = (
            detail_url
            .rstrip("/")
            .split("/")[-1]
        )

        print(
            f"Fetching detail "
            f"{index}/"
            f"{len(detail_refs)}... "
            f"{detail_id}"
        )

        detail = fetch_detail(
            detail_url
        )

        if detail is not None:

            details.append(
                detail
            )

        else:

            failed_refs.append(
                detail_url
            )

    # --------------------------------------------------------
    # RETRY FAILED REFERENCES ONE MORE ROUND
    # --------------------------------------------------------

    if failed_refs:

        print()
        print("=" * 70)
        print("SECOND RETRY ROUND")
        print("=" * 70)

        remaining_failed = []

        for detail_url in failed_refs:

            detail_id = (
                detail_url
                .rstrip("/")
                .split("/")[-1]
            )

            print(
                f"Retrying failed "
                f"detail: {detail_id}"
            )

            time.sleep(
                RETRY_DELAY
            )

            detail = fetch_detail(
                detail_url
            )

            if detail is not None:

                details.append(
                    detail
                )

            else:

                remaining_failed.append(
                    detail_url
                )

        failed_refs = remaining_failed

    # --------------------------------------------------------
    # SORT DETAILS
    # --------------------------------------------------------

    details.sort(
        key=lambda x: (
            x.get("period", 0),
            x.get("sequence", 0)
        )
    )

    # --------------------------------------------------------
    # BUILD OUTPUT
    # --------------------------------------------------------

    output = {

        "series_id": SERIES_ID,

        "match_id": match_id,

        "total_details": total_details,

        "fetched_details": len(
            details
        ),

        "failed_details": len(
            failed_refs
        ),

        "failed_refs": failed_refs,

        "details": details

    }

    # --------------------------------------------------------
    # SAVE DATA
    # --------------------------------------------------------

    if save_file:

        data_file = (
            Path(__file__).parent
            / f"scorecard_{match_id}_raw.json"
        )

        with open(
            data_file,
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
            "Saved raw details to:"
        )

        print(
            data_file
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("FETCH COMPLETED")
    print("=" * 70)

    print()
    print(
        "EXPECTED DETAILS:",
        total_details
    )

    print(
        "FETCHED DETAILS:",
        len(details)
    )

    print(
        "FAILED DETAILS:",
        len(failed_refs)
    )

    if len(details) == total_details:

        print()
        print(
            "SUCCESS: "
            "ALL DETAILS FETCHED."
        )

    else:

        print()
        print(
            "WARNING: "
            "SOME DETAILS WERE NOT FETCHED."
        )

        print()
        print(
            "FAILED DETAIL REFERENCES:"
        )

        for ref in failed_refs:

            print(ref)

    return output


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # Test the first NPL match
    fetch_all_details(
        "1510977"
    )