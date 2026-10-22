"""Subprocess-level CLI and historical data acceptance tests."""

import csv
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATCHES = ROOT / "data" / "1974_75_week10_matches.csv"
EXPECTED = ROOT / "data" / "1974_75_week10_standings.csv"
SOURCE = ROOT / "data" / "fixtures_source.txt"


def invoke(*args, input_text=None):
    return subprocess.run(
        [sys.executable, "-m", "football_standings", *map(str, args)],
        input=input_text, text=True, capture_output=True, cwd=ROOT, check=False,
    )


class CliTests(unittest.TestCase):
    def test_historical_standings_match_committed_golden_file(self):
        result = invoke("--input", MATCHES, "--as-of", "1974-09-28")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, EXPECTED.read_text(encoding="utf-8"))
        self.assertEqual(result.stderr, "")

    def test_historical_invariants(self):
        with MATCHES.open(encoding="utf-8", newline="") as handle:
            match_rows = list(csv.DictReader(handle))
        with EXPECTED.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(match_rows), 107)
        self.assertEqual(len(rows), 22)
        self.assertEqual(sum(int(row["played"]) for row in rows), 214)
        self.assertEqual(sum(int(row["won"]) for row in rows), sum(int(row["lost"]) for row in rows))
        self.assertEqual(sum(int(row["goals_for"]) for row in rows), sum(int(row["goals_against"]) for row in rows))
        self.assertEqual((rows[0]["team"], rows[0]["points"]), ("Ipswich Town", "16"))
        self.assertEqual(rows[-1]["team"], "Queens Park Rangers")
        self.assertTrue(all(row["date"] <= "1974-09-28" for row in match_rows))

    def test_published_fixture_results_are_in_input(self):
        # Independently listed at https://uflc.co.uk/results/1974-75
        uflc_results = {
            ("1974-08-17", "Leicester City", "Arsenal", "0", "1"),
            ("1974-08-20", "Arsenal", "Ipswich Town", "0", "1"),
            ("1974-08-24", "Ipswich Town", "Burnley", "2", "0"),
            ("1974-08-27", "Ipswich Town", "Arsenal", "3", "0"),
            ("1974-08-31", "Sheffield United", "Ipswich Town", "3", "1"),
            ("1974-09-07", "West Ham United", "Sheffield United", "1", "2"),
            ("1974-09-14", "Sheffield United", "Middlesbrough", "1", "0"),
            ("1974-09-21", "Leeds United", "Sheffield United", "5", "1"),
            ("1974-09-28", "Everton", "Leeds United", "3", "2"),
        }
        # Round 10 at https://www.bdfutbol.com/en/t/teng1974-75.html
        round_ten_results = {
            ("1974-09-28", "Everton", "Leeds United", "3", "2"),
            ("1974-09-28", "Leicester City", "Coventry City", "0", "1"),
            ("1974-09-28", "Newcastle United", "Ipswich Town", "1", "0"),
            ("1974-09-28", "Tottenham Hotspur", "Middlesbrough", "1", "2"),
            ("1974-09-28", "Birmingham City", "Arsenal", "3", "1"),
            ("1974-09-28", "Stoke City", "Derby County", "1", "1"),
            ("1974-09-28", "Sheffield United", "Liverpool", "1", "0"),
            ("1974-09-28", "Manchester City", "Queens Park Rangers", "1", "0"),
            ("1974-09-28", "Luton Town", "Carlisle United", "3", "1"),
            ("1974-09-28", "Chelsea", "Wolverhampton Wanderers", "0", "1"),
            ("1974-09-28", "Burnley", "West Ham United", "3", "5"),
        }
        with MATCHES.open(encoding="utf-8", newline="") as handle:
            fixtures = {
                (row["date"], row["home_team"], row["away_team"], row["home_goals"], row["away_goals"])
                for row in csv.DictReader(handle)
            }
        self.assertTrue(uflc_results <= fixtures)
        self.assertEqual({row for row in fixtures if row[0] == "1974-09-28"}, round_ten_results)

    def test_postponed_round_nine_fixtures_are_excluded(self):
        # BDFutbol lists 11 fixtures in each of rounds 1-10, including these late games.
        source_rows = [line.split("|") for line in SOURCE.read_text(encoding="utf-8").splitlines()
                       if line and not line.startswith("#")]
        self.assertEqual(Counter(int(row[0]) for row in source_rows),
                         Counter({round_number: 11 for round_number in range(1, 11)}))
        postponed = {tuple(row) for row in source_rows if row[1] > "1974-09-28"}
        self.assertEqual(postponed, {
            ("9", "1974-12-04", "Leeds", "2", "1", "Tottenham"),
            ("9", "1974-12-10", "Middlesbrough", "3", "0", "Leicester"),
            ("9", "1975-04-23", "Newcastle", "3", "1", "Arsenal"),
        })
        with MATCHES.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(len(list(csv.DictReader(handle))), len(source_rows) - len(postponed))

    def test_standings_against_independent_september_28_table(self):
        # P/W/D/L/GF/GA/Pts from https://www.lfchistory.net/games/818
        # Wolves is expanded; Arsenal and Tottenham are ranked by exact goal average.
        reference = """\
Ipswich Town|10|8|0|2|18|6|16
Manchester City|10|6|2|2|14|11|14
Liverpool|10|6|1|3|17|8|13
Everton|10|4|5|1|14|11|13
Sheffield United|10|5|3|2|14|14|13
Newcastle United|9|5|2|2|16|13|12
Middlesbrough|9|4|3|2|12|7|11
Derby County|10|3|5|2|16|13|11
Stoke City|10|4|3|3|13|11|11
Wolverhampton Wanderers|10|3|5|2|12|11|11
Carlisle United|10|4|2|4|8|8|10
West Ham United|10|4|1|5|20|18|9
Burnley|10|4|1|5|17|18|9
Birmingham City|10|3|2|5|12|17|8
Coventry City|10|2|4|4|11|17|8
Leicester City|9|2|3|4|13|17|7
Luton Town|10|1|5|4|11|16|7
Chelsea|10|2|3|5|10|18|7
Leeds United|9|2|2|5|12|14|6
Arsenal|9|2|2|5|9|12|6
Tottenham Hotspur|9|3|0|6|11|15|6
Queens Park Rangers|10|1|4|5|8|13|6
"""
        expected_rows = [tuple(line.split("|")) for line in reference.splitlines()]
        with EXPECTED.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        actual_rows = [tuple(row[column] for column in
                             ("team", "played", "won", "drawn", "lost", "goals_for", "goals_against", "points"))
                       for row in rows]
        self.assertEqual(actual_rows, expected_rows)
        self.assertEqual([row["position"] for row in rows], [str(i) for i in range(1, 23)])

    def test_stdin_stdout(self):
        contents = "date,home_team,away_team,home_goals,away_goals\n1974-09-28,A,B,2,0\n"
        result = invoke(input_text=contents)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1,A,1,1,0,0,2,0,INF,2", result.stdout)

    def test_four_hundred_digit_score_produces_complete_csv(self):
        huge = "9" * 400
        contents = (
            "date,home_team,away_team,home_goals,away_goals\n"
            f"1974-09-28,A,B,{huge},1\n"
        )
        result = invoke(input_text=contents)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        rows = list(csv.DictReader(result.stdout.splitlines()))
        self.assertEqual(len(rows), 2)
        self.assertEqual((rows[0]["team"], rows[0]["goal_average"]), ("A", f"{huge}.000"))
        self.assertEqual(rows[1]["team"], "B")

    def test_can_write_to_named_output_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "table.csv"
            result = invoke("--input", MATCHES, "--output", target)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(target.read_bytes(), EXPECTED.read_bytes())
            self.assertEqual(result.stdout, "")

    def test_invalid_data_uses_nonzero_exit_and_stderr(self):
        result = invoke(input_text="date,home_team,away_team,home_goals,away_goals\n1974-09-28,A,B,-1,2\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("line 2", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_failure_does_not_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "table.csv"
            source = Path(directory) / "bad.csv"
            output.write_text("previous result", encoding="utf-8")
            source.write_text("not,a,valid,header\n", encoding="utf-8")
            result = invoke("--input", source, "--output", output)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_text(encoding="utf-8"), "previous result")

    def test_missing_input_file_returns_error(self):
        result = invoke("--input", "no-such-file.csv")
        self.assertEqual(result.returncode, 2)
        self.assertIn("error:", result.stderr)

    def test_invalid_as_of_date_returns_error(self):
        result = invoke("--input", MATCHES, "--as-of", "1974-02-31")
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid calendar date", result.stderr)

    def test_help_exits_successfully(self):
        result = invoke("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--as-of", result.stdout)


if __name__ == "__main__":
    unittest.main()
