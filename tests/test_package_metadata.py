from __future__ import annotations

import tomllib
from pathlib import Path

import fashion_radar

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
README = ROOT / "README.md"
LICENSE = ROOT / "LICENSE"


def _project_metadata() -> dict[str, object]:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]


def test_package_core_metadata_matches_runtime_version() -> None:
    project = _project_metadata()

    assert project["name"] == "fashion-radar"
    assert project["version"] == fashion_radar.__version__
    assert project["readme"] == "README.md"
    assert project["requires-python"] == ">=3.11"
    assert project["license"] == {"text": "MIT"}
    assert README.exists()
    assert LICENSE.exists()


def test_package_script_and_wheel_package_are_declared() -> None:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

    assert data["project"]["scripts"]["fashion-radar"] == "fashion_radar.cli:app"
    assert data["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"] == ["src/fashion_radar"]


def test_sdist_excludes_internal_agent_artifacts() -> None:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

    assert data["tool"]["hatch"]["build"]["targets"]["sdist"]["exclude"] == [
        "/.codegraph/**",
        "/docs/reviews/**",
        "/docs/superpowers/**",
    ]


def test_public_package_metadata_is_complete() -> None:
    project = _project_metadata()

    assert {
        "fashion",
        "trend-analysis",
        "local-first",
        "rss",
        "gdelt",
        "community-signals",
    }.issubset(set(project["keywords"]))
    assert {
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Office/Business :: News/Diary",
        "Topic :: Text Processing :: Indexing",
    }.issubset(set(project["classifiers"]))
    assert project["urls"] == {
        "Homepage": "https://github.com/Lordakee/fashion-radar",
        "Repository": "https://github.com/Lordakee/fashion-radar",
        "Documentation": "https://github.com/Lordakee/fashion-radar/tree/main/docs",
        "Issues": "https://github.com/Lordakee/fashion-radar/issues",
        "Changelog": "https://github.com/Lordakee/fashion-radar/blob/main/CHANGELOG.md",
        "Security": "https://github.com/Lordakee/fashion-radar/blob/main/SECURITY.md",
    }
