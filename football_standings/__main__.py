"""Allow `python3 -m football_standings` without installation."""

from .cli import main

raise SystemExit(main())
