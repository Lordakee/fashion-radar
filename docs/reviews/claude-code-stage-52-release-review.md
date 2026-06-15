## Findings

### Important — documented JSON example diverges from the actual producer profile contract

**File:** `docs/community-signal-import.md:94`

The example manifest JSON lists:

```json
"prohibited_fields": ["author_handle", "account_id", "cookies", "sessions", "tokens"]
```

…but the actual manifest is derived from `build_community_signal_profile()` and emits the sorted values from `PROHIBITED_COMMUNITY_SIGNAL_FIELDS`, including singular field names:

- `cookie`
- `session`
- `token`

not `cookies`, `sessions`, `tokens`.

It also includes additional prohibited fields such as `raw_comment`, `follower_count`, `image_url`, `video_url`, `profile_url`, `full_post_body`, and `direct_message`.

This creates a public contract mismatch for external local producer tools reading the docs instead of invoking the command. Since the Stage 52 objective emphasizes that the manifest must not duplicate or diverge from the profile/workflow contracts, I’d update the example to either:

1. show the exact emitted list from the current profile, or
2. make the example explicitly abbreviated, e.g. `"prohibited_fields": ["author_handle", "..."]`, while directing tools to use the command output as authoritative.

No code change appears required for this issue.

## Notes / confirmations

- I did **not** find evidence that `community-handoff-manifest` inspects the supplied directory. The CLI accepts `directory` as `str`, converts to `Path`, and passes it through to builders that stringify paths and construct commands. I did not see `exists()`, `iterdir()`, globbing, SQLite, subprocess, or importer calls in the command path.
- The manifest builder reuses `build_community_signal_profile()` and `build_community_handoff_workflow()` rather than reimplementing their contracts, which is good.
- JSON key order is explicitly covered by tests for both the builder and CLI output.
- The storage warning about saving a manifest inside a JSON handoff directory matched by `--pattern "*.json"` is present in code and docs.
- I did not see scraping/crawling/browser/account/cookie/session/platform API/compliance automation behavior added.
- `git status --short` shows no `uv.lock` modification and no obvious generated runtime/build artifacts in the change set.
