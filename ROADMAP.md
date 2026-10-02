# AI Developer Roadmap

This roadmap is the execution queue for the daily AI developer workflow. Work is performed in small, reviewable increments on a separate branch and proposed through a pull request. Never commit generated application changes directly to `main`.

## Priority 0 — Security and correctness
- [ ] Add authentication and authorization.
- [ ] Add per-user/tenant ownership and enforce it on link operations.
- [ ] Add request validation and safe error handling.
- [ ] Add IP/account rate limiting and abuse controls.
- [ ] Add security headers and secure proxy configuration.
- [ ] Add secret/configuration hygiene checks.
- [ ] Add dependency and vulnerability scanning.

## Priority 1 — Test coverage and reliability
- [ ] Expand API integration tests for create/list/detail/delete/redirect flows.
- [ ] Add expiry and disabled-link tests.
- [ ] Add database tests for SQLite and PostgreSQL-compatible behavior.
- [ ] Add negative/edge-case tests and regression tests for every bug fixed.
- [ ] Improve structured logging and health/readiness checks.

## Priority 2 — SaaS foundations
- [ ] Add user accounts and tenant isolation.
- [ ] Add link management/editing and bulk operations.
- [ ] Add pagination, filtering and search.
- [ ] Add analytics summaries and export.
- [ ] Add database migrations with Alembic.

## Priority 3 — Product improvements
- [ ] Improve dashboard UX and accessibility.
- [ ] Add custom domains/domain verification.
- [ ] Add QR-code generation.
- [ ] Add API keys and API usage limits.
- [ ] Add admin moderation and abuse-report workflows.

## Priority 4 — Operations
- [ ] Improve Docker production configuration.
- [ ] Add observability, metrics and error monitoring hooks.
- [ ] Add backup/restore documentation.
- [ ] Review performance and caching opportunities.

## Daily agent rules
1. Select the highest-priority unchecked item that can be completed safely in one PR.
2. Inspect the existing architecture before changing it.
3. Add or update tests for every behavior change and bug fix.
4. Run the full test suite before committing.
5. Do not expose, create, rotate, or commit secrets.
6. Do not make destructive database or infrastructure changes without explicit human approval.
7. Keep changes focused; do not rewrite unrelated code.
8. Create a separate branch and pull request; never push application changes directly to `main`.
9. If tests fail or the task is ambiguous, stop and explain the blocker rather than forcing a merge.
