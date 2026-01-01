#!/usr/bin/env python3
"""
Download all available resources from Dr. Carlos Cortés bibliography.
"""

import os
import json
import time
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# Configuration
BASE_DIR = Path(__file__).parent.parent
SOURCES_DIR = BASE_DIR / "sources"
EXTRACTED_DIR = BASE_DIR / "extracted"
METADATA_DIR = BASE_DIR / "metadata"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for d in [SOURCES_DIR, EXTRACTED_DIR, METADATA_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Session with retry
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# Logging
log_file = LOGS_DIR / f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log(msg):
    """Log to file and console."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def download_file(url, dest_path, timeout=60):
    """Download a file from URL."""
    try:
        response = session.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        size = os.path.getsize(dest_path)
        log(f"  Downloaded: {dest_path.name} ({size:,} bytes)")
        return True
    except Exception as e:
        log(f"  FAILED: {url} - {e}")
        return False

def get_md5(filepath):
    """Calculate MD5 hash of file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def create_metadata(item_id, title, resource_type, source_url, source_path, **kwargs):
    """Create metadata sidecar JSON."""
    metadata = {
        "id": item_id,
        "title": title,
        "resource_type": resource_type,
        "source_info": {
            "url": source_url,
            "downloaded_at": datetime.now().isoformat()
        },
        "file_info": {
            "source_path": str(source_path),
            "source_size_bytes": os.path.getsize(source_path) if source_path.exists() else 0,
            "source_md5": get_md5(source_path) if source_path.exists() else None
        },
        "extraction": {
            "status": "pending"
        }
    }
    metadata.update(kwargs)
    return metadata

# ============================================================================
# ERIC Documents
# ============================================================================

ERIC_DOCS = [
    {
        "id": "ED079204",
        "title": "Teaching the Chicano Experience",
        "year": 1973,
        "url": "https://files.eric.ed.gov/fulltext/ED079204.pdf"
    },
    {
        "id": "ED304241",
        "title": "The Education of Language Minority Students: A Contextual Interaction Model",
        "year": 1986,
        "url": "https://files.eric.ed.gov/fulltext/ED304241.pdf"
    }
]

def download_eric_docs():
    """Download ERIC documents."""
    log("\n=== Downloading ERIC Documents ===")
    results = []

    for doc in ERIC_DOCS:
        dest_dir = SOURCES_DIR / "eric_docs"
        dest_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{doc['year']}-Cortes-{doc['id']}.pdf"
        dest_path = dest_dir / filename

        log(f"Downloading {doc['id']}: {doc['title']}")
        success = download_file(doc['url'], dest_path)

        if success:
            # Create metadata
            meta = create_metadata(
                item_id=doc['id'].lower(),
                title=doc['title'],
                resource_type="eric_document",
                source_url=doc['url'],
                source_path=dest_path,
                year=doc['year'],
                eric_id=doc['id']
            )

            meta_path = METADATA_DIR / "eric_docs" / f"{filename.replace('.pdf', '.json')}"
            meta_path.parent.mkdir(parents=True, exist_ok=True)
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2)

            results.append({"id": doc['id'], "status": "downloaded", "path": str(dest_path)})
        else:
            results.append({"id": doc['id'], "status": "failed"})

        time.sleep(1)  # Be respectful

    return results

# ============================================================================
# Archive.org Book
# ============================================================================

def download_archive_org_book():
    """Download the Archive.org book."""
    log("\n=== Downloading Archive.org Book ===")

    # The Making—and Remaking—of a Multiculturalist
    url = "https://archive.org/download/makingremakingof0000cort/makingremakingof0000cort.pdf"

    dest_dir = SOURCES_DIR / "books"
    dest_dir.mkdir(parents=True, exist_ok=True)

    filename = "2002-Cortes-Making-Remaking-Multiculturalist.pdf"
    dest_path = dest_dir / filename

    log(f"Downloading: The Making—and Remaking—of a Multiculturalist")
    success = download_file(url, dest_path, timeout=120)

    if success:
        meta = create_metadata(
            item_id="cortes_2002_making_remaking",
            title="The Making—and Remaking—of a Multiculturalist",
            resource_type="book",
            source_url=url,
            source_path=dest_path,
            year=2002,
            authors=["Carlos E. Cortés"],
            publisher="Teachers College Press",
            archive_org_id="makingremakingof0000cort"
        )

        meta_path = METADATA_DIR / "books" / f"{filename.replace('.pdf', '.json')}"
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2)

        return {"status": "downloaded", "path": str(dest_path)}

    return {"status": "failed"}

