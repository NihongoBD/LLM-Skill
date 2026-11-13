---
name: automation
description: Builds complete software projects from a list of ideas such as "Event Management System with Admin & Organizer Panel" or "Restaurant Management System", and learns from every project. Researches all features, picks the latest verified stack, writes PRD, DESIGN_SYSTEM, ARCHITECTURE, DATABASE, API, AGENTS and README, installs 14 project skills (setup, features, security, MCP, testing, compound ask, plan, analysis, work, fix, PR review and more), builds each project in its own folder with parallel agents that share lessons, hardens it with rate limits, CAPTCHA and RBAC, attacks its own local build and auto-fixes findings. Keeps a knowledge base of proven solutions and data structures, recommends the best option with evidence, and runs a daily update that proposes improvements for the user to approve. Use whenever the user lists app, system or management-system ideas to plan, build or fully set up, asks which solution or stack is best, or says daily update or what did you learn, even without naming this skill.
compatibility: Full workflow needs Claude Code (or any agent with bash, git, web search and subagents), Node.js with pnpm, Docker, and Python 3 for the scripts. Without those, run phases 0 to 5 only. The knowledge base learns only where the skill folder is writable (Claude Code).
---

# Automation

Turn project ideas into finished codebases — researched, documented, built, hardened, attacked and fixed — and get smarter with every project. Each project lives in its own folder with its own docs and skills. Everything learned goes into this skill's `knowledge/` folder, so the next project starts from what already worked.

## Workflow at a glance

Same numbering as `WORKFLOW.md` and `workflow.html` (open the HTML file in a browser to see it as a picture).

```
Your idea list
  → Check knowledge (show waiting suggestions)              ← knowledge: best option
  → Split into projects (one agent + one folder each)
     ┌── each agent, in its own folder, all at the same time ──┐
     │ 1 Research features                                      │
     │ 2 Pick stack              ← knowledge: proven stack       │
     │ 3 Create project folder                                  │
     │ 4 Write 7 docs            ← knowledge: data models        │
     │ 5 Install 14 skills                                      │
     │ 6 Build features          ↔ knowledge: share lessons      │
     │ 7 Harden security                                        │
     │ 8 Hack and fix            → knowledge: holes found        │
     │ 9 Verify                                                 │
     └──────────────────────────────────────────────────────────┘
  → 10 Learn and suggest         → knowledge: new lessons, scores
  → Finished projects

Every day: collect lessons → score → recheck versions and security news
           → suggest improvements → you approve? yes: skill improves / no: reason saved ↻
```

| Box | Where in this file | Tools |
|---|---|---|
| Check knowledge, Split into projects | Phase 0 | `learn.py pending`, latest `knowledge/reports/` |
| 1 Research features | Phase 1 | web search, `learn.py suggest … --category feature` |
| 2 Pick stack | Phase 2 | `learn.py suggest stack …`, `check_versions.py` |
| 3 Create project folder | Phase 3 | `init_project.py` |
| 4 Write 7 docs | Phase 4 | templates in `assets/docs/`, `learn.py suggest … --category data-model` |
| 5 Install 14 skills | Phase 5 | installed by `init_project.py`, then tailored |
| 6 Build features | Phase 6 | project skills, `learn.py suggest` / `add` |
| 7 Harden security | Phase 7 | `auth-security/references/security-baseline.md` |
| 8 Hack and fix | Phase 8 | `auth-security/references/red-team.md`, `learn.py add --category security` |
| 9 Verify | Phase 9 | `validate_project.py` |
| 10 Learn and suggest | Phase 10 | `learn.py harvest`, `ingest`, `report`, `knowledge/SUGGESTIONS.md` |
| Daily update | Daily update section | `references/learning-loop.md` §6 and §9 |

## What one project looks like when you are done

