# Dependency Mirrors

Use mirrors where possible when installing dependencies or software.

## Python

Recommended PyPI mirror command:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --dev
```

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
- Keep dependencies in `pyproject.toml`.
- Avoid committing local virtual environments or downloaded package caches.
- Keep heavyweight optional dependencies out of early-stage core installs until their stage needs them.

