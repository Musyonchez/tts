import sys
import requests
import pyttsx3
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.fanmtl.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_chapter(url: str):
    print(f"\nFetching: {url}")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


def extract_content(soup: BeautifulSoup):
    title_tag = soup.select_one("h2")
    title = title_tag.get_text(strip=True) if title_tag else "Chapter"

    content_div = (
        soup.select_one("div#chapter-content")
        or soup.select_one("div.chapter-content")
        or soup.select_one("div.reading-content")
        or soup.select_one("div.content")
    )

    if not content_div:
        print("WARNING: Could not find chapter content div.")
        return title, ""

    for tag in content_div.select("script, style, ins, .ads, [class*='adv']"):
        tag.decompose()

    paragraphs = content_div.get_text(separator="\n").splitlines()
    text = "\n".join(line.strip() for line in paragraphs if line.strip())
    return title, text


def find_next_url(soup: BeautifulSoup) -> str | None:
    for a in soup.select("a"):
        label = a.get_text(strip=True).lower()
        if "next" in label:
            href = a.get("href", "")
            if href and "_" in href and href.endswith(".html"):
                return urljoin(BASE_URL, href)
    return None


def speak(engine: pyttsx3.Engine, title: str, text: str):
    print(f"\n--- {title} ---")
    print(f"Reading {len(text.split())} words...\n")
    engine.say(title)
    engine.say(text)
    engine.runAndWait()


def main():
    start_url = sys.argv[1] if len(sys.argv) > 1 else (
        "https://www.fanmtl.com/novel/ke407980_1.html"
    )

    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)  # Zira
    engine.setProperty("rate", 450)
    engine.setProperty("volume", 1.0)

    url = start_url
    while url:
        soup = fetch_chapter(url)
        title, text = extract_content(soup)

        if not text:
            print("No content found — stopping.")
            break

        speak(engine, title, text)

        next_url = find_next_url(soup)
        if not next_url or next_url == url:
            print("\nNo next chapter found — done.")
            break

        print(f"\nMoving to next chapter: {next_url}")
        url = next_url


if __name__ == "__main__":
    main()
