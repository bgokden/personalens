"""Render a Report to Markdown (for PR comments) and track scores over time."""

from __future__ import annotations

import json

from personalens.types import Report


def to_markdown(report: Report) -> str:
    lines = [
        f"# Persona review — {report.url}",
        "",
        f"**Average score: {report.average_score}/10** across {len(report.reviews)} personas",
        "",
        "| Persona | Score |",
        "|---|:--:|",
    ]
    for r in sorted(report.reviews, key=lambda x: x.score):
        lines.append(f"| {r.persona} | {r.score}/10 |")
    lines.append("")
    for r in report.reviews:
        lines.append(f"## {r.persona} — {r.score}/10")
        if r.summary:
            lines.append(f"_{r.summary}_")
        for label, items in (("Positives", r.positives), ("Problems", r.problems), ("Visual issues", r.visual_issues)):
            if items:
                lines.append(f"\n**{label}**")
                lines += [f"- {x}" for x in items]
        lines.append("")
    return "\n".join(lines)


def to_scores(report: Report, timestamp: str | None = None) -> dict:
    d = {
        "url": report.url,
        "average_score": report.average_score,
        "scores": {r.persona: r.score for r in report.reviews},
    }
    if timestamp:
        d["timestamp"] = timestamp
    return d


def write_report(
    report: Report,
    out_md: str | None = None,
    scores_json: str | None = None,
    history_jsonl: str | None = None,
    timestamp: str | None = None,
) -> dict:
    if out_md:
        with open(out_md, "w", encoding="utf-8") as fh:
            fh.write(to_markdown(report))
    scores = to_scores(report, timestamp)
    if scores_json:
        with open(scores_json, "w", encoding="utf-8") as fh:
            json.dump(scores, fh, indent=2, ensure_ascii=False)
    if history_jsonl:
        with open(history_jsonl, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(scores, ensure_ascii=False) + "\n")
    return scores
