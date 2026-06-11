# Claude Code Stage 8 Code Rereview Prompt

Review the fixes for the Stage 8 Claude Code findings.

Repo: `/home/ubuntu/fashion-radar`
Previous code review: `docs/reviews/claude-code-stage-8-code-review.md`
Fix commit: `0b708bb`

User rules:

- This review must use `--effort max`.
- This is a read-only code rereview. Do not edit files, run collectors, access
  social platforms, scrape/crawl websites, mutate config, or perform network
  source collection. Return review findings only.
- Fix Critical and Important findings before GitHub sync.

Previous Important findings and implemented fixes:

1. Public candidate outputs exposed internal extraction `contexts`.
   - Removed `contexts` from `CandidateReport`.
   - Stopped copying metric contexts in `reports._candidate_report()`.
   - Removed the Markdown `Context labels` line.
   - Removed contexts from CLI `CandidateReport` construction.
   - Updated report tests to assert candidate JSON/Markdown do not contain
     `contexts`, `proper_name_span`, `fashion_anchor`, or `single_token`.

2. Stored known-entity filtering was not bounded by `as_of`.
   - `_stored_entity_keys()` now joins `item_entities` to `items` and only uses
     rows whose `items.collected_at <= as_of`.
   - Added a regression test proving a future high-confidence stored entity
     match does not suppress a historical candidate report.

Previous Minor finding and implemented fix:

- Configured known-entity filtering now accepts `as_of` and skips entities whose
  active window does not include the report date.

Verification after fixes:

```text
.venv/bin/python -m pytest -q
162 passed in 4.56s

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
62 files already formatted

uv lock --check
Resolved 84 packages

uv sync --locked --dev --check
Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
Would make no changes
```

Please verify:

1. Are both previous Important findings fully fixed?
2. Did the fixes introduce any new Critical or Important issue?
3. Is Stage 8 now safe to commit/sync to GitHub?

Return findings by severity:

- Critical
- Important
- Minor

End with exactly one of:

- Approved for Stage 8 commit and GitHub sync
- Approved after fixes
- Do not proceed
