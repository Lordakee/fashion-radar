# Security Policy

Fashion Radar is pre-1.0. Security support is best-effort on `main` and future
`0.1.x` tags.

## Reporting

Do not report sensitive issues in public issues if they include secrets,
cookies, session files, browser profiles, private source lists, private URLs,
local SQLite databases, generated reports, or exploit details.

Use GitHub private vulnerability reporting from this repository's **Security**
tab for sensitive security reports. Do not include sensitive details in public
issues.

If the Security tab is unavailable, open a minimal public issue that says a
private security contact is needed, without sensitive details.

## Scope

Security-relevant reports include:

- accidental secret, cookie, token, or session exposure
- unsafe file writes or path handling
- dashboard exposure risks
- dependency vulnerabilities
- behavior that bypasses source boundaries, robots rules, paywalls, CAPTCHAs,
  or login-cookie restrictions
- unsafe handling of local config/data/report directories

Unsupported connector requests, broad source-coverage complaints, and social
scraping requests are feature requests only if they respect the project
boundaries.

## Redaction

When reporting:

- replace tokens, cookies, and secrets with `[REDACTED]`
- redact private URLs and local paths if needed
- trim logs to the relevant error
- do not attach SQLite databases, generated reports, browser profiles, or
  account/session files

## Dashboard Boundary

The dashboard is read-only and binds to `127.0.0.1` by default. It has no
authentication layer. Binding it to another host may expose it on the network.
