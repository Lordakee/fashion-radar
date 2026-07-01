from __future__ import annotations

from html import escape
from urllib.parse import urlsplit

from fashion_radar.models.report import (
    CandidateReport,
    CollectorRunReport,
    DailyBrief,
    DailyReport,
    EntityReport,
    SourceHealthReport,
)


def _esc(value: object) -> str:
    return escape(str(value), quote=True) if value else ""


def _safe_url(url: str | None) -> str:
    if not url:
        return ""
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https"):
        return ""
    return escape(url, quote=True)


def render_html_report(
    report: DailyReport, *, recent_items: list[dict[str, object]] | None = None
) -> str:
    metadata = report.metadata
    brief = report.brief
    entities = report.entities
    candidates = report.candidates
    source_health = report.source_health
    recent_runs = report.recent_runs

    brief_html = _render_brief(brief)
    signals_html = _render_signals(entities)
    candidates_html = _render_candidates(candidates)
    health_html = _render_health(source_health, recent_runs)
    news_html = _render_recent_items(recent_items or [])

    return _HTML_TEMPLATE.format(
        date=metadata.report_date.strftime("%Y-%m-%d"),
        generated_at=metadata.generated_at.strftime("%Y-%m-%d %H:%M UTC"),
        item_count=metadata.item_count,
        entity_count=len(entities),
        candidate_count=len(candidates),
        brief_html=brief_html,
        signals_html=signals_html,
        candidates_html=candidates_html,
        health_html=health_html,
        news_html=news_html,
    )


def _render_brief(brief: DailyBrief) -> str:
    parts = [f"<p class='brief-summary'>{_esc(brief.summary)}</p>"]
    for section in brief.sections:
        if section.items:
            parts.append(f"<h3>{_esc(section.title)}</h3>")
            for item in section.items:
                reasons = ", ".join(item.reason_codes) if item.reason_codes else "none"
                parts.append(
                    f"<div class='brief-item'><span class='brief-title'>{_esc(item.title)}</span>"
                    f"<span class='brief-detail'>{_esc(item.summary)} "
                    f"<em>Reasons: {_esc(reasons)}</em></span></div>"
                )
    return "\n".join(parts)


def _render_signals(entities: list[EntityReport]) -> str:
    if not entities:
        return "<p class='empty'>No entity signals in this window.</p>"
    cards = []
    for entity in entities:
        items_html = _render_representative_items(entity.representative_items)
        score_pct = min(100, int(entity.heat_score * 10))
        label_class = _esc(entity.label)
        cards.append(
            f"""<div class='signal-card'>
            <div class='signal-header'>
                <span class='signal-name'>{_esc(entity.entity_name)}</span>
                <span class='signal-label {label_class}'>{_esc(entity.label)}</span>
            </div>
            <div class='signal-meta'>
                <span class='score-bar'><span class='score-fill' style='width:{score_pct}%'></span></span>
                <span class='score-value'>{entity.heat_score:.1f}</span>
            </div>
            <div class='signal-stats'>
                {entity.current_mentions} current · {entity.distinct_sources} sources
            </div>
            {items_html}
            </div>"""
        )
    return "\n".join(cards)


def _render_candidates(candidates: list[CandidateReport]) -> str:
    if not candidates:
        return "<p class='empty'>No untracked candidate signals in this window.</p>"
    cards = []
    for candidate in candidates:
        cards.append(
            f"""<div class='candidate-card'>
            <span class='candidate-name'>{_esc(candidate.phrase)}</span>
            <span class='candidate-label'>{_esc(candidate.label)}</span>
            <span class='candidate-score'>{candidate.score:.1f}</span>
            </div>"""
        )
    return "\n".join(cards)


def _render_health(
    source_health: list[SourceHealthReport],
    recent_runs: list[CollectorRunReport],
) -> str:
    parts = []
    if source_health:
        parts.append("<h3>Source Health</h3>")
        for source in source_health:
            raw_error = source.last_error_message or ""
            error = (raw_error[:80] + "...") if len(raw_error) > 80 else (raw_error or "no error")
            cls = "health-ok" if source.consecutive_failures == 0 else "health-warn"
            parts.append(
                f"<div class='health-item {cls}'>"
                f"<span>{_esc(source.source_name)} ({_esc(source.source_type)})</span>"
                f"<span>{source.consecutive_failures} failures</span>"
                f"<span class='health-error'>{_esc(error)}</span>"
                f"</div>"
            )
    if recent_runs:
        parts.append("<h3>Recent Collector Runs</h3>")
        for run in recent_runs[:10]:
            parts.append(
                f"<div class='run-item'>"
                f"<span class='run-time'>{run.started_at.strftime('%H:%M')}</span>"
                f"<span>{_esc(run.source_name)} ({_esc(run.source_type)})</span>"
                f"<span class='run-status run-{_esc(run.status)}'>{_esc(run.status)}</span>"
                f"<span>{run.items_stored}/{run.items_seen} stored</span>"
                f"</div>"
            )
    if not parts:
        return "<p class='empty'>No source health issues recorded.</p>"
    return "\n".join(parts)


