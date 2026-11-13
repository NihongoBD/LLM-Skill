# {{PROJECT_NAME}}

<!-- AUTO: one-paragraph description: what it does and for whom. -->

## Features

<!-- AUTO: short list of the main features grouped by role (from PRD Must/Should). -->

## Tech stack

<!-- AUTO: one line per layer with major versions; link to docs/ARCHITECTURE.md for detail. -->

## Prerequisites

<!-- AUTO: exact Node.js LTS line, pnpm, Docker + Docker Compose; anything else. -->

## Quick start

```bash
git clone <repo-url> {{PROJECT_SLUG}} && cd {{PROJECT_SLUG}}
pnpm install
cp .env.example .env            # then fill any values marked REQUIRED
pnpm infra:up                   # Postgres :{{DB_PORT}}, Redis :{{REDIS_PORT}}, Mailpit :{{MAIL_UI_PORT}}
pnpm db:migrate && pnpm db:seed
pnpm dev                        # web http://localhost:{{WEB_PORT}}  api http://localhost:{{API_PORT}}
```

<!-- AUTO: confirm these commands match the real scripts; this block is tested in the final phase. -->

## Development accounts (seeded, local only)

<!-- AUTO: one row per role: email, panel URL. Password comes from SEED_PASSWORD in .env. -->

## Scripts

See the command contract in [AGENTS.md](AGENTS.md#command-contract).

## Project structure

<!-- AUTO: short tree of top-level folders with one-line descriptions. -->

## Testing

<!-- AUTO: how to run unit, integration, E2E and security tests; coverage thresholds. -->

## Security

Security controls and the latest red-team results: [docs/SECURITY_REPORT.md](docs/SECURITY_REPORT.md). Report vulnerabilities privately to <!-- AUTO: contact -->.

## Documentation

[PRD](docs/PRD.md) · [Design system](docs/DESIGN_SYSTEM.md) · [Architecture](docs/ARCHITECTURE.md) · [Database](docs/DATABASE.md) · [API](docs/API.md) · [Agents](AGENTS.md)

## License

<!-- AUTO: licence chosen by the user, or "Proprietary — all rights reserved" by default. -->
