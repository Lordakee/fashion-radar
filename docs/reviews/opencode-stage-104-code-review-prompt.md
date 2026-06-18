# Stage 104 Code Review Prompt

Review the Stage 104 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 104 adds `tests/test_security_docs.py`, a standalone docs drift guard for
the `## Redaction` section in `SECURITY.md`. It asserts that security reporting
guidance keeps explicit instructions to redact tokens, cookies, secrets, private
URLs, and local paths; trim logs to the relevant error; and avoid attaching
SQLite databases, generated reports, browser profiles, or account/session files.

## Files To Review

- `tests/test_security_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-104-security-redaction-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-104-security-redaction-docs-plan.md`
- `docs/reviews/opencode-stage-104-plan-review-prompt.md`
- `docs/reviews/opencode-stage-104-plan-review.md`

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

Do not propose security scanners, credential inspection, release-hygiene
behavior, packaging metadata changes, issue template changes, connector
behavior, platform search, social monitoring, scraping automation,
browser/account/proxy/CAPTCHA/paywall flows, dashboard/report behavior,
compliance/audit/legal review product features, or runtime validation.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_security_docs.py -q
uv --no-config run --frozen pytest tests/test_security_docs.py tests/test_package_archives.py tests/test_package_metadata.py -q
uv --no-config run --frozen ruff check tests/test_security_docs.py
uv --no-config run --frozen ruff format --check tests/test_security_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 104 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `SECURITY.md` `## Redaction` section?
3. Is the new standalone test independent from package metadata/archive tests,
   upload-checklist docs, and release-hygiene behavior?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
