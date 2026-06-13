## Critical

None.

## Important

### 1. Verification does not prove the docs-only boundary

The docs-only scope is stated clearly in the design/plan, but the planned verification does not actually prove that implementation stayed docs-only.

Current verification appears to rely mainly on:

- a wording/boundary scan over docs
- `git diff --check`

That is not enough to confirm that production code, tests, configs, dependencies, generated artifacts, or `uv.lock` were untouched.

**Blocking fix:** Add an explicit changed-file verification step, such as:

```bash
git diff --name-only
```

and require the result to contain only the intended documentation/changelog files. The verification should explicitly confirm that `uv.lock` is absent from the diff.

This blocks implementation because Stage 27B’s central constraint is docs-only scope.

---

### 2. Boundary scan misses several prohibited implication categories

The design/plan correctly says the docs must avoid implying:

- platform coverage
- proof of demand
- source quality/ranking
- scraping
- monitoring
- acquisition
- scheduling
- dashboard updates
- report generation
- database import
- entity YAML generation

However, the planned scan terms only cover part of that boundary. It should also scan for terms/phrases around:

- `scraper`, `scraping`
- `watcher`, `watch`
- `scheduler`, `scheduled`
- `acquisition`
- `report generation`, `report writer`
- `dashboard update`
- `database import`
- `SQLite import`, `SQLite write`
- `entity YAML`, `entity config`
- `source connector`

**Blocking fix:** Expand the verification scan so it catches all prohibited framing categories named in the Stage 27B constraints.

This blocks implementation because the verification steps are not yet sufficient for a docs-only node with tight semantic boundaries.

## Minor

### 1. Some planned snippets use compressed privacy/output-boundary wording

The plan does include the full exclusion list in key places, but some planned additions use shorter phrases such as “row-level source text” or “row-level source values.”

For this stage, the docs should explicitly state that output does **not** include:

- local file paths
- row URLs
- row titles
- summaries
- raw text
- normalized keys
- candidate contexts
- representative item details

The full list does not necessarily need to be repeated everywhere, but the checklist/review-facing docs should either include the list or link directly to the boundary section containing it.

### 2. “Aggregate candidate phrase counts” slightly underspecifies the output

The planned wording “prints aggregate candidate phrase counts before import” is safe, but slightly narrow.

Stage 27A output is aggregate-only, but it includes candidate phrase metrics rather than just counts. More precise wording would be something like:

> prints aggregate candidate phrase metrics before import

or

> prints aggregate-only candidate rows before import

## Overall status

Implementation should **not** start yet.

The docs-only scope and intended product framing are mostly clear and safe, but the verification plan needs to be tightened before editing docs. Critical/Important blockers remain.
