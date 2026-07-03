"""Screenshot capture via Playwright (install ``personalens[browser]`` + ``playwright install chromium``).

Playwright is imported lazily inside ``capture()`` so the rest of the package (and
its offline tests) needs no browser.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Capture:
    url: str
    title: str = ""
    page_text: str = ""
    screenshots: list[bytes] = field(default_factory=list)


class PlaywrightCapture:
    def __init__(self, width: int = 1280, height: int = 900, full_page: bool = True, wait_ms: int = 2000) -> None:
        self.width, self.height, self.full_page, self.wait_ms = width, height, full_page, wait_ms

    def capture(self, url: str) -> Capture:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": self.width, "height": self.height})
            page.goto(url, wait_until="load", timeout=60000)
            page.wait_for_timeout(self.wait_ms)
            shots = [page.screenshot(full_page=False)]
            if self.full_page:
                shots.append(page.screenshot(full_page=True))
            try:
                text = page.inner_text("body")
            except Exception:
                text = ""
            title = page.title()
            browser.close()
        return Capture(url=url, title=title, page_text=text, screenshots=shots)
