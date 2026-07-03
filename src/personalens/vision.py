"""Pluggable vision-LLM backends (they read the screenshots as a persona).

A backend implements ``review(persona, images, page_text, schema) -> dict``.
Reference is Ollama with a local vision model (llama3.2-vision / qwen2-vl); swap in
an API model (GPT-4o / Claude vision) or a Fake for tests via the same protocol.
"""

from __future__ import annotations

import base64
import json
import urllib.request
from typing import Any, Protocol, runtime_checkable

from personalens.types import Persona

#: Structured schema the model must fill (grounded, no free-form drift).
REVIEW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 0, "maximum": 10},
        "summary": {"type": "string"},
        "positives": {"type": "array", "items": {"type": "string"}},
        "problems": {"type": "array", "items": {"type": "string"}},
        "visual_issues": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["score", "summary", "positives", "problems", "visual_issues"],
}


def build_prompt(persona: Persona, page_text: str) -> str:
    return (
        f"{persona.prompt_intro()}\n\n"
        "Look at the attached screenshot(s) of the page and review it strictly from "
        "this persona's point of view. Give an honest score from 0 to 10, a one-line "
        "summary, what works (positives), problems/friction, and visual issues "
        "(layout, spacing, readability, hierarchy). Be specific and critical.\n\n"
        f"Visible page text (for context):\n{page_text[:4000]}\n"
    )


@runtime_checkable
class VisionBackend(Protocol):
    def review(
        self, persona: Persona, images: list[bytes], page_text: str, schema: dict[str, Any]
    ) -> dict[str, Any]: ...


class OllamaVisionBackend:
    """Local Ollama vision model with JSON-schema-constrained output."""

    def __init__(
        self,
        model: str = "llama3.2-vision",
        host: str = "http://localhost:11434",
        temperature: float = 0.2,
        timeout: float = 240.0,
    ) -> None:
        self.model = model
        self.host = host.rstrip("/")
        self.temperature = temperature
        self.timeout = timeout

    def review(self, persona, images, page_text, schema):
        body = {
            "model": self.model,
            "prompt": build_prompt(persona, page_text),
            "images": [base64.b64encode(img).decode("ascii") for img in images],
            "stream": False,
            "format": schema,
            "options": {"temperature": self.temperature},
        }
        req = urllib.request.Request(
            f"{self.host}/api/generate",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return json.loads(payload["response"])


class FakeVisionBackend:
    """Deterministic backend for offline tests — cycles canned reviews."""

    def __init__(self, responses: list[dict[str, Any]]) -> None:
        if not responses:
            raise ValueError("FakeVisionBackend needs at least one response")
        self.responses = list(responses)
        self.calls = 0

    def review(self, persona, images, page_text, schema):
        r = self.responses[self.calls % len(self.responses)]
        self.calls += 1
        return r
