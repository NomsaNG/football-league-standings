"""Rebuild the committed week-10 CSV from the attributed source transcription.

Intentionally no network access or external dependencies required. Run from the
repository root: python3 scripts/prepare_historical_data.py
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "fixtures_source.txt"
DEST = ROOT / "data" / "1974_75_week10_matches.csv"
CUTOFF = date(1974, 9, 28)

TEAM_NAMES = {
    "Birmingham": "Birmingham City",
    "Carlisle": "Carlisle United",
    "Coventry": "Coventry City",
    "Leeds": "Leeds United",
    "Leicester": "Leicester City",
    "Luton": "Luton Town",
    "Newcastle": "Newcastle United",
    "Tottenham": "Tottenham Hotspur",
    "West Ham": "West Ham United",
    "Wolverhampton": "Wolverhampton Wanderers",
}


def main() -> None:
    included = []
    excluded = []
    rounds = Counter()
    for line_number, line in enumerate(SOURCE.read_text(encoding="utf-8").splitlines(), start=1):
        if not line or line.lstrip().startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) != 6:
            raise ValueError(f"source line {line_number}: expected 6 fields")
        round_number, day, home, hg, ag, away = parts
        if not 1 <= int(round_number) <= 10:
            raise ValueError(f"source line {line_number}: round beyond 10")
        rounds[int(round_number)] += 1
        home = TEAM_NAMES.get(home, home)
        away = TEAM_NAMES.get(away, away)
        row = (day, home, away, int(hg), int(ag))
        if date.fromisoformat(day) <= CUTOFF:
            included.append(row)
        else:
            excluded.append(row)

    # Independent safety checks against the historical round structure.
    assert rounds == Counter({**{n: 11 for n in range(1, 11)}}), rounds
    assert len(included) == 107, len(included)
    assert len(excluded) == 3, len(excluded)
    assert len({team for _, home, away, _, _ in included for team in (home, away)}) == 22
    included.sort()
    with DEST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("date", "home_team", "away_team", "home_goals", "away_goals"))
        writer.writerows(included)
    print(f"Wrote {len(included)} matches through {CUTOFF} to {DEST}")
    print("Excluded three postponed round-9 matches played in December 1974 and April 1975.")


if __name__ == "__main__":
    main()
