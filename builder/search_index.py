"""Builds a lightweight JSON search index covering every loaded item.

Client-side `app.js` uses this for fuzzy-ish substring search across all
content types at once (not just the currently visible tab).
"""

import json


def build(items_by_type):
    entries = []
    for type_key, items in items_by_type.items():
        for item in items:
            # Pull a handful of searchable fields depending on type.
            name = (
                item.get("title")
                or item.get("term")
                or item.get("_slug")
            )
            haystack_parts = [
                name,
                item.get("summary", ""),
                item.get("stage", ""),
                item.get("persona", ""),
                " ".join(item.get("tags", []) if isinstance(item.get("tags"), list) else []),
                " ".join(item.get("aliases", []) if isinstance(item.get("aliases"), list) else []),
            ]
            entries.append({
                "type": type_key,
                "slug": item["_slug"],
                "name": name,
                "haystack": " ".join(p for p in haystack_parts if p).lower(),
            })
    return json.dumps(entries, ensure_ascii=False)
