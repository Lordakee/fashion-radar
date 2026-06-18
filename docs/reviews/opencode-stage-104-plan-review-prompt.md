# Stage 104 Plan Review Prompt

Review the Stage 104 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `SECURITY.md`, scoped only to the
`## Redaction` section, so sensitive-report guidance remains explicit about
redacting tokens, cookies, secrets, private URLs, local paths, and avoiding
attached SQLite databases, generated reports, browser profiles, or
account/session files.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-104-security-redaction-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-104-security-redaction-docs-plan.md`
- `SECURITY.md`

## Planned Test

The implementation will add `tests/test_security_docs.py` with one docs-only
test that extracts `## Redaction` and asserts:

- `When reporting:`
- `replace tokens, cookies, and secrets with `[REDACTED]``
- `redact private URLs and local paths if needed`
- `trim logs to the relevant error`
- `do not attach SQLite databases, generated reports, browser profiles, or account/session files`

## Scope Constraints

Allowed changes:

- `tests/test_security_docs.py`
- Stage 104 review artifacts

Disallowed changes:

- `SECURITY.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- issue templates
- `.gitignore`
- package metadata or archive tests
- `tests/test_cli_docs.py`
- runtime security, release hygiene, source acquisition, connector, scraping,
  browser automation, account/cookie/session/proxy/CAPTCHA/paywall, dashboard,
  report, or CLI tests

Do not expand this stage into security scanners, credential inspection,
release-hygiene behavior, packaging metadata changes, issue template changes,
connector behavior, platform search, social monitoring, scraping automation,
browser/account/proxy/CAPTCHA/paywall flows, dashboard/report behavior,
compliance/audit/legal review product features, or runtime validation.

## Review Questions

1. Does the plan protect a real `SECURITY.md` redaction boundary without changing
   product behavior or repository security settings?
2. Are the planned phrases present in `SECURITY.md` and scoped narrowly enough
   to `## Redaction`?
3. Does the plan avoid overlap with package metadata/archive tests, upload
   checklist wording, `SECURITY.md` reporting/scope/dashboard sections, and
   release-hygiene behavior?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