def _render_representative_items(items: list) -> str:
    if not items:
        return ""
    parts = ["<div class='rep-items'>"]
    for item in items[:3]:
        raw_summary = item.summary or ""
        summary = raw_summary[:120] + "..." if len(raw_summary) > 120 else raw_summary
        url = _safe_url(item.source_url)
        title = _esc(item.title)
        if url:
            parts.append(
                f"<div class='rep-item'>"
                f"<a href='{url}' target='_blank' rel='noopener'>{title}</a>"
                f"<span class='rep-source'>{_esc(item.source_name)}</span>"
                f"<p class='rep-summary'>{_esc(summary)}</p>"
                f"</div>"
            )
        else:
            parts.append(
                f"<div class='rep-item'>"
                f"<span class='rep-title-no-link'>{title}</span>"
                f"<span class='rep-source'>{_esc(item.source_name)}</span>"
                f"<p class='rep-summary'>{_esc(summary)}</p>"
                f"</div>"
            )
    parts.append("</div>")
    return "\n".join(parts)


def _render_recent_items(items: list[dict[str, object]]) -> str:
    if not items:
        return "<p class='empty'>No items collected in this window.</p>"
    cards = []
    for item in items[:50]:
        title = _esc(item.get("title", ""))
        url = _safe_url(str(item.get("url") or ""))
        source = _esc(item.get("source_name", ""))
        raw_summary = str(item.get("summary") or "")
        summary = _esc(raw_summary[:200] + "..." if len(raw_summary) > 200 else raw_summary)
        if url:
            cards.append(
                f"<div class='news-card'>"
                f"<a href='{url}' target='_blank' rel='noopener'>{title}</a>"
                f"<span class='news-source'>{source}</span>"
                f"<p class='news-summary'>{summary}</p>"
                f"</div>"
            )
        else:
            cards.append(
                f"<div class='news-card'>"
                f"<span class='news-title-nolink'>{title}</span>"
                f"<span class='news-source'>{source}</span>"
                f"<p class='news-summary'>{summary}</p>"
                f"</div>"
            )
    return "\n".join(cards)


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fashion Radar — {date}</title>
<style>
:root {{
  --bg: #faf9f7; --card: #ffffff; --text: #2c2c2c; --muted: #888;
  --accent: #c44569; --accent-light: #f8e0e8; --border: #e8e6e3;
  --green: #4a9; --amber: #d80; --red: #c44; --blue: #49c;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}
header {{ background: var(--text); color: #fff; padding: 2rem; text-align: center; }}
header h1 {{ font-size: 1.8rem; font-weight: 700; letter-spacing: 0.05em; }}
header .date {{ color: var(--muted); font-size: 0.9rem; margin-top: 0.3rem; }}
header .stats {{ margin-top: 0.8rem; font-size: 0.85rem; color: var(--accent-light); }}
main {{ max-width: 900px; margin: 0 auto; padding: 1.5rem; }}
section {{ margin-bottom: 2rem; }}
h2 {{ font-size: 1.3rem; font-weight: 700; margin-bottom: 0.8rem; padding-bottom: 0.3rem; border-bottom: 2px solid var(--accent); }}
h3 {{ font-size: 1rem; font-weight: 600; margin: 1rem 0 0.5rem; color: var(--muted); }}
.brief-summary {{ font-size: 0.95rem; color: var(--text); margin-bottom: 0.5rem; }}
.brief-item {{ margin-bottom: 0.4rem; }}
.brief-title {{ font-weight: 600; }}
.brief-detail {{ font-size: 0.85rem; color: var(--muted); }}
.brief-detail em {{ font-style: italic; }}
.signal-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin-bottom: 0.8rem; }}
.signal-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }}
.signal-name {{ font-size: 1.1rem; font-weight: 700; }}
.signal-label {{ font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; text-transform: uppercase; font-weight: 600; }}
.signal-label.new {{ background: var(--accent-light); color: var(--accent); }}
.signal-label.rising {{ background: #e8f5e9; color: var(--green); }}
.signal-label.hot {{ background: #fff3e0; color: var(--amber); }}
.signal-label.stable {{ background: #e3f2fd; color: var(--blue); }}
.signal-label.cooling {{ background: #fce4ec; color: var(--red); }}
.signal-meta {{ display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem; }}
.score-bar {{ flex: 1; height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }}
.score-fill {{ display: block; height: 100%; background: var(--accent); border-radius: 3px; }}
.score-value {{ font-weight: 700; font-size: 0.9rem; min-width: 30px; text-align: right; }}
.signal-stats {{ font-size: 0.8rem; color: var(--muted); }}
.rep-items {{ margin-top: 0.5rem; }}
.rep-item {{ margin-bottom: 0.4rem; padding-left: 0.8rem; border-left: 3px solid var(--accent-light); }}
.rep-item a {{ color: var(--accent); text-decoration: none; font-weight: 600; font-size: 0.9rem; }}
.rep-item a:hover {{ text-decoration: underline; }}
.rep-title-no-link {{ font-weight: 600; font-size: 0.9rem; }}
.rep-source {{ font-size: 0.75rem; color: var(--muted); margin-left: 0.3rem; }}
.rep-summary {{ font-size: 0.8rem; color: var(--text); margin-top: 0.2rem; }}
.candidate-card {{ display: flex; align-items: center; gap: 0.5rem; background: var(--card); border: 1px solid var(--border); border-radius: 6px; padding: 0.5rem 0.8rem; margin-bottom: 0.4rem; }}
.candidate-name {{ font-weight: 600; flex: 1; }}
.candidate-label {{ font-size: 0.7rem; color: var(--muted); }}
.candidate-score {{ font-weight: 700; color: var(--accent); }}
.health-item {{ display: flex; gap: 1rem; padding: 0.4rem 0.6rem; border-radius: 4px; margin-bottom: 0.3rem; font-size: 0.85rem; }}
.health-ok {{ background: #e8f5e9; }}
.health-warn {{ background: #fff3e0; }}
.health-error {{ color: var(--muted); font-style: italic; flex: 1; }}
.run-item {{ display: flex; gap: 1rem; padding: 0.3rem 0; font-size: 0.85rem; border-bottom: 1px solid var(--border); }}
.run-time {{ color: var(--muted); font-family: monospace; }}
.run-status {{ font-weight: 600; }}
.run-success {{ color: var(--green); }}
.run-failed {{ color: var(--red); }}
.run-skipped {{ color: var(--muted); }}
.empty {{ color: var(--muted); font-style: italic; padding: 0.5rem 0; }}
.news-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 0.8rem 1rem; margin-bottom: 0.6rem; }}
.news-card a {{ color: var(--accent); text-decoration: none; font-weight: 600; font-size: 0.95rem; display: block; }}
.news-card a:hover {{ text-decoration: underline; }}
.news-title-nolink {{ font-weight: 600; font-size: 0.95rem; display: block; }}
.news-source {{ font-size: 0.75rem; color: var(--muted); }}
.news-summary {{ font-size: 0.82rem; color: var(--text); margin-top: 0.3rem; }}
footer {{ text-align: center; padding: 1.5rem; color: var(--muted); font-size: 0.8rem; border-top: 1px solid var(--border); margin-top: 2rem; }}
</style>
</head>
<body>
<header>
  <h1>FASHION RADAR</h1>
  <p class="date">{date} · Generated {generated_at}</p>
  <div class="stats">{item_count} signals · {entity_count} tracked entities · {candidate_count} candidates</div>
</header>
<main>
  <section id="brief"><h2>Daily Brief</h2>{brief_html}</section>
  <section id="signals"><h2>Top Signals</h2>{signals_html}</section>
  <section id="candidates"><h2>Candidate Signals</h2>{candidates_html}</section>
  <section id="health"><h2>Source Health & Runs</h2>{health_html}</section>
  <section id="news"><h2>Latest Collected News</h2>{news_html}</section>
</main>
<footer>
  Fashion Radar · Local observed signals from configured sources · No demand proof · No platform coverage verification
</footer>
</body>
</html>"""
