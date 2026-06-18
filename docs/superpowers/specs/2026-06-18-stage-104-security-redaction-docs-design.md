# Stage 104 Security Redaction Docs Design

## Goal

Add a standalone docs drift guard for the `## Redaction` section in
`SECURITY.md` so future edits keep sensitive-report guidance explicit: reporters
should redact tokens, cookies, secrets, private URLs, and local paths, trim logs
to the relevant error, and avoid attaching SQLite databases, generated reports,
browser profiles, or account/session files.

## Scope

Stage 104 is docs-test-only. It creates one focused pytest module that reads the
existing security policy, extracts the `## Redaction` section, normalizes
whitespace and case, and asserts redaction guidance phrases.

Allowed changes:

- `tests/test_security_docs.py`
- Stage 104 spec, plan, and review artifacts

Out of scope:

- `SECURITY.md` source text
- issue templates, GitHub private vulnerability reporting settings, release
  hygiene rules, packaging metadata, archive contents, `.gitignore`, secret
  scanners, runtime security behavior, CLI behavior, schemas, configs,
  dependencies, CI, or `uv.lock`
- broad `SECURITY.md` parity checks across `## Reporting`, `## Scope`, or
  `## Dashboard Boundary`
- compliance/audit/legal review product features

## Boundary Phrases

The guard should extract only `## Redaction` and assert these phrases after
whitespace collapse and case-folding:

- `When reporting:`
- `replace tokens, cookies, and secrets with `[REDACTED]``
- `redact private URLs and local paths if needed`
- `trim logs to the relevant error`
- `do not attach SQLite databases, generated reports, browser profiles, or account/session files`

These phrases pin public security reporting redaction guidance without expanding
into package metadata checks, release hygiene, runtime security features, or
private vulnerability reporting configuration.

## Test Shape

Use the same lightweight pattern as recent docs-boundary stages:

- stdlib-only imports
- repository root derived from `Path(__file__).resolve().parents[1]`
- helper to read `SECURITY.md`
- helper to normalize whitespace and case
- helper to extract one Markdown `##` section
- one test function with a focused phrase loop

The test must not import application modules, execute CLI commands, run security
scanners, inspect git credentials, read or write data/report files, fetch
network resources, or write files.

## Verification

Focused verification should cover the new docs guard, adjacent package
metadata/archive tests that reference `SECURITY.md`, ruff, formatting, and
whitespace checks. Full verification before commit should reuse the repository
release gate: release hygiene, full pytest with proxy vars unset, repo-wide ruff
check and format check, lockfile check, mirror URL scan, `uv.lock`/
`pyproject.toml` diff guard, staged hygiene, and staged secret scan.

## Risks

`SECURITY.md` also contains `## Reporting`, `## Scope`, and
`## Dashboard Boundary`. Stage 104 deliberately scopes to `## Redaction` only so
the guard does not duplicate packaging metadata checks or dashboard boundary
docs.

The section includes sensitive terms (`tokens`, `cookies`, `secrets`,
`SQLite databases`, `browser profiles`, `account/session files`) as negative
reporting guidance. In this stage those terms are allowed only in docs and
tests that pin redaction wording.

Phrase assertions may need deliberate updates if the security policy is
rewritten. That is acceptable because the goal is to catch accidental drift from
the public redaction guidance.
