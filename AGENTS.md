# Code project instructions

## Mission

Help build, explain, test, and improve a reliable Python 3.11+ CLI to calculate historical 1974/75 English First Division standings from input CSV. Keep this a general reusable standings calculator, not a hard-coded league table.

## Historical invariants

- Award **2** points per win and **1** per draw. Never silently substitute modern 3-point rules.
- Order by points descending, then **goal average** (GF / GA) descending, then goals scored descending. Goal difference is NOT the historical tiebreaker.
- Never use rounded display strings to compare goal average: use exact ratios / `fractions.Fraction`.
- Preserve handling of zero conceded and zero scored as described in README; mark any changes as assumptions.
- Interpret 'week 10' as the table as at **1974-09-28**, excluding postponed fixtures played in December 1974 or April 1975.
- Preserve complete text input and output CSV files in `data/`.

## Software engineering requirements

- Use Python 3.11+ standard library for the core CLI, no network or external runtime dependencies.
- Keep business rules pure, separate from CLI and CSV I/O.
- Support stdin and stdout (`-`) and named input/output files, with an optional inclusive `--as-of` filter.
- Strict CSV validation: headers, ISO dates, score fields, blank/identical teams, duplicate fixtures, and readable errors to stderr.
- No debug prints in stdout; it is reserved for machine-readable CSV data.
- Keep tests automated and include unit tests, subprocess tests, and historical acceptance tests.
- Execute `python3 -m unittest discover -s tests -v` after editing.
- Regenerate and verify historical CSV files when relevant.
- Explain important tradeoffs and risks to the human developer before changing historical assumptions or public API.

## AI assessment integrity

- The user is being evaluated on genuine collaboration with an AI assistant. Do not fabricate Codex transcripts, project session records, git history, benchmarks, or reflection anecdotes.
- Preserve actual session artifacts from this project's OpenAI Codex CLI usage. Do not create fake `.jsonl` conversation data or copy unrelated sessions.
- Ask the user to review any uncertainty in historical data or implementation decisions.
- Treat `AI_REFLECTION.md` as a first-person personal document the human must approve and make factually accurate.
- Avoid placing credentials or confidential content in logs destined for a public GitHub repository.

## Useful commands

```bash
python3 scripts/prepare_historical_data.py
python3 -m football_standings --input data/1974_75_week10_matches.csv --as-of 1974-09-28 --output data/1974_75_week10_standings.csv
python3 -m unittest discover -s tests -v
python3 -m football_standings --help
```
