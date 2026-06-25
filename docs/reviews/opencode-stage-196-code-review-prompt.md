# Stage 196 Code Review Prompt

Review current Stage 196 code changes in `/home/ubuntu/fashion-radar`.

Scope:

- `src/fashion_radar/extract/text.py`
- `tests/test_text.py`
- `tests/test_dedupe.py`
- `tests/test_matcher.py`
- `tests/test_cli_docs.py`
- Stage 196 plan/review artifacts

Questions:

1. Does `_fold_diacritics()` now fold only the intended non-decomposing Latin overrides (`ø`, `Ø`, `ı`) after NFD combining-mark stripping?
2. Do normalization, content hashes, parent-brand keys, and runtime alias matching agree for these variants?
3. Is the README Configuration docs guard section-scoped and offline?
4. Does the change avoid broad transliteration, source connector changes, social scraping, platform APIs, source ranking, demand proof, platform-wide coverage claims, and compliance-review product features?
5. Are tests and formatting adequate?

Return:

- Verdict: APPROVED / NEEDS_WORK
- Critical findings
- Important findings
- Minor findings
- Verification observed or recommended
- Concrete fixes required before release
