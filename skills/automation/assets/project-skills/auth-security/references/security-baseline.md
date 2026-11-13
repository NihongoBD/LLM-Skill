# Security baseline — {{PROJECT_NAME}}

Target: OWASP ASVS Level 2, covering the OWASP Top 10. Each control lists what to build and the test that proves it. A control without a passing test is not done.

## Contents
1. Authentication · 2. Sessions and tokens · 3. Authorisation · 4. Input validation and injection · 5. Output, XSS and headers · 6. CSRF and CORS · 7. Rate limiting · 8. CAPTCHA and bot defence · 9. File uploads · 10. Business logic and concurrency · 11. Payments and webhooks · 12. Outbound requests (SSRF) · 13. Secrets and configuration · 14. Data protection and privacy · 15. Logging, audit and monitoring · 16. Errors · 17. Dependencies and supply chain · 18. Frontend specifics · 19. Infrastructure

## 1. Authentication
Build:
- Passwords hashed with argon2id (at least OWASP's minimum: 19 MiB memory, 2 iterations, parallelism 1; raise if login stays fast).
- Password policy: minimum 8 characters (12 for admin roles), allow at least 64, block common and breached passwords, no composition rules, no forced periodic change.
- Email verification before sensitive actions; verification and reset tokens are random (≥128 bits), stored hashed, single-use, expire (15–60 min).
- Identical response and similar timing for "unknown account" and "wrong password"; signup and reset never reveal whether an email exists.
- Progressive delay and temporary account lock after repeated failures (also rate limited per IP, see §7).
- MFA (TOTP) required for admin roles; recovery codes stored hashed; MFA reset requires re-authentication.
- Re-authentication for sensitive actions (change email/password, disable MFA, delete account).
Test: brute force hits 429/lock; enumeration responses identical; reset token reuse and expiry rejected; admin login without MFA fails.

## 2. Sessions and tokens
Build:
- Browser: cookies with `__Host-` prefix, `Secure`, `HttpOnly`, `SameSite=Lax` (or `Strict` for admin panels), `Path=/`.
- Either server-side sessions in Redis, or a short access token (≤15 min) plus a rotating refresh token (stored hashed, one family per login, reuse of an old refresh token revokes the whole family).
- If JWTs are used: fixed algorithm allowlist, verify signature, `exp`, `iss`, `aud`; never trust role claims without checking the user still has that role.
- New session ID on login and privilege change; logout and password change revoke sessions; session list with "sign out other devices".
- Mobile clients: tokens in secure storage (Keychain/Keystore), never in plain storage.
Test: tampered token, `alg: none`, expired token and replayed refresh token are rejected; logout invalidates server-side.

## 3. Authorisation
Build:
- Deny by default: every route declares its roles; a lint rule or test fails if a route has no guard decision.
- Ownership checked in the service layer for every record access (owner, or admin), including nested resources and bulk operations.
- Admin actions that change roles or delete data require confirmation and are audit-logged.
- Output filtered per role (an organizer never receives another organizer's attendee emails).
Test: the permission matrix (every endpoint × every role); IDOR tests with a second user of the same role; mass-assignment test sending `role`, `ownerId`, `isVerified`, `price` in bodies.

## 4. Input validation and injection
Build:
- Schema validation on every input (body, query, params, headers used, files, webhooks, queue jobs, env), with lengths, formats and enums; unknown fields rejected.
- ORM parameterised queries only; raw SQL only with bound parameters and a code comment explaining why.
- Sort and filter fields from an allowlist; `limit` capped.
- CSV/Excel exports neutralise cells starting with `=`, `+`, `-`, `@`, tab or carriage return.
- Email templates escape user content; no header injection (newlines rejected in names/subjects).
- File paths never built from user input; IDs map to stored paths.
Test: injection payloads in every string field produce 400 or are stored inertly; export formula test; path traversal test.

## 5. Output, XSS and security headers
Build:
- Framework auto-escaping; no raw HTML rendering unless sanitised with DOMPurify and an allowlist.
- CSP with nonces: `default-src 'self'; script-src 'self' 'nonce-…' 'strict-dynamic'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'`, plus only the CAPTCHA provider's required origins.
- Headers: HSTS (with preload once HTTPS is permanent), `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` disabling unused features, `Cross-Origin-Opener-Policy: same-origin`.
- No user-controlled URLs in `href`/`src` without scheme allowlist (`https:`, `mailto:`).
Test: stored XSS payload in every rich/text field renders as text; header test asserts each header on web and API.

## 6. CSRF and CORS
Build:
- Cookie-authenticated state-changing requests require a CSRF token (synchronizer or double-submit) and a matching `Origin`/`Referer`.
- CORS: explicit origin allowlist from env, credentials only for those origins, never reflect arbitrary `Origin`, never `*` with credentials.
Test: cross-origin POST without token fails; `Origin: https://evil.example` gets no CORS allow headers.

## 7. Rate limiting
Build:
- Redis-backed sliding window shared by all instances.
- Tiers from `docs/API.md` §4: global per IP; auth per IP **and** per account; sensitive (signup, reset, OTP, email change); expensive (exports, reports, search) per user; write per user.
- Client IP from the trusted proxy chain only (configure trusted proxies; ignore client-sent `X-Forwarded-For` otherwise).
- 429 with `Retry-After` and `RateLimit-*` headers.
- Temporary IP ban: repeated 429s or failed CAPTCHAs within a window add the IP to a Redis ban set with escalating TTL (e.g. 15 min → 1 h → 24 h); admins can view and lift bans; health checks are exempt.
Test: each tier triggers at its limit; spoofed `X-Forwarded-For` does not reset counters; changing email case does not reset per-account counters; ban applies and expires.

## 8. CAPTCHA and bot defence
Build:
- CAPTCHA (Cloudflare Turnstile or hCaptcha) on signup, password reset, public forms (contact, booking, reviews), and on login after a few failures.
- Verify server-side with the secret key: check success, expected hostname and action, and reject reused tokens. Use the provider's official test keys in dev/test.
- Honeypot field and minimum time-to-submit on public forms; silent reject on trigger.
- Disposable-email and obvious automation signals can raise CAPTCHA difficulty or trigger review.
Test: missing, invalid and reused tokens rejected; honeypot submissions dropped.

## 9. File uploads
Build: size limit per type; type checked by magic bytes, not extension; random server-side names; stored outside the web root (private bucket); images re-encoded and metadata stripped; SVG and HTML rejected or sanitised; downloads with `Content-Disposition: attachment` and signed, expiring URLs; per-user storage quota.
Test: oversized, wrong-type, polyglot, SVG-with-script and `../` filename uploads rejected.

## 10. Business logic and concurrency
Build: server computes all prices, totals, discounts and capacities; state machines for orders/bookings/events with allowed transitions only; transactions with row locks or atomic conditional updates for capacity, stock and seats; unique constraints for "once only" actions (one check-in per ticket, one coupon use per user); quantities validated (positive, max).
Test: 20 concurrent requests for the last seat produce exactly one success; skipping a state (pending → confirmed without payment) fails; negative and huge quantities rejected; client-sent price ignored.

## 11. Payments and webhooks
Build: amounts from the server; idempotency keys; payment confirmed only from a verified server-to-server callback or webhook (signature checked, timestamp window, event ID de-duplicated); never trust redirect query parameters as proof of payment.
Test: forged webhook (bad signature) rejected; replayed webhook processed once; success redirect without a verified payment does not confirm the order.

## 12. Outbound requests (SSRF)
Build: if the app fetches user-supplied URLs (webhooks, image import), use an allowlist or resolve and block private, loopback, link-local and metadata IP ranges, block redirects to them, set timeouts and size caps.
Test: `http://127.0.0.1`, `http://169.254.169.254` and DNS-rebinding style hostnames rejected.

## 13. Secrets and configuration
Build: secrets only in env (or a secret manager in production); `.env` git-ignored; `.env.example` without real values; env validated at boot; separate keys per environment; secret scanning in pre-commit and CI; rotate anything that was ever committed.
Test: gitleaks clean on full history; app refuses to start with missing secrets.

## 14. Data protection and privacy
Build: collect the minimum PII; classify data in `docs/DATABASE.md`; TLS everywhere outside localhost; encrypt especially sensitive fields at rest; least-privilege DB roles; backups encrypted and restore tested; account deletion and data export flows if the PRD requires; no PII in URLs.
Test: API responses for each role contain only allowed fields (snapshot tests).

## 15. Logging, audit and monitoring
Build: structured logs with request IDs; redact passwords, tokens, cookies, authorization headers and card data; log security events (login success/failure, lockouts, MFA changes, role changes, permission denials, rate-limit bans); append-only audit log table for admin actions with actor, action, target, before/after, IP, time.
Test: log output for a login request contains no password or token; role change creates an audit entry.

## 16. Errors
Build: one exception filter; problem+json; generic messages for 500s; no stack traces, SQL or file paths in responses; framework debug pages, Swagger UI and source maps disabled or protected in production.
Test: forced 500 returns a generic body; `/docs` and `*.map` not reachable with production config.

## 17. Dependencies and supply chain
Build: exact versions and lockfile; new packages verified as official and maintained; minimum release age 14 days; install scripts allowlisted; `pnpm audit:deps` (and osv-scanner) in CI failing on High/Critical; Renovate/Dependabot; CI actions pinned by SHA; no `curl | sh` in scripts.
Test: CI job runs the audit and fails on a known-vulnerable fixture.

## 18. Frontend specifics
Build: no secrets in client-exposed env vars (e.g. `NEXT_PUBLIC_*`); auth decisions never only in the client; third-party scripts minimised, loaded with integrity where possible and allowed in CSP; `rel="noopener noreferrer"` on external links; clickjacking blocked by `frame-ancestors`.
Test: grep the production build output for secret-looking strings and private env names.

## 19. Infrastructure
Build: multi-stage Docker images, non-root user, read-only filesystem where possible, no secrets baked into images, healthchecks; databases not exposed publicly (local compose binds to 127.0.0.1); HTTPS termination with modern TLS in production.
Test: container runs as non-root; image scan (e.g. Trivy) has no Critical findings.
