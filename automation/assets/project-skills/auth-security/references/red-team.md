# Red-team playbook — {{PROJECT_NAME}}

Think like an attacker whose goal is to read data they should not see, act as someone else, get things without paying, or take the service down. Then prove each attempt fails with an automated test.

## Rules of engagement (read first, every time)

- **In scope**: only this project's local stack — `http://localhost:{{WEB_PORT}}`, `http://localhost:{{API_PORT}}` and the containers in Docker Compose project `{{PROJECT_SLUG}}`.
- **Out of scope**: every other host. That includes third-party APIs the code calls (payment, email, CAPTCHA, maps), other projects on this machine, staging and production. If a test would send traffic outside localhost, stub that dependency instead.
- Before running any scanner, check that the target host is `localhost`, `127.0.0.1`, `::1` or `host.docker.internal`; abort if not.
- Use only seeded test accounts and a disposable database (`pnpm db:reset` before and after a round).
- Keep load tests small and bounded (seconds, not minutes); the point is to find unbounded behaviour, not to stress the laptop.

## Round structure

1. `pnpm db:reset && pnpm infra:up && pnpm dev` (production-like config where possible: `NODE_ENV=production` build).
2. Recon → attacks A–K below → record findings.
3. For each finding: add a failing test in `tests/security/`, fix with `compound-fix`, see the test pass.
4. Re-run the whole round. Repeat until no Critical or High remain open.
5. Fill `docs/SECURITY_REPORT.md` (summary table, tooling results, findings).

Severity guide: **Critical** — unauthenticated data access, account takeover, remote code execution, payment bypass. **High** — authenticated privilege escalation or cross-tenant/IDOR access, stored XSS in admin views, auth rate limits missing. **Medium** — missing headers/CSRF on low-impact actions, information leaks, weak limits. **Low** — hardening gaps with little direct impact.

## Recon

- List every route: generated OpenAPI spec, `docs/API.md`, and a grep of controllers/route handlers (the code is the truth; undocumented routes are prime targets).
- List roles and seeded accounts; create a second account for each role (needed for IDOR tests).
- Note trust boundaries: public pages, each role panel, webhooks, file uploads, background jobs, exports.
- Check what the client bundle and responses reveal: API base URLs, feature flags, env names, source maps.

## A. Authentication
- Brute force login for one account and spray one password across accounts → expect lockout/429.
- Username enumeration: compare messages, status codes and timing for real vs fake emails on login, signup, reset.
- Token tampering: change role/user ID in the token, `alg: none`, wrong signature, expired token, token from another environment.
- Refresh token reuse after rotation → whole family revoked.
- Reset token: reuse, expiry, use for another account, still valid after password change.
- Session fixation; logout then reuse the old cookie/token.
- Admin login without MFA; MFA brute force (rate limited?).

## B. Authorisation
- Vertical: call every admin endpoint as each lower role, and unauthenticated.
- Horizontal (IDOR): with organizer A, read/update/delete organizer B's resources by swapping IDs in path, query, body and nested routes; also in bulk endpoints, exports and file downloads.
- Mass assignment: add `role`, `ownerId`, `status`, `price`, `isVerified`, `deletedAt` to create/update bodies.
- UI-only restrictions: actions hidden in the UI but callable directly.
- Response over-sharing: compare fields returned to each role against the allowed list.

## C. Injection
- In every string input: SQL fragments (`' OR '1'='1`), operators in JSON (`{"$ne": null}`), template syntax (`{{7*7}}`), HTML/JS (`<img src=x onerror=alert(1)>`), very long strings, Unicode edge cases, null bytes.
- Stored XSS: save payloads in names, descriptions, comments; view them in every panel (especially admin) and in emails.
- CSV export formula injection (`=HYPERLINK(...)`).
- Path traversal in file names and download IDs (`../../etc/passwd`).
- Header and email injection via newlines in names/subjects.

## D. CSRF and CORS
- Cross-origin form POST to state-changing endpoints with the victim's cookie and no CSRF token.
- `Origin: https://evil.example` → check the response does not reflect it in `Access-Control-Allow-Origin` with credentials.

## E. Rate limits, CAPTCHA and bot defence
- Exceed each tier; then try to reset counters by rotating `X-Forwarded-For`, changing email case/whitespace, adding `+tag` to emails, switching between web and mobile endpoints.
- Submit without CAPTCHA token, with a garbage token, and reuse a valid token.
- Fill the honeypot; submit faster than the minimum time.
- Parallel bursts (50 requests at once) to beat non-atomic counters.

## F. Business logic and races
- Concurrent purchase/booking/check-in of the last unit (20–50 parallel requests) → exactly one success.
- Negative, zero, fractional and huge quantities; price, discount or total sent from the client.
- Coupon/voucher reuse, stacking, use after expiry.
- Skipping state transitions (cancel after check-in, confirm without payment, refund twice).
- Time tricks: booking past events, changing time zones, editing locked records (e.g. attendance after day lock).

## G. File uploads
- Oversized files, wrong content type with right extension, double extensions, polyglot image/HTML, SVG with script, ZIP bombs if archives are accepted, `../` in names. Check stored location and how files are served.

## H. Information disclosure
- Force errors (bad JSON, wrong types, missing fields) → no stack traces, SQL, paths or versions.
- Probe `/.env`, `/.git/`, `/swagger`, `/docs`, `/graphql`, `/debug`, `*.map`, backup files.
- Grep the production web build for secrets and private env names.
- Check `Server`/`X-Powered-By` headers and verbose health endpoints.

## I. Resource exhaustion (bounded)
- Very large JSON bodies, deep nesting, huge arrays, `limit=100000`, expensive search terms, regex-heavy inputs, export of everything. Expect 400/413/capped results and response times that stay flat.

## J. Dependencies, secrets, static analysis
```bash
pnpm audit:deps
docker run --rm -v "$PWD":/repo zricethezav/gitleaks:latest detect -s /repo --no-banner
docker run --rm -v "$PWD":/src semgrep/semgrep semgrep scan --config p/owasp-top-ten --config p/typescript --error /src
```
Verify image names on first use (they change occasionally). Treat High/Critical results as findings.

## K. Automated DAST (OWASP ZAP)
```bash
# Linux: --network host and http://localhost:PORT ; macOS/Windows: http://host.docker.internal:PORT
docker run --rm -v "$PWD/tests/security/zap":/zap/wrk ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://host.docker.internal:{{WEB_PORT}} -r web-baseline.html
docker run --rm -v "$PWD/tests/security/zap":/zap/wrk ghcr.io/zaproxy/zaproxy:stable \
  zap-api-scan.py -t /zap/wrk/openapi.json -f openapi -r api-scan.html
```
Copy the OpenAPI spec into `tests/security/zap/` first and set its server URL to the local API. Triage alerts: real issues become findings; false positives are noted in the report with the reason.

## Turning attacks into permanent tests

Every attack above that applies to this product gets a test in `tests/security/` (API attacks with Supertest or Playwright's request context, browser attacks with Playwright). Group by letter: `a-authentication.spec.ts`, `b-authorization.spec.ts`, and so on, plus `permission-matrix.spec.ts`. `pnpm test:security` runs them all against the local stack and runs in CI on every pull request, so a regression is caught the moment it is introduced.
