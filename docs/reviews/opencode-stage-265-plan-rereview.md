# Stage 265 Plan Rereview — ROW ONE Local Daily Ops

## Verdict: **Approve** — no Critical or Important findings. The plan is executable as written.

## Prior findings — all resolved

| Prior | Status | Evidence |
|---|---|---|
| **I-1** impossible contiguous substrings | ✅ Fixed | Task 1 test (plan:67-86) now asserts token-level substrings (`"fashion-radar run"`, `'--as-of "$AS_OF"'`, `"--config-dir /repo/configs"`, …) that each match the renderer output. |
| **M-1** layering | ✅ Fixed | Renderer lives in `src/fashion_radar/row_one/ops.py`; `row_one` → `scheduling` is one-way (verified no `row_one` import of `scheduling` exists today; `scheduling.py` is stdlib-only, no cycle). |
| **M-2** help-coverage asymmetry | ✅ Fixed | Task 3 adds `("row-one","local-ops","--help")` to the help loop (check_first_run_smoke.py:2780-2787) **and** the full invocation with `assert_output_contains_text`. |
| **M-3** docs-test mapping | ✅ Fixed | Strings are bound to named functions; all three exist — `test_row_one_docs_include_user_required_phrases` (test_row_one_docs.py:66), `test_row_one_cli_docs_list_build_preview_serve_and_schedule_commands` (:156), `test_row_one_upload_checklist_covers_subcommand_help` (:189). |
| **M-4** missing import | ✅ Fixed | `from fashion_radar.row_one.ops import ...` present (plan:52). |
| **M-5** mock placement | ✅ Fixed | Explicit: "alongside schedule/preview handlers, before the fallthrough" — verified handlers at test_first_run_smoke.py:4213-4249 and fallthrough at :4332. |
| **M-6** storage wording | ✅ Fixed | "inside a directory marked with a `.row-one-site` file" — matches render.py:18,39,59-66. |
| **M-7** redundant escapes | ✅ Fixed | f-string uses single-quote wrapping for `"$AS_OF"`. |
| Design↔plan dir-flag agreement | ✅ Fixed | Design:37-38 now shows explicit dir flags. |
| Package archive guardrail | ✅ Fixed | Task 1b adds `src/fashion_radar/row_one/ops.py` to `SDIST_REQUIRED_PATHS` (check_package_archives.py:58) and `SDIST_FILES` (test_package_archives.py:51). |

## Executability verification

- Renderer output cross-checked token-by-token against the test: `raw_as_of_shell()` (scheduling.py:24), `_cron_parts("04:00")`→`0 4 * * *`, `format_row_one_site_access_message("0.0.0.0",8787)`→`Open locally: http://127.0.0.1:8787` + `Open from LAN: http://<LAN-IP>:8787` (server.py:15-25). All assertions hold.
- CLI option constants exist (cli.py:204-233); `row_one_app` group and `@row_one_app.command` registration pattern verified (cli.py:1518,1564); `row-one preview` (cli.py:1421-1438) accepts every flag the renderer prints (`--host`, `--port`, `--as-of`, `--latest-only`, `--dry-run-serve-url`).
- `validate_hhmm` raises `ValueError("time must be in 24-hour HH:MM format")` (scheduling.py:20) — matches the `pytest.raises(match=...)`; renderer calls it first (plan:145), so the invalid-time test passes.

## Boundary / scope — preserved

Command body is `typer.echo(render_row_one_local_ops_runbook(...))` only. It prints, installs no timers, starts no servers, builds no site, reads no SQLite, mutates no files. Reused helpers are pure string work. No change to `row-one-app/v1` JSON (render.py untouched), collection/scoring/ranking, scheduling semantics, or static-site behavior.

## Minor (new, non-blocking)

- **Mn-1.** Renderer header `Daily 04:00-style cron snippet:` (plan:171) is a literal string, not parameterized by `time`. With `--time 02:30` the header still says "04:00-style" while the snippet correctly shows `30 2 * * *`. Cosmetic; the Task 1 test only covers `04:00` so it won't surface. Consider `f"Daily {time} cron snippet:"`.
- **Mn-2.** Design Proposed Surface (design:40) shows the preview command without `--host`/`--port`/`--as-of`; the renderer (plan:163) includes them. All are valid `preview` flags, so the printed command is correct/pasteable — purely a design-doc shorthand gap, no action required.
- **Mn-3.** Task 3 assumes `assert_first_run_flow_commands` enforces an exact ordered sequence and that inserting the local-ops tuple "after preview" matches execution order. Execution order is schedule → preview → local-ops (check_first_run_smoke.py:2788-2824), which agrees with the plan's placement; low risk since the focused smoke test is run in Step 4.

Proceed to implementation.
