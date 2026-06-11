Critical

- None.

Important

- None.

Minor

- None.

The latest plan fixes resolve the remaining prior Important findings:

- The `run` acceptance test now has both sides of the proof: configured `The Row` / `Margaux` content must be absent, while unconfigured `Le Teckel bag` must be present. The collect and match monkeypatches make the test specifically exercise loaded `entities.yaml` flowing into report candidate discovery rather than relying on stored `item_entities`.
- Serialization safety testing now seeds and captures sentinel internal alias, reason, and context terms from the existing report fixture and asserts those exact values are absent from candidate JSON and Markdown. It also constrains candidate `contexts` to controlled public labels.
- Stored-entity filtering now explicitly tests low-confidence stored entities do not filter, while high-confidence stored entities with non-`accepted` reason `manual_review_sentinel_not_accepted` still filter. This locks in the confidence-based predicate without requiring `reason == "accepted"`.
- Read-only CLI coverage now checks missing DB non-creation, missing data directory non-creation, and existing empty SQLite file schema failure without table creation.

Approved for Stage 8 implementation
