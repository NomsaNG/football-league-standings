"""Validation tests for reading and writing standards-compliant CSV."""

import csv
import io
import unittest
from datetime import date

from football_standings.core import calculate_standings
from football_standings.csv_io import InputError, parse_iso_date, read_matches, write_standings

HEADER = "date,home_team,away_team,home_goals,away_goals\n"


class ReadCsvTests(unittest.TestCase):
    def test_quoted_team_names_with_commas(self):
        sample = HEADER + '1974-09-28,"A, FC",B,3,2\n'
        row = read_matches(io.StringIO(sample))[0]
        self.assertEqual((row.home_team, row.home_goals), ("A, FC", 3))

    def test_csv_columns_may_arrive_out_of_order_with_extras(self):
        sample = "away_goals,round,home_goals,away_team,date,home_team\n0,10,3,B,1974-09-28,A\n"
        self.assertEqual(read_matches(io.StringIO(sample))[0].home_goals, 3)

    def test_as_of_excludes_postponed_fixtures(self):
        sample = HEADER + "1974-09-28,A,B,2,0\n1974-12-04,C,D,1,1\n"
        rows = read_matches(io.StringIO(sample), as_of=date(1974, 9, 28))
        self.assertEqual([row.home_team for row in rows], ["A"])

    def test_invalid_date_format_or_calendar_date(self):
        for value in ("28/09/1974", "1974-02-30", "1974-9-28"):
            with self.subTest(value=value), self.assertRaises(InputError):
                parse_iso_date(value)

    def test_bad_scores_rejected(self):
        for value in ("-1", "two", "2.0", "", "+1"):
            with self.subTest(value=value), self.assertRaises(InputError):
                read_matches(io.StringIO(HEADER + f"1974-09-28,A,B,{value},0\n"))

    def test_missing_header(self):
        with self.assertRaisesRegex(InputError, "header"):
            read_matches(io.StringIO(""))

    def test_missing_columns(self):
        with self.assertRaisesRegex(InputError, "missing required"):
            read_matches(io.StringIO("home_team,home_goals\nA,1\n"))

    def test_duplicate_column_names(self):
        with self.assertRaisesRegex(InputError, "duplicate column"):
            read_matches(io.StringIO(HEADER.replace("date,", "date,date,")))

    def test_missing_or_extra_fields(self):
        for row in ("1974-09-28,A,B,2\n", "1974-09-28,A,B,2,0,EXTRA\n"):
            with self.subTest(row=row), self.assertRaises(InputError):
                read_matches(io.StringIO(HEADER + row))

    def test_empty_team_or_self_fixture(self):
        for row in ("1974-09-28,,B,2,0\n", "1974-09-28,A,a,2,0\n"):
            with self.subTest(row=row), self.assertRaises(InputError):
                read_matches(io.StringIO(HEADER + row))

    def test_inconsistent_team_casing_is_rejected_instead_of_creating_two_clubs(self):
        sample = HEADER + "1974-09-21,Arsenal,Chelsea,2,0\n1974-09-28,ARSENAL,Everton,1,1\n"
        with self.assertRaisesRegex(InputError, "inconsistent spelling/casing"):
            read_matches(io.StringIO(sample))

    def test_enormous_score_returns_useful_error(self):
        sample = HEADER + f"1974-09-28,A,B,{'1' * 5000},0\n"
        with self.assertRaisesRegex(InputError, "integer is too large"):
            read_matches(io.StringIO(sample))

    def test_duplicate_fixture_rejected_even_if_score_changes(self):
        csv_text = HEADER + "1974-09-28,A,B,2,0\n1974-09-28,A,B,3,0\n"
        with self.assertRaisesRegex(InputError, "duplicate fixture"):
            read_matches(io.StringIO(csv_text))

    def test_empty_selected_date_range_fails(self):
        sample = HEADER + "1974-09-28,A,B,1,0\n"
        with self.assertRaisesRegex(InputError, "no completed matches"):
            read_matches(io.StringIO(sample), as_of=date(1974, 9, 27))

    def test_write_csv_roundtrip(self):
        source = HEADER + '1974-09-28,"A, FC",B,2,1\n'
        table = calculate_standings(read_matches(io.StringIO(source)))
        output = io.StringIO()
        write_standings(output, table)
        rows = list(csv.DictReader(io.StringIO(output.getvalue())))
        self.assertEqual(rows[0]["team"], "A, FC")
        self.assertEqual(rows[0]["points"], "2")
        self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
