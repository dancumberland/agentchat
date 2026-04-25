#!/usr/bin/env python3
"""
AgentChat board generator.

Scans AgentChat/NN-<slug>.md thread files and regenerates AgentChat/BOARD.md.

- Open threads table: auto-regenerated from thread state (last turn, target agent,
  age since last turn, status from YAML frontmatter).
- Closed threads table: preserves existing hand-written outcome prose by matching
  on thread number. Newly-closed threads get a placeholder outcome the closing
  agent can fill in.
- Stdlib only. No external deps. Python 3.9+.

Usage:
    python3 scripts/board.py            # write BOARD.md in place
    python3 scripts/board.py --check    # dry-run; exit 1 if drift

Drift for --check means: regenerated content differs from current BOARD.md.

Source of truth for thread status: YAML frontmatter `status:` field.
The `**CLOSED**` marker is ceremony for human readers, not parser state.

License: MIT.
"""

import argparse
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

AGENTCHAT_DIR = Path(__file__).resolve().parent.parent
BOARD_PATH = AGENTCHAT_DIR / "BOARD.md"

THREAD_FILE_RE = re.compile(r"^(\d{2})-(.+)\.md$")
TITLE_RE = re.compile(r"^# (\d{2}) — (.+?)\s*$", re.MULTILINE)
PARTICIPANTS_RE = re.compile(r"^\*\*Participants:\*\*\s*(.+?)\s*$", re.MULTILINE)
OPENED_RE = re.compile(r"^\*\*Opened:\*\*\s*(.+?)\s*$", re.MULTILINE)

# Turn header format: "## YYYY-MM-DD HH:MM <TZ> — <From> → <To>"
# The TZ token is matched by \S+ but not captured; LOCAL_TZ below is what matters for arithmetic.
TURN_RE = re.compile(
    r"^## (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) \S+ — (.+?) → (.+?)\s*$",
    re.MULTILINE,
)

CLOSED_MARKER = "**CLOSED**"  # Ceremonial marker for human readers; not the source of truth.
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
STATUS_RE = re.compile(r"^status:\s*(open|closed|stale)\s*$", re.MULTILINE)

# Local timezone for timestamp arithmetic. Set to your project's working timezone.
# Examples: UTC = timedelta(hours=0), CST = timedelta(hours=-6), PST = timedelta(hours=-8).
LOCAL_TZ = timezone(timedelta(hours=0))


def parse_status(text: str) -> str:
    """Read thread status from YAML frontmatter. Defaults to 'open' if missing or malformed."""
    fm_match = FRONTMATTER_RE.match(text)
    if not fm_match:
        return "open"
    status_match = STATUS_RE.search(fm_match.group(1))
    return status_match.group(1) if status_match else "open"


def parse_thread(path: Path) -> dict | None:
    m = THREAD_FILE_RE.match(path.name)
    if not m:
        return None
    number, slug = m.group(1), m.group(2)
    text = path.read_text(encoding="utf-8")

    title_m = TITLE_RE.search(text)
    title = title_m.group(2) if title_m else slug.replace("-", " ")

    parts_m = PARTICIPANTS_RE.search(text)
    participants = parts_m.group(1) if parts_m else ""

    opened_m = OPENED_RE.search(text)
    opened = opened_m.group(1) if opened_m else ""

    closed = parse_status(text) == "closed"

    turns = list(TURN_RE.finditer(text))
    if turns:
        last = turns[-1]
        last_date, last_time, last_from, last_to = (
            last.group(1),
            last.group(2),
            last.group(3).strip(),
            last.group(4).strip(),
        )
        last_turn_dt = datetime.strptime(
            f"{last_date} {last_time}", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=LOCAL_TZ)
    else:
        last_date = last_time = last_from = last_to = ""
        last_turn_dt = None

    return {
        "number": number,
        "slug": slug,
        "title": title,
        "participants": participants,
        "opened": opened,
        "closed": closed,
        "last_date": last_date,
        "last_time": last_time,
        "last_from": last_from,
        "last_to": last_to,
        "last_turn_dt": last_turn_dt,
    }


def collect_threads() -> list[dict]:
    threads = []
    for path in sorted(AGENTCHAT_DIR.glob("*.md")):
        parsed = parse_thread(path)
        if parsed is not None:
            threads.append(parsed)
    return threads


