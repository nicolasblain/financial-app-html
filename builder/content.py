"""Phase 1-3: discover, parse, validate content files by type."""

import os
from pathlib import Path

from . import frontmatter


class ContentError(Exception):
    pass


def discover(content_root, content_type):
    """Return sorted list of .md file paths under content/<content_type>/, skipping `_` files."""
    folder = Path(content_root) / content_type
    if not folder.exists():
        return []
    return sorted(
        p for p in folder.iterdir()
        if p.suffix == ".md" and not p.name.startswith("_")
    )


def load_item(path):
    """Read a markdown file, return dict with frontmatter + metadata."""
    text = path.read_text(encoding="utf-8")
    meta, body = frontmatter.parse(text)
    meta["_file"] = path.name
    meta["_path"] = str(path)
    meta["_slug"] = meta.get("slug") or path.stem
    meta["_body"] = body
    return meta


def validate(item, schema, source_label):
    """Validate a single item against a schema dict.

    schema = {
        "required": [...],
        "enums": {field: [allowed, ...]},
        "types": {field: type_or_tuple},
    }
    """
    for field in schema.get("required", []):
        if field not in item or item[field] == "":
            raise ContentError(
                f"{source_label}: missing required field '{field}'"
            )
    for field, allowed in schema.get("enums", {}).items():
        if field in item and item[field] not in allowed:
            raise ContentError(
                f"{source_label}: field '{field}' = {item[field]!r} not in {allowed}"
            )
    for field, expected in schema.get("types", {}).items():
        if field in item and item[field] != "" and not isinstance(item[field], expected):
            raise ContentError(
                f"{source_label}: field '{field}' must be {expected}, got {type(item[field]).__name__}"
            )
    return item


def load_type(content_root, content_type, schema):
    """Discover + parse + validate all items of a content type. Drafts are excluded."""
    items = []
    for path in discover(content_root, content_type):
        item = load_item(path)
        if item.get("status") == "draft":
            continue
        validate(item, schema, f"{content_type}/{path.name}")
        items.append(item)
    return items
