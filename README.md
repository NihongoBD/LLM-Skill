# LLM-Skill

Agent skills for Claude Code, Codex, Cursor and any other agent that reads `SKILL.md` skills.

| Skill | What it does |
|---|---|
| [`automation`](skills/automation/SKILL.md) | Turns a list of app ideas into finished codebases: researches features, picks a verified stack, writes the 7 spec docs, installs 14 project skills, builds with parallel agents, hardens and red-teams its own local build, and learns from every project through a scored knowledge base. |

## Install

### With the `skills` CLI (any agent)

```bash
npx skills@latest add NihongoBD/LLM-Skill --skill=automation
```

The CLI asks which agents to install to and whether to install into this project or globally. To skip the prompts:

```bash
# Global, Claude Code only, no prompts
npx skills@latest add NihongoBD/LLM-Skill --skill=automation -g -a claude-code -y

# List the skills in this repo without installing
npx skills@latest add NihongoBD/LLM-Skill --list
```

This repository is private, so the CLI needs GitHub access to it. It uses your Git credentials, the GitHub CLI (`gh auth login`), or SSH, in that order.

### As a Claude Code plugin

In Claude Code:

```
/plugin marketplace add NihongoBD/LLM-Skill
/plugin install nihongobd-skills@nihongobd
```

### Manually

```bash
git clone https://github.com/NihongoBD/LLM-Skill.git
cp -r LLM-Skill/skills/automation ~/.claude/skills/automation
```

To build a `.skill` package (for upload to claude.ai), zip the folder so `automation/` is the top-level entry:

```bash
cd skills && zip -r ../automation.skill automation -x '*/__pycache__/*'
```

## Requirements

Full workflow: Claude Code (bash, git, web search, subagents), Node.js with pnpm, Docker, and Python 3 for the scripts in `skills/automation/scripts/`. Without those, only phases 0–5 (research, stack, scaffold, docs, skills) run.

## Keeping what the skill learned

The skill writes lessons to its own `knowledge/` folder. Reinstalling or updating replaces that folder, so first copy `knowledge/` somewhere safe and put it back afterwards, or set `AUTOMATION_KNOWLEDGE_DIR` to a folder outside the skill (see `skills/automation/references/learning-loop.md`).

## Use it

In your agent, list your ideas:

```
Build these:
- Event Management System with Admin & Organizer Panel
- Restaurant Management System
```

Other triggers: "which stack is best for …", "daily update", "what did you learn".

## Full workflow

From your idea list to finished, secured projects. Every project gets its own agent and folder, and all agents learn from a shared knowledge base.

### 1. Complete workflow

The dashed box is what each agent does in its own folder, all at the same time. Red steps are security.

<p align="center"><img src="docs/images/workflow.svg" alt="Complete workflow: idea list, check knowledge, split into projects, then per project: research features, pick stack, create folder, write 7 docs, install 14 skills, build features, harden security, hack and fix, verify; then learn and suggest, finished projects. A shared knowledge base feeds and learns from every step." width="680"></p>

### 2. Daily update

How the skill improves day by day. Knowledge updates automatically; the skill's own rules change only after you approve.

<p align="center"><img src="docs/images/daily-update.svg" alt="Daily update: collect lessons, score them, recheck versions and security news, suggest improvements, you approve. Yes: skill improves and changelog is updated. No: nothing changes and the reason is saved. Runs again tomorrow." width="680"></p>

### 3. What each step does

