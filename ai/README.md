# Genuine Codex CLI conversation exports

OpenAI Codex CLI is the coding assistant used for this project. This README explains how to include genuine project conversations; it is **not** a conversation export and does not satisfy the assignment by itself. No Claude Code session is claimed.

The installed Codex CLI stores local session JSONL files under `~/.codex/sessions/YYYY/MM/DD/`. Its current help does not provide a dedicated `export` command. From the repository root, locate candidate files by checking the first JSONL record's `payload.cwd` against this repository's absolute path:

```bash
python3 - <<'PY'
import json
from pathlib import Path

project = str(Path.cwd().resolve())
for path in (Path.home() / ".codex" / "sessions").rglob("*.jsonl"):
    with path.open(encoding="utf-8") as source:
        first = json.loads(source.readline())
    if first.get("type") == "session_meta" and first.get("payload", {}).get("cwd") == project:
        print(path)
PY
```

Confirm which candidate contains this project's actual prompts. Do not copy the entire `~/.codex` directory or unrelated sessions; it can contain authentication and private material.

After the session is complete, inspect the **specific** session file for credentials, personal information, unrelated tool output, and private paths. Copy that reviewed file into `ai/` with its original filename. If redaction is needed for public GitHub, disclose what was redacted without inventing or altering the substance of the exchange. Confirm that the exported file is a real Codex record from this project before staging it.

`AI_REFLECTION.md` remains the human author's own account of the actual collaboration. An empty `ai/` directory or only this README leaves the session-export requirement incomplete.
