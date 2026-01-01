#!/usr/bin/env python3
"""
Download additional blog posts by searching the site.
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent
SOURCES_DIR = BASE_DIR / "sources" / "blog_posts"
EXTRACTED_DIR = BASE_DIR / "extracted" / "blog_posts"
METADATA_DIR = BASE_DIR / "metadata" / "blog_posts"

SOURCES_DIR.mkdir(parents=True, exist_ok=True)
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def scrape_blog_post(url, dest_html_path, dest_txt_path):
    """Scrape a blog post."""
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()

        with open(dest_html_path, 'w', encoding='utf-8') as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, 'lxml')

        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()

        article = soup.find('article') or soup.find('main') or soup.find(class_='entry-content')

        if article:
            title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"

            paragraphs = article.find_all(['p', 'h2', 'h3', 'h4', 'blockquote', 'li'])
            content_lines = [title, "=" * len(title), ""]

            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 10:
                    content_lines.append(text)
                    content_lines.append("")

            clean_text = "\n".join(content_lines)
        else:
            clean_text = soup.get_text(separator='\n', strip=True)

        with open(dest_txt_path, 'w', encoding='utf-8') as f:
            f.write(clean_text)

        return True, len(clean_text.split())

    except Exception as e:
        log(f"  FAILED: {e}")
        return False, 0

# Additional blog post URLs to try (reconstructed patterns)
ADDITIONAL_POSTS = [
    # Diversity and Speech series - missing parts
    {"slug": "diversity-and-speech-part-25-growing-up-bi-religious-by-carlos-cortes", "title": "Diversity and Speech #25: Growing Up Bi-religious"},
    {"slug": "diversity-and-speech-25-growing-up-bi-religious-by-carlos-cortes", "title": "Diversity and Speech #25: Growing Up Bi-religious (alt)"},
    {"slug": "diversity-and-speech-part-31-health-equity-by-carlos-cortes", "title": "Diversity and Speech Part 31: Health Equity"},
    {"slug": "diversity-and-speech-31-health-equity-by-carlos-cortes", "title": "Diversity and Speech Part 31: Health Equity (alt)"},
    {"slug": "diversity-and-speech-part-32-language-tensions-by-carlos-cortes", "title": "Diversity and Speech Part 32: Language Tensions"},
    {"slug": "diversity-and-speech-32-language-tensions-by-carlos-cortes", "title": "Diversity and Speech Part 32: Language Tensions (alt)"},
    {"slug": "diversity-and-speech-part-34-revisiting-privilege-by-carlos-cortes", "title": "Diversity and Speech Part 34: Revisiting Privilege"},
    {"slug": "diversity-and-speech-34-revisiting-privilege-by-carlos-cortes", "title": "Diversity and Speech Part 34: Revisiting Privilege (alt)"},
    {"slug": "diversity-and-speech-part-38-conversations-at-the-cheech-by-carlos-cortes", "title": "Diversity and Speech Part 38: Conversations at The Cheech"},
    {"slug": "diversity-and-speech-38-conversations-at-the-cheech-by-carlos-cortes", "title": "Diversity and Speech Part 38: Conversations at The Cheech (alt)"},
    {"slug": "diversity-and-speech-part-39-creating-health-equity-by-carlos-cortes", "title": "Diversity and Speech Part 39: Creating Health Equity"},
    {"slug": "diversity-and-speech-39-creating-health-equity-by-carlos-cortes", "title": "Diversity and Speech Part 39: Creating Health Equity (alt)"},
    # Renewing Diversity series - missing parts
    {"slug": "renewing-diversity-2-teaching-health-equity-by-carlos-cortes", "title": "Renewing Diversity #2: Teaching Health Equity"},
    {"slug": "renewing-diversity-part-2-teaching-health-equity-by-carlos-cortes", "title": "Renewing Diversity Part 2: Teaching Health Equity"},
    {"slug": "renewing-diversity-3-we-failed-george-floyd-by-carlos-cortes", "title": "Renewing Diversity #3: We Failed George Floyd"},
    {"slug": "renewing-diversity-part-3-we-failed-george-floyd-by-carlos-cortes", "title": "Renewing Diversity Part 3: We Failed George Floyd"},
    {"slug": "renewing-diversity-4-a-sliver-of-bone-by-carlos-cortes", "title": "Renewing Diversity No. 4: A Sliver of Bone"},
    {"slug": "renewing-diversity-no-4-a-sliver-of-bone-by-carlos-cortes", "title": "Renewing Diversity No. 4: A Sliver of Bone (alt)"},
    {"slug": "renewing-diversity-part-8-updating-the-classics-by-carlos-cortes", "title": "Renewing Diversity Part 8: Updating the Classics"},
    {"slug": "renewing-diversity-8-updating-the-classics-by-carlos-cortes", "title": "Renewing Diversity Part 8: Updating the Classics (alt)"},
    {"slug": "renewing-diversity-part-10-unpacking-the-inclusivity-dilemma-by-carlos-cortes", "title": "Renewing Diversity Part 10: Unpacking the Inclusivity Dilemma"},
    {"slug": "renewing-diversity-10-unpacking-the-inclusivity-dilemma-by-carlos-cortes", "title": "Renewing Diversity Part 10: Unpacking the Inclusivity Dilemma (alt)"},
    {"slug": "renewing-diversity-part-11-the-mysterious-world-of-diversity-and-economics-by-carlos-cortes", "title": "Renewing Diversity Part 11: Diversity and Economics"},
    {"slug": "renewing-diversity-11-the-mysterious-world-of-diversity-and-economics-by-carlos-cortes", "title": "Renewing Diversity Part 11: Diversity and Economics (alt)"},
]

def main():
    log("=== Searching for Additional Blog Posts ===")
    results = []
    found = 0

    for post in ADDITIONAL_POSTS:
        url = f"https://americandiversityreport.com/{post['slug']}/"

        filename_base = post['slug'][:80]
        html_path = SOURCES_DIR / f"{filename_base}.html"
        txt_path = EXTRACTED_DIR / f"{filename_base}.txt"

        # Skip if already exists
        if html_path.exists():
            log(f"Already exists: {post['title'][:50]}...")
            continue

        log(f"Trying: {post['title'][:50]}...")

        try:
            response = session.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                success, word_count = scrape_blog_post(url, html_path, txt_path)
                if success:
                    log(f"  FOUND! {word_count} words")
                    found += 1
                    results.append({"title": post['title'], "status": "found", "words": word_count})
            else:
                log(f"  Not found (HTTP {response.status_code})")
        except Exception as e:
            log(f"  Error: {e}")

        time.sleep(1)

    log(f"\n=== Summary: Found {found} additional posts ===")
    return results

if __name__ == "__main__":
    main()
