# opencode Stage 327 Code Review

Reviewer: local opencode using `zhipuai-coding-plan/glm-5.2 --variant max`.

Claude Code review was attempted first with `--effort max`, but the non-interactive review command timed out before producing usable findings. This review is the fallback review for the completed Stage 327 code node.

## Verification Re-run By Reviewer

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_signal_index.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py -q`
  - Result: `231 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check ...`
  - Result: clean
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check ...`
  - Result: clean

## Findings

### Critical

None.

### Important

None.

### Medium

None.

### Minor

- `saved_signal_index.py`: `_referenced_paragraph_indices()` returns `tuple[object, ...]` so invalid input values can be filtered downstream. This is defensive and correct, but a comment could make the intent clearer.
- `saved_signal_index.py`: `_section_items_by_signal_key()` uses `setdefault()` with an eagerly constructed default. At current ROW ONE edition scale this is harmless; an explicit `if key not in entries_by_key` branch would avoid the small discarded allocation.
- `saved_signal_index.py`: the empty `entries` check after slicing a known non-empty dict is defensive but effectively unreachable.
- `templates.py`: some filtering of rendered card/support strings is redundant because the helpers always return non-empty strings. This matches nearby helper style.
- `templates.py`: fragment regexes rely on `.fullmatch()` for start anchoring. This is inherited local style and not a new risk.
- `saved_signal_index.py`: frozen dataclasses still contain mutable `list` fields. This matches existing `RowOneSavedArticleLibrary` style, though tuples would express immutability more strictly.

## Reviewer Conclusion

No Critical or Important issues remain. Stage 327 is safe to promote.
