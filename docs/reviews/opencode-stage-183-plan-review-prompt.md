# Stage 183 Plan Review Prompt

Review the Stage 183 plan for `/home/ubuntu/fashion-radar`.

Return only the final review body, starting with:

```text
# Stage 183 Plan Review
```

Files to review:

- `docs/superpowers/specs/2026-06-24-stage-183-package-archive-entry-point-case-design.md`
- `docs/superpowers/plans/2026-06-24-stage-183-package-archive-entry-point-case-plan.md`
- `tests/test_package_archives.py`
- `scripts/check_package_archives.py`

Review questions:

1. Does the plan satisfy the objective: guard wheel console-script names as
   case-sensitive?
2. Is the proposed fixture meaningful for catching a future removal of
   `parser.optionxform = str` in `validate_wheel_entry_points(...)`?
3. Is the planned test placement and assertion shape consistent with existing
   package archive tests?
4. Does the plan stay test-only unless the new test exposes a real checker
   defect?
5. Are focused verification commands sufficient before the full release gate?

Report findings under Critical, Important, and Minor. If acceptable, approve
implementation.