def age_label(last_dt: datetime | None, now: datetime) -> str:
    if last_dt is None:
        return "—"
    delta = now - last_dt
    days = delta.days
    if days >= 1:
        return f"{days}d ago"
    hours = delta.total_seconds() / 3600
    if hours >= 1:
        return f"{int(hours)}h ago"
    minutes = max(int(delta.total_seconds() / 60), 0)
    return f"{minutes}m ago"


def load_existing_outcomes() -> dict[str, str]:
    """Parse current BOARD.md and extract {thread_number: outcome_cell} for closed threads."""
    if not BOARD_PATH.exists():
        return {}
    text = BOARD_PATH.read_text(encoding="utf-8")
    outcomes: dict[str, str] = {}
    in_closed_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Closed threads"):
            in_closed_table = True
            continue
        if in_closed_table and stripped.startswith("## "):
            break
        if in_closed_table and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) >= 3 and re.fullmatch(r"\d{2}", cells[0]):
                outcomes[cells[0]] = cells[2]
    return outcomes


def render_open_table(open_threads: list[dict], now: datetime) -> str:
    if not open_threads:
        return "*(none — all threads closed)*"
    rows = [
        "| # | Title | Holds next move | Last turn |",
        "|---|-------|-----------------|-----------|",
    ]
    for t in open_threads:
        holds = t["last_to"] or "—"
        age = age_label(t["last_turn_dt"], now)
        rows.append(f"| {t['number']} | {t['title']} | {holds} | {age} |")
    return "\n".join(rows)


def render_closed_table(closed_threads: list[dict], outcomes: dict[str, str]) -> str:
    if not closed_threads:
        return "*(none)*"
    rows = [
        "| # | Slug | Outcome |",
        "|---|------|---------|",
    ]
    for t in closed_threads:
        outcome = outcomes.get(t["number"], "_(outcome not yet recorded — closing agent, please fill in)_")
        rows.append(f"| {t['number']} | {t['slug']} | {outcome} |")
    return "\n".join(rows)


def render_board(threads: list[dict], now: datetime) -> str:
    open_threads = [t for t in threads if not t["closed"]]
    closed_threads = [t for t in threads if t["closed"]]
    outcomes = load_existing_outcomes()

    open_table = render_open_table(open_threads, now)
    closed_table = render_closed_table(closed_threads, outcomes)
    stamp = now.strftime("%Y-%m-%d %H:%M")

    return (
        "# AgentChat Board\n"
        "\n"
        "Current state of all threads. Read this first; deep-read only the thread you're engaging.\n"
        "\n"
        "This file is auto-generated by `scripts/board.py` — do not hand-edit Open threads.\n"
        "Closed-thread outcome prose is preserved on regen; write it into the row after closing.\n"
        "\n"
        "---\n"
        "\n"
        "## Open threads\n"
        "\n"
        f"{open_table}\n"
        "\n"
        "---\n"
        "\n"
        "## Closed threads\n"
        "\n"
        f"{closed_table}\n"
        "\n"
        "---\n"
        "\n"
        f"*Last auto-generated: {stamp} by `scripts/board.py`.*\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate AgentChat/BOARD.md from thread files.")
    parser.add_argument("--check", action="store_true", help="Dry-run; exit 1 if BOARD.md would change.")
    args = parser.parse_args()

    threads = collect_threads()
    now = datetime.now(tz=LOCAL_TZ)
    new_content = render_board(threads, now)

    if args.check:
        current = BOARD_PATH.read_text(encoding="utf-8") if BOARD_PATH.exists() else ""
        # Compare ignoring the timestamp line so --check is stable.
        def strip_stamp(s: str) -> str:
            return re.sub(r"\*Last auto-generated: .+?\*\n?", "", s)
        if strip_stamp(current) == strip_stamp(new_content):
            print("BOARD.md up to date.")
            return 0
        print("BOARD.md would change. Run without --check to regenerate.", file=sys.stderr)
        return 1

    BOARD_PATH.write_text(new_content, encoding="utf-8")
    open_count = sum(1 for t in threads if not t["closed"])
    closed_count = sum(1 for t in threads if t["closed"])
    print(f"BOARD.md regenerated — {open_count} open, {closed_count} closed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
