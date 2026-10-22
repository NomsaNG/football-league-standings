# Historical Football League Standings CLI

A zero-runtime-dependency Python 3.11+ command-line tool that calculates standings from football match results supplied as CSV. This repository includes a documented historical snapshot for the **English First Division, 1974/75, at the end of fixture round 10 (28 September 1974)**.

## Install and run on macOS

Install Python 3.11 or later if `python3 --version` reports an older release or Python is unavailable. Ensure `python3` resolves to that version; if your installation provides `python3.11` instead, use that command in the examples below. The calculator uses only the Python standard library and can run directly from the repository without installing a package.

```bash
cd /path/to/football-league-standings
python3 --version
python3 -m football_standings --help
python3 -m football_standings \
  --input data/1974_75_week10_matches.csv \
  --as-of 1974-09-28 \
  --output data/1974_75_week10_standings.csv
```

No API key or internet connection is needed to run or test the application. To install the optional console command into an active Python environment, run `python3 -m pip install -e .`; then use `football-standings` with the same options.

## Command-line options

```text
python3 -m football_standings [-i INPUT_CSV] [-o OUTPUT_CSV] [--as-of YYYY-MM-DD]
```

- `--input` / `-i`: input CSV filename; `-` means stdin (default)
- `--output` / `-o`: output CSV filename; `-` means stdout (default)
- `--as-of`: optionally ignore fixtures **played after** this inclusive date
- Exit code `0` on success; `2` for malformed CSV, invalid dates, missing files, or I/O errors. Errors go to stderr, so CSV output remains parseable on stdout.

### Stdin/stdout example

```bash
cat data/1974_75_week10_matches.csv | python3 -m football_standings > /tmp/standings.csv
```

The input CSV must have a header and one result per line:

```csv
date,home_team,away_team,home_goals,away_goals
1974-09-28,Everton,Leeds United,3,2
1974-09-28,Leicester City,Coventry City,0,1
```

Additional columns are accepted and ignored. Header order may vary; strings may use standard CSV quoting. Dates use ISO `YYYY-MM-DD`; scores must be nonnegative whole numbers. Duplicated fixtures, inconsistent team casing, invalid dates, incomplete rows, blank team names, and same-team fixtures produce actionable errors rather than silently producing a misleading table.

Output is conventional league-standing CSV, one row per team:

```csv
position,team,played,won,drawn,lost,goals_for,goals_against,goal_average,points
1,Ipswich Town,10,8,0,2,18,6,3.000,16
2,Manchester City,10,6,2,2,14,11,1.273,14
3,Liverpool,10,6,1,3,17,8,2.125,13
```

`goal_average` is shown to 3 decimal places, but the rank is computed with exact rational arithmetic, not rounded displays.

## Historical league rules

For the 1974/75 English First Division season:

1. **2 points** for a win, **1 point** for a draw, **0** for a loss.
2. Rank by **points** (descending).
3. On points ties, rank by **goal average** (`goals_for / goals_against`), descending. This is **not** the same as modern goal difference.
4. On exact goal-average ties, rank by **goals scored** (descending).
5. If all historical criteria are tied, rank alphabetically for stable, deterministic CSV output. This last fallback is an implementation convention, not a claimed historical tie-breaking rule.

If a team has scored goals but conceded zero, its goal average is considered infinite (`INF` in output). If it has scored and conceded zero, the otherwise undefined ratio is treated as a neutral **1.000**. This handling is an explicit engineering assumption for an edge case in arbitrary CSV input and does not affect the supplied historical table.

Sources for historical rules:
- https://goonergrove.co.uk/table/1970_1979/table_1974_75.php
- https://en.wikipedia.org/wiki/1974%E2%80%9375_in_English_football

## Meaning of "10th week" and historical match data

**Assumption:** "10th week" means the table **as it stood after the tenth fixture round**, on **28 September 1974**. This gives 22 teams and **107 actually played league matches**.

Three scheduled round-9 matches were delayed and **must not** appear in a September 1974 standings table:

| Original round | Played | Match |
| --- | --- | --- |
| 9 | 1974-12-04 | Leeds United 2-1 Tottenham Hotspur |
| 9 | 1974-12-10 | Middlesbrough 3-0 Leicester City |
| 9 | 1975-04-23 | Newcastle United 3-1 Arsenal |

These do appear in the attributed source transcription (`data/fixtures_source.txt`), but are omitted from `data/1974_75_week10_matches.csv` because their playing dates are after the September 28 cutoff. Consequently some teams have played 9 and others 10 matches by this date. This is historically accurate and preferable to falsely assuming each team had exactly 10 games played.

The historical matches were transcribed from BDFutbol's season-by-round match results:
- https://www.bdfutbol.com/en/t/teng1974-75.html

The round-10 fixtures were cross-checked with FBref:
- https://fbref.com/en/comps/9/1974-1975/schedule/1974-1975-Premier-League-Scores-and-Fixtures

