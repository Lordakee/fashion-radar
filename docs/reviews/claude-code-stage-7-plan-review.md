# Claude Code Stage 7 Plan Review

Reviewed against local head `eb52d36`.

## Summary

Claude Code reviewed the Stage 7 design and plan against the existing CLI,
settings, source models, example configs, and tests. The goal is safe and useful
and the architecture fits the current project, but the initial plan contains one
Critical scheduling correctness issue and three Important implementation/test
gaps that must be fixed before Stage 7 implementation.

## Critical

1. `%` in the date format is mangled by both cron and systemd.
   A shared `$(date -u +%Y-%m-%dT%H:%M:%SZ)` string is invalid in cron because
   unescaped `%` becomes newline/stdin, and invalid in systemd because `%`
   expands unit specifiers. Cron needs `\%`; systemd needs `%%`; GitHub Actions
   can use raw `%`.

## Important

1. Updating the default source name away from `Vogue Business RSS` will break
   `tests/test_stage1_hardening.py`; the plan must update that test.
2. The cron example should account for cron's minimal `PATH`; otherwise `uv`
   may not be found.
3. `--time` has different timezone semantics by mode: cron/systemd use the
   machine local timezone, while GitHub Actions schedule cron is UTC. Docs and
   rendered snippets must state this.

## Minor

1. The new source-template sync test duplicates existing hardening coverage.
2. RSS endpoint availability is point-in-time and can rot; docs should say the
   source-pack check is not an ongoing guarantee.
3. Scheduling docs should explain that `run --as-of` uses the fire-time UTC
   timestamp for both collection time and report time.

## Verdict

**Approved after fixes.**

Fix the Critical and Important items before implementation.
