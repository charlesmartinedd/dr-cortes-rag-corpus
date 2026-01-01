# Dr. Carlos Cortés RAG Corpus

Academic corpus for RAG (Retrieval Augmented Generation) containing works by Dr. Carlos E. Cortés on multicultural education, diversity, and ethnic studies.

## Source

Built from: [Dr. Carlos Cortés Annotated Bibliography (APA 7)](https://github.com/alexandriasworld1234-source/carlosecortes/blob/main/Dr_Carlos_Cortes_Annotated_Bibliography_APA7.txt)

## Structure

```
dr-cortes-rag-corpus/
├── sources/           # Original downloaded files
│   ├── books/
│   ├── journal_articles/
│   ├── blog_posts/    # HTML files
│   ├── policy_docs/
│   └── eric_docs/     # ERIC PDFs
├── extracted/         # Plain text extractions
│   └── (mirrors sources/)
├── metadata/          # JSON sidecar files
├── scripts/           # Download & extraction scripts
├── logs/              # Processing logs
└── manifest.json      # Master index of all items
```

## Corpus Statistics

| Category | Downloaded | Placeholders | Words |
|----------|------------|--------------|-------|
| ERIC Docs | 1 | 1 | 106,688 |
| Blog Posts | 20 | - | 23,655 |
| Books | - | 5 | 1,840 |
| Journal Articles | - | 1 | 316 |
| Reference Works | - | 1 | 304 |
| Plays | - | 1 | 333 |
| **Total** | **21** | **9** | **133,136** |

**Placeholders**: AI-generated one-page summaries for items that couldn't be downloaded (books requiring borrowing, paywalled articles, out-of-print works). These provide context for the RAG even when full text isn't available.

## Usage

```python
# Load manifest
import json
with open('manifest.json') as f:
    manifest = json.load(f)

# Get all extracted texts
for item in manifest['items']:
    if item['extraction_status'] == 'completed':
        with open(item['extracted_path']) as f:
            text = f.read()
```

## Key Topics

- Multicultural education
- Diversity and inclusion
- Ethnic studies curriculum
- Media representation
- Language minority education
- Health equity
- Anti-racism

## About Dr. Carlos E. Cortés

Professor Emeritus of History at UC Riverside, Dr. Cortés has published extensively on multicultural education, media literacy, and diversity. He has consulted for major entertainment companies including DreamWorks and Nickelodeon.

## License

Downloaded materials retain their original copyright. This repository is for educational research purposes.
