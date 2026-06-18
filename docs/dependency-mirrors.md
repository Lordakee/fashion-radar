# Dependency Mirrors

Use mirrors where possible when installing dependencies or software.

## Python

Default reproducible setup for public CI and GitHub contributors:

```bash
uv sync --locked --dev
```

Recommended local mirror command for users in mainland China or slower networks:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev
```

Optional article extraction installs a heavier parser stack. Use this only when
the local network can reliably download those packages:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --extra article
```

Optional dashboard dependencies can also be installed through the mirror:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --extra dashboard
```

`--frozen` installs from the committed lockfile without rewriting it. Do not run
`uv lock` or an unfrozen `uv sync` while `UV_DEFAULT_INDEX` points at a mirror if
the resulting `uv.lock` will be committed. Public lockfiles should keep the
default PyPI registry URLs so GitHub Actions and global contributors get
reproducible installs.

If `~/.config/uv/uv.toml` sets a mirror as the default index, run public
lockfile checks with `UV_NO_CONFIG=1`.

For direct package installation into an existing virtual environment:

```bash
uv pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple <packages>
```

Alternative mirrors:

```bash
https://mirrors.aliyun.com/pypi/simple/
https://pypi.mirrors.ustc.edu.cn/simple/
```

## Project Practice

- Prefer mirror-based install commands in local development notes.
- Use `uv sync --frozen --dev` with mirrors for local installs.
- Use `UV_NO_CONFIG=1 uv lock --check` for public lockfile validation, so
  user-level mirror config cannot rewrite or invalidate the public lockfile.
- Use `UV_NO_CONFIG=1 uv sync --locked --dev` for fresh CI/release installs,
  then `UV_NO_CONFIG=1 uv sync --locked --dev --check` after the project
  environment exists.
- Keep dependencies in `pyproject.toml`.
- Avoid committing local virtual environments or downloaded package caches.
- Avoid committing mirror-bound URLs in `uv.lock`.
- Keep heavyweight optional dependencies out of the core install when the core
  workflow can degrade safely without them.
- Before GitHub upload, verify the public lockfile does not contain mirror URLs:

  ```bash
  rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
  ```

## Recover A Mirror-Rewritten Lockfile

If `uv.lock` was already rewritten locally with mirror URLs, do not commit it.
When dependencies did not intentionally change, restore the committed public
lockfile before release work:

```bash
git restore -- uv.lock
UV_NO_CONFIG=1 uv lock --check
rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
git diff --quiet -- uv.lock
```

The `rg` check above should find no matches; when you use shell negation in a
release script, `! rg ... uv.lock` passes only when no mirror markers are
found. Local mirror installs should remain frozen mirror install commands, not
lockfile regeneration commands.

If `pyproject.toml` intentionally changed and the lockfile must be
regenerated, run the lock operation with user uv config disabled, then review
the lockfile diff before committing it:

```bash
UV_NO_CONFIG=1 uv lock
UV_NO_CONFIG=1 uv lock --check
rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
git diff -- uv.lock
```