```
<workspace>/<project-slug>/          ← one project = one folder = one git repo
├── README.md  AGENTS.md  CLAUDE.md
├── AUTOMATION_STATUS.md             ← phase tracker; lets any session resume
├── .env.example  .gitignore  .mcp.json
├── .claude/skills/                  ← 14 project skills (installed from assets/)
├── docs/
│   ├── PRD.md  DESIGN_SYSTEM.md  ARCHITECTURE.md  DATABASE.md  API.md
│   ├── SECURITY_REPORT.md
│   ├── adr/  plans/  solutions/  research/
├── apps/  packages/  infra/  tests/ ← shape depends on the chosen stack
```

## Golden rules (why they matter)

1. **One project, one top-level folder.** Never put a project inside another project, and never create shared "add-on", "common" or "extras" folders between projects. Each project must install, test and ship on its own. If two projects need the same code, each gets its own copy.
2. **Docs before code, and docs stay true.** Code follows PRD → ARCHITECTURE → DATABASE → API. When code has to diverge, update the doc in the same commit.
3. **Verify, don't remember.** Library versions, APIs and package names are checked live. Training memory is stale, and an invented package name is a real supply-chain attack vector.
4. **Security from the first commit.** Auth, RBAC, validation, rate limits and CAPTCHA are part of the foundation.
5. **Attack only your own local build.** The red-team phase targets localhost and the project's own Docker network, never external hosts, third-party APIs or production.
6. **Every fix compounds.** A bug or finding is closed only with a regression test and a lesson in `docs/solutions/`.
7. **Evidence before "done".** Never report a step complete without running the command and seeing it pass.
8. **Learn from everything; suggest the best; change rules only with approval.** Every proven solution, data structure, stack result and security finding becomes knowledge with evidence. Before each important decision, ask the knowledge base for the best known option and say why. The knowledge base updates itself; this skill's own rules change only when the user approves a suggestion, and never in a direction that weakens security or testing.

## Knowledge and suggestions (read before deciding anything)

Full detail: `references/learning-loop.md`. The tool is `scripts/learn.py`:

```bash
python <skill-dir>/scripts/learn.py suggest <topic words>     # best known solutions, with evidence
python <skill-dir>/scripts/learn.py add --category … --title … --project … --outcome worked|failed --evidence … --body "Problem: … Solution: … Use when: … Avoid when: …"
python <skill-dir>/scripts/learn.py ingest                    # orchestrator only: merge inbox, rescore
```

When a decision matters (stack, data structure, auth approach, provider, fix for a class of bug):
1. Run `suggest` for the topic and read `knowledge/KNOWLEDGE.md` for the category.
2. Prefer the top **proven** entry; treat **baseline** and **candidate** entries as strong defaults to verify; avoid **risky** ones unless an ADR explains why.
3. When you show the user a choice, present it like this:

```
Best solution: <name> — worked in N projects, M failures (evidence: …)
Why it fits here: <one line>
Alternative: <name> — <why it ranks lower>
```

4. Record the result afterwards with `learn.py add` (`worked` or `failed`), so the ranking improves.

## Phase 0 — Intake (the only phase that may talk to the user)

1. **Check what the skill has learned.** Run `learn.py pending` and look at the newest file in `knowledge/reports/`. If suggestions are waiting, mention them in one line ("3 improvements are waiting for your approval — want to see them?"); do not block the run on them.
2. **Split the input into projects.** Each line or bullet is one project. Derive a clean name and kebab-case slug, and keep role hints. Example: "Event Management System Project with Admin & Organizer Panel" → name `Event Management System`, slug `event-management-system`, roles hint `Admin, Organizer`.
3. **Platform.** If not stated, ask once for all projects: Web, Web + Mobile, Mobile, Desktop or API only (per-project overrides allowed). If nobody can answer, default to Web and record the assumption.
4. **Workspace.** Use the current directory unless the user names one. Each project goes to `<workspace>/<slug>/`. If the folder has `AUTOMATION_STATUS.md`, resume from it; if it exists without one, stop and ask.
5. **Confirm in five lines or fewer** (projects, platform, workspace, that the rest runs unattended), then go. From here on, ask only when blocked (see Autonomy).

## Phase 1 — Feature research

