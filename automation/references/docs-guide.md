# Writing the project documents

Templates are already in the project after the scaffold. Each contains `<!-- AUTO: … -->` comments that say what goes there; replace every one with real content (the validator fails if any remain).

## Order and dependencies

| # | File | Built from | Its job |
|---|---|---|---|
| 1 | `docs/PRD.md` | research inventory | What and why: roles, features with IDs, acceptance criteria, business rules, NFRs |
| 2 | `docs/DESIGN_SYSTEM.md` | PRD roles and flows | Tokens, components, layouts per panel, accessibility rules |
| 3 | `docs/ARCHITECTURE.md` | PRD + stack decision | Containers, layers, folder layout, auth flow, security architecture, ports, version notes |
| 4 | `docs/DATABASE.md` | PRD features + business rules | ERD, tables, constraints and indexes that enforce the rules |
| 5 | `docs/API.md` | PRD + DATABASE | Every endpoint with roles, rate-limit tier, request/response, errors |
| 6 | `AGENTS.md` | all of the above | Short operating manual for coding agents |
| 7 | `README.md` | all of the above | Human quick start and overview |

## Cross-document consistency (check before committing)

- Every Must/Should feature ID in the PRD appears in API.md (endpoints that serve it) and has at least one acceptance criterion.
- Every business rule `BR-xx` is enforced somewhere named in DATABASE.md (constraint, index, lock) or ARCHITECTURE.md (service rule), and will get a test.
- Every table in DATABASE.md is used by at least one endpoint; every endpoint's data exists in a table.
- Every role in the PRD appears in the API permission column and has a panel or app in DESIGN_SYSTEM/ARCHITECTURE.
- Every endpoint has a rate-limit tier; every public form endpoint has CAPTCHA noted.
- Ports and env variable names are identical in ARCHITECTURE.md, README.md, `.env.example` and `infra/docker-compose.yml`.

## Quality bar

- Concrete over generic: "Organizer can export attendee list as CSV, max 50k rows, async above 5k" beats "export functionality".
- Testable acceptance criteria in Given/When/Then.
- Diagrams in Mermaid (renders on GitHub): C4 context and containers, ERD, sequence diagram for login and token refresh, flowchart per main role journey.
- AGENTS.md stays short (under ~150 lines). It is loaded into every agent session, so it holds rules and pointers, not essays.
- README quick start must be copy-paste runnable; you will test it in Phase 9.

## Keeping docs alive

After the build, API.md must match the generated OpenAPI spec and DATABASE.md must match the ORM schema. The `pr-reviewer` skill blocks merges that change one without the other.
