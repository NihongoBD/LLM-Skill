# Build pipeline (Phase 6)

Run the project's own skills (in `<project>/.claude/skills/`) in this order. Tick the matching box in `AUTOMATION_STATUS.md` and commit after each step.

## Step 1 — Setup and initialisation (`setup-initialization`)

Monorepo, tooling, Docker Compose with this project's ports, typed env validation, logger, error filter, health endpoints, CI workflow, and the command contract scripts. Exit check: `pnpm verify` passes on an empty app and `docker compose up -d` brings services to healthy.

## Step 2 — Security foundation (`auth-security`)

Before any feature: authentication, sessions/tokens, RBAC and ownership guard, global validation, security headers, CORS, CSRF, Redis rate limiter with tiers, CAPTCHA verification service, audit log, upload policy. Every later feature plugs into these instead of inventing its own. Exit check: auth tests and the role-permission matrix test skeleton pass.

## Step 3 — Data layer

Translate DATABASE.md into the ORM schema, create the first migration, add constraints and indexes for business rules, and write a seed that creates one test account per role (dev and test only, passwords from env, never in production). Exit check: `pnpm db:reset` runs clean twice in a row.

## Step 4 — Features (`feature-development`, with the compound loop)

For each feature in PRD order (Must first, then Should):

1. `compound-ask` only if the PRD leaves something blocking open.
2. `compound-plan` → `docs/plans/<date>-<feature-id>.md`.
3. `compound-analysis` on the plan: impact, risk, security, performance.
4. `compound-work` → implement the vertical slice with tests on a branch (or a worktree when running in parallel).
5. `pr-reviewer` → fix every P1/P2, then merge.
6. Update API.md / DATABASE.md if they changed, tick the feature in AUTOMATION_STATUS.

Schema-changing work is serialised (one migration at a time on `main`); features that only touch their own module can run in parallel. See `parallel-agents.md`.

## Step 5 — Integrations (`integrations`)

Email, payments, storage, SMS, PDF/QR, calendar — whatever the PRD lists — each behind an adapter with a fake for tests and sandbox credentials in dev.

## Step 6 — MCP connection (`mcp-connection`)

Configure dev-time MCP servers in `.mcp.json` (browser automation, read-only database, GitHub, library docs), and build the product's own MCP server only if the PRD asks for AI/agent access.

## Step 7 — Testing and QA (`testing-qa`)

Fill the gaps: acceptance criteria → tests mapping, full role-permission matrix, E2E journeys per role, accessibility checks, performance budget, coverage thresholds. Exit check: `pnpm verify && pnpm test:e2e` green.

## Whenever something breaks

Use `debugging` to find the root cause and `compound-fix` to fix it with a regression test and a lesson in `docs/solutions/`. Never skip, disable or weaken a test or a security control to get green.
