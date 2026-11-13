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

See [`skills/automation/WORKFLOW.md`](skills/automation/WORKFLOW.md) for the full flow, or open `skills/automation/workflow.html` in a browser for a diagram.

## Adding another skill

Create `skills/<name>/SKILL.md` with `name` and `description` frontmatter, then add `./skills/<name>` to `skills` in `.claude-plugin/plugin.json`. Check it is discovered with `npx skills@latest add ./ --list`.
