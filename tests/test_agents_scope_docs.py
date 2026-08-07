from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DOC = ROOT / "AGENTS.md"


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_agents_scope_boundaries_keep_two_tier_source_contract() -> None:
    scope_boundaries = _section(
        AGENTS_DOC.read_text(encoding="utf-8"),
        "Scope Boundaries",
    )
    normalized = _normalized(scope_boundaries)

    for phrase in (
        "`v0.1.0` minimum core sources are rss/atom, rsshub-compatible feeds, and gdelt",
        "html seed-url collection and sitemap discovery are optional capabilities "
        "provided by the `article` extra",
        "google news rss is not part of `v0.1.0`",
        "social-platform connectors are opt-in",
    ):
        assert phrase in normalized

    assert (
        "core sources are rss/atom, rsshub-compatible, gdelt, html seed-url collection, "
        "and sitemap discovery"
    ) not in normalized


def test_agents_parallel_execution_contract_covers_scope_ownership_and_reuse() -> None:
    parallel_execution = _section(
        AGENTS_DOC.read_text(encoding="utf-8"),
        "Parallel Agent Execution",
    )
    normalized = _normalized(parallel_execution)

    required_clauses = (
        (
            "parallel execution is the mandatory default",
            "parallel agent execution as a mandatory default",
        ),
        (
            "delegation records exact writable files or globs",
            "exact writable files or globs",
        ),
        (
            "delegation records the coupled write set",
            "any coupled write set",
        ),
        ("delegation records the owner", "name the owner"),
        ("delegation records expected completion state", "expected completion state"),
        ("conflicting claims are prohibited", "conflicting claim on that write set"),
        (
            "independent nodes run in parallel",
            "run independent nodes in parallel",
        ),
        (
            "parallel nodes require disjoint scopes and coupled write sets",
            "writable scopes and coupled write sets are disjoint",
        ),
        (
            "serialization is limited to real constraints",
            "serialize only for a real dependency, an external rate limit, or a shared write set",
        ),
        ("terminal state is reconciled", "reconcile its terminal state"),
        ("handoff records changed files", "changed-file list"),
        ("handoff records verification", "verification commands/results"),
        ("handoff records unresolved work", "unresolved work"),
        ("handoff records partial writes", "partial writes"),
        ("handoff is recorded", "record a short handoff"),
        (
            "errored or incomplete work remains owned",
            "an errored or incomplete task remains owned",
        ),
        (
            "ownership can transfer the remaining write set to a named successor",
            "transfers its remaining write set to a named successor",
        ),
        (
            "reclaim follows collected handoff and completion or transfer",
            "after collecting that handoff and once the coordinator has marked the task complete "
            "or transferred its remaining write set to a named successor",
        ),
        (
            "completed or no-longer-needed agents are immediately reclaimed",
            "immediately reclaim a completed, errored, or no-longer-needed agent",
        ),
        (
            "freed capacity is immediately reused",
            "immediately assign the freed capacity to a named successor or a new bounded task",
        ),
        (
            "eligible work cannot wait behind finished agents",
            "do not leave finished agents open while eligible work is waiting",
        ),
        (
            "coordination stays in the existing main worktree and branch",
            "existing `main` worktree on the `main` branch",
        ),
        (
            "other worktrees or branches are prohibited",
            "do not create, use, or switch to another git worktree or branch",
        ),
    )
    for label, clause in required_clauses:
        assert clause in normalized, f"Parallel Agent Execution is missing {label}: {clause!r}"

    ownership_transfer = "transfers its remaining write set to a named successor"
    reclaim = "immediately reclaim a completed, errored, or no-longer-needed agent"
    freed_capacity_reuse = (
        "immediately assign the freed capacity to a named successor or a new bounded task"
    )
    assert ownership_transfer != freed_capacity_reuse
    assert normalized.index(ownership_transfer) < normalized.index(reclaim)
    assert normalized.index(reclaim) < normalized.index(freed_capacity_reuse)
