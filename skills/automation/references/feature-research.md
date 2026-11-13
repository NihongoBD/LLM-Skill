# Feature research

Goal: a complete, prioritised inventory of roles, modules, features and functions, good enough that PRD.md can be written from it without guessing.

## 1. Roles first

List every actor before any feature, because features are "who can do what". Typical sets:

- Event management: Super Admin, Admin, Organizer, Staff/Check-in, Attendee, Guest
- Attendance management: Admin, Teacher, Student, Parent/Guardian
- Restaurant management: Owner/Admin, Manager, Waiter, Kitchen, Cashier, Customer

If the topic names panels ("Admin & Organizer Panel"), each named panel is a role with its own UI area. Add the public visitor if anything is visible without login.

## 2. Research (5–10 searches per project)

Search for, in this order:

1. Leading commercial products in the category and their feature or pricing pages (pricing tiers reveal which features matter most).
2. Open-source projects on GitHub for the same domain (their README feature lists and issue trackers show real-world needs and edge cases).
3. "<domain> system requirements", "<domain> management system modules", "<domain> software features checklist".
4. Domain rules: regulations or norms that change the design (for example attendance privacy for minors, food-order tax and receipts, ticket refunds).

Extract ideas, never copy text. Keep a source list for PRD §13. Save notes to `docs/research/notes.md`.

## 3. Build the inventory

Structure: **Module → Feature → Functions**. A function is one thing a role can do ("Organizer duplicates an event"). Give each feature a stable ID `F-<MODULE>-<NN>`; these IDs are used in plans, tests and commits for the rest of the project.

| ID | Module | Feature | Functions | Roles | Priority | Release |
|---|---|---|---|---|---|---|
| F-EVT-01 | Events | Create event | Create draft, set date/venue/capacity, upload banner, publish/unpublish | Organizer | Must | MVP |
| F-EVT-02 | Events | Approve event | Review queue, approve/reject with reason, notify organizer | Admin | Must | MVP |
| F-TKT-03 | Tickets | QR check-in | Scan QR, validate once, offline queue, check-in stats | Staff | Should | MVP |

Priority rules:
- **Must**: the product is useless or unsafe without it. Built in MVP.
- **Should**: expected by real users. Built in MVP if time allows; automation builds them by default.
- **Could**: nice to have. Goes to the PRD backlog, not built.

## 4. Always include these cross-cutting modules

Most "management system" projects need them, and they are easy to forget:

- Authentication (signup, login, logout, email verification, password reset, optional MFA for admins)
- Roles and permissions (RBAC plus ownership: users touch only their own records)
- User and profile management, admin user management (invite, suspend, change role)
- Dashboard per role with the numbers that role cares about
- Search, filters, sorting and pagination on every list
- Notifications (in-app, email; SMS if the domain needs it)
- Audit log of admin and sensitive actions
- Settings (organisation, branding, preferences)
- Export (CSV/PDF) and reports
- File uploads where the domain needs them
- Accessibility (WCAG 2.2 AA) and i18n readiness
- Security features visible to users: session list, sign out other devices, CAPTCHA on public forms

## 5. Non-functional requirements

Record targets, not adjectives: page load (LCP under 2.5 s on 4G), API p95 latency, expected users and data volume, uptime, backup/restore, data retention, supported browsers and devices, languages.

## 6. Business rules and edge cases

For each module, list the rules that must never break, with IDs `BR-01…`. These become database constraints and tests. Examples: capacity can never be exceeded even under concurrent booking; an attendance record cannot be edited after the day is locked; an order total is always computed on the server.

## 7. Output

The inventory, roles, NFRs and business rules go straight into PRD.md sections 3, 4, 7 and 8. Anything you assumed goes into PRD §12 so the user can review it later.