Read `references/feature-research.md`. First run `learn.py suggest <domain words> --category feature` to reuse feature patterns from earlier projects in the same domain, then research real products and open-source systems to complete the inventory (Must / Should / Could, stable IDs like `F-EVT-01`). Save notes and sources to `docs/research/` once the scaffold exists.

## Phase 2 — Platform and stack

Read `references/stack-selection.md`. Run `learn.py suggest stack <platform words>` first: proven stack entries win over the default table unless they are flagged as old. Then verify versions live:

```bash
python <skill-dir>/scripts/check_versions.py next react @nestjs/core prisma tailwindcss
```

The script picks the newest stable release at least 14 days old and flags missing or pre-release packages. Pin exact versions and record each choice and its reason in `docs/ARCHITECTURE.md` and `docs/adr/0001-stack.md`.

## Phase 3 — Scaffold

```bash
python <skill-dir>/scripts/init_project.py --workspace <dir> --name "<Project Name>" --platform web --index <n>
```

`--index` is the project's position (0, 1, 2…) and gives it its own ports. The script refuses to nest projects, copies the doc templates, installs the 14 project skills into `.claude/skills/`, writes `.env.example`, `.gitignore`, `CLAUDE.md` and `AUTOMATION_STATUS.md` (which records where this skill and its knowledge live), and runs `git init`. Read `references/project-layout.md` before creating source folders.

## Phase 4 — Documentation

Read `references/docs-guide.md`. Fill the templates in order: PRD → DESIGN_SYSTEM → ARCHITECTURE → DATABASE → API → AGENTS → README. Replace every `<!-- AUTO: … -->` guidance comment. Before writing DATABASE.md, run `learn.py suggest <entities and rules>` with `--category data-model` and reuse proven data structures (roles and ownership, audit log, capacity locking, money, state machines) adapted to this domain. Commit: `docs: initial specification`.

## Phase 5 — Tailor the project skills

The 14 skills are installed by the scaffold. Replace generic parts with this project's specifics (real commands if not Node/pnpm, real module names, roles, providers). They must work for an agent that has never seen this skill.

| Skill | Use it for |
|---|---|
| `project-implementation` | Entry point: reads AUTOMATION_STATUS and routes to the right skill |
| `setup-initialization` | Monorepo, tooling, Docker, env validation, CI, command contract |
| `feature-development` | Building one PRD feature as a full vertical slice |
| `auth-security` | Auth, RBAC, rate limits, CAPTCHA, headers; holds the security baseline and red-team playbook |
| `mcp-connection` | Dev-time MCP servers and an optional product MCP server |
| `integrations` | Email, payments, storage, SMS and other providers behind adapters |
| `testing-qa` | Test pyramid, permission matrix, E2E, accessibility, performance gates |
| `debugging` | Reproduce → isolate → root cause |
| `compound-ask` | Turning vague requests into precise specs |
| `compound-plan` | Writing an implementation plan in `docs/plans/` |
| `compound-analysis` | Impact, risk, performance and drift analysis |
| `compound-work` | Executing a plan on a branch or worktree with tests and small commits |
| `compound-fix` | Fixing bugs and findings so the whole class of bug is closed |
| `pr-reviewer` | Reviewing every change before merge (P1–P4; P1/P2 block) |

## Phase 6 — Build

Read `references/build-pipeline.md` and `references/parallel-agents.md`. Order: setup → security foundation → data layer and seed → features (MVP first, each through ask → plan → analysis → work → review) → integrations → MCP → full test suite. Before each plan and each fix, run `learn.py suggest`; when something is proven by a passing test, record it with `learn.py add`. Commit after every step and tick `AUTOMATION_STATUS.md`.

## Phase 7 — Harden

Open `<project>/.claude/skills/auth-security/references/security-baseline.md` and verify every control is implemented and tested. Anything missing becomes a `compound-work` task.

## Phase 8 — Red team (act like an attacker, against your own build only)

