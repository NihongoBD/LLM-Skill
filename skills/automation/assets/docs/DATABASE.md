# {{PROJECT_NAME}} — Database

## 1. Engine and conventions

- Engine / ORM: <!-- AUTO: e.g. PostgreSQL + Prisma, versions from ARCHITECTURE.md -->
- Table names: snake_case plural; columns snake_case, mapped to camelCase in code.
- Primary keys: UUID (v7 preferred for index locality) unless a reason is recorded.
- Every table: `created_at`, `updated_at` (timestamptz, UTC). Soft delete with `deleted_at` only where recovery or audit needs it.
- Money: integer minor units + currency code; never floating point.
- Enums: database enums or check constraints, mirrored in shared types.
- Foreign keys always declared, with explicit `ON DELETE` behaviour.
- Indexes for every foreign key and every column used in filters, sorting or uniqueness.

## 2. Entity relationship diagram

<!-- AUTO: Mermaid erDiagram covering all tables. -->

## 3. Tables

<!-- AUTO: one section per table:

### table_name
Purpose: …
| Column | Type | Null | Default | Constraints | Notes |
|---|---|---|---|---|---|
Indexes: …
Used by features: F-…
-->

## 4. Business rules enforced in the database

| Rule | Mechanism |
|---|---|
<!-- AUTO: map BR-xx from the PRD to unique constraints, check constraints, exclusion constraints, or transaction + row lock (SELECT … FOR UPDATE) for capacity/stock/double-booking. -->

## 5. Data classification and retention

| Data | Class (public / internal / personal / sensitive) | Retention | Notes |
|---|---|---|---|
<!-- AUTO: passwords are argon2id hashes only; tokens stored hashed; note anything encrypted at rest. -->

## 6. Access

- Application user has only the privileges it needs (no superuser, no DDL at runtime).
- Migrations run with a separate migration role.
- Read-only role for reporting and for the dev MCP database server.

## 7. Migrations

- One migration per schema change, reviewed like code, never edited after merge.
- Destructive changes in two steps (expand → migrate data → contract).
- `pnpm db:reset` must succeed from zero at any commit.

## 8. Seed data (development and test only)

<!-- AUTO: one account per role (emails like admin@example.test; passwords from env SEED_PASSWORD), plus realistic sample data per module. Seed refuses to run when NODE_ENV=production. -->
