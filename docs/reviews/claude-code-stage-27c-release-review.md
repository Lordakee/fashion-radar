Critical

None.

Important

None.

Minor

None.

Review notes

- The previous blocking validation-error leak is fixed for the `community-candidates` CLI path: `ManualSignalImportError` is now handled with the generic error message `input file could not be read or validated`, and the regression test asserts malformed private row values are not echoed.
- The Stage 27A code remains local, one-file, read-only, pre-import, and aggregate-only. The implementation reads one supplied file via the manual signal loader, performs in-memory candidate extraction/scoring, does not open SQLite, does not fetch URLs, and does not write database/report/dashboard/config artifacts.
- The output model and render path expose aggregate candidate fields only. They omit supplied input paths, row URLs, row titles, summaries/raw text, normalized keys, candidate contexts, representative item details, and source/import path internals.
- Stage 27B docs describe the boundary accurately and include the required negative claims around demand proof, platform coverage, source ranking, connectors/acquisition/scraping/watchers/scheduling, report/dashboard generation, SQLite/database import, and entity YAML/config generation.
- `uv.lock` is currently modified in the worktree but not staged; `pyproject.toml` is not part of the diff. The explicit staging allowlist and staged-name validation are adequate to keep `uv.lock` out of the release commit.
- The revised final-review-output process using a temporary file, non-empty check, approval phrase check, then `mv` is adequate for the previously observed blank-review-file process issue.
- The planned post-review scans and explicit staging checks are adequate.
- The planned push method uses a non-persistent `git -c http.https://github.com/.extraheader=... push` scoped to a subshell and avoids token-bearing remotes or persistent git config. That is token-safe provided the real token is supplied only in the in-memory shell environment for that push command and not written into docs, logs, shell profile, remote URL, or git config.

APPROVED FOR STAGE 27 RELEASE COMMIT AND PUSH
