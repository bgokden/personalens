"""Run personas over a captured page and aggregate into a Report."""

from __future__ import annotations

from typing import Any

from personalens.capture import Capture
from personalens.types import Persona, PersonaReview, Report
from personalens.vision import REVIEW_SCHEMA, VisionBackend


def review_captured(
    capture: Capture,
    personas: list[Persona],
    backend: VisionBackend,
    schema: dict[str, Any] | None = None,
    on_error: str = "skip",
) -> Report:
    """Review an already-captured page with each persona. Testable without a browser."""
    schema = schema or REVIEW_SCHEMA
    reviews: list[PersonaReview] = []
    for p in personas:
        try:
            d = backend.review(p, capture.screenshots, capture.page_text, schema)
            reviews.append(
                PersonaReview(
                    persona=p.name,
                    score=max(0, min(10, int(d.get("score", 0)))),
                    summary=d.get("summary", ""),
                    positives=list(d.get("positives", [])),
                    problems=list(d.get("problems", [])),
                    visual_issues=list(d.get("visual_issues", [])),
                )
            )
        except Exception:
            if on_error == "raise":
                raise
            continue
    return Report(url=capture.url, reviews=reviews)


def review_url(
    url: str,
    personas: list[Persona],
    backend: VisionBackend,
    capturer=None,
    schema: dict[str, Any] | None = None,
) -> Report:
    """Capture the URL with Playwright, then review it."""
    from personalens.capture import PlaywrightCapture

    cap = (capturer or PlaywrightCapture()).capture(url)
    return review_captured(cap, personas, backend, schema)
