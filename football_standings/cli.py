"""Command line interface supporting filenames or stdin/stdout ('-')."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from contextlib import ExitStack
from datetime import date
from pathlib import Path
from typing import Sequence

from .core import calculate_standings
from .csv_io import InputError, parse_iso_date, read_matches, write_standings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="football-standings",
        description="Calculate a historical English Football League standings CSV (2 points per win, goal average).",
    )
    parser.add_argument("-i", "--input", default="-", metavar="CSV",
                        help="input CSV path, or '-' for stdin (default: '-')")
    parser.add_argument("-o", "--output", default="-", metavar="CSV",
                        help="output CSV path, or '-' for stdout (default: '-')")
    parser.add_argument("--as-of", metavar="YYYY-MM-DD",
                        help="include only matches played on or before this date")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        cutoff: date | None = parse_iso_date(args.as_of, context="--as-of") if args.as_of else None
        with ExitStack() as stack:
            source = sys.stdin if args.input == "-" else stack.enter_context(
                open(args.input, "r", encoding="utf-8-sig", newline="")
            )
            table = calculate_standings(read_matches(source, as_of=cutoff))

        if args.output == "-":
            write_standings(sys.stdout, table)
        else:
            # Write atomically to avoid a partial result if the output fails.
            destination = Path(args.output)
            temp_path: str | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", newline="", dir=destination.parent,
                    prefix=".standings-", suffix=".tmp", delete=False,
                ) as output:
                    temp_path = output.name
                    write_standings(output, table)
                os.replace(temp_path, destination)
            finally:
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
        return 0
    except (InputError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
