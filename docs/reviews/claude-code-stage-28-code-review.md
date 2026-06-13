Critical
- None.

Important
- `src/fashion_radar/cli.py:528-533` — `fashion-radar community-candidates` still prints arbitrary unexpected exception text unless the message contains the input path or filename. This can leak row values, validation internals, normalized keys, candidate context, URLs/titles/summaries/raw text, source/import paths, or account/private fields if any downstream unexpected exception includes those values but not the path/name:
  ```python
  except Exception as exc:
      message = str(exc)
      if str(path) in message or path.name in message:
          message = "input file could not be read or validated"
      typer.echo(f"Could not preview community candidates: {message}", err=True)
  ```
  The new directory command uses the safer fixed generic error for unexpected exceptions at `src/fashion_radar/cli.py:591-597`, so `community-candidates` is inconsistent with the Stage 28 safety boundary. Because the changed area includes both candidate preview commands and the stated risk includes unexpected exceptions not leaking sensitive values, this should block release until the single-file command also emits a generic unexpected-error message.

Minor
- None.

I do **not** approve release commit/push yet because the Important finding is a blocking output-safety issue.
