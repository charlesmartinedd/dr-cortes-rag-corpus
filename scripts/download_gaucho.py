#!/usr/bin/env python3
"""
Download Gaúcho Politics in Brazil from Archive.org.
"""

import requests
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
SOURCES_DIR = BASE_DIR / "sources" / "books"
METADATA_DIR = BASE_DIR / "metadata" / "books"

SOURCES_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

def main():
    identifier = "gachopoliticsinb0000cort"

    # Get metadata first
    print(f"Fetching metadata for {identifier}...")
    meta_url = f"https://archive.org/metadata/{identifier}"

    try:
        response = session.get(meta_url, timeout=30)
        metadata = response.json()

        files = metadata.get("files", [])
        pdf_files = [f for f in files if f.get("name", "").endswith(".pdf")]

        if pdf_files:
            pdf_file = pdf_files[0]
            pdf_name = pdf_file["name"]
            pdf_url = f"https://archive.org/download/{identifier}/{pdf_name}"

            print(f"Found PDF: {pdf_name}")
            print(f"Attempting download...")

            # Try to download
            pdf_response = session.get(pdf_url, timeout=120, stream=True)
            pdf_response.raise_for_status()

            dest_path = SOURCES_DIR / "1974-Cortes-Gaucho-Politics-Brazil.pdf"
            with open(dest_path, 'wb') as f:
                for chunk in pdf_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded: {dest_path}")
            print(f"Size: {dest_path.stat().st_size:,} bytes")

            # Save metadata
            meta = {
                "id": "cortes_1974_gaucho_politics",
                "title": "Gaúcho Politics in Brazil: The Politics of Rio Grande do Sul, 1930-1964",
                "authors": ["Carlos E. Cortés"],
                "year": 1974,
                "resource_type": "book",
                "publisher": "University of New Mexico Press",
                "source_info": {
                    "url": pdf_url,
                    "archive_org_id": identifier,
                    "downloaded_at": datetime.now().isoformat()
                }
            }

            meta_path = METADATA_DIR / "1974-Cortes-Gaucho-Politics-Brazil.json"
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2)

            return True
        else:
            print("No PDF files found in this item")
            print("Available files:", [f.get("name") for f in files[:10]])
            return False

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print("This book may require 'borrowing' through Archive.org's lending library")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()
