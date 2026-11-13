# Project layout and code standards

Copy the chosen layout into `docs/ARCHITECTURE.md` so the project documents itself.

## Workspace

```
<workspace>/
├── event-management-system/        ← project (own git repo)
├── student-attendance-system/      ← project (own git repo)
├── restaurant-management-system/   ← project (own git repo)
└── AUTOMATION_SUMMARY.md                ← optional single file, written by the orchestrator
```

Nothing else at workspace level: no shared folders, no "common", "add-ons", "shared-libs" or "tmp". Git worktrees for parallel features live inside their own project at `.worktrees/` (git-ignored).

## Web monorepo (default)

```
<slug>/
├── apps/
│   ├── web/                       Next.js
│   │   └── src/
│   │       ├── app/
│   │       │   ├── (public)/      landing, auth pages
│   │       │   ├── (admin)/admin/ admin panel routes
│   │       │   ├── (organizer)/organizer/  one route group per role panel
│   │       │   └── api/           only BFF/health if backend is split
│   │       ├── features/<module>/ components, hooks, api client, schemas per module
│   │       ├── components/        app-wide composites (layout shells, nav)
│   │       ├── lib/               auth client, fetcher, env, utils
│   │       └── styles/
│   └── api/                       NestJS
│       └── src/
│           ├── main.ts            bootstrap: helmet, CORS, validation, logger
│           ├── config/            typed env (validated at boot)
│           ├── common/            guards, interceptors, filters, decorators, pipes
│           ├── modules/<module>/
│           │   ├── <module>.module.ts
│           │   ├── <module>.controller.ts   HTTP only: routes, guards, DTOs
│           │   ├── <module>.service.ts      business rules
│           │   ├── <module>.repository.ts   data access only
│           │   ├── dto/                     request/response schemas
│           │   └── <module>.spec.ts         unit tests next to code
│           ├── integrations/<provider>/     adapters (email, payments, storage)
│           ├── jobs/                        queue processors
│           └── prisma/                      schema, migrations, seed
├── packages/
│   ├── ui/                        design-system components + tokens
│   ├── validation/                shared Zod schemas (web + api)
│   ├── types/                     shared TS types/contracts
│   └── config/                    eslint, tsconfig, tailwind presets
├── infra/
│   ├── docker-compose.yml         postgres, redis, mailpit, minio (project ports)
│   └── docker/                    Dockerfiles (multi-stage, non-root)
├── tests/
│   ├── e2e/                       Playwright, one folder per role
│   ├── security/                  red-team regression tests
│   └── load/                      optional k6 scripts
├── docs/  .claude/  .github/workflows/
└── package.json  pnpm-workspace.yaml  turbo.json
```

For Next.js full-stack, drop `apps/api` and put modules under `apps/web/src/server/<module>/` with the same controller → service → repository split.

## Layering rules

- Controller/route handler: parse and validate input, check auth and role, call one service method, map the result. No business logic, no database calls.
- Service: business rules, transactions, ownership checks, events. No HTTP objects.
- Repository: database queries only. The only place the ORM client is used.
- Frontend: pages compose feature components; feature components use hooks; hooks call the typed API client. No `fetch` scattered in components.
- Dependencies point inward: `modules` may use `common`; `common` never imports a module; packages never import apps.

## Code standards

- TypeScript `strict: true`, no `any` (use `unknown` + narrowing), no non-null assertions on external data.
- Validate every external input at the boundary (HTTP body/query/params, env, webhooks, files, queue payloads).
- Errors: typed domain errors mapped to HTTP problem responses in one filter; never leak stack traces.
- Naming: kebab-case files, PascalCase components/classes, camelCase functions, SCREAMING_SNAKE env vars, snake_case DB columns mapped to camelCase in code.
- Size limits as a smell check: files over ~300 lines or functions over ~50 lines get split.
- No dead code, no commented-out code, no `console.log` (use the logger), no TODO without a linked plan item.
- Conventional Commits with feature IDs: `feat(events): F-EVT-01 create event draft`.
- Accessibility: semantic HTML, labels on every input, focus states, keyboard paths, contrast from DESIGN_SYSTEM tokens.
