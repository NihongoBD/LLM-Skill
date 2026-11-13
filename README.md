# LLM-Skill

Agent skills for Claude Code (and any agent that reads `SKILL.md` skills).

| Skill | What it does |
|---|---|
| [`automation`](automation/SKILL.md) | Turns a list of app ideas into finished codebases: researches features, picks a verified stack, writes the 7 spec docs, installs 14 project skills, builds with parallel agents, hardens and red-teams its own local build, and learns from every project through a scored knowledge base. |

## Install the `automation` skill

The skill is the `automation/` folder. Copy it into a skills directory:

```bash
# Personal (all projects)
git clone https://github.com/NihongoBD/LLM-Skill.git
cp -r LLM-Skill/automation ~/.claude/skills/automation

# Or one workspace only
mkdir -p .claude/skills && cp -r LLM-Skill/automation .claude/skills/automation
```

On Windows (PowerShell):

```powershell
Copy-Item -Recurse LLM-Skill\automation "$env:USERPROFILE\.claude\skills\automation"
```

To build a `.skill` package (for upload to claude.ai), zip the folder so `automation/` is the top-level entry:

```bash
zip -r automation.skill automation -x '*/__pycache__/*'
```

### Requirements

Full workflow: Claude Code (bash, git, web search, subagents), Node.js with pnpm, Docker, and Python 3 for the scripts in `automation/scripts/`. Without those, only phases 0–5 (research, stack, scaffold, docs, skills) run.

### Keeping what the skill learned

The skill writes lessons to `automation/knowledge/`. Before reinstalling or updating the skill, copy that folder somewhere safe and put it back afterwards, or set `AUTOMATION_KNOWLEDGE_DIR` to a folder outside the skill (see `automation/references/learning-loop.md`).

## Use it

In Claude Code, list your ideas:

```
Build these:
- Event Management System with Admin & Organizer Panel
- Restaurant Management System
```

Other triggers: "which stack is best for …", "daily update", "what did you learn".

See [`automation/WORKFLOW.md`](automation/WORKFLOW.md) for the full flow, or open `automation/workflow.html` in a browser for a diagram.

## Quick check of the scripts

```bash
python automation/scripts/learn.py pending
python automation/scripts/learn.py suggest audit log --category data-model
python automation/scripts/check_versions.py react next
```
