The `.venv/bin/python` correction is appropriate.

- It matches this repo’s virtualenv-oriented command style and is suitable when the environment lacks a bare `python` binary.
- For a `uv.lock` diff guard, using the project venv interpreter is more deterministic than relying on PATH resolution.
- I see no evidence that this change weakens the release-gate plan or introduces a new Critical or Important issue.
- The Stage 31 release-gate plan remains acceptable to execute.

APPROVED FOR STAGE 31 RELEASE GATE
