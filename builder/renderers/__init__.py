"""Per-content-type renderers. Each module exports render(items) -> str."""

import html as _html


def esc(s):
    return _html.escape("" if s is None else str(s), quote=True)


def tag_attr(tags):
    if isinstance(tags, list):
        return " ".join(tags)
    return tags or ""
