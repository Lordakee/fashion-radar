Critical findings: None.

Important findings:

1. **Installed mode can still be source-contaminated via inherited `PYTHONPATH`**
   - The plan ensures installed mode does not *prepend* `repo_root/src`, but it intentionally preserves any existing `PYTHONPATH`.
   - That means if CI or a release operator has `PYTHONPATH=/home/ubuntu/fashion-radar/src` or equivalent already set, the installed smoke can pass by importing the source tree rather than the installed wheel.
   - This weakens the stated goal: “prove the built wheel can run the local sample flow.”
   - Recommended fix to the plan: in `--installed` mode, either:
     - remove `repo_root/src` from `PYTHONPATH` before invoking CLI commands, preserving unrelated entries; or
     - fail fast if `repo_root/src` is present in `PYTHONPATH`; and ideally
     - add a preflight import check using the target Python:
       ```bash
       python -c "import fashion_radar, pathlib; print(pathlib.Path(fashion_radar.__file__).resolve())"
       ```
       and assert the resolved path is not under `repo_root/src`.
   - The current unit tests actually codify the weaker behavior by asserting installed mode preserves `/already/here`. That is okay for unrelated paths, but the tests should also cover the repo `src/` contamination case.

Minor findings:

1. **CI placement is reasonable**
   - Adding the installed smoke after wheel install and after installed `doctor` is appropriate.
   - Keeping the existing source-checkout first-run smoke unchanged is also appropriate.
   - Running before the dashboard extra smoke is fine because the first-run smoke validates the base wheel before optional extras.

2. **The smoke does exercise the packaged CLI path under normal CI conditions**
   - The script uses:
     ```python
     [context.python, "-m", "fashion_radar", *args]
     ```
     and in installed mode no longer prepends `src/`.
   - With a clean GitHub Actions environment, this should import from the installed wheel because repo root itself does not expose `src/fashion_radar` on `sys.path`.
   - The remaining concern is environmental contamination, not the core command structure.

3. **Docs consistency coverage is good but brittle**
   - The proposed `tests/test_cli_docs.py` checks exact command strings in CI/checklist/docs. This is effective for drift prevention.
   - It may be brittle if line wrapping or shell variable names change, but that is consistent with the existing style in this repo.

4. **Test coverage is mostly adequate**
   - Good planned coverage:
     - source mode still prepends `src`;
     - installed mode changes environment behavior;
     - `--installed` parsing;
     - context records source/installed mode;
     - `run_cli()` passes the mode through;
     - CI/checklist/README document the command.
   - Missing coverage:
     - installed mode should not allow `repo_root/src` to remain on `PYTHONPATH`;
     - optional preflight should verify `fashion_radar.__file__` resolves outside the source tree.

5. **Release verification is strong**
   - Building the wheel, checking package archives, installing into a fresh venv, and running the installed first-run smoke is the right end-to-end release gate.
   - If the `PYTHONPATH` contamination gap is closed, this will be a solid verification path.
