"""CSV parsing and formatting, with useful row-level errors."""

from __future__ import annotations

import csv
import re
from datetime import date
from typing import TextIO

from .core import Match, Standing


INPUT_COLUMNS = ("date", "home_team", "away_team", "home_goals", "away_goals")
OUTPUT_COLUMNS = (
    "position", "team", "played", "won", "drawn", "lost",
    "goals_for", "goals_against", "goal_average", "points",
)


class InputError(ValueError):
    """Invalid CSV file or unparseable match data."""


def parse_iso_date(value: str, *, context: str = "date") -> date:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise InputError(f"{context}: expected YYYY-MM-DD, got {value!r}")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f"{context}: invalid calendar date {value!r}") from exc


def _nonnegative_int(value: str, *, context: str) -> int:
    if not re.fullmatch(r"\d+", value):
        raise InputError(f"{context}: expected a non-negative integer, got {value!r}")
    try:
        return int(value)
    except ValueError as exc:
        raise InputError(f"{context}: integer is too large to parse") from exc


def read_matches(source: TextIO, *, as_of: date | None = None) -> list[Match]:
    try:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise InputError("input CSV is empty; expected a header row")
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        if len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise InputError("input CSV contains duplicate column names")
        missing = sorted(set(INPUT_COLUMNS) - set(reader.fieldnames))
        if missing:
            raise InputError(f"missing required CSV columns: {', '.join(missing)}")

        matches: list[Match] = []
        seen: set[tuple[date, str, str]] = set()
        canonical_names: dict[str, str] = {}
        for row in reader:
            line = reader.line_num
            if None in row:
                raise InputError(f"line {line}: too many CSV fields")
            if any(value is None for value in row.values()):
                raise InputError(f"line {line}: missing CSV fields")
            cells = {key: value.strip() for key, value in row.items()}
            played_on = parse_iso_date(cells["date"], context=f"line {line} date")
            home = cells["home_team"]
            away = cells["away_team"]
            if not home or not away:
                raise InputError(f"line {line}: team names cannot be empty")
            if home.casefold() == away.casefold():
                raise InputError(f"line {line}: a team cannot play itself")
            for team in (home, away):
                previous = canonical_names.setdefault(team.casefold(), team)
                if previous != team:
                    raise InputError(
                        f"line {line}: inconsistent spelling/casing for team {team!r}; "
                        f"previously {previous!r}"
                    )
            home_goals = _nonnegative_int(cells["home_goals"], context=f"line {line} home_goals")
            away_goals = _nonnegative_int(cells["away_goals"], context=f"line {line} away_goals")
            key = (played_on, home.casefold(), away.casefold())
            if key in seen:
                raise InputError(f"line {line}: duplicate fixture {played_on} {home} vs {away}")
            seen.add(key)
            if as_of is None or played_on <= as_of:
                matches.append(Match(played_on, home, away, home_goals, away_goals))
    except csv.Error as exc:
        raise InputError(f"malformed CSV: {exc}") from exc
    if not matches:
        raise InputError("no completed matches found for the selected date range")
    return matches


def write_standings(destination: TextIO, table: list[Standing]) -> None:
    writer = csv.writer(destination, lineterminator="\n")
    writer.writerow(OUTPUT_COLUMNS)
    for position, row in enumerate(table, 1):
        writer.writerow((
            position, row.team, row.played, row.won, row.drawn, row.lost,
            row.goals_for, row.goals_against, row.goal_average, row.points,
        ))
