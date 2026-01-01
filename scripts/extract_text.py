#!/usr/bin/env python3
"""
Extract text from all downloaded PDFs.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from pypdf import PdfReader

BASE_DIR = Path(__file__).parent.parent
SOURCES_DIR = BASE_DIR / "sources"
EXTRACTED_DIR = BASE_DIR / "extracted"
METADATA_DIR = BASE_DIR / "metadata"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def extract_pdf(pdf_path, txt_path):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text_parts = []

        for i, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"[Page {i}]")
                text_parts.append(page_text)
                text_parts.append("")

        full_text = "\n".join(text_parts)

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

        word_count = len(full_text.split())
        return True, word_count, len(reader.pages)

    except Exception as e:
        log(f"  FAILED: {e}")
        return False, 0, 0

def main():
    log("=== Extracting Text from PDFs ===")

    # Find all PDFs in sources
    pdf_files = []
    for subdir in ['eric_docs', 'books', 'journal_articles', 'policy_docs']:
        pdf_dir = SOURCES_DIR / subdir
        if pdf_dir.exists():
            pdf_files.extend(pdf_dir.glob('*.pdf'))

    log(f"Found {len(pdf_files)} PDF files")

    results = []
    for pdf_path in pdf_files:
        # Determine output path
        rel_path = pdf_path.relative_to(SOURCES_DIR)
        txt_path = EXTRACTED_DIR / rel_path.with_suffix('.txt')
        txt_path.parent.mkdir(parents=True, exist_ok=True)

        log(f"Extracting: {pdf_path.name}")
        success, word_count, page_count = extract_pdf(pdf_path, txt_path)

        if success:
            log(f"  Extracted {word_count:,} words from {page_count} pages")

            # Update metadata
            meta_path = METADATA_DIR / rel_path.with_suffix('.json')
            if meta_path.exists():
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
            else:
                meta = {}

            meta['extraction'] = {
                'status': 'completed',
                'method': 'pypdf',
                'extracted_at': datetime.now().isoformat(),
                'word_count': word_count,
                'page_count': page_count
            }
            meta['file_info'] = meta.get('file_info', {})
            meta['file_info']['extracted_path'] = str(txt_path)

            meta_path.parent.mkdir(parents=True, exist_ok=True)
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2)

            results.append({
                'file': pdf_path.name,
                'status': 'extracted',
                'words': word_count,
                'pages': page_count
            })
        else:
            results.append({'file': pdf_path.name, 'status': 'failed'})

    log(f"\n=== Extracted {len([r for r in results if r['status'] == 'extracted'])} PDFs ===")
    return results

if __name__ == "__main__":
    main()
