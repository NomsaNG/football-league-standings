"""Pure football standings calculations; no file I/O or network dependency."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from typing import Iterable


POINTS_FOR_WIN = 2
POINTS_FOR_DRAW = 1


@dataclass(frozen=True, slots=True)
class Match:
    played_on: date
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int


@dataclass(slots=True)
class Standing:
    team: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def points(self) -> int:
        return self.won * POINTS_FOR_WIN + self.drawn * POINTS_FOR_DRAW

    @property
    def goal_average(self) -> str:
        """A display-only value. Rankings use exact fractions, never rounded text."""
        if self.goals_against == 0:
            return "INF" if self.goals_for > 0 else "1.000"
        whole, remainder = divmod(self.goals_for, self.goals_against)
        thousandths, remainder = divmod(remainder * 1000, self.goals_against)
        # Match fixed-point round-to-even formatting without converting to float.
        if 2 * remainder > self.goals_against or (
            2 * remainder == self.goals_against and thousandths % 2
        ):
            thousandths += 1
        if thousandths == 1000:
            whole += 1
            thousandths = 0
        return f"{whole}.{thousandths:03d}"

    def goal_average_sort_key(self) -> tuple[int, Fraction]:
        """Represent nonzero-goals/zero-conceded as greater than finite ratios.

        A 0-0 aggregate is treated as a neutral average of 1.0. This is an
        explicitly documented convention for the mathematically undefined case.
        """
        if self.goals_against == 0:
            return (1, Fraction(0)) if self.goals_for > 0 else (0, Fraction(1))
        return (0, Fraction(self.goals_for, self.goals_against))


def calculate_standings(matches: Iterable[Match]) -> list[Standing]:
    """Rank by 1974/75 rules: points, goal average, goals scored.

    An alphabetical fallback makes otherwise exact ties deterministic.
    All supplied matches are treated as played league fixtures.
    """
    by_team: dict[str, Standing] = {}
    for match in matches:
        home = by_team.setdefault(match.home_team, Standing(match.home_team))
        away = by_team.setdefault(match.away_team, Standing(match.away_team))
        home.played += 1
        away.played += 1
        home.goals_for += match.home_goals
        home.goals_against += match.away_goals
        away.goals_for += match.away_goals
        away.goals_against += match.home_goals
        if match.home_goals > match.away_goals:
            home.won += 1
            away.lost += 1
        elif match.home_goals < match.away_goals:
            away.won += 1
            home.lost += 1
        else:
            home.drawn += 1
            away.drawn += 1

    ranked = sorted(by_team.values(), key=lambda s: s.team.casefold())
    # Python's stable sort retains alphabetical order for exact ties.
    ranked.sort(
        key=lambda s: (s.points, *s.goal_average_sort_key(), s.goals_for),
        reverse=True,
    )
    return ranked
