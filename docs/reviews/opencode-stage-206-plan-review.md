# Stage 206 Plan Review

## Verdict

No Critical findings. One Important planning issue must be fixed before
implementation. With that issue fixed, the plan is approvable.

## Critical

None.

## Important

1. Matcher and linter behavior diverge when `requires_context: true` and
   `safe_single_word: true` are combined on one alias.

   The planned matcher checks `alias.requires_context` before the
   `safe_single_word` branch, so an alias with both flags is context-gated.
   The planned linter only changes `_alias_requires_context(...)`; the
   `_classify_alias_gate(...)` body would still classify the same alias as a
   safe alias when `safe_single_word` and `reason` are present. That would make
   `safe_aliases` and `context_gated_aliases` disagree with runtime matcher
   behavior.

   Recommended fix: in `_classify_alias_gate(...)`, test
   `alias.requires_context` first and return `CONTEXT_REQUIRED` before
   consulting `safe_single_word`. This mirrors the matcher ordering and keeps
   the no-new-finding-code plan intact.

## Minor

1. The planned matcher `_requires_context(...)` change includes an unreachable
   `alias.requires_context or` clause because explicit aliases return before
   that helper is consulted. Drop it from the matcher helper and keep the
   `requires_context` check only in the explicit matcher branch and the linter
   helper.

2. Add tests that pin the runtime self-satisfaction fix motivating the context
   term tuning. Examples such as `Mary Jane shoes were noted.` should be
   rejected without surrounding context, so future edits cannot reintroduce
   context terms satisfied only by the alias text itself.

3. Clarify that any sample-workflow fallback edits apply only to the
   `summary` column in `examples/community-signals.watchlist.example.csv`, with
   `example.com` URLs kept unchanged.

## Answers To The Review Questions

1. Adding `requires_context: bool = False` to `AliasDefinition` is the right
   minimal backward-compatible model change.

2. Explicit context gates should run before `safe_single_word`, but the linter
   must mirror that ordering.

3. Config validation for aliases without `context_terms` is sufficient for that
   case, but the mixed `safe_single_word` case needs linter-ordering coverage.

4. Classifying explicit gates as `context_gated_aliases` is correct once
   `_classify_alias_gate(...)` checks `alias.requires_context` first.

5. `Mary Jane Shoes`, `East-West Bags`, `Boat Shoes`, and `Suede Sneakers` are
   appropriate high-risk category aliases. Leaving `Sandy Liang` out is
   reasonable.

6. The planned tests cover matcher, config, linter, watchlist false positives,
   and sample workflow compatibility, but should add self-satisfaction
   assertions.

7. Docs, changelog, review artifacts, and verification gates are sufficient.

8. Scope control is clean: the plan avoids source acquisition, connectors,
   scraping, ranking, demand proof, platform coverage verification, dependency
   changes, and compliance-review behavior.
