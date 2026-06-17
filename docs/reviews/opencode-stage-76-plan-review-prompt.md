# Stage 76 Plan Review Prompt

Review the Stage 76 design and implementation plan in
`/home/ubuntu/fashion-radar`:

- `docs/superpowers/specs/2026-06-18-stage-76-adapter-smoke-full-contract-design.md`
- `docs/superpowers/plans/2026-06-18-stage-76-adapter-smoke-full-contract-plan.md`

Use a planning/code-review stance. Lead with Critical or Important findings if
present; include Minor notes after. Do not propose adding scraping, connectors,
browser automation, platform APIs, login/cookie/session/token/proxy behavior,
CAPTCHA handling, media download, monitoring/scheduling, source acquisition,
demand proof, ranking, coverage verification, or compliance-review product
behavior.

For this stage, the user explicitly directed local review through
`opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`; this
stage-local review path does not change broader repository review protocol
documents.

## Goal

Harden the first-run smoke validator for `external-tool-adapters --format json`
so it catches drift in JSON key order, adapter descriptions, upstream tool
examples, field mappings, full recommended command strings, adapter boundaries,
and registry boundaries.

## Planned Scope

- Modify `scripts/check_first_run_smoke.py`.
- Modify `tests/test_first_run_smoke.py`.
- Add Stage 76 design/plan/review artifacts.
- Keep runtime CLI, adapter registry code, public docs, dependency manifests,
  and lockfiles unchanged.
- Preserve the single existing `external-tool-adapters --format json` smoke
  command in `run_first_run_flow()`.
- Set smoke-local `FASHION_RADAR_CONFIG_DIR=configs` and
  `FASHION_RADAR_DATA_DIR=data` so full recommended command validation is
  deterministic and does not depend on platformdirs user defaults.
- Keep generated recommended commands print-only: validate their strings, do
  not execute them.

## Review Questions

1. Does the plan cover the actual remaining first-run smoke validator gap after
   Stages 73-75?
2. Are the expected metadata, field mapping, full-command, boundary, and key
   order constants aligned with the current runtime registry/fixture contract?
3. Are the parameterized negative tests strong enough to prove the new validator
   checks are active without overloading the existing Stage 73 negative test?
4. Is it correct to avoid docs and `CHANGELOG.md` changes for this internal
   smoke/test hardening stage?
5. Does the plan avoid runtime behavior and external platform behavior changes?
6. Are there any Critical or Important issues to fix before implementation?
