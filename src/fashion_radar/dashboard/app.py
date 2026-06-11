from __future__ import annotations

import argparse
from pathlib import Path

from fashion_radar.dashboard.queries import (
    dashboard_summary,
    database_path,
    latest_candidate_report,
    source_health_rows,
    top_entities,
)
from fashion_radar.utils.paths import default_data_dir, default_reports_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--data-dir", type=Path, default=default_data_dir())
    parser.add_argument("--reports-dir", type=Path, default=default_reports_dir())
    args, _unknown = parser.parse_known_args()
    return args


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
    st.caption(f"Reports: {args.reports_dir}")
    daily_tab, candidate_tab, brand_tab, product_tab, celebrity_tab, health_tab = st.tabs(
        [
            "Daily Brief",
            "Candidate Signals",
            "Brand Mentions",
            "Product Mentions",
            "Celebrity Mentions",
            "Source Health",
        ]
    )

    with daily_tab:
        st.metric("Items", summary["item_count"])
        st.metric("Entity matches", summary["match_count"])
        st.caption(f"Latest collected at: {summary['latest_collected_at'] or 'n/a'}")

    with candidate_tab:
        st.caption(
            "Candidate signals are observed phrases from configured sources and need review."
        )
        st.caption(f"Report date: {candidate_report['report_date'] or 'n/a'}")
        if "error" in candidate_report:
            st.warning(candidate_report["error"])
        rows = candidate_report["rows"]
        if rows:
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No untracked candidate signals in the latest report.")

    with brand_tab:
        st.dataframe(top_entities(args.data_dir, entity_type="brand"), use_container_width=True)

    with product_tab:
        st.dataframe(top_entities(args.data_dir, entity_type="product"), use_container_width=True)

    with celebrity_tab:
        st.dataframe(
            top_entities(args.data_dir, entity_type="celebrity"),
            use_container_width=True,
        )

    with health_tab:
        st.dataframe(source_health_rows(args.data_dir), use_container_width=True)


if __name__ == "__main__":
    main()
