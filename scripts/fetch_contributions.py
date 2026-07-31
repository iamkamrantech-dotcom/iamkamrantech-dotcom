#!/usr/bin/env python3
"""
fetch_contributions.py
----------------------
GitHub ka public contribution calendar scrape karta hai (koi token / API key nahi chahiye)
aur data/contributions.json me save karta hai.

Usage:
    python scripts/fetch_contributions.py
    python scripts/fetch_contributions.py --user SOME_OTHER_USERNAME
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------------
# YAHAN APNA GITHUB USERNAME LIKHO
# ----------------------------------------------------------------------------
USERNAME = "iamkamrantech-dotcom"

OUT_PATH = os.path.join("data", "contributions.json")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; profile-art-bot/1.0)",
    "Accept": "text/html",
}


def fetch_html(user: str) -> str:
    url = f"https://github.com/users/{user}/contributions"
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 404:
        sys.exit(f"[x] Username '{user}' nahi mila (404). Spelling check karo.")
    r.raise_for_status()
    return r.text


def parse(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # 1) tooltip map: cell-id -> contribution count
    counts = {}
    for tip in soup.select("tool-tip"):
        target = tip.get("for")
        if not target:
            continue
        m = re.search(r"([\d,]+)\s+contribution", tip.get_text(strip=True))
        counts[target] = int(m.group(1).replace(",", "")) if m else 0

    # 2) har din ka cell
    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        if not date:
            continue  # khaali padding cell
        days.append(
            {
                "date": date,
                "level": int(td.get("data-level") or 0),
                "count": counts.get(td.get("id"), 0),
            }
        )

    days.sort(key=lambda d: d["date"])

    # 3) total (h2 heading me hota hai)
    total = sum(d["count"] for d in days)
    h2 = soup.find("h2")
    if h2:
        m = re.search(r"([\d,]+)\s+contribution", h2.get_text(" ", strip=True))
        if m:
            total = int(m.group(1).replace(",", ""))

    return days, total


def streaks(days):
    """Current streak aur longest streak nikaalo."""
    longest = cur = 0
    for d in days:
        if d["count"] > 0:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0

    # current streak: aaj (ya kal) se peeche ki taraf ginte hain
    current = 0
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        elif current == 0 and d is days[-1]:
            continue  # aaj abhi 0 hai to bhi streak toota hua nahi mante
        else:
            break
    return current, longest


def monthly(days):
    out = {}
    for d in days:
        key = d["date"][:7]  # YYYY-MM
        out[key] = out.get(key, 0) + d["count"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GH_USERNAME", USERNAME))
    args = ap.parse_args()

    print(f"[*] Fetching contributions for @{args.user} ...")
    days, total = parse(fetch_html(args.user))
    if not days:
        sys.exit("[x] Koi day cell nahi mila. GitHub ne HTML badal diya ho sakta hai.")

    cur, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])

    payload = {
        "username": args.user,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "total": total,
        "days": days,
        "stats": {
            "current_streak": cur,
            "longest_streak": longest,
            "best_day": best["date"],
            "best_day_count": best["count"],
            "active_days": sum(1 for d in days if d["count"] > 0),
            "monthly": monthly(days),
        },
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"[+] {len(days)} din save hue -> {OUT_PATH}")
    print(f"    total={total}  current_streak={cur}  longest_streak={longest}")


if __name__ == "__main__":
    main()
