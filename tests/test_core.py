"""Focused tests for 1974/75 league rules and numerical ordering."""

import unittest
from datetime import date

from football_standings.core import Match, calculate_standings


TODAY = date(1974, 9, 28)


def match(home, away, hg, ag):
    return Match(TODAY, home, away, hg, ag)


class StandingsRulesTests(unittest.TestCase):
    def test_home_win_awards_two_points_and_loss_zero(self):
        home, away = calculate_standings([match("A", "B", 2, 1)])
        self.assertEqual((home.team, home.played, home.won, home.points), ("A", 1, 1, 2))
        self.assertEqual((away.team, away.lost, away.points), ("B", 1, 0))
        self.assertEqual(home.goal_average, "2.000")

    def test_away_win_is_recorded_correctly(self):
        first, last = calculate_standings([match("Home", "Away", 0, 2)])
        self.assertEqual((first.team, first.won, first.goals_for), ("Away", 1, 2))
        self.assertEqual((last.team, last.lost, last.goals_against), ("Home", 1, 2))

    def test_draw_awards_one_point_each(self):
        rows = calculate_standings([match("A", "B", 2, 2)])
        self.assertEqual({row.points for row in rows}, {1})
        self.assertEqual({row.drawn for row in rows}, {1})

    def test_points_take_precedence_over_goal_average(self):
        rows = calculate_standings([
            match("A", "B", 1, 0),  # A: 2 pts, average infinity
            match("C", "A", 2, 0),  # A: 2 pts, average 0.5
            match("D", "C", 0, 0),  # D: 1 pt, average 1.0
        ])
        teams = [s.team for s in rows]
        self.assertLess(teams.index("A"), teams.index("D"))

    def test_goal_average_not_goal_difference(self):
        # A's GD +1 and goal average 2; B's GD +2 but average 1.5.
        # Both have 2 pts, so 1974/75 rules rank A above B.
        rows = calculate_standings([
            match("A", "C", 2, 1),
            match("B", "D", 6, 4),
        ])
        self.assertEqual([s.team for s in rows[:2]], ["A", "B"])

    def test_goals_scored_breaks_exact_goal_average_tie(self):
        rows = calculate_standings([
            match("A", "C", 2, 2),
            match("B", "D", 1, 1),
        ])
        self.assertLess([s.team for s in rows].index("A"), [s.team for s in rows].index("B"))

    def test_equal_ratios_do_not_depend_on_display_rounding(self):
        rows = calculate_standings([
            match("A", "C", 2, 6),
            match("B", "D", 1, 3),
        ])
        # 2/6 and 1/3 are equal ratios; goals scored breaks the tie.
        self.assertLess([s.team for s in rows].index("A"), [s.team for s in rows].index("B"))

    def test_different_ratios_with_identical_display_rank_exactly(self):
        rows = calculate_standings([
            match("A", "C", 1000, 999),
            match("B", "D", 1001, 1000),
        ])
        # Both display as 1.001, but 1000/999 exceeds 1001/1000.
        self.assertEqual([s.team for s in rows[:2]], ["A", "B"])
        self.assertEqual([s.goal_average for s in rows[:2]], ["1.001", "1.001"])

    def test_four_hundred_digit_goal_average_formats_without_float(self):
        huge = int("9" * 400)
        rows = calculate_standings([match("A", "B", huge, 1)])
        self.assertEqual(rows[0].goal_average, f"{huge}.000")
        self.assertEqual(rows[1].goal_average, "0.000")

    def test_goal_average_rounds_half_even_and_carries(self):
        rows = calculate_standings([
            match("A", "B", 2001, 2000),
            match("C", "D", 2003, 2000),
            match("E", "F", 1999, 2000),
        ])
        averages = {row.team: row.goal_average for row in rows}
        self.assertEqual(averages["A"], "1.000")
        self.assertEqual(averages["C"], "1.002")
        self.assertEqual(averages["E"], "1.000")

    def test_zero_against_positive_for_uses_infinite_average(self):
        rows = calculate_standings([match("Alpha", "Beta", int("9" * 400), 0)])
        self.assertEqual(rows[0].goal_average, "INF")
        self.assertEqual(rows[1].goal_average, "0.000")

    def test_zero_zero_average_has_documented_neutral_fallback(self):
        rows = calculate_standings([match("A", "B", 0, 0)])
        self.assertEqual([s.team for s in rows], ["A", "B"])
        self.assertEqual([s.goal_average for s in rows], ["1.000", "1.000"])

    def test_repeated_matches_aggregate_correctly(self):
        rows = calculate_standings([
            match("A", "B", 1, 0),
            match("B", "A", 2, 2),
        ])
        a = next(s for s in rows if s.team == "A")
        b = next(s for s in rows if s.team == "B")
        self.assertEqual((a.played, a.won, a.drawn, a.lost, a.points), (2, 1, 1, 0, 3))
        self.assertEqual((b.played, b.won, b.drawn, b.lost, b.points), (2, 0, 1, 1, 1))

    def test_no_matches_returns_empty_table(self):
        self.assertEqual(calculate_standings([]), [])


if __name__ == "__main__":
    unittest.main()
