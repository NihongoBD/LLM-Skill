# {{PROJECT_NAME}} — Architecture

## 1. Context

<!-- AUTO: Mermaid C4-style context diagram: users per role, the system, external services (email, payments, storage, CAPTCHA). -->

## 2. Containers

<!-- AUTO: Mermaid diagram + table: web app, API, worker, database, cache/queue, object storage, mail; what each does and how they talk. -->

## 3. Technology stack

All versions verified live on {{DATE}} (newest stable at least 14 days old) and pinned exactly.

| Layer | Package | Version | Why chosen | Rejected alternatives |
|---|---|---|---|---|
<!-- AUTO: one row per core package from the stack decision. -->

### Version notes

<!-- AUTO: 3–5 important changes in the chosen majors (from official upgrade guides) that code must respect. -->

## 4. Repository layout

<!-- AUTO: paste the chosen folder tree and one line per top-level folder. -->

## 5. Layers and request lifecycle

```
Request → reverse proxy/TLS → security headers → rate limiter → auth (session/token)
        → CSRF check (cookie auth) → validation (DTO schema, unknown fields rejected)
        → role guard → controller → service (business rules + ownership check)
        → repository (ORM) → database
Response ← serializer (only allowed fields) ← error filter (problem+json, no stack traces)
```

Layering rules: controllers hold no business logic; services hold no HTTP objects; only repositories talk to the ORM; dependencies point inward.

## 6. Authentication and sessions

<!-- AUTO: Mermaid sequence diagrams for signup + email verification, login (with CAPTCHA after failures, MFA for admins), token/session refresh with rotation and reuse detection, logout, password reset. State token lifetimes and cookie flags. -->

## 7. Authorisation model

<!-- AUTO: roles, permissions per role, ownership rules (e.g. organizer may only access events where organizerId = user.id), how the guard and service enforce both. -->

## 8. Security architecture

Implements `.claude/skills/auth-security/references/security-baseline.md`.

| Control | Implementation | Where |
|---|---|---|
| Rate limiting | Redis sliding window, tiers: global, auth, sensitive, expensive, per-user | <!-- AUTO --> |
| CAPTCHA | <!-- AUTO: provider --> verified server-side on signup, login after N failures, password reset, public forms | <!-- AUTO --> |
| Bot defence | honeypot, minimum submit time, temporary IP ban list in Redis | <!-- AUTO --> |
| Headers / CSP | helmet + nonce-based CSP | <!-- AUTO --> |
| CSRF / CORS | <!-- AUTO --> | <!-- AUTO --> |
| Secrets | env validated at boot; `.env` never committed; gitleaks in CI | <!-- AUTO --> |
| Audit log | admin and sensitive actions, append-only | <!-- AUTO --> |

## 9. Data, caching and background jobs

<!-- AUTO: what is cached (and invalidation), queues and jobs (emails, exports, reminders), idempotency, retries. -->

## 10. Files and storage

<!-- AUTO: upload limits, allowed types (checked by content), storage location (S3-compatible; MinIO locally), signed URLs. -->

## 11. Observability

<!-- AUTO: structured logs with request IDs (secrets redacted), health/readiness endpoints, metrics, error tracking. -->

## 12. Configuration and ports

| Service | Port | Env var |
|---|---|---|
| Web | {{WEB_PORT}} | `WEB_PORT` |
| API | {{API_PORT}} | `API_PORT` |
| PostgreSQL | {{DB_PORT}} | `DB_PORT` |
| Redis | {{REDIS_PORT}} | `REDIS_PORT` |
| Mailpit SMTP / UI | {{MAIL_PORT}} / {{MAIL_UI_PORT}} | `MAIL_PORT` / `MAIL_UI_PORT` |

Docker Compose project name: `{{PROJECT_SLUG}}`.

## 13. Deployment

<!-- AUTO: build artefacts, multi-stage non-root Docker images, environments, migrations on deploy, backups, rollback. Do not deploy without the user's approval. -->

## 14. Decision records

<!-- AUTO: list docs/adr/*.md with one-line summaries. -->
