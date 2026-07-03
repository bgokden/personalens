"""personalens — persona-based UI/product review (a code review, but for UX)."""

from personalens.capture import Capture
from personalens.personas import default_personas, load_personas, parse_personas
from personalens.report import to_markdown, to_scores, write_report
from personalens.review import review_captured, review_url
from personalens.types import Persona, PersonaReview, Report
from personalens.vision import FakeVisionBackend, OllamaVisionBackend, VisionBackend

__version__ = "0.1.0"

__all__ = [
    "Persona",
    "PersonaReview",
    "Report",
    "Capture",
    "parse_personas",
    "load_personas",
    "default_personas",
    "review_captured",
    "review_url",
    "to_markdown",
    "to_scores",
    "write_report",
    "VisionBackend",
    "OllamaVisionBackend",
    "FakeVisionBackend",
]
