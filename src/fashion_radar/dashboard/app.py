from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from fashion_radar.dashboard.queries import (
    dashboard_summary,
    database_path,
    latest_candidate_report,
    load_trend_comparison,
    recent_signals,
    source_health_rows,
    top_entities,
)
from fashion_radar.models.entity import EntityType
from fashion_radar.models.trend import TrendComparison
from fashion_radar.settings import (
    ConfigError,
    ScoringSettings,
    load_entity_config,
    load_scoring_config,
)
from fashion_radar.utils.dates import parse_datetime_utc
from fashion_radar.utils.paths import default_config_dir, default_data_dir, default_reports_dir

CANDIDATE_SIGNAL_CAPTION = (
    "Candidate signals are observed phrases from configured sources and "
    "imported local signals and need review."
)
TREND_SIGNAL_CAPTION = (
    "Local observed signal deltas from configured RSS/web sources and imported manual "
    "signals. These are directional signals only and need review; they describe only "
    "this configured source set."
)
TREND_EMPTY_MESSAGE = "No local observed signal deltas in this comparison."
ENTITY_MENTION_TABS = tuple(
    (entity_type.value, f"{entity_type.value.title()} Mentions") for entity_type in EntityType
)
DASHBOARD_TAB_LABELS = (
    "Daily Brief",
    "Candidate Signals",
    "Trend Deltas",
    *(label for _entity_type, label in ENTITY_MENTION_TABS),
    "Source Health",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config-dir", type=Path, default=default_config_dir())
    parser.add_argument("--data-dir", type=Path, default=default_data_dir())
    parser.add_argument("--reports-dir", type=Path, default=default_reports_dir())
    args, _unknown = parser.parse_known_args()
    return args


def trend_comparison_window(
    scoring: ScoringSettings,
    *,
    now: datetime | None = None,
) -> tuple[datetime, datetime]:
    as_of = parse_datetime_utc(now or datetime.now(UTC))
    baseline_as_of = as_of - timedelta(days=scoring.current_window_days)
    if baseline_as_of >= as_of:
        raise ValueError("trend baseline must be before as-of")
    return as_of, baseline_as_of


def trend_delta_rows(comparison: TrendComparison) -> list[dict[str, Any]]:
    return [
        {
            "observed_status": delta.status.value,
            "signal_kind": delta.signal_kind.value,
            "type": delta.signal_type,
            "name": delta.name,
            "current_score": round(delta.current_score, 3),
            "baseline_score": round(delta.baseline_score, 3),
            "score_delta": round(delta.score_delta, 3),
            "current_mentions": delta.current_mentions,
            "baseline_mentions": delta.baseline_mentions,
            "mention_delta": delta.mention_delta,
            "current_growth_ratio": _round_optional(delta.current_growth_ratio),
            "baseline_growth_ratio": _round_optional(delta.baseline_growth_ratio),
            "current_label": delta.current_label,
            "baseline_label": delta.baseline_label,
            "first_seen_at": delta.first_seen_at.isoformat() if delta.first_seen_at else None,
        }
        for delta in comparison.deltas
    ]


def render_trend_deltas(
    st: Any,
    *,
    config_dir: Path,
    data_dir: Path,
    now: datetime | None = None,
) -> None:
    st.caption(TREND_SIGNAL_CAPTION)
    try:
        scoring_config = load_scoring_config(config_dir / "scoring.yaml")
        entity_path = config_dir / "entities.yaml"
        entity_config = load_entity_config(entity_path) if entity_path.exists() else None
        as_of, baseline_as_of = trend_comparison_window(scoring_config.scoring, now=now)
    except (ConfigError, ValueError) as exc:
        st.warning(f"Could not load trend config: {exc}")
        return

    try:
        comparison = load_trend_comparison(
            data_dir=data_dir,
            scoring=scoring_config.scoring,
            candidate_discovery=scoring_config.candidate_discovery,
            entity_config=entity_config,
            as_of=as_of,
            baseline_as_of=baseline_as_of,
        )
    except Exception as exc:
        st.warning(f"Could not read trend deltas: {exc}")
        return

    st.caption(f"Comparison as of: {comparison.as_of.isoformat()}")
    st.caption(f"Baseline as of: {comparison.baseline_as_of.isoformat()}")
    rows = trend_delta_rows(comparison)
    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info(TREND_EMPTY_MESSAGE)


def _round_optional(value: float | None) -> float | None:
    return round(value, 3) if value is not None else None


def main() -> None:
    import streamlit as st

    args = parse_args()
    db_path = database_path(args.data_dir)
    st.set_page_config(page_title="Fashion Radar", layout="wide")
    st.title("Fashion Radar")
    summary = dashboard_summary(args.data_dir)
    candidate_report = latest_candidate_report(args.reports_dir)
    if not summary["database_exists"]:
        st.info("No local database found yet. Run the CLI workflow first.")

    st.caption(f"Database: {db_path}")
    st.caption(f"Config: {args.config_dir}")
    st.caption(f"Reports: {args.reports_dir}")
    tabs = st.tabs(list(DASHBOARD_TAB_LABELS))
    daily_tab, candidate_tab, trend_tab = tabs[:3]
    entity_tabs = tabs[3:-1]
    health_tab = tabs[-1]

    with daily_tab:
        st.metric("Items", summary["item_count"])
        st.metric("Entity matches", summary["match_count"])
        st.caption(f"Latest collected at: {summary['latest_collected_at'] or 'n/a'}")
        rows = recent_signals(args.data_dir)
        if rows:
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No recent local signals yet.")

    with candidate_tab:
        st.caption(CANDIDATE_SIGNAL_CAPTION)
        st.caption(f"Report date: {candidate_report['report_date'] or 'n/a'}")
        if "error" in candidate_report:
            st.warning(candidate_report["error"])
        rows = candidate_report["rows"]
        if rows:
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No untracked candidate signals in the latest report.")

    with trend_tab:
        render_trend_deltas(st, config_dir=args.config_dir, data_dir=args.data_dir)

    for entity_tab, (entity_type, _label) in zip(
        entity_tabs,
        ENTITY_MENTION_TABS,
        strict=True,
    ):
        with entity_tab:
            st.dataframe(
                top_entities(args.data_dir, entity_type=entity_type),
                use_container_width=True,
            )

    with health_tab:
        st.dataframe(source_health_rows(args.data_dir), use_container_width=True)


if __name__ == "__main__":
    main()
