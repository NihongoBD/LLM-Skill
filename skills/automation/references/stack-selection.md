# Platform and stack selection

Pick a stack **family** from the table, then verify versions live. Never write a version number from memory.

## 1. Default families by platform

| Platform | Frontend | Backend | Data | Notes |
|---|---|---|---|---|
| Web (panels, dashboards) | Next.js (App Router) + React + TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, React Hook Form + Zod | NestJS (TypeScript) | PostgreSQL + Prisma, Redis | Turborepo + pnpm monorepo: `apps/web`, `apps/api`, shared `packages/` |
| Web, small scope | Next.js full-stack (Route Handlers / Server Actions) | inside Next.js | PostgreSQL + Prisma, Redis | Use only when the decision rule below says so |
| Web + Mobile | Web stack above + Expo (React Native, Expo Router) in `apps/mobile` | NestJS shared by both | same | Mobile talks only to the public API, never to the DB |
| Mobile only | Expo (React Native) | NestJS | PostgreSQL + Prisma, Redis | Admin panel still needs a small web app |
| Desktop | Tauri + React + TypeScript (Electron only if Node APIs are required) | NestJS or local SQLite | PostgreSQL or SQLite | Sign builds; disable remote code |
| API only | — | NestJS (or Fastify for tiny services) | PostgreSQL + Prisma, Redis | OpenAPI is the product |

Shared tooling for every family: TypeScript strict, ESLint (flat config) + Prettier, Vitest, Supertest (API), Playwright (E2E + axe for accessibility), Husky + lint-staged + commitlint, Docker Compose for local Postgres/Redis/Mailpit/MinIO, GitHub Actions CI, Renovate or Dependabot, pino logging, gitleaks, osv-scanner or `pnpm audit`.

Security libraries (verify names and versions live): helmet, a Redis-backed rate limiter (e.g. `@nestjs/throttler` with a Redis store), argon2 for password hashing, Cloudflare Turnstile or hCaptcha (server-side verification), DOMPurify where HTML must be rendered.

### Decision rule: split backend vs Next.js full-stack

Choose the split NestJS backend when any of these hold: more than one client (web + mobile/desktop), background jobs or queues, external API consumers, more than about 25 Must features, or several role panels with complex permissions. Otherwise Next.js full-stack is simpler and fine. Record the reason in ADR 0001.

### When the user names a stack

The user's choice wins. Map it onto the same structure (command contract, layers, security baseline) and note any gaps in the ADR.

## 2. Verify versions live

```bash
python <skill-dir>/scripts/check_versions.py next react react-dom @nestjs/core @nestjs/common prisma @prisma/client tailwindcss typescript vitest @playwright/test
python <skill-dir>/scripts/check_versions.py --pypi django   # for Python stacks
```

The script reports for each package: newest stable version, its age, and the version to use (newest stable that is at least 14 days old). The 14-day buffer exists because freshly published releases are where malicious or broken versions get caught.

For every chosen package also check:
- It is the official package (repository URL points to the real project; meaningful weekly downloads). Look-alike names are a common attack.
- It is maintained (release in the last year) and its licence is compatible.
- It does not need install scripts, or you allow them explicitly (pnpm `onlyBuiltDependencies`).

## 3. Read the upgrade notes before coding

Frameworks change APIs between major versions: renamed files and conventions, new caching defaults, changed router or config APIs. Before writing code, open the official docs and "upgrade guide" / "migration" page for the chosen major of each core framework (frontend framework, backend framework, ORM, CSS framework, test runner) and write the 3–5 most important differences into `docs/ARCHITECTURE.md` under "Version notes". Code written from memory of an older major is the most common AI-generated bug.

## 4. Pin and record

- Exact versions in `package.json` (no `^` or `~` for runtime dependencies), lockfile committed.
- `.nvmrc` / `engines` set to the active LTS of Node.js (verify which line is LTS today).
- `docs/ARCHITECTURE.md` stack table: package, version, purpose, why chosen, alternatives rejected.
- `docs/adr/0001-stack.md`: context, decision, consequences.
