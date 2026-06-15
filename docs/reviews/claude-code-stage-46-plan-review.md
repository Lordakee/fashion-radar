## Critical findings

None.

## Important findings

1. **CI will likely fail because `actions/checkout` persists a GitHub auth extraheader by default.**  
   The proposed hygiene script intentionally fails on persistent `http.*.extraheader` authorization config, but `.github/workflows/ci.yml` currently uses:

   ```yaml
   - uses: actions/checkout@v4
   ```

   Without `persist-credentials: false`, GitHub Actions commonly leaves an auth extraheader in local git config for the checked-out repo. Since the plan adds `check_release_hygiene.py` in CI, the new check may fail in CI by design.  
   **Required fix before implementation:** update the plan to set:

   ```yaml
   - uses: actions/checkout@v4
     with:
       persist-credentials: false
   ```

   or otherwise explicitly clear/scope credentials before running the release hygiene check.

2. **The plan’s Task 5 includes push and GitHub Actions polling, which conflicts with the stated boundaries unless separately user-authorized.**  
   The Stage 46 goal is a local release hygiene gate and human upload alignment. The proposed boundaries preserve “no external services” and no remote/publishing behavior, but Task 5 says to push to `main` and run `gh run list`. That is outside the hygiene-gate implementation itself and should not be part of the executable Stage 46 implementation plan unless the user explicitly asks for push/remote verification.  
   **Required fix:** remove Task 5 from the implementation plan or clearly mark it as optional/manual/out-of-scope and only to be run after explicit user approval.

3. **Token content scanning needs length-aware, high-confidence regexes to avoid self-failing on docs/tests.**  
   The spec and plan mention token prefixes such as `ghp_`, and the new tests/docs will likely contain those literal prefixes. If implementation scans merely for the prefix, the hygiene script will flag its own tracked documentation or tests.  
   **Required fix:** make the plan explicit that GitHub token detection must use valid-looking, length-aware patterns, not prefix-only matching. Tests should use a valid-looking dummy token only inside temporary repositories and assert that tracked repo docs/tests containing prefix examples are not flagged.

4. **Local credential config filenames are not consistently covered across ignore, tracked, untracked, and archive policies.**  
   The `.gitignore` update lists `.pypirc`, `pip.conf`, and `uv.toml`, but the archive denylist task’s concrete classifier does not include those names, and the tracked-path policy only says “local credential … names” generically. A forced add or accidental archive inclusion of `.pypirc`, `pip.conf`, `uv.toml`, `.netrc`, etc. would be release-sensitive.  
   **Required fix:** explicitly add local credential/config filenames to the tracked-path and archive-member denylist, and decide whether they should also be in the high-risk untracked policy. At minimum: `.pypirc`, `pip.conf`, `pip.ini`, `uv.toml`, `.netrc`, and possibly `.npmrc` if the repo wants a broader standard release hygiene guard.

## Minor findings

1. **The untracked policy and `.gitignore` policy should be explained together.**  
   The design intentionally checks only unignored untracked files via `git ls-files --others --exclude-standard`, while also adding ignore rules for many high-risk local artifacts. That is defensible because ignored files are not normally candidates for git publication, but the plan should state this explicitly so reviewers do not expect ignored high-risk files to be reported.

2. **Archive path matching should distinguish “name contains session/cookie” from precise high-risk path names.**  
   The plan says archive members with names containing `session`, `cookie`, etc. should be rejected. For archive member paths, this is less risky than content scanning, but future docs or examples with benign path names could be blocked. Prefer segment/basename-oriented matching where practical, e.g. `cookies.txt`, `session.json`, `storage-state.json`, `browser-profiles/`, `private-exports/`.

3. **The package archive checker still hardcodes project name/version.**  
   This was already accepted in Stage 45, but extending release gates is another opportunity to note that version bumps require synchronized updates. Not a Stage 46 blocker.

4. **The release hygiene script should define behavior outside a git repository.**  
   The plan says it runs git commands in the target repo, but tests should include or the implementation should clearly handle “not a git repository” with a clean error rather than a traceback.

## Answers to the specific questions

1. **Is Stage 46 the right next node after Stage 45 package archive readiness?**  
   Yes. After archive metadata/readiness, a repository hygiene gate is a natural next release-readiness node.

2. **Is the release hygiene script scoped tightly enough to avoid false positives while catching high-confidence leaks?**  
   Mostly, but only if the token scanner is explicitly length-aware and high-confidence. Prefix-only matching would be too broad and likely self-fail.

3. **Are the forbidden tracked, untracked, and archive-member policies complete enough?**  
   Close, but not yet. Credential config filenames must be consistently included across tracked/archive policies, and CI credential handling must be addressed.

4. **Is the TDD sequence credible?**  
   Yes overall. The RED/GREEN sequencing for the new release hygiene script, archive denylist, and docs/CI drift tests is credible. The tests should be tightened around realistic token patterns and CI checkout credential behavior.

5. **Does the plan avoid product compliance-review functionality and scraping/crawling/social platform automation or account/cookie/session tooling?**  
   The hygiene-gate work itself does. However, Task 5’s push/GitHub Actions polling is external-service behavior and should be removed or made explicitly manual/user-authorized.

6. **Any Critical or Important blockers?**  
   Yes: the CI checkout credential issue, Task 5 remote actions, token regex precision, and inconsistent credential config denylisting are Important blockers.

## Verdict

Stage 46 is directionally sound and valuable, but the plan needs the Important blockers above fixed before implementation.