| Step | What happens | Output |
|---|---|---|
| Your idea list | You give one or more project ideas and, if you like, the platform | — |
| Check knowledge | Shows improvements waiting for your approval and the latest learning report; asks the platform once if missing | Confirmed plan (5 lines) |
| Split into projects | One clean name, folder and agent per project; agents run at the same time | One agent per project |
| 1. Research features | Roles, modules, features and functions from real products and open-source systems, reusing feature patterns learned before | Prioritised feature list with IDs |
| 2. Pick stack | Best proven stack from the knowledge base, then live version check (newest stable, at least 14 days old) | Stack table + ADR |
| 3. Create project folder | Own folder, own ports, own git repo; refuses to nest projects | Project skeleton |
| 4. Write 7 docs | PRD → DESIGN_SYSTEM → ARCHITECTURE → DATABASE → API → AGENTS → README, using proven data models | Complete specification |
| 5. Install 14 skills | Setup, feature development, auth & security, MCP, integrations, testing, debugging, compound ask/plan/analysis/work/fix, PR reviewer | `.claude/skills/` tailored to the stack |
| 6. Build features | Setup → security foundation → data layer → each feature through ask, plan, analyze, work, review → integrations → MCP → tests; lessons shared with other agents | Working app with tests |
| 7. Harden security | Every control checked: login safety, roles and ownership, validation, headers, CSRF, rate limits, CAPTCHA, IP bans, uploads, secrets | Hardening checklist done |
| 8. Hack and fix | Attacks its own localhost build (login, data access, injection, bypasses, races, uploads, leaks, scans), fixes everything, each attack becomes a test; vulnerability classes are sent to the other agents | SECURITY_REPORT with no open Critical/High |
| 9. Verify | Fresh install works, all tests green, validator passes | Ready project |
| 10. Learn and suggest | Collects lessons from all projects, scores them, writes the report, proposes improvements | Updated knowledge + suggestions |
| Finished projects | Short report per project, plus what was learned and what waits for your approval | — |
| Daily update | Collect → score → recheck → suggest → your approval → skill improves; repeats every day | Daily report |

### 4. Steps, phases and tools

Each step maps to a phase in [`SKILL.md`](skills/automation/SKILL.md) and the scripts in [`skills/automation/scripts/`](skills/automation/scripts/).

| Step | Phase | Tools |
|---|---|---|
| Check knowledge, Split into projects | Phase 0 — Intake | `learn.py pending`, latest `knowledge/reports/` |
| 1. Research features | Phase 1 | web search, `learn.py suggest … --category feature` |
| 2. Pick stack | Phase 2 | `learn.py suggest stack …`, `check_versions.py` |
| 3. Create project folder | Phase 3 | `init_project.py` |
| 4. Write 7 docs | Phase 4 | templates in `assets/docs/`, `learn.py suggest … --category data-model` |
| 5. Install 14 skills | Phase 5 | installed by `init_project.py`, then tailored |
| 6. Build features | Phase 6 | project skills, `learn.py suggest` / `add` |
| 7. Harden security | Phase 7 | `auth-security/references/security-baseline.md` |
| 8. Hack and fix | Phase 8 | `auth-security/references/red-team.md`, `learn.py add --category security` |
| 9. Verify | Phase 9 | `validate_project.py` |
| 10. Learn and suggest | Phase 10 | `learn.py harvest`, `ingest`, `report`, `knowledge/SUGGESTIONS.md` |
| Daily update | Daily update | `references/learning-loop.md` §6 and §9 |

### 5. What one finished project looks like

```
<workspace>/<project-slug>/          ← one project = one folder = one git repo
├── README.md  AGENTS.md  CLAUDE.md
├── AUTOMATION_STATUS.md             ← phase tracker; lets any session resume
├── .env.example  .gitignore  .mcp.json
├── .claude/skills/                  ← 14 project skills
├── docs/
│   ├── PRD.md  DESIGN_SYSTEM.md  ARCHITECTURE.md  DATABASE.md  API.md
│   ├── SECURITY_REPORT.md
│   ├── adr/  plans/  solutions/  research/
├── apps/  packages/  infra/  tests/ ← shape depends on the chosen stack
```

The same flow as Mermaid diagrams is in [`skills/automation/WORKFLOW.md`](skills/automation/WORKFLOW.md); open [`skills/automation/workflow.html`](skills/automation/workflow.html) in a browser for the original page (light and dark mode). After editing `workflow.html`, regenerate the README images with `python tools/export_workflow_svgs.py`.

## Adding another skill

Create `skills/<name>/SKILL.md` with `name` and `description` frontmatter, then add `./skills/<name>` to `skills` in `.claude-plugin/plugin.json`. Check it is discovered with `npx skills@latest add ./ --list`.
