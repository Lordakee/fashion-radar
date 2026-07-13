# Stage 389 Daily Operations Reliability Design

## Goal

Make the local daily ROW ONE workflow truthful and observable: mandatory
SQLite retention failure must be visible to schedulers, systemd previews and
installation must have one canonical shape, and the operations check must
describe exactly what it can prove without interpreting host-managed systemd
state. Align public wording with the shipped local source-diversity scorer and
the first-run smoke that already exists.

## Context

A subsequent source and compliance audit identified six current mismatches:

- The Project Brief promises cross-platform heat spread, while scoring uses
  distinct source_name values in configured local data.
- row-one refresh prints a non-skipped SQLite retention error but exits 0.
- row-one schedule --mode systemd emits legacy two-unit headings, while
  install-local already generates the canonical refresh service, refresh timer,
  and fixed serve service.
- Default ops-check turns the presence of three files into ready, despite
  neither inspecting the host user manager nor proving a future timer run.
- The first-run guide says the smoke only checks dry-run serving even though it
  starts a temporary local server and fetches generated routes.
- User-systemd guidance omits the lingering prerequisite for unattended work
  after logout or boot.

## Considered Approaches

### A. Documentation-only correction

This would correct user-facing wording but leave schedulers unable to observe a
required retention failure and leave schedule previews inconsistent with local
installation. Reject.

### B. Bounded local reliability correction

Keep the local-only architecture and make deterministic changes:

- Describe local source diversity rather than platform spread.
- Preserve generated artifacts and diagnostics, then return nonzero for a
  required SQLite retention failure.
- Use one ordered canonical systemd unit definition for preview, installation,
  and filename evidence.
- Make ops-check identify only canonical unit filenames and explicitly label
  scheduler execution as unverified.
- Document manual lingering, manual activation, and the real temporary HTTP
  smoke.

This is the selected approach. It improves a daily 04:00 local workflow without
adding account access, deployment automation, external monitoring, or source
collection.

### C. Static systemd directive parser

A parser could look for ExecStart, OnCalendar, and Persistent fields and call
the result configured. That would recreate only a brittle subset of systemd
semantics: resets, command substitutions, invalid values, drop-ins, and
user-manager state remain outside Fashion Radar's authority. Reject.

### D. Automatic activation or live systemd probing

Having Fashion Radar call loginctl, systemctl, or enable units would be
host-specific, may require authorization, and still could not prove future
scheduled refreshes will succeed. Reject. Operators own activation and live
verification.

## Design

### Scoring Contract

The Product Brief will state:

~~~
Score local heat changes using mention volume, recent growth, source weight,
and source diversity across configured sources and imported local signals.
~~~

The scoring guide will state that imported item platform labels are local
provenance for review output only. They do not affect heat scores or establish
platform coverage. No scoring model, schema, configuration key, or report
calculation changes.

### Retention Completion Contract

row-one refresh continues to collect, match, write reports, build the site, and
prune stale dated reports before item retention. If non-skipped SQLite retention
fails, it preserves every generated artifact and normal diagnostic, prints
SQLite retention: failed: <reason>, then exits 1 only after the final site access
output. It must not print the pipeline-wide ROW ONE refresh failed message. A
successful run and an explicit --skip-data-retention remain 0.

This gives cron and systemd a truthful process result while leaving the rendered
site available for diagnosis.

### Canonical Systemd Preview And Installation

One shared ordered definition owns these names:

1. row-one-refresh.service
2. row-one-refresh.timer
3. row-one-serve.service

row-one schedule --mode systemd becomes a no-write preview of the same three
payloads that row-one install-local --dry-run uses, including the selected serve
host and port. It does not change the unrelated generic
schedule-example --mode systemd command. The implicit same-basename
timer-to-service binding remains unchanged; no timer Unit override is added.

The CLI does not invoke systemctl, loginctl, or enable services. Guides will
show manual commands for an operator to inspect lingering, enable it where host
policy permits, reload the user manager, enable the timer and serve unit, and
inspect their state.

### Ops-Check Evidence Boundary

Default row-one ops-check remains local, read-only, and intentionally narrow.
It will inspect exactly the three canonical primary filenames with Path.is_file
and will not read or parse their contents. It will not inspect drop-ins, call
systemctl or loginctl, query user-manager status, verify enablement, or prove a
future scheduled refresh.

Its systemd payload is an evidence record:

~~~json
{
  "status": "unit_files_present",
  "verification": "filenames_only"
}
~~~

when every canonical path is a file. The existing units boolean map remains for
compatibility. If any canonical filename is absent, systemd.status stays
missing, verification remains filenames_only, and the existing install-local
inspection action is returned. Arbitrary, malformed, unrelated, or empty
contents in present files deliberately produce the same unit_files_present
evidence: Fashion Radar makes no static configuration claim.

When the generated site, freshness, server response, local article route and
content checks are otherwise healthy and the filenames are present, the sole
positive top-level status becomes:

~~~
site_ready_scheduler_unverified
~~~

This means the local site is ready and expected unit filenames exist. It does
not mean the unit contents are valid, the user manager is running, the units are
enabled or active, or the next refresh will succeed. attention retains its
existing precedence for stale, missing, invalid, unreachable, or incomplete site
evidence and for missing filenames; unknown retains its existing role for
incomplete runtime evidence. Nested local-article health payloads may continue
to use their existing ready enum because they describe a different contract.

Human text output will display the filenames-only evidence and explicitly say
that scheduler state is not verified. The command retains its current diagnostic
exit behavior: it returns payload output rather than failing merely because a
diagnostic status is attention.

### First-Run Smoke Documentation

The first-run guide will state both verified behaviors: the smoke checks the
dry-run URL path and starts a temporary local HTTP server, fetches representative
generated routes, then terminates that temporary process. It does not claim the
smoke only uses dry-run serving or leaves a long-running server behind.

## Compatibility And Scope

The two changed ops-check enums are visible in the CLI JSON and text output:
top-level ready becomes site_ready_scheduler_unverified, and systemd present
becomes unit_files_present with an additive verification field. The changelog
and documentation will call out this intentional truthfulness correction. ok:
true, the units map, and diagnostic command exit behavior remain unchanged.

Stage 389 does not add platform-spread scoring, platform connectors, browser
automation, automatic job installation, activation, privileged commands,
background daemons, external services, LLM calls, schemas, or generated-site
data-contract changes.

## Validation

- CLI tests prove a retention failure exits 1 after all report/site output.
- Scheduling tests prove systemd preview and install-local --dry-run use the
  same canonical ordered payloads and carry host/port.
- Ops-check tests prove file names alone yield unit_files_present,
  filenames_only, and site_ready_scheduler_unverified; a direct helper test
  makes unit-file content-read APIs fail; missing names yield attention and
  exact install guidance; unrelated contents are not parsed.
- Documentation tests pin scoring provenance, manual operator guidance,
  filenames-only boundaries, and temporary HTTP smoke wording.
- Archive tests make every newly changed public guide an explicit sdist
  requirement.
- Full tests, Ruff, release hygiene, first-run smoke, public lock validation,
  package validation, and isolated installed-wheel checks run before publication.
