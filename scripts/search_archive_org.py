#!/usr/bin/env python3
"""
Search Archive.org for Dr. Cortés's books.
"""

import requests
import json
from datetime import datetime

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Research Bot)'})

def search_archive(query):
    """Search Archive.org for items."""
    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": query,
        "output": "json",
        "rows": 10,
        "page": 1,
        "fl[]": ["identifier", "title", "creator", "year", "mediatype"]
    }

    try:
        response = session.get(url, params=params, timeout=30)
        data = response.json()
        return data.get("response", {}).get("docs", [])
    except Exception as e:
        print(f"Search failed: {e}")
        return []

def main():
    print("=== Searching Archive.org for Dr. Cortés's Books ===\n")

    searches = [
        'creator:"Carlos Cortes" AND mediatype:texts',
        'creator:"Carlos E. Cortes" AND mediatype:texts',
        'title:"multicultural" AND creator:"cortes"',
        'title:"children are watching" AND creator:"cortes"',
        'title:"gaucho politics"',
    ]

    all_results = {}

    for query in searches:
        print(f"Searching: {query}")
        results = search_archive(query)

        for item in results:
            identifier = item.get("identifier")
            if identifier and identifier not in all_results:
                all_results[identifier] = {
                    "identifier": identifier,
                    "title": item.get("title"),
                    "creator": item.get("creator"),
                    "year": item.get("year"),
                    "url": f"https://archive.org/details/{identifier}"
                }
                print(f"  Found: {item.get('title', 'Unknown')[:60]}")

    print(f"\n=== Total unique items found: {len(all_results)} ===")

    for identifier, info in all_results.items():
        print(f"\n{info['title']}")
        print(f"  URL: {info['url']}")
        print(f"  Year: {info.get('year', 'Unknown')}")

    return all_results

if __name__ == "__main__":
    main()
