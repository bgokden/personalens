"""Real end-to-end (opt-in): Playwright capture + Ollama vision on a live URL.

Skipped by default and in CI. Run locally:
    PERSONALENS_INTEGRATION=1 pytest tests/test_integration.py -q
Requires: pip install -e ".[browser]" && playwright install chromium, plus Ollama
running with a vision model (default llama3.2-vision; override PERSONALENS_MODEL).
"""

import os

import pytest


@pytest.mark.integration
def test_review_real_url():
    if os.environ.get("PERSONALENS_INTEGRATION") != "1":
        pytest.skip("set PERSONALENS_INTEGRATION=1 (browser + Ollama vision) to run")
    pytest.importorskip("playwright")

    from personalens import default_personas, review_url
    from personalens.vision import OllamaVisionBackend

    url = os.environ.get("PERSONALENS_URL", "https://example.com")
    backend = OllamaVisionBackend(model=os.environ.get("PERSONALENS_MODEL", "llama3.2-vision"))
    report = review_url(url, default_personas()[:2], backend)

    assert report.url == url
    for r in report.reviews:
        assert 0 <= r.score <= 10
