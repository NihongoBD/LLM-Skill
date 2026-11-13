# AGENTS.md — {{PROJECT_NAME}}

Operating manual for AI coding agents. Read this first, then the doc the task needs.

## Project

<!-- AUTO: two sentences on what the product is and who uses it; list the roles. -->

## Where things are

| Need | Look in |
|---|---|
| What to build, acceptance criteria | `docs/PRD.md` (feature IDs `F-…`, rules `BR-…`) |
| UI tokens, components, layouts | `docs/DESIGN_SYSTEM.md`, `packages/ui` |
| Layers, folders, auth flow, ports | `docs/ARCHITECTURE.md` |
| Tables, constraints, seed accounts | `docs/DATABASE.md` |
| Endpoints, roles, rate tiers | `docs/API.md` |
| Past bugs and their fixes | `docs/solutions/` (search here before debugging) |
| Plans in progress | `docs/plans/` |
| Build progress | `AUTOMATION_STATUS.md` |
| Workflows | `.claude/skills/` — start with `project-implementation` |

## Command contract

| Command | Does |
|---|---|
| `pnpm dev` | Run all apps (web :{{WEB_PORT}}, api :{{API_PORT}}) |
| `pnpm infra:up` / `pnpm infra:down` | Start/stop Docker services for this project |
| `pnpm lint` / `pnpm typecheck` | Static checks |
| `pnpm test` | Unit + integration tests |
| `pnpm test:e2e` | Playwright end-to-end tests |
| `pnpm test:security` | Red-team regression tests |
| `pnpm build` | Production build |
| `pnpm verify` | lint + typecheck + test + build (run before every commit) |
| `pnpm db:migrate` / `pnpm db:seed` / `pnpm db:reset` | Database |
| `pnpm audit:deps` | Dependency vulnerability scan |

<!-- AUTO: if the stack is not Node/pnpm, replace the commands with the real ones but keep the same names in the left column. -->

## Always

- Follow the layer rules: controller → service → repository; no business logic in controllers, no ORM outside repositories.
- Validate every external input with a schema; reject unknown fields.
- Put role checks and ownership checks on every endpoint; add a negative test (wrong role, other user's record) for each.
- Give every new endpoint a rate-limit tier; add CAPTCHA to public forms.
- Use design-system components and tokens; handle loading, empty, error and success states.
- Write tests with the code; reference the feature ID in test names and commits.
- Update `docs/API.md` / `docs/DATABASE.md` in the same change when endpoints or schema change.
- Verify library APIs against the pinned version's official docs before using them.

## Never

- Commit secrets, `.env`, real customer data, or test passwords in code.
- Weaken, skip or delete a test or security control to make something pass.
- Use raw SQL with string-built user input, `dangerouslySetInnerHTML` without sanitising, or `eval`-like constructs.
- Add a dependency without checking it is the official, maintained package (see `pr-reviewer`).
- Leave placeholders, mock data or TODOs in production code paths.
- Touch files outside this project folder, or scan/attack any host other than this project's localhost stack.

## Definition of done (per change)

`pnpm verify` green · acceptance criteria covered by tests · authz negative tests present · docs updated · `pr-reviewer` has no open P1/P2 · conventional commit with feature ID.
