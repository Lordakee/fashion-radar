# Stage 195 Plan Review

Verdict: **NEEDS_WORK**

Critical findings:

- The plan's diacritic-insensitive matching approach was incomplete. It proposed changing `normalize_text()` only, but `alias_pattern()` compiles and searches raw literal regexes. The planned assertion that `alias_pattern("Hermes")` should match `Hermès` would still fail unless `alias_pattern()` or its call sites also fold diacritics.
- The source expansion section was based on an outdated premise. `configs/source-packs/fashion-public.example.yaml` already contains a broad curated public pack with RSS and GDELT lanes, so the plan should not claim that the public source pack has only two sources or blindly expand it.

Important findings:

- The plan mixed up default starter config files and the public source pack. The real gap is that the default init sample is still small, while the public source pack is already broader.
- The proposed tests used arbitrary source-count assertions instead of precise offline invariants tied to the current source of truth.
- The documentation and artifact scope was broader than necessary for the implementation.

Concrete fixes required before implementation:

1. Update the diacritic plan so runtime alias matching is covered, not only normalized keys.
2. Rebase source-coverage work on the current repository state: public source pack is already broad; default starter config remains small.
3. Replace arbitrary source-count tests with offline invariants that prove the intended default-sample coverage and root/package parity.
4. Use existing files and test names (`settings.py`, `models/source.py`, `source_packs.py`, `tests/test_config.py`, `tests/test_source_packs.py`, `tests/test_stage1_hardening.py`) instead of non-existent paths.
5. Keep the implementation scope narrow and do not add social scraping, live URL guarantees, source ranking, demand proof, or compliance-review product features.
