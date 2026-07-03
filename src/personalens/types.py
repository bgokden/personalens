"""Core types: personas, per-persona reviews, and the aggregate report."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Persona:
    name: str
    role: str = ""
    description: str = ""

    def prompt_intro(self) -> str:
        bits = [f"You are reviewing a web page as this persona: {self.name}"]
        if self.role:
            bits.append(f"({self.role})")
        if self.description:
            bits.append(f"— {self.description}")
        return " ".join(bits)


@dataclass
class PersonaReview:
    persona: str
    score: int  # 0-10
    summary: str = ""
    positives: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    visual_issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "persona": self.persona,
            "score": self.score,
            "summary": self.summary,
            "positives": self.positives,
            "problems": self.problems,
            "visual_issues": self.visual_issues,
        }


@dataclass
class Report:
    url: str
    reviews: list[PersonaReview]

    @property
    def average_score(self) -> float:
        if not self.reviews:
            return 0.0
        return round(sum(r.score for r in self.reviews) / len(self.reviews), 2)

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "average_score": self.average_score,
            "reviews": [r.to_dict() for r in self.reviews],
        }