Open `<project>/.claude/skills/auth-security/references/red-team.md`. Attack the local stack in the playbook's order, write each attack as a test in `tests/security/`, log findings in `docs/SECURITY_REPORT.md`, fix with `compound-fix`, and re-attack until no Critical or High remain. Record every fixed finding as a `security` lesson (the mistake, the fix, the test) so future projects avoid it from the start.

## Phase 9 — Verify and hand over

From a clean state, see each pass:
1. Fresh clone → README quick start works as written.
2. `pnpm verify`, `pnpm test:e2e` and `pnpm test:security`.
3. `python <skill-dir>/scripts/validate_project.py <project-dir>` exits 0.
4. Several projects: `python <skill-dir>/scripts/validate_project.py --workspace <dir>` also passes.

## Phase 10 — Learn and suggest

1. `learn.py harvest --workspace <dir>` drafts lessons from `docs/solutions/`, ADRs and fixed findings.
2. Review each draft (reusable title, category, tags, Problem / Solution / Use when / Avoid when, no secrets or project noise), remove its `needs_review` line, or delete it.
3. `learn.py ingest`, then `learn.py report`.
4. Where the evidence supports it, add proposals to `knowledge/SUGGESTIONS.md` (format in `references/learning-loop.md` §7). Never apply them without the user's approval.

## Multiple projects

Do Phase 0 for all projects together, then give each project to its own subagent at the same time, using the brief in `references/parallel-agents.md`. Each subagent owns exactly one folder and runs Phases 1–9 there; the orchestrator runs Phase 10 once for the whole workspace. Without subagents, run the projects one after another with the same rules.

**Cross-project learning rule** (details: `references/learning-loop.md` §5):
1. Share knowledge, never folders or code. A data structure proven in one project is copied into another project's own code and docs, never imported from the other folder.
2. Agents write lessons to `knowledge/inbox/` with `learn.py add` as soon as something is proven (one file per lesson, so parallel agents never conflict). Only the orchestrator runs `ingest`.
3. At every checkpoint (after docs, data layer, each block of features, red team) the orchestrator ingests and tells each running agent which new entries matter to it.
4. Agents run `learn.py suggest` before writing DATABASE.md, before each feature plan and before each fix, so a problem solved in one project is solved the same way in the others.
5. A vulnerability class found in one project is tested in every other project immediately.
6. Shared concepts (users, roles, payments, notifications, audit logs) use the same proven data structure in every project, adapted to each domain.
7. A result that contradicts a proven entry is recorded as `failed` or `mixed` with evidence; scores and the daily review decide, not the newest opinion.

## Daily update (the skill improves day by day)

When the user says "daily update", "learn" or "what did you learn", or when a scheduled run starts the skill, follow `references/learning-loop.md` §6: harvest, review drafts, ingest, re-verify stack knowledge and check for new advisories, write the report, propose suggestions, then tell the user in three to six lines what was learned, the best new solution, anything risky, and what waits for approval. Scheduling with cron or Task Scheduler is in §9.

When the user approves a suggestion: apply exactly that change, bump `CHANGELOG.md`, and mark it `applied`. Reject anything that would weaken security, testing or the localhost-only attack scope, whatever the evidence.

## Autonomy: when to decide and when to stop

Decide on your own (record it in an ADR or PRD §12) for anything the docs leave open, using the knowledge base's recommendation where one exists.

Stop and ask the user only for: real credentials or paid sign-ups (until then use sandbox mode, test keys and `.env.example` placeholders, and keep building), deploying or pushing to a remote, deleting anything outside the project folder, a risky legal or business rule (refund policy, data retention law), or approving changes to this skill.

Long runs: `AUTOMATION_STATUS.md` plus the docs are the memory. Update the status file after every step so a new session can continue from the next unchecked box.

## Final report (in chat)

For each project: folder path, stack with pinned major versions, features built (Must/Should counts) and backlog, how to run it (three commands), test results with numbers, security summary (found, fixed, accepted with reason), decisions made without asking, and anything that still needs the user. Then for the whole run: **learned this run** (new proven entries, risky ones), the **best solution** recommendations that changed, and **suggestions waiting for approval**. Keep it short and factual.
