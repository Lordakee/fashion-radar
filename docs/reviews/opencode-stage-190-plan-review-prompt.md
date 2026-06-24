# Stage 190 Plan Review Prompt

Review the Stage 190 source-liveness diagnostics design and implementation plan
before coding.

Repository: `/home/ubuntu/fashion-radar`

Files to review:

- `docs/superpowers/specs/2026-06-24-stage-190-source-liveness-diagnostics-design.md`
- `docs/superpowers/plans/2026-06-24-stage-190-source-liveness-diagnostics-plan.md`
- `src/fashion_radar/collectors/rss.py`
- `src/fashion_radar/collectors/gdelt.py`
- `src/fashion_radar/utils/http.py`
- `src/fashion_radar/source_packs.py`
- `src/fashion_radar/cli.py`
- `tests/test_cli.py`
- `docs/source-pack-quality.md`
- `docs/source-packs.md`

Review questions:

1. Does the design preserve the boundary between offline `source-pack-lint`,
   ingestion via `collect_sources`, and read-only live diagnostics?
2. Are the proposed models, JSON shape, table rendering, and exit semantics
   coherent and testable?
3. Are RSS/RSSHub and GDELT probe semantics correct for a liveness diagnostic
   without over-claiming source coverage or demand proof?
4. Does the TDD plan contain enough RED/GREEN verification, including no live
   network in pytest and synthetic proxy safety?
5. Are there any implementation risks in the planned fake-client seams,
   elapsed-time seams, or CLI monkeypatch tests?
6. Does the plan avoid external/social/community handoff expansion?

Report findings under:

- Critical
- Important
- Minor

Critical or Important findings must block implementation. If acceptable, say the
plan is approved for implementation.

Start the response exactly with:

```text
# Stage 190 Plan Review
```

Do not include process chatter, command logs, ANSI output, or tool-status lines.
