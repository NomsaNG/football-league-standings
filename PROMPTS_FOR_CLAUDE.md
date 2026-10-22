# Legacy prompt starter guide — not a conversation record

These sample prompts were written before the choice to use OpenAI Codex CLI. They are optional starting ideas for reviewing this Python project, **not evidence that a Claude Code session took place** and not a record of prompts actually sent to Codex. Follow `ai/README.md` for this project's genuine Codex session-export procedure. Review every suggested edit and use only actual conversations in the submission.

## Prompt 1 — Read the brief and audit the repository

> Read AGENTS.md, CLAUDE.md, and README.md, then inspect the repository. Summarize the assignment requirements as a checklist and mark each as met, partial, or missing. Do not edit anything yet. Highlight any interpretations that require a documented assumption, especially the meaning of "10th week," historical ranking criteria, and the required AI artefacts. Propose three concrete improvements and rank them by importance.

**Human check:** Verify that the assistant notices the real-session-export and personal-reflection requirements; they're not satisfied by scaffolding alone.

## Prompt 2 — Prove the historical rules

> Inspect football_standings/core.py. Check the 1974/75 league rules using reliable historical sources. Explain why 2 points per win and goal average (not goal difference) matter. Identify any mathematically tricky cases such as a team conceding 0 goals or an exact tie on goal average. Do not change code until you give me a small set of test cases that distinguish correct from incorrect historical rankings.

**Human check:** Use the goal-average-vs-goal-difference test as a counterexample; ask for a fix if the source or reasoning is wrong.

## Prompt 3 — Review CLI quality and error handling

> Audit the Python CLI as if reviewing a production code submission. Check stdin/stdout behavior, CSV header handling, invalid dates and scores, duplicate fixtures, error exit codes, portability on macOS, and partial output files. Suggest improvements that add reliability without unnecessary dependencies or overengineering. Implement the best agreed improvement in a small, reviewable patch. Show which files changed and why.

**Human check:** Review the actual diff before proceeding. Preserve stdout as pure CSV and stderr for errors.

## Prompt 4 — Strengthen automated tests

> Review the test suite and identify meaningful untested edge cases. Add focused automated regression tests for at least one concrete gap you find, avoiding tests that merely restate the implementation. Run `python3 -m unittest discover -s tests -v`, show the test results, and explain how the new tests would fail on a buggy implementation. Do not delete existing tests.

**Human check:** Make sure Claude executes the tests rather than simply saying they should pass.

## Prompt 5 — Verify week-10 historical evidence

> Inspect `data/fixtures_source.txt`, `scripts/prepare_historical_data.py`, the generated input CSV, and the expected standings CSV. Confirm all first-10-round fixtures and the inclusive cutoff date of 1974-09-28 using the source links in README.md. In particular, explain why three postponed round-9 games must be excluded. Regenerate the input and output CSV, report match/team counts and the top five standings, and flag any uncertain rows for manual review. Do not invent historical results or silently correct questionable results.

**Human check:** A week-10 table should have 22 teams and 107 fixtures actually played by September 28, not 110. Some clubs have 9 matches played.

## Prompt 6 — Challenge the design and collaborate

> Play the role of a demanding technical reviewer. Give me two concrete risks or improvements in this implementation, including one where you disagree with an existing choice. Present tradeoffs and recommend one. Wait for my decision before changing the code. After my decision, make the smallest sensible change, update tests/docs, and show the verified outcome.

**Human check:** Record your actual disagreement/decision. It can form the basis of your own honest `AI_REFLECTION.md`.

## Prompt 7 — Final validation and docs

> Perform a final independent submission audit. Verify Python 3.11+ compatibility, CLI help, reproducible input/output CSV, historical sorting order, errors, all tests, README instructions, CI configuration, and project layout. Confirm that `CLAUDE.md`, `.claude/`, `ai/`, and `AI_REFLECTION.md` are present, but distinguish scaffolds from genuine AI artifacts. List blockers that require a human action. Do not claim readiness if genuine Codex session exports or a genuine reflection are still missing.

**Human check:** Compare the output with the reference historical sources; inspect the source data for accuracy.


## Prompt 8 — Check Git before public publishing

> Check git status and the tracked-file list. Report whether all required deliverables are included, whether tests pass, whether the committed input/output CSVs are current, and whether real Codex CLI session exports exist in `ai/`. Remind me to inspect transcripts and configuration for secrets before publishing. Do not commit or push anything without my instruction. Provide the exact commands I should run to create the final public GitHub repository.

**Human check:** Export real transcripts, inspect files for secrets, run tests, and only then commit and publish.

## Current export instructions

This file contains suggested prompts only. For the actual Codex CLI conversation export, use `ai/README.md`, select this project's completed session, inspect it for sensitive material, and include only a genuine reviewed record. Stage, commit, and publish after the human author has approved the final reflection and submission contents.
