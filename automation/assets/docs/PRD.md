# {{PROJECT_NAME}} — Product Requirements Document

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | {{DATE}} |
| Platform | {{PLATFORM}} |
| Status | Draft |

## 1. Summary

<!-- AUTO: 3–5 sentences: what the product is, who uses it, the problem it solves, and the outcome it delivers. -->

## 2. Goals and non-goals

### Goals
<!-- AUTO: 3–6 measurable goals, e.g. "An organizer can publish an event in under 3 minutes". -->

### Non-goals
<!-- AUTO: what this release deliberately does not do. -->

## 3. Users and roles

| Role | Who they are | Main permissions | Panel / app |
|---|---|---|---|
<!-- AUTO: one row per role, including public visitor if anything is visible without login. -->

## 4. Feature inventory

IDs are stable for the life of the project: `F-<MODULE>-<NN>`.

| ID | Module | Feature | Functions (what the user can do) | Roles | Priority | Release |
|---|---|---|---|---|---|---|
<!-- AUTO: full inventory from research. Priority: Must / Should / Could. Release: MVP / v1.1 / Later. -->

## 5. User stories and acceptance criteria

<!-- AUTO: one block per Must and Should feature, in this shape:

### F-XXX-01 Feature name
As a <role>, I want <capability>, so that <benefit>.
- AC1: Given <state>, when <action>, then <result>.
- AC2: Given <unauthorised role>, when <action>, then the request is rejected with 403.
Edge cases: <empty, limits, concurrency, invalid input>
-->

## 6. Key user flows

<!-- AUTO: one Mermaid flowchart or numbered list per role's main journey. -->

## 7. Business rules

| ID | Rule | Enforced by |
|---|---|---|
<!-- AUTO: invariants that must never break (BR-01…), and where: DB constraint, transaction/lock, service check. -->

## 8. Non-functional requirements

| Area | Target |
|---|---|
| Performance | <!-- AUTO: e.g. LCP < 2.5 s on 4G, API p95 < 300 ms --> |
| Scale | <!-- AUTO: users, records, concurrent sessions --> |
| Availability & backups | <!-- AUTO --> |
| Security | Follows `.claude/skills/auth-security/references/security-baseline.md` (OWASP ASVS L2 target) |
| Privacy & retention | <!-- AUTO: PII collected, retention period, deletion requests --> |
| Accessibility | WCAG 2.2 AA |
| i18n | <!-- AUTO: languages, date/currency formats --> |
| Browsers & devices | <!-- AUTO --> |

## 9. Notifications and integrations

<!-- AUTO: each notification (trigger, channel, recipient) and each external service (purpose, provider, sandbox available?). -->

## 10. Reports and analytics

<!-- AUTO: dashboards per role, exports, metrics. -->

## 11. Release plan

<!-- AUTO: MVP scope (Must + Should), v1.1, Later (Could). -->

## 12. Assumptions and open questions

<!-- AUTO: every decision made without asking the user, so they can review it. Mark each Assumption or Open. -->

## 13. Research sources

<!-- AUTO: links to products, open-source projects and articles consulted. -->
