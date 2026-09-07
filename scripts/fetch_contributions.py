"""
Fetch the public GitHub contribution calendar for munazimbhat.

Output:
    data/contributions.json

No GitHub token is required.
"""

import json
import os
import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


USERNAME = "munazimbhat"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "contributions.json")

URL = f"https://github.com/users/{USERNAME}/contributions"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


def extract_count(text):
    """
    Extract a contribution count from text such as:

        "2 contributions on September 7th"
        "1 contribution on May 1st"
        "No contributions on June 3rd"
    """

    if not text:
        return 0

    match = re.search(
        r"(\d[\d,]*)\s+contribution",
        text,
        re.IGNORECASE,
    )

    if match:
        return int(match.group(1).replace(",", ""))

    return 0


def main():
    print(f"fetching {URL}")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # GitHub's contribution cells.
    cells = soup.select(
        ".ContributionCalendar-day[data-date][data-level]"
    )

    if not cells:
        # Fallback if GitHub changes the class name.
        cells = soup.select("[data-date][data-level]")

    if not cells:
        raise RuntimeError(
            "Could not find GitHub contribution cells. "
            "GitHub may have changed its page structure."
        )

    # GitHub stores the readable contribution count in <tool-tip>
    # elements associated with each cell's id.
    tooltips = {}

    for tooltip in soup.select("tool-tip[for]"):
        target = tooltip.get("for")
        text = tooltip.get_text(" ", strip=True)

        if target:
            tooltips[target] = text

    contributions = []

    for cell in cells:
        date = cell.get("data-date")

        if not date:
            continue

        level = int(cell.get("data-level") or 0)

        cell_id = cell.get("id")

        # Try several places in order.
        label = cell.get("aria-label", "")

        if not label:
            label = cell.get("title", "")

        if not label and cell_id:
            label = tooltips.get(cell_id, "")

        count = extract_count(label)

        contributions.append(
            {
                "date": date,
                "count": count,
                "level": level,
            }
        )

    # Remove duplicate dates.
    unique = {}

    for item in contributions:
        unique[item["date"]] = item

    contributions = list(unique.values())

    contributions.sort(key=lambda x: x["date"])

    # GitHub's page heading contains the authoritative yearly total.
    page_text = soup.get_text(" ", strip=True)

    total_match = re.search(
        r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year",
        page_text,
        re.IGNORECASE,
    )

    if total_match:
        page_total = int(total_match.group(1).replace(",", ""))
    else:
        page_total = sum(
            item["count"] for item in contributions
        )

    output = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": page_total,
        "contributions": contributions,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    parsed_total = sum(
        item["count"] for item in contributions
    )

    print(f"wrote {OUT}")
    print(f"days: {len(contributions)}")
    print(f"parsed daily total: {parsed_total}")
    print(f"github total: {page_total}")
    print(f"tooltips found: {len(tooltips)}")


if __name__ == "__main__":
    main()
