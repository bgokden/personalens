"""Personas are defined in a versioned Markdown file so reviews are comparable
and scores can be tracked over time. Format:

    ## Name — Role
    One or more lines describing what this persona cares about.
"""

from __future__ import annotations

import re

from personalens.types import Persona

DEFAULT_PERSONAS_MD = """# Personas

## Impatient First-Time Visitor
Lands for the first time and skims for ~10 seconds. Wants to instantly get what
this is and what to do next. Leaves if confused or if the value isn't obvious.

## Mobile User
On a phone, one thumb. Cares about tap-target size, readability, and whether
content fits the screen without horizontal scrolling.

## Skeptical Evaluator
Actively looking for reasons NOT to trust this. Flags vague claims, missing proof,
unclear pricing, and anything that feels like marketing fluff.

## Accessibility-Conscious User
Cares about colour contrast, text size, clear hierarchy, and whether the page
would work with a screen reader or keyboard.
"""

_HEADING = re.compile(r"^##\s+(.+?)\s*$")


def parse_personas(text: str) -> list[Persona]:
    personas: list[Persona] = []
    name: str | None = None
    role = ""
    body: list[str] = []

    def flush() -> None:
        if name:
            personas.append(Persona(name=name, role=role, description=" ".join(body).strip()))

    for line in text.splitlines():
        m = _HEADING.match(line)
        if m:
            flush()
            head = m.group(1)
            if " — " in head:
                name, role = (p.strip() for p in head.split(" — ", 1))
            elif " - " in head:
                name, role = (p.strip() for p in head.split(" - ", 1))
            else:
                name, role = head.strip(), ""
            body = []
        elif name is not None and line.strip():
            body.append(line.strip())
    flush()
    return personas


def load_personas(path: str) -> list[Persona]:
    with open(path, encoding="utf-8") as fh:
        personas = parse_personas(fh.read())
    if not personas:
        raise ValueError(f"No personas found in {path}")
    return personas


def default_personas() -> list[Persona]:
    return parse_personas(DEFAULT_PERSONAS_MD)
