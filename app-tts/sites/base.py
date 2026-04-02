from abc import ABC, abstractmethod
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


class BaseSite(ABC):
    BASE_URL: str = ""

    def fetch_chapter(self, url: str) -> BeautifulSoup:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")

    @abstractmethod
    def extract_content(self, soup: BeautifulSoup) -> tuple[str, str]:
        """Return (title, text) where text is newline-separated paragraphs."""
        ...

    @abstractmethod
    def find_next_url(self, soup: BeautifulSoup, current_url: str = "") -> str | None:
        ...

    def find_prev_url(self, soup: BeautifulSoup, current_url: str = "") -> str | None:
        return None

    def _clean_content_div(self, content_div) -> str:
        for tag in content_div.select("script, style, ins, .ads, [class*='adv']"):
            tag.decompose()
        paragraphs = content_div.get_text(separator="\n").splitlines()
        return "\n".join(line.strip() for line in paragraphs if line.strip())
