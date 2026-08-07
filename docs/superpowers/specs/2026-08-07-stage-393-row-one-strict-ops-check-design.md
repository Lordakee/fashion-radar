# Stage 393 ROW ONE Strict Operations Check Design

## Goal

Make the existing local ROW ONE operations diagnostic usable as an automation
postcondition. An operator or timer wrapper should be able to distinguish a
healthy, current, serving site from a diagnostic that needs attention without
parsing human output or treating every successful command invocation as a
healthy result.

This closes the operations gap after the collect -> match -> report -> publish
pipeline: Stage 392 prevents an unacceptable refresh from publishing, while
Stage 393 lets a caller fail explicitly when the published site or its local
runtime evidence is not healthy.

## Problem

`row-one ops-check` already reports site presence, runtime freshness, server
reachability, local article routes/content, and the presence of canonical
systemd filenames. Its default command is intentionally diagnostic and exits
successfully even for `attention` or `unknown` statuses. That is useful for
human inspection but unsuitable for a shell or scheduled post-refresh health
gate. The command currently has no explicit strict mode, so callers must parse
JSON or text themselves.

The top-level health derivation also treats any nested local-article status
other than `missing` as acceptable. The current producers emit only
`ready`, `not_applicable`, or `missing`; accepting an unknown future value would
silently turn an unrecognized diagnostic into a healthy top-level result.

## Decision

Add an opt-in `--strict` flag to `row-one ops-check`.

- Without `--strict`, preserve the existing diagnostic behavior and exit status.
- With `--strict`, print the same selected text or JSON diagnostic first, then
  exit `0` only when the top-level status is the canonical healthy status
  `site_ready_scheduler_unverified`.
- With `--strict`, `attention` and `unknown` statuses exit `1` after output.
- If payload construction fails, the existing `ROW ONE ops check failed:` error
  and exit `1` remain unchanged.
- `--strict` does not change the payload shape, the `ok` field, server probing,
  systemd filename-only evidence, or any generated site contract.

Define the healthy status once in `row_one.ops_check` and use that constant as
the `_overall_status` return value and as the comparison target inside the CLI
strict predicate. The pure predicate accepts a payload status and returns
whether it is strictly healthy; it performs no I/O. It must return false for a
missing key, `None`, an empty value, or any unrecognized string. The local
article route/content allowlist is a separate known set `{ready,
not_applicable}` used only by `_overall_status`; it is not the CLI strict
predicate.

## CLI Contract

Examples:

```bash
fashion-radar row-one ops-check --strict
fashion-radar row-one ops-check --strict --json
```

The command prints the same diagnostic in either mode. The strict decision is
made after printing so a failed automation step retains actionable evidence in
its captured output. The deliberate `typer.Exit(1)` must be raised outside the
existing `try/except Exception` block; otherwise it would be caught as
`ROW ONE ops check failed:` and corrupt the strict contract. `--json` remains
valid machine-readable JSON; no status field is added or renamed, and ordinary
`--json` and `--strict --json` stdout are byte-identical for the same payload.
A caller can use the process exit status as the gate and retain stdout as the
diagnostic record.

The default `ops-check` command remains read-only. Strict mode does not start,
stop, refresh, publish, install, enable, or inspect live systemd manager state.

## Status Semantics

The only strict success is:

```text
site_ready_scheduler_unverified
```

This status means the local site evidence is current, the configured server
probe sees ROW ONE, canonical unit filenames are present, and local article
health is `ready` or `not_applicable`. The existing `scheduler_unverified` suffix remains
intentional: filename presence does not prove systemd activation or the next
scheduled run.

`attention` and `unknown` are strict failures. The current diagnostic payload
and action suggestions remain the source of explanation. The pure status
helper must treat missing, empty, non-string, or any future status as false.
The payload's existing `ok: true` means that diagnostic construction
succeeded; it does not mean that the site is healthy. Strict JSON consumers
must gate on the process exit code, not on `ok` alone.

## Compatibility And Non-Goals

This stage does not change the default exit behavior, existing payload keys,
generated app/runtime/manifest contracts, report files, source collection,
matching, scoring, ranking, scheduling installation, server lifecycle, or
systemd probing. It does not add a daemon, remote monitoring, authentication,
deployment, or a new dependency.

## Verification

- Pure ops-check tests cover the canonical healthy status, `attention`,
  `unknown`, empty/non-string status, and strict local-article status allowlist.
- CLI tests cover default permissive behavior, strict text success/failure,
  strict JSON success/failure, byte-identical ordinary/strict JSON output,
  output-before-exit ordering, the absence of the generic
  `ROW ONE ops check failed:` message on deliberate strict failure, `--help`
  exposing only `--strict` (not `--no-strict`), and construction failure
  behavior.
- Documentation tests cover the flag, exit semantics, unchanged default mode,
  and the scheduler-unverified boundary. Scheduled refresh snippets must not
  include `ops-check --strict` because this stage does not install a health
  gate automatically.
- Run focused tests, full pytest, Ruff, lock/sync checks, release hygiene,
  diff checks, package smoke checks, and fresh code/release review before
  publication.
