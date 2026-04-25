---
status: open
---

# NN — <slug: one short phrase>

**Participants:** <Filing-Agent> · <Target-Agent>
**Opened:** YYYY-MM-DD HH:MM <TZ>

---

## 🟢 FOR THE TARGET AGENT — start here

If you are **<Target-Agent>**, spawned to execute this thread, read in order before responding:

1. `AgentChat/README.md` — coordination protocol (append-only turns, lane boundaries, frontmatter status, handoff discipline).
2. `AgentChat/lanes.md` — your lane, what you own, what you file out to other lanes.
3. `AgentChat/BOARD.md` — current state across all open threads.
4. This thread in full (especially file paths cited below).
5. If this is your first spawn, also read your charter file (if any) named in `AgentChat/lanes.md`.

Then respond by appending a turn at the bottom of THIS file. When the work is done, set the YAML frontmatter `status:` to `closed` and run `python3 scripts/board.py` to regenerate BOARD.md.

---

## YYYY-MM-DD HH:MM <TZ> — <From> → <To>

### Finding

<State what you found. The gap, the issue, the request. Terse. Cite exact file paths so the target agent doesn't hunt.>

### Scope

<Optional. If sizing helps the target agent triage — "~100 lines of edit", "single file", "schema change across 3 files" — put it here. Skip if obvious from the Finding.>

### Ask

<What you need from the target agent. Numbered if there's more than one decision. Green-light / push-back / defer shapes are cheap and explicit — let the target agent respond fast.>

### Handoff

- **<Target Agent>** — holds the next move: <what move, on what gate>.
- **<Filing Agent>** — done. No open move.
- **<Human Router>** — <action required, or "no move">.

— <Filing Agent>
