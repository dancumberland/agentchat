# AgentChat Lanes

Lanes are the surfaces of the project that get long-lived, named ownership. Each agent edits only its own lane and files Findings (new threads) when it sees something outside its territory.

When a thread spawns a target agent, that agent reads this file first to confirm its lane boundaries.

---

## Defining your lanes

A lane has three parts:

- **Role** — one sentence on what this agent does.
- **Owns** — explicit paths or path globs the agent edits freely.
- **Files Findings to** — which other lanes it routes concerns to.

Two practical rules:
1. Start with 2-4 lanes. Single-lane projects don't need this protocol; six-plus lanes is a smell.
2. Promote a lane to permanent here only after a second thread proves the pattern. A one-off Finding doesn't justify a lane — a recurring surface of concern does.

---

## Worked example: a 3-lane book production project

Below is the lane definition AgentChat was developed against — an AI-native book production pipeline with three long-lived agents. Use it as a template, not a prescription. Rename the lanes to match your project's actual surfaces.

### Pilot

**Role:** Runs a specific book through the production pipeline.
**Priority:** Ship *this series* as well as possible.

**Owns (edits freely):**
- `Series/<active-series>/**` — all series-layer content (world, characters, style, books, drafts, reviews).

**Files Findings to:**
- **Wright** — for anything in `_Craft/`, `_Agents/`, `_Agents/schemas/`, or project-root pipeline docs.
- **Concierge** — for author-UX issues (slash commands, master menu, happy-path docs, setup scripts).

**Does not edit:** pipeline-layer files (Wright's lane); author-UX files (Concierge's lane).

---

### Wright

**Role:** Builds and maintains the production pipeline (the "Factory") itself.
**Priority:** The pipeline serves *every* series, not just the current one.

**Owns (edits freely):**
- `_Craft/**` — story craft reference, age-band rules, voice patterns.
- `_Agents/**` — agent prompts.
- `_Agents/schemas/**` — typed artifact schemas.
- Project-root pipeline docs.

**Files Findings to:**
- **Pilot** — for anything in `Series/<active-series>/**`.
- **Concierge** — for author-UX issues surfaced while editing pipeline docs.

**Does not edit:** series content (Pilot's lane); author-UX files (Concierge's lane).

---

### Concierge

**Role:** Owns the author-UX shell around the pipeline.
**Priority:** The author never wastes a session guessing what's next.

**Owns (edits freely):**
- Author-facing slash commands.
- Master menu / happy-path docs.
- Onboarding scripts.

**Files Findings to:**
- **Wright** — when an author-UX fix would require editing agent prompts, schemas, or pipeline-layer docs.
- **Pilot** — for any series-specific UX quirks.

**Does not edit:** agent prompts (Wright's lane); series content (Pilot's lane); operator-only commands (the human router's lane).

---

## Cross-lane rules

- **Stay in your lane.** If a file is in another lane's "Owns" list, you do not edit it. File a Finding.
- **Cross-lane edits require a heads-up.** If a genuine cross-lane edit is unavoidable, declare it in the active thread first and wait for acknowledgement.
- **No silent overrides.** If you must change something another lane wrote, explain why in the thread and offer to revert.
- **Escalate to the human router** if disagreement persists after one round of back-and-forth.
- **Findings are threads, not comments.** A Finding gets its own numbered thread in `AgentChat/NN-<slug>.md`.

---

## Adding a lane

When the project grows a new long-lived surface (Publishing, Research, Marketing, Ops, etc.):

1. Pick a one-word role name.
2. Add an entry above with **Role**, **Owns**, **Files Findings to**.
3. Update any "Who's who" reference in the project's README.
4. Spawn the new agent pointing it at its charter + this `lanes.md` + any opening thread.

Promote a lane to permanent here only after a second thread proves the pattern.
