# Parallel agents

Two levels of parallelism: one agent per project, and (inside a project) several agents on independent features using git worktrees.

## Level 1 — One agent per project

The orchestrator runs Phase 0 for all projects, runs `init_project.py` once per project with `--index 0, 1, 2…` (so ports never collide), then launches one subagent per project **in the same turn** so they work simultaneously. Keep concurrency to what the machine can handle; 3–5 projects at once is a sensible ceiling because each runs Docker services and test suites.

### Brief for each project subagent

```
You are the lead engineer for ONE project.

Project: <Project Name>
Folder (your only writable project area): <absolute path to workspace>/<slug>/
Platform: <platform>
Roles hint: <roles from the topic, if any>
Automation skill folder: <absolute path to the automation skill>

Do Phases 1–9 of <automation skill>/SKILL.md for this project only.
Rules:
- Read and write only inside your project folder. The single exception: you may ADD new
  lesson files to <automation skill>/knowledge/inbox/ with `learn.py add`. Never edit or
  delete other files in the skill, and never run `learn.py ingest` (the orchestrator does).
- Before writing DATABASE.md, before each feature plan, and before each fix, run
  `learn.py suggest <topic>` and prefer proven solutions; say which one you used and why.
- As soon as a solution is proven by a passing test (or something fails), record it with
  `learn.py add --project <slug> --outcome worked|failed --evidence <test or finding>`.
- Copy proven patterns into your own code; never import from another project's folder.
- Use only your own ports (see .env.example); never stop or reuse other projects' containers.
  Docker Compose project name must be <slug>.
- Update AUTOMATION_STATUS.md after every step and commit.
- Decide open questions yourself and record them (PRD §12 / ADR). Only escalate:
  credentials, paid services, deployment, deleting outside your folder.
- Red-team only your own localhost stack. If the orchestrator reports a vulnerability class
  found in another project, test your project for it right away.
- When finished, reply with the final report format from SKILL.md, including the lessons you added.
```

### Orchestrator duties while agents run

- Poll each project's `AUTOMATION_STATUS.md` (cheap and objective) rather than asking agents for status.
- **Learning checkpoints**: when all projects pass a phase (docs, data layer, each block of features, red team), run `learn.py ingest`, then send each running agent the new entries relevant to it (`learn.py suggest <its topics>`). This is how a solution found by one agent reaches the others during the same run.
- **Security spread**: when any project logs a High or Critical finding, tell every other agent to test for the same class immediately.
- If an agent escalates, answer from what the user said in Phase 0, or collect all escalations and ask the user once.
- Never edit project code yourself; send instructions to the owning agent.
- At the end, run `validate_project.py --workspace <dir>`, run Phase 10 (learn and suggest) for the whole workspace, then write the chat report (and optionally `AUTOMATION_SUMMARY.md` at workspace root).

### Without subagents

Run the projects sequentially with exactly the same rules and briefs. The folder isolation and port allocation still apply, so the result is identical, just slower.

## Level 2 — Parallel features inside one project (git worktrees)

Use when several features are independent. Worktrees live **inside** the project so nothing leaks into the workspace:

```bash
# from the project root, on an up-to-date main
git worktree add .worktrees/F-EVT-02 -b feat/F-EVT-02-approve-event
git worktree add .worktrees/F-TKT-03 -b feat/F-TKT-03-qr-checkin
# each feature agent works only inside its own .worktrees/<id>/ folder
```

`.worktrees/` is in `.gitignore` (the scaffold adds it).

### What can run in parallel

- Safe: features that touch only their own module folder, their own UI route group, and their own tests.
- Serialise: anything that changes the database schema, shared packages (`packages/ui`, `packages/validation`), auth/guards, global config, or the API client generator. Do these on `main` first, merge, then start the parallel features from the new `main`.
- Rule of thumb: if two plans list the same file under "files to touch", they are not parallel.

### Each worktree agent

1. Installs dependencies in its worktree, uses a separate test database name (`<slug>_test_<feature>`), and does not start a second copy of shared Docker services.
2. Follows `compound-work` for its plan.
3. Rebases on `main`, runs `pnpm verify`, then hands the branch to `pr-reviewer`.
4. Merge order: smallest diff first; after each merge the remaining branches rebase and re-run `pnpm verify`.
5. Clean up: `git worktree remove .worktrees/<id>` and delete the merged branch.
