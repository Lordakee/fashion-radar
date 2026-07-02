# Stage 261 ROW ONE Editorial Synthesis Design

## Goal

Stage 261 upgrades ROW ONE from a link-forward static site into a deterministic
editorial briefing. It adds local, report-derived synthesis to each story so the
site explains what the signal is, why it is grouped there, and how a reader
should scan it, without adding new collection, scraping, platform connectors,
LLM calls, translation services, paid APIs, deployment, demand proof, platform
coverage verification, or compliance-review features.

## Product Gap

Stage 260 closed the report-to-site gap by creating a static ROW ONE site,
detail pages, bilingual UI controls, local serving, and 04:00 scheduling.
The remaining product gap is readability: a user can see headlines, source
summaries, and links, but the site does not yet organize the information into
an edited brief. Stage 261 closes that gap inside the existing
`collect -> match -> report -> ROW ONE` path by turning current report fields
into concise editorial context.

## Chosen Approach

Add a deterministic synthesis layer inside `fashion_radar.row_one`. Each
`RowOneStory` gets three new bilingual fields:

- `editorial_takeaway`: one compact sentence that states the reader-facing
  signal.
- `signal_context`: one compact sentence that adds context not already covered
  by `why_it_matters`, such as mention deltas, growth ratio, first-seen timing,
  source name, or retained local-item status.
- `reader_path`: one compact sentence that tells the reader how to scan or
  follow the story inside ROW ONE, with per-story variation based on label,
  tag, source, or rank.

The fields are generated from already available local values. The current
implementation uses section key, entity/candidate name or phrase, source name,
labels, mention counts, growth ratio, first-seen timing, and recent-item title
and metadata. Existing `why_it_matters` remains the place for heat score,
candidate score, source count, and section placement. The copy is deterministic
bilingual UI framing and does not claim to translate or summarize full external
articles beyond retained local snippets.

## Data Inputs

Stage 261 can reuse:

- `EntityReport.entity_name`, `entity_type`, `label`, `heat_score`,
  `current_mentions`, `baseline_mentions`, `growth_ratio`, and representative
  items.
- `CandidateReport.phrase`, `candidate_type`, `label`, `score`,
  `current_mentions`, `baseline_mentions`, `growth_ratio`, `first_seen_at`, and
  representative items.
- Recent item fields already selected by `write_row_one_site_files`:
  `source_name`, `url`, `title`, `summary`, and `collected_at`.

Stage 261 will not add domestic/international grouping. The current report and
item schema do not provide deterministic country, region, or market metadata, so
any split would be heuristic and weaker than the current data model.

## Rendering

The homepage story cards should show the new `editorial_takeaway` so each card
has an edited point of view beyond headline and source summary. Detail pages
should show all three synthesis fields in a labeled editorial panel before the
evidence list. All dynamic values remain HTML-escaped, and source/evidence URL
sanitization remains unchanged.

## JSON Output

`data/edition.json` should expose the new fields as part of each story. The
existing JSON URL sanitization still applies to story `source_url` and evidence
URLs. No new persisted scoring artifacts are created.

## Boundaries

This stage is presentation-only. It does not:

- collect new sources;
- add scraping, browser automation, platform APIs, login cookies, proxy pools,
  CAPTCHA bypass, or paywall bypass;
- call LLMs, translation services, image services, or paid APIs;
- add domestic/international grouping without explicit source metadata;
- add compliance-review product behavior;
- claim demand proof or platform coverage verification;
- persist new scoring, matching, or ranking artifacts.

## Acceptance Criteria

- `RowOneStory` exposes non-empty `editorial_takeaway`, `signal_context`, and
  `reader_path` fields for generated entity, candidate, and recent-item stories.
- `signal_context` does not restate `why_it_matters`; it uses mention deltas,
  growth ratio, first-seen timing, or local-item/source context.
- `reader_path` varies by story label, tag, source, or rank rather than being a
  static section-level sentence repeated across every story.
- Empty editions remain valid and do not fabricate story synthesis when there
  are no stories.
- Homepage story cards render `editorial_takeaway` with the existing bilingual
  language toggle behavior.
- Detail pages render all three synthesis fields in an editorial panel before
  evidence links.
- `data/edition.json` includes the new synthesis fields and still sanitizes
  unsafe URLs.
- The synthesis text is deterministic and derived only from retained local
  report/item fields.
- Documentation states that ROW ONE editorial synthesis is deterministic local
  information organization, not translation, LLM generation, new scraping, or
  new scoring.
- Focused ROW ONE tests and the full verification gate pass.
