## Verdict: APPROVED with required fixes

The direction is correct: `edition_brief` is the right narrow, deterministic next step, derived purely from existing `stories` / `content_sections` / `daily_digest` / `story_directory` data, with no collection/scoring/ranking/ID changes. The payload shape is safely derivable and the schema/drift approach is sound. Four Important issues must be fixed before or during implementation.

## Answers to the evaluation questions

1. **Right next step?** Yes. A deterministic overview layer is the correct response to "organize daily information instead of mostly links/cards," and it stays inside the ROW ONE presentation-only boundary.
2. **Payload shape deterministic/safe?** Yes — every field is a projection of already-built payload fields. No new source inference.
3. **Schema/drift sufficient for `additionalProperties: false`?** Adequate, not exhaustive (see note below). Top-level + nested `additionalProperties: false` are both covered by drift cases.
4. **Risk of adding a required field under `row-one-app/v4`?** Low for this project. Technically a required-field addition is not purely additive for an external v4 consumer, but Fashion Radar is local-first with a single producer and the only consumer is the in-repo homepage, so no migration is warranted. Acceptable.
5. **Rendering/escaping/docs/test gaps?** Yes — four gaps below.

## Important findings (required fixes)

1. **Dead anchor targets — `#briefing-topics` and `#briefing-path` do not exist on the page.** `_render_briefing_topics` (`templates.py:1072`) and `_render_briefing_path` (`templates.py:1160`) emit `<section class="...">` with **no `id`**. The edition-brief "Briefing Topics"/"Briefing Path" links therefore jump nowhere, undermining the feature's navigation goal. The link schema pattern also hard-codes exactly these two anchors.
   - Fix: add `id="briefing-topics"` / `id="briefing-path"` to those two `<section>` elements (and keep the schema href pattern), or point the links at existing valid targets. No test in the plan asserts the anchors resolve, so this would ship broken without an explicit fix.

2. **Escaping test assertion is unachievable as written.** In Task 3 Step 2, `assert "onerror" not in index_html` will fail: `_esc` (`templates.py:1808`) escapes `<`, `>`, `"`, `'` but leaves the attribute *name* intact, so `Headline <img src=x onerror="alert(1)">` renders as `Headline &lt;img src=x onerror=&quot;alert(1)&quot;&gt;` — the substring `onerror` is still present. The RED→GREEN transition cannot succeed.
   - Fix: assert `'onerror="alert'` not in output (the executable form), or `'<img'` not in output, instead of the bare word `onerror`.

3. **Stray diff markers in the metrics template snippet.** Task 3 Step 4's `_render_edition_brief_metrics` shows literal `+` prefixes on the `<strong>`/`<span>` lines. Copied verbatim, the homepage will emit `+      <strong>...` HTML.
   - Fix: drop the leading `+` markers from the snippet before implementing.

4. **Shape example diverges from the schema/implementation.** The "Proposed `edition_brief` Shape" (plan lines 48–76) omits `story_directory_story_count`, yet Task 2 marks it **required** in the schema and emits it in `_edition_brief_payload`. The same shape shows "1 topic" / "1 follow-up path" (singular) while the `_edition_brief_dek` f-string always pluralizes ("1 topics"). Neither breaks a test today, but the shape is what reviewers diff against.
   - Fix: add `story_directory_story_count` to the shape example and either singularize the dek counts or update the example to match the plural form.

## Minor notes (not blockers)

- Drift coverage is adequate but could also assert: missing `story_directory_story_count`, a `metrics` array with ≠4 items (minItems/maxItems=4), and a malformed `summary_points` entry.
- `daily_digest.lead_story_id` is loosely typed (`minLength: 1`) while `edition_brief.lead_story_id` uses the strict `$defs/storyId` pattern. This mirrors the existing `story_directory` precedent and is safe given current story IDs, but is a latent typing inconsistency worth a one-line comment.
- The review-gate command in Task 5 uses `opencode run -m ... --pure`; AGENTS.md specifies `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar`. Align the flags when you record the fallback invocation.

## Environment note

Per your note and AGENTS.md, this review is produced by the local opencode fallback (GLM-5.2) acting as primary reviewer in place of Claude Code. When you create `docs/reviews/claude-code-stage-286-plan-review.md`, record the `401 authentication_failed` condition and cross-reference this output in `docs/reviews/opencode-stage-286-plan-review.md`.
