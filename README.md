# personalens

[![CI](https://github.com/bgokden/personalens/actions/workflows/ci.yml/badge.svg)](https://github.com/bgokden/personalens/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![deps](https://img.shields.io/badge/runtime%20deps-0-brightgreen)

**A code review, but for UI/products.** Point it at a URL and it reviews the page
from the point of view of each of your **personas** — driving a browser
(Playwright), taking **screenshots**, and asking a **vision LLM** to score it and
list problems. You get a report and per-persona **scores you can track over time**,
and — like a code reviewer on a PR — it can **comment and gate the merge**.

Runs local-first (Ollama vision), zero runtime dependencies in the core.

## Why

Automated tests tell you the code works. They don't tell you a first-time visitor
is confused, the mobile layout is broken, or a skeptic doesn't trust your claims.
`personalens` puts that persona-based UX review in your pipeline, so a regression in
*experience* fails the check the same way a broken test does.

## Quickstart

```bash
pip install "personalens[browser]"
playwright install chromium
ollama pull qwen3-vl                 # best; or qwen2.5-vl / llama3.2-vision — a capable vision model
                                     # (newer/larger vision models review best; tiny ones
                                     #  like moondream are too weak)

personalens review https://example.com \
  --personas personas.md \
  --out report.md --scores scores.json --history scores-history.jsonl
```

Output — a Markdown report and, per persona, a score 0–10 with positives,
problems, and visual issues:

```
Persona review — https://example.com
Average: 7.2/10
   5/10  Mobile User
   7/10  Skeptical Evaluator
   8/10  Impatient First-Time Visitor
   9/10  Accessibility-Conscious User
```

## Example review (real output)

A real run (Playwright + **Qwen2.5-VL**) reviewing a product landing page:

```markdown
## Impatient First-Time Visitor — 7/10
_Clear tagline and message, but lacks a clear call-to-action for someone skimming._

**Problems**
- No clear call-to-action — not obvious what to do next
- Content is dense and could overwhelm a first-time skimmer

## Mobile User — 7/10
_Visually striking and easy to navigate; some sections run long._

**Problems**
- Long sections could be broken into smaller, digestible chunks
- Dense sections would benefit from subheadings, bullets, or a visual
```

Review quality tracks the vision model — **Qwen3-VL** gives the sharpest, most
critical feedback; **Qwen2.5-VL** / **llama3.2-vision** are solid; very small models
are too weak. (The Ollama backend falls back to prompt-based JSON for models that
don't support the `format` schema constraint, so newer vision models work too.)

## Personas (tracked over time)

Personas live in a versioned [`personas.md`](personas.md):

```markdown
## Impatient First-Time Visitor
Skims for ~10 seconds; wants to instantly get what this is and what to do next.

## Skeptical Evaluator
Looking for reasons NOT to trust this — vague claims, missing proof, unclear pricing.
```

Because the personas are pinned, scores are comparable across runs. Append each run
to `scores-history.jsonl` and you have a trend line for every persona.

## In CI — review every deploy (the "code review" part)

Run it on each PR against your preview URL, comment the result, and fail the check
if a persona score regresses:

```yaml
# .github/workflows/ux-review.yml
name: UX review
on: pull_request
jobs:
  personalens:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install "personalens[browser]" && playwright install --with-deps chromium
      # point --model/--host at your vision backend (local runner or hosted)
      - run: personalens review "$PREVIEW_URL" --out report.md --fail-under 6
        env:
          PREVIEW_URL: ${{ steps.deploy.outputs.preview-url }}
      - if: always()
        uses: marocchino/sticky-pull-request-comment@v2
        with: { path: report.md }
```

`--fail-under N` exits non-zero when the average drops below `N`, turning UX into a
merge gate.

## Pluggable vision backends

An image reviewer is just `review(persona, images, page_text, schema) -> dict`:

- **`OllamaVisionBackend`** — local (`llama3.2-vision` / `qwen2-vl`), default, zero deps.
- Bring your own for **GPT-4o / Claude vision** or any endpoint via the protocol.
- **`FakeVisionBackend`** — deterministic, for offline tests.

Output is **JSON-schema-constrained**, so scores and findings are structured, not free text.

## Choosing a vision model

| Model | Approx. local RAM | Notes |
|---|---|---|
| `qwen3-vl:8b` | ~8–12 GB | **Recommended local default** — sharpest reviews in testing |
| `qwen2.5-vl:7b` | ~8 GB | Solid local alternative |
| `llama3.2-vision` | ~8 GB | General-purpose |
| `qwen3.6` *(36B, native multimodal)* | ~40+ GB | Best quality, but too large for a typical laptop — run it via a **cloud / OpenAI-compatible endpoint** (`--host`), not locally |
| `moondream` | tiny | Too weak — avoid |

Large native-multimodal models won't load on a typical 32 GB machine (Ollama returns
`unable to load model`); personalens skips a model it can't load rather than crashing.
Point `--host`/`--model` at a hosted endpoint to use them.

## How it works

1. **Capture** — Playwright loads the URL and screenshots key states (viewport + full page).
2. **Personas** — loaded from `personas.md` (or a sensible built-in set).
3. **Review** — each persona scores the *same* screenshots via the vision LLM.
4. **Report** — Markdown + `scores.json`, with a `scores-history.jsonl` trend.

## Roadmap

- Autonomous click-through (a browser agent exploring flows, not just the landing page).
- Diff mode — compare two URLs / before-and-after a change.
- Hosted runner with dashboards and score history.

## Development

```bash
pip install -e ".[dev]"
pytest        # offline core tests (FakeVisionBackend + a built Capture; no browser/model)
```

Real browser + vision are exercised by a gated integration test
(`PERSONALENS_INTEGRATION=1`) and verified locally.

## License

MIT © [Berk Gökden](https://berkgokden.com)