# ============================================================================
# Blog Posts
# ============================================================================

BLOG_POSTS = [
    # Complete URLs
    {"slug": "speech-vs-diversity-diversity-vs-speech-by-carlos-e-cortes", "title": "Speech vs. Diversity, Diversity vs. Speech", "series": "diversity_speech"},
    {"slug": "diversity-vs-free-speech-part-1-an-invented-conflict-by-carlos-e-cortes", "title": "Diversity vs. Free Speech Part 1: An Invented Conflict", "series": "diversity_speech"},
    {"slug": "diversity-and-speech-part-10-harmful-speech-2070-by-carlos-e-cortes", "title": "Diversity and Speech Part 10: Harmful Speech 2070", "series": "diversity_speech"},
    {"slug": "diversity-and-speech-part-11-dehumanizing-speech-2070-by-carlos-e-cortes", "title": "Diversity and Speech Part 11: Dehumanizing Speech 2070", "series": "diversity_speech"},
    {"slug": "diversity-speech-part-15-english-language-learners-by-carlos-cortes", "title": "Diversity & Speech Part 15: English Language Learners", "series": "diversity_speech"},
    {"slug": "diversity-speech-part-16-creating-an-anti-racism-vision-statement-by-carlos-e-cortes", "title": "Diversity & Speech Part 16: Creating an Anti-Racism Vision Statement", "series": "diversity_speech"},
    {"slug": "diversity-and-speech-part-18-hate-speech-by-carlos-e-cortes", "title": "Diversity and Speech Part 18: Hate Speech", "series": "diversity_speech"},
    {"slug": "diversity-and-speech-no-27-training-future-psychologists-using-the-lens-of-history-by-carlos-e-cortes-marjorie-graham-howard", "title": "Diversity and Speech No. 27: Training Future Psychologists", "series": "diversity_speech"},
    {"slug": "diversity-and-speech-33-bi-religious-by-carlos-cortes-gary-cortes", "title": "Diversity and Speech #33: Bi-religious", "series": "diversity_speech"},
    {"slug": "diversity-and-speech-part-44-generations-of-gender-talk-by-carlos-cortes", "title": "Diversity and Speech Part 44: Generations of Gender Talk", "series": "diversity_speech"},
    {"slug": "diversity-and-speech-no-46-the-art-of-turning-90-by-carlos-cortes", "title": "Diversity and Speech No. 46: The Art of Turning 90", "series": "diversity_speech"},
    {"slug": "diversity-and-speech-part-14-health-equity-by-carlos-cortes-adwoa-osei", "title": "Diversity and Speech Part 14: Health Equity", "series": "diversity_speech"},
    {"slug": "renewing-diversity-1-high-school-ethnic-studies-by-carlos-cortes", "title": "Renewing Diversity #1: High School Ethnic Studies", "series": "renewing_diversity"},
    {"slug": "renewing-diversity-part-9-rediscovering-my-professional-journey-by-carlos-cortes", "title": "Renewing Diversity Part 9: Rediscovering My Professional Journey", "series": "renewing_diversity"},
    {"slug": "from-conditional-to-equitable-inclusion-by-carlos-cortes", "title": "From Conditional to Equitable Inclusion", "series": "standalone"},
]

