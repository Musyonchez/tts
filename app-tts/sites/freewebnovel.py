from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import BaseSite


class FreeWebNovel(BaseSite):
    BASE_URL = "https://freewebnovel.com"

    def extract_content(self, soup: BeautifulSoup) -> tuple[str, str]:
        title_tag = soup.select_one("h1.tit, h2.tit, .chapter-title, h1")
        title = title_tag.get_text(strip=True) if title_tag else "Chapter"

        content_div = (
            soup.select_one("div#chapter-article")
            or soup.select_one("div.txt")
            or soup.select_one("div.chapter-content")
            or soup.select_one("div.content")
        )

        if not content_div:
            return title, ""

        return title, self._clean_content_div(content_div)

    def find_next_url(self, soup: BeautifulSoup, current_url: str = "") -> str | None:
        for a in soup.select("a"):
            label = a.get_text(strip=True).lower()
            if "next" in label:
                href = a.get("href", "")
                if href:
                    next_url = urljoin(self.BASE_URL, href)
                    if next_url != current_url:
                        return next_url
        return None
