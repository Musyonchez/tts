import sys
import re
import requests
import pyttsx3
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://freewebnovel.com"

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
    # Title
    title_tag = soup.select_one("h1.tit, h2.tit, .chapter-title, h1")
    title = title_tag.get_text(strip=True) if title_tag else "Chapter"

    # Chapter text — freewebnovel puts it in div#chapter-article or div.txt
    content_div = (
        soup.select_one("div#chapter-article")
        or soup.select_one("div.txt")
        or soup.select_one("div.chapter-content")
        or soup.select_one("div.content")
    )

    if not content_div:
        print("WARNING: Could not find chapter content div.")
        return title, ""

    # Remove ads / script tags
    for tag in content_div.select("script, style, ins, .ads, [class*='adv']"):
        tag.decompose()

    paragraphs = content_div.get_text(separator="\n").splitlines()
    text = "\n".join(line.strip() for line in paragraphs if line.strip())
    return title, text


def find_next_url(soup: BeautifulSoup, current_url: str) -> str | None:
    # Look for a "Next chapter" link
    for a in soup.select("a"):
        label = a.get_text(strip=True).lower()
        if "next" in label:
            href = a.get("href", "")
            if href:
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
        "https://freewebnovel.com/novel/beast-taming-abyssal-descent/chapter-1"
    )

    engine = pyttsx3.init()
    # Optional: tweak rate/volume
    engine.setProperty("rate", 175)   # words per minute
    engine.setProperty("volume", 1.0)

    url = start_url
    while url:
        soup = fetch_chapter(url)
        title, text = extract_content(soup)

        if not text:
            print("No content found — stopping.")
            break

        speak(engine, title, text)

        next_url = find_next_url(soup, url)
        if not next_url or next_url == url:
            print("\nNo next chapter found — done.")
            break

        print(f"\nMoving to next chapter: {next_url}")
        url = next_url


if __name__ == "__main__":
    main()