def scrape_blog_post(url, dest_html_path, dest_txt_path):
    """Scrape a blog post, save HTML and extracted text."""
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()

        # Save raw HTML
        with open(dest_html_path, 'w', encoding='utf-8') as f:
            f.write(response.text)

        # Extract text
        soup = BeautifulSoup(response.text, 'lxml')

        # Remove scripts and styles
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()

        # Try to find main content
        article = soup.find('article') or soup.find('main') or soup.find(class_='post-content') or soup.find(class_='entry-content')

        if article:
            # Get title
            title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"

            # Get content
            paragraphs = article.find_all(['p', 'h2', 'h3', 'h4', 'blockquote', 'li'])
            content_lines = [title, "=" * len(title), ""]

            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 10:  # Skip tiny fragments
                    content_lines.append(text)
                    content_lines.append("")

            clean_text = "\n".join(content_lines)
        else:
            # Fallback: get all text
            clean_text = soup.get_text(separator='\n', strip=True)

        # Save extracted text
        with open(dest_txt_path, 'w', encoding='utf-8') as f:
            f.write(clean_text)

        word_count = len(clean_text.split())
        return True, word_count

    except Exception as e:
        log(f"  FAILED: {url} - {e}")
        return False, 0

def download_blog_posts():
    """Download all blog posts."""
    log("\n=== Downloading Blog Posts ===")
    results = []

    html_dir = SOURCES_DIR / "blog_posts"
    txt_dir = EXTRACTED_DIR / "blog_posts"
    meta_dir = METADATA_DIR / "blog_posts"

    html_dir.mkdir(parents=True, exist_ok=True)
    txt_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    for post in BLOG_POSTS:
        url = f"https://americandiversityreport.com/{post['slug']}/"

        # Clean filename from slug
        filename_base = post['slug'][:80]  # Truncate long slugs
        html_path = html_dir / f"{filename_base}.html"
        txt_path = txt_dir / f"{filename_base}.txt"

        log(f"Scraping: {post['title'][:60]}...")
        success, word_count = scrape_blog_post(url, html_path, txt_path)

        if success:
            meta = {
                "id": f"blog_{post['slug'][:50]}",
                "title": post["title"],
                "resource_type": "blog_post",
                "series": post["series"],
                "source_info": {
                    "url": url,
                    "downloaded_at": datetime.now().isoformat()
                },
                "file_info": {
                    "html_path": str(html_path),
                    "txt_path": str(txt_path),
                    "word_count": word_count
                },
                "extraction": {
                    "status": "completed",
                    "method": "beautifulsoup"
                }
            }

            meta_path = meta_dir / f"{filename_base}.json"
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2)

            results.append({"title": post['title'], "status": "downloaded", "words": word_count})
        else:
            results.append({"title": post['title'], "status": "failed"})

        time.sleep(2)  # Be respectful to the server

    return results

# ============================================================================
# Main
# ============================================================================

def main():
    log("=" * 60)
    log("Dr. Carlos Cortés RAG Corpus Downloader")
    log("=" * 60)

    all_results = {
        "started_at": datetime.now().isoformat(),
        "eric_docs": [],
        "archive_org": {},
        "blog_posts": [],
    }

    # Phase 1: ERIC Documents
    all_results["eric_docs"] = download_eric_docs()

    # Phase 2: Archive.org Book
    all_results["archive_org"] = download_archive_org_book()

    # Phase 3: Blog Posts
    all_results["blog_posts"] = download_blog_posts()

    all_results["completed_at"] = datetime.now().isoformat()

    # Save results
    results_path = BASE_DIR / "download_results.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)

    # Summary
    log("\n" + "=" * 60)
    log("DOWNLOAD SUMMARY")
    log("=" * 60)

    eric_success = sum(1 for r in all_results["eric_docs"] if r["status"] == "downloaded")
    log(f"ERIC Documents: {eric_success}/{len(ERIC_DOCS)}")

    archive_status = all_results["archive_org"].get("status", "unknown")
    log(f"Archive.org Book: {archive_status}")

    blog_success = sum(1 for r in all_results["blog_posts"] if r["status"] == "downloaded")
    log(f"Blog Posts: {blog_success}/{len(BLOG_POSTS)}")

    total_words = sum(r.get("words", 0) for r in all_results["blog_posts"])
    log(f"Total words from blogs: {total_words:,}")

    log(f"\nResults saved to: {results_path}")
    log(f"Log file: {log_file}")

if __name__ == "__main__":
    main()
