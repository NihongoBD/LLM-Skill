# Changelog — automation skill

Versions follow: patch = wording or defaults, minor = new rules or steps, major = removed or reversed rules.
Approved suggestions from knowledge/SUGGESTIONS.md are recorded here with their ID.

## 2.1.1 — 2026-11-13
- Fixed: `init_project.py` and `validate_project.py` crashed on Windows consoles (cp1252) when printing → and ✗; all four scripts now write UTF-8 to stdout/stderr.

## 2.1.0 — 2026-11-13
- Added the complete workflow to the skill: "Workflow at a glance" map in SKILL.md (same numbering as the picture), WORKFLOW.md with diagrams and a table of what each box does, and workflow.html, a picture that opens in any browser (light and dark mode).
- Added a table linking every workflow box to its phase and tools.

## 2.0.0 — 2026-11-13
- Renamed the skill from project-forge to automation (status file is now AUTOMATION_STATUS.md, scaffold script is init_project.py).
- Added the learning loop: knowledge base, `learn.py` (add, ingest, suggest, harvest, report, pending, verify, retire), daily update and scheduling.
- Added the cross-project rule for building multiple products: share knowledge through the inbox, checkpoints, read-before-deciding, immediate spread of security findings.
- Added "suggest the best solution" before every major decision, with evidence.
- Skill rule changes now go through SUGGESTIONS.md and need the user's approval.
- Seeded the knowledge base with 10 baseline patterns (roles and ownership, audit log, capacity locking, money, state machine, keys, token rotation, rate limits, parallel work, web stack).

## 1.0.0 — 2026-11-13
- First version (as project-forge): 10 phases, 7 docs, 14 project skills, version checker, scaffold, validator.
