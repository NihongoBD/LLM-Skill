# {{PROJECT_NAME}} — API

The generated OpenAPI spec (`<!-- AUTO: path, e.g. apps/api/openapi.json -->`) must match this document. CI fails if they drift.

## 1. Conventions

- Base URL: `http://localhost:{{API_PORT}}/api/v1` (dev). Versioned by path.
- Auth: <!-- AUTO: httpOnly Secure SameSite cookies, or Bearer tokens for mobile; describe both if both exist. -->
- Content type: `application/json`; request bodies limited to <!-- AUTO: e.g. 1 MB --> (uploads use their own endpoint and limit).
- Unknown fields in a request body are rejected (400), which prevents mass assignment.
- IDs are opaque strings; never sequential integers in URLs.
- Timestamps ISO 8601 UTC.

## 2. Errors

All errors use RFC 9457 problem details:

```json
{ "type": "https://errors.{{PROJECT_SLUG}}.dev/validation", "title": "Validation failed", "status": 400,
  "detail": "One or more fields are invalid", "errors": [{ "field": "email", "message": "Invalid email" }],
  "requestId": "…" }
```

Never include stack traces, SQL, or internal paths. Auth failures use the same message for "no such user" and "wrong password".

## 3. Pagination, filtering, sorting

Cursor pagination: `?limit=20&cursor=…` (max `limit` 100, enforced). Filters as query params validated by schema; sort with `?sort=-createdAt` limited to an allowlist of fields.

## 4. Rate-limit tiers

| Tier | Limit (per window) | Keyed by | Applies to |
|---|---|---|---|
| global | <!-- AUTO: e.g. 300/min --> | IP | everything |
| auth | <!-- AUTO: e.g. 5/min and 20/hour --> | IP + account | login, MFA, token refresh |
| sensitive | <!-- AUTO: e.g. 3/15 min --> | IP + account | signup, password reset, email change, OTP |
| expensive | <!-- AUTO: e.g. 10/min --> | user | exports, reports, search |
| write | <!-- AUTO: e.g. 60/min --> | user | create/update/delete |

Responses include `RateLimit-*` headers; exceeding returns 429 with `Retry-After`. Repeated abuse adds the IP to a temporary ban list.

## 5. Idempotency

`POST` endpoints that create payments, orders, bookings or send messages accept an `Idempotency-Key` header; repeating a key returns the original result.

## 6. Endpoints

<!-- AUTO: one table per module. Every endpoint lists roles, ownership rule, rate tier, CAPTCHA (yes/no) and the feature IDs it serves.

### Module: Events
| Method | Path | Roles | Ownership | Tier | CAPTCHA | Request | Success | Errors | Features |
|---|---|---|---|---|---|---|---|---|---|
| POST | /events | organizer | creator becomes owner | write | no | CreateEventDto | 201 Event | 400, 401, 403, 429 | F-EVT-01 |
-->

## 7. Webhooks

<!-- AUTO: inbound (payment provider etc.): signature verification, replay window, idempotent processing. Outbound if any. -->

## 8. Health

`GET /health` (liveness, no auth, no details) and `GET /health/ready` (readiness: DB and Redis reachable).
