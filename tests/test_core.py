"""Offline tests: personas parsing, review aggregation, report, scoring.

No browser, no vision model — FakeVisionBackend + a hand-built Capture.
"""

import json

from personalens import (
    Capture,
    FakeVisionBackend,
    Report,
    default_personas,
    parse_personas,
    review_captured,
    to_markdown,
    to_scores,
    write_report,
)

CAPTURE = Capture(url="https://example.com", title="Example", page_text="Welcome to Example", screenshots=[b"\x89PNG-fake"])


def _backend():
    return FakeVisionBackend(
        [
            {"score": 8, "summary": "Clear and fast.", "positives": ["Clear CTA"], "problems": [], "visual_issues": ["Low contrast footer"]},
            {"score": 5, "summary": "Confusing on mobile.", "positives": [], "problems": ["No obvious next step"], "visual_issues": ["Text too small"]},
        ]
    )


def test_parse_personas_name_and_role():
    ps = parse_personas("## Nadia — Recruiter\nScans in 10 seconds for keywords.\n")
    assert len(ps) == 1
    assert ps[0].name == "Nadia" and ps[0].role == "Recruiter"
    assert "10 seconds" in ps[0].description


def test_default_personas_load():
    ps = default_personas()
    assert len(ps) >= 3
    assert all(p.name for p in ps)


def test_review_captured_aggregates_and_scores():
    ps = parse_personas("## A\nx\n## B\ny\n")
    report = review_captured(CAPTURE, ps, _backend())
    assert isinstance(report, Report)
    assert [r.persona for r in report.reviews] == ["A", "B"]
    assert report.reviews[0].score == 8 and report.reviews[1].score == 5
    assert report.average_score == 6.5
    assert report.reviews[0].visual_issues == ["Low contrast footer"]


def test_score_is_clamped():
    ps = parse_personas("## A\nx\n")
    backend = FakeVisionBackend([{"score": 42, "summary": "", "positives": [], "problems": [], "visual_issues": []}])
    report = review_captured(CAPTURE, ps, backend)
    assert report.reviews[0].score == 10  # clamped to 0..10


def test_review_skips_backend_errors():
    class Boom:
        def review(self, *a, **k):
            raise RuntimeError("model down")

    ps = parse_personas("## A\nx\n")
    report = review_captured(CAPTURE, ps, Boom())  # on_error='skip' default
    assert report.reviews == []


def test_markdown_and_scores():
    ps = parse_personas("## A\nx\n## B\ny\n")
    report = review_captured(CAPTURE, ps, _backend())
    md = to_markdown(report)
    assert "Persona review" in md and "Average score: 6.5/10" in md
    assert "## A — 8/10" in md
    scores = to_scores(report)
    assert scores["scores"] == {"A": 8, "B": 5} and scores["average_score"] == 6.5


def test_write_report_and_history(tmp_path):
    ps = parse_personas("## A\nx\n")
    report = review_captured(CAPTURE, ps, FakeVisionBackend([{"score": 7, "summary": "ok", "positives": [], "problems": [], "visual_issues": []}]))
    md = tmp_path / "r.md"
    sc = tmp_path / "s.json"
    hist = tmp_path / "h.jsonl"
    write_report(report, out_md=str(md), scores_json=str(sc), history_jsonl=str(hist), timestamp="2026-07-03T00:00:00Z")
    assert md.read_text().startswith("# Persona review")
    assert json.loads(sc.read_text())["scores"]["A"] == 7
    write_report(report, history_jsonl=str(hist), timestamp="2026-07-04T00:00:00Z")
    assert len(hist.read_text().strip().splitlines()) == 2  # tracked over time
