#!/usr/bin/env python3
"""
Generate manifest.json from all downloaded resources.
"""

import os
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SOURCES_DIR = BASE_DIR / "sources"
EXTRACTED_DIR = BASE_DIR / "extracted"
METADATA_DIR = BASE_DIR / "metadata"

def count_words_in_file(filepath):
    """Count words in a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return len(f.read().split())
    except:
        return 0

def generate_manifest():
    manifest = {
        "version": "1.0",
        "corpus_name": "Dr. Carlos Cortés Academic Corpus",
        "description": "Corpus for RAG - Multicultural education, diversity, ethnic studies",
        "source_bibliography": "https://github.com/alexandriasworld1234-source/carlosecortes/blob/main/Dr_Carlos_Cortes_Annotated_Bibliography_APA7.txt",
        "generated_at": datetime.now().isoformat(),
        "statistics": {
            "total_items_in_bibliography": 63,
            "items_downloaded": 0,
            "items_extracted": 0,
            "total_word_count": 0,
            "by_type": {}
        },
        "items": []
    }

    total_words = 0
    items_downloaded = 0
    items_extracted = 0
    by_type = {}

    # Scan all resource types
    for resource_type in ['eric_docs', 'books', 'journal_articles', 'blog_posts', 'policy_docs']:
        sources_path = SOURCES_DIR / resource_type
        extracted_path = EXTRACTED_DIR / resource_type
        metadata_path = METADATA_DIR / resource_type

        if not sources_path.exists():
            continue

        type_count = 0
        type_words = 0

        # Scan source files
        for source_file in sources_path.iterdir():
            if source_file.is_file():
                item = {
                    "resource_type": resource_type,
                    "source_file": source_file.name,
                    "source_path": str(source_file.relative_to(BASE_DIR)),
                    "download_status": "downloaded",
                    "extraction_status": "pending",
                    "word_count": 0
                }

                # Check for extracted text
                if source_file.suffix == '.pdf':
                    txt_file = extracted_path / source_file.with_suffix('.txt').name
                elif source_file.suffix == '.html':
                    # For blog posts, txt is in extracted folder
                    txt_file = extracted_path / source_file.with_suffix('.txt').name
                else:
                    txt_file = None

                if txt_file and txt_file.exists():
                    item["extraction_status"] = "completed"
                    item["extracted_path"] = str(txt_file.relative_to(BASE_DIR))
                    item["word_count"] = count_words_in_file(txt_file)
                    total_words += item["word_count"]
                    items_extracted += 1

                # Check for metadata
                meta_file = metadata_path / source_file.with_suffix('.json').name
                if meta_file.exists():
                    try:
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            meta = json.load(f)
                        item["title"] = meta.get("title", source_file.stem)
                        item["metadata_path"] = str(meta_file.relative_to(BASE_DIR))
                    except:
                        item["title"] = source_file.stem
                else:
                    item["title"] = source_file.stem

                manifest["items"].append(item)
                items_downloaded += 1
                type_count += 1
                type_words += item["word_count"]

        if type_count > 0:
            by_type[resource_type] = {
                "count": type_count,
                "word_count": type_words
            }

    # Update statistics
    manifest["statistics"]["items_downloaded"] = items_downloaded
    manifest["statistics"]["items_extracted"] = items_extracted
    manifest["statistics"]["total_word_count"] = total_words
    manifest["statistics"]["by_type"] = by_type

    # Sort items by type then name
    manifest["items"].sort(key=lambda x: (x["resource_type"], x["source_file"]))

    # Save manifest
    manifest_path = BASE_DIR / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest generated: {manifest_path}")
    print(f"\nStatistics:")
    print(f"  Items downloaded: {items_downloaded}")
    print(f"  Items extracted: {items_extracted}")
    print(f"  Total word count: {total_words:,}")
    print(f"\nBy type:")
    for rtype, stats in by_type.items():
        print(f"  {rtype}: {stats['count']} items, {stats['word_count']:,} words")

    return manifest

if __name__ == "__main__":
    generate_manifest()