Club naming is consistently expanded (e.g. `Leeds` -> `Leeds United`, `Wolverhampton` -> `Wolverhampton Wanderers`). This is a historical data preparation step, not fuzzy team matching in the CLI.

### Independent snapshot check

The "10th week" interpretation remains an **assumption**: this snapshot includes matches actually played through 28 September 1974, rather than all fixtures assigned to rounds 1–10 regardless of their eventual playing dates. A row-by-row check against [BDFutbol's first ten rounds](https://www.bdfutbol.com/en/t/teng1974-75.html) found 110 scheduled fixtures, including the three later round-9 matches above; all 107 included CSV rows matched its dates, home and away teams, and scores after the documented name expansions. The nine matches through 28 September listed by [UFLC](https://uflc.co.uk/results/1974-75) also matched; UFLC covers a title-holder sequence, not the full league schedule.

An independently published [28 September table at LFChistory](https://www.lfchistory.net/games/818) agrees with all 22 teams' played, won, drawn, lost, goals for, goals against, and points. It reverses Arsenal and Tottenham Hotspur in positions 20–21. On its own figures, Arsenal's goal average is `9/12 = 0.750`, above Tottenham's `11/15 ≈ 0.733`, with both on six points. The CSV retains Arsenal 20th under the [two-point and goal-average rules](https://goonergrove.co.uk/table/1970_1979/table_1974_75.php); the LFChistory position ordering is the remaining source discrepancy. Goonergrove shows the final-season table and rules, not a week-10 snapshot.

### Reproduce the historical CSVs

```bash
python3 scripts/prepare_historical_data.py
python3 -m football_standings \
  --input data/1974_75_week10_matches.csv \
  --as-of 1974-09-28 \
  --output data/1974_75_week10_standings.csv
```

The preparation script asserts there are 110 round-1-to-10 scheduled fixtures, 3 postponed matches after the cutoff, 107 played matches through the cutoff, and 22 distinct competing clubs.

## Testing

```bash
python3 -m unittest discover -s tests -v
```

Automated tests verify points for win/draw/loss, home/away consistency, **goal average versus goal difference**, score-based ties, mathematically undefined goal-average cases, invalid data, duplicates, filename mode, stdin/stdout, atomic output writing, historical data invariants, independently sourced fixture and standings checks, and exact output matching the supplied golden CSV. The GitHub Actions workflow is configured to run tests and compare regenerated historical files on pushes and pull requests once the project is published.

No third-party runtime or test libraries are needed; the tests use Python's built-in `unittest`. If you already have `pytest`, it can run these test cases too.

## Structure

```text
football_standings/      Business rules, CSV parsing, CLI
scripts/prepare_historical_data.py  Reproducible 1974/75 fixture CSV preparation
data/                   Historical fixtures, supplied input CSV, supplied output CSV
tests/                  Unit, integration and historical acceptance tests
AGENTS.md               Project instructions read by Codex CLI
CLAUDE.md               Preserved assignment-required instruction file
.claude/                Preserved assignment-required directory; no Claude session claimed
ai/                     Reviewed, genuine Codex CLI conversation exports before submission
AI_REFLECTION.md        Human-authored reflection to complete from actual collaboration
PROMPTS_FOR_CLAUDE.md   Legacy prompt starter guide, not conversation evidence
.github/workflows/      CI test workflow
```

## AI collaboration and submission artifacts

The assistant used for this assessment is **OpenAI Codex CLI**. The assignment permits an AI coding assistant other than Claude Code when equivalent genuine collaboration artifacts are supplied. `AGENTS.md` provides Codex project guidance. The required `CLAUDE.md` and `.claude/` directory are preserved, but neither is evidence of a Claude Code conversation, and this project does not claim one took place.

Before the final public GitHub submission:

1. Identify the actual Codex CLI session for this repository, review it, and place only genuine project conversation exports in `ai/`. Follow [ai/README.md](ai/README.md); do not copy all of `~/.codex` or create a synthetic transcript.
2. Inspect exported material for credentials, personal details, unrelated tool output, and private paths before staging it in a public repository. Disclose necessary redactions without inventing conversation history.
3. Write and approve `AI_REFLECTION.md` in the human author's own voice, using only this project's real collaboration and verifiable changes. It is intentionally still a template.
4. Confirm that the working CLI, input and output CSVs, tests, README, `CLAUDE.md`, `.claude/`, `AGENTS.md`, `ai/` exports, and reflection are staged together for the final commit. Run the test suite and historical regeneration check before publishing the public GitHub repository.

A README or configuration scaffold alone does not satisfy the genuine AI conversation-export or personal reflection requirements.

## Responsible development and review

Input data and calculations are deterministic, offline, and independently testable. The project does not hard-code the 1974/75 standings: only historical fixtures are provided, and the generic calculator produces standings for any compatible league CSV. Any coding-assistant edits should preserve the historical rules, regenerate the CSV, rerun tests, and be reviewed by the human author before committing.
