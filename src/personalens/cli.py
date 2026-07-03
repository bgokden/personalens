"""CLI: personalens review <url> — a code-review, but for UI/products."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from personalens import __version__


def _cmd_review(args) -> int:
    from personalens.personas import default_personas, load_personas
    from personalens.report import write_report
    from personalens.review import review_url
    from personalens.vision import OllamaVisionBackend

    personas = load_personas(args.personas) if args.personas else default_personas()
    backend = OllamaVisionBackend(model=args.model, host=args.host)

    report = review_url(args.url, personas, backend)
    write_report(
        report,
        out_md=args.out,
        scores_json=args.scores,
        history_jsonl=args.history,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    print(f"Persona review — {args.url}", file=sys.stderr)
    print(f"Average: {report.average_score}/10", file=sys.stderr)
    for r in sorted(report.reviews, key=lambda x: x.score):
        print(f"  {r.score:>2}/10  {r.persona}", file=sys.stderr)

    if args.fail_under is not None and report.average_score < args.fail_under:
        print(f"FAIL: average {report.average_score} < {args.fail_under}", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="personalens", description="Persona-based UI/product review — like code review, for UX")
    p.add_argument("--version", action="version", version=f"personalens {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("review", help="Review a URL with personas")
    r.add_argument("url")
    r.add_argument("--personas", help="Path to a personas.md (default: built-in set)")
    r.add_argument("--out", help="Write the Markdown report here")
    r.add_argument("--scores", help="Write scores JSON here")
    r.add_argument("--history", help="Append scores to this JSONL to track over time")
    r.add_argument("--model", default="llama3.2-vision", help="Ollama vision model")
    r.add_argument("--host", default="http://localhost:11434", help="Ollama host")
    r.add_argument("--fail-under", type=float, help="Exit non-zero if average score is below this (CI gate)")
    r.set_defaults(func=_cmd_review)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
