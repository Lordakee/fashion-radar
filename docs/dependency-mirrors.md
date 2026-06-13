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
- Use `UV_NO_CONFIG=1 uv sync --locked --dev --check` and
  `UV_NO_CONFIG=1 uv lock --check` for CI and release checks, so user-level
  mirror config cannot rewrite or invalidate the public lockfile.
- Keep dependencies in `pyproject.toml`.
- Avoid committing local virtual environments or downloaded package caches.
- Avoid committing mirror-bound URLs in `uv.lock`.
- Keep heavyweight optional dependencies out of the core install when the core
  workflow can degrade safely without them.
- Before GitHub upload, verify the public lockfile does not contain mirror URLs:

  ```bash
  rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
  ```
