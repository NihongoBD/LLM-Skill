# {{PROJECT_NAME}} — Security Report

Red-team assessment of the project's own local build. Playbook: `.claude/skills/auth-security/references/red-team.md`.

## Scope

- Target: `http://localhost:{{WEB_PORT}}` (web) and `http://localhost:{{API_PORT}}` (API), Docker Compose project `{{PROJECT_SLUG}}`.
- Out of scope: every external host, third-party API and production system.
- Test accounts: seeded role accounts only.
- Date(s): <!-- AUTO: dates of each round -->

## Summary

| Severity | Found | Fixed | Accepted (with reason) | Open |
|---|---|---|---|---|
| Critical | 0 | 0 | 0 | 0 |
| High | 0 | 0 | 0 | 0 |
| Medium | 0 | 0 | 0 | 0 |
| Low | 0 | 0 | 0 | 0 |

Exit criteria: no open Critical or High; every Medium fixed or accepted with a written reason; `pnpm test:security` green.

## Tooling results

| Tool | Result | Notes |
|---|---|---|
| Dependency audit | <!-- AUTO --> | |
| Secret scan (gitleaks) | <!-- AUTO --> | |
| Static analysis (semgrep) | <!-- AUTO --> | |
| DAST (OWASP ZAP baseline) | <!-- AUTO --> | |
| Container scan (if images built) | <!-- AUTO --> | |

## Findings

<!-- Copy this block per finding. Status: Open | Fixed | Verified | Accepted.

### SEC-001 — <short title>
- Severity: Critical | High | Medium | Low
- Category: e.g. Broken access control (IDOR)
- Location: endpoint / file:line
- Reproduction: numbered steps or the test name in tests/security/
- Impact: what an attacker gains
- Fix: what changed (commit hash)
- Regression test: tests/security/<file>
- Lesson: docs/solutions/<file>
- Status: Open
-->

_No findings recorded yet._
