# AUTOMATION_STATUS — {{PROJECT_NAME}}

Slug: `{{PROJECT_SLUG}}` · Platform: {{PLATFORM}} · Created: {{DATE}}
Automation skill: `{{SKILL_DIR}}` · Knowledge: `{{KNOWLEDGE_DIR}}`
Ports: web {{WEB_PORT}} · api {{API_PORT}} · db {{DB_PORT}} · redis {{REDIS_PORT}} · mail {{MAIL_PORT}}/{{MAIL_UI_PORT}}

Tick a box only after its exit check has passed. Any agent resuming work starts at the first unticked box.

## Phases

- [x] 0. Intake
- [ ] 1. Feature research (docs/research/notes.md, inventory ready)
- [ ] 2. Stack selected and versions verified (ADR 0001)
- [x] 3. Scaffold
- [ ] 4. Docs: PRD
- [ ] 4. Docs: DESIGN_SYSTEM
- [ ] 4. Docs: ARCHITECTURE
- [ ] 4. Docs: DATABASE
- [ ] 4. Docs: API
- [ ] 4. Docs: AGENTS
- [ ] 4. Docs: README
- [ ] 5. Project skills tailored to this stack
- [ ] 6.1 Setup and initialisation (`pnpm verify` green on empty apps)
- [ ] 6.2 Security foundation (auth, RBAC, rate limits, CAPTCHA, headers)
- [ ] 6.3 Data layer (schema, migrations, seed)
- [ ] 6.4 Features (see list below)
- [ ] 6.5 Integrations
- [ ] 6.6 MCP connection
- [ ] 6.7 Testing and QA (`pnpm verify && pnpm test:e2e` green)
- [ ] 7. Hardening checklist complete
- [ ] 8. Red team: no open Critical/High; `pnpm test:security` green
- [ ] 9. Final verification (clean-clone quick start, validate_project.py passes)
- [ ] 10. Lessons from this project recorded in the knowledge inbox (`learn.py add`)

## Features

<!-- AUTO: one checkbox per Must/Should feature ID from the PRD, e.g.
- [ ] F-EVT-01 Create event
-->

## Decisions made without asking

<!-- AUTO: date — decision — where recorded (ADR/PRD §12). -->

## Notes for the next session

<!-- AUTO: anything a fresh agent must know to continue (blockers, half-done work, branch names). -->
