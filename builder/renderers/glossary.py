"""Renders glossary terms. Each card is small and inline — no overlay by default."""

from . import esc, tag_attr


def _card(item):
    term = item["term"]
    slug = item["_slug"]
    aliases = item.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases] if aliases else []
    search_name = term + (" " + " ".join(aliases) if aliases else "")
    tags = tag_attr(aliases)
    alias_html = (
        f'<p class="card-desc">{esc(", ".join(aliases))}</p>' if aliases else ""
    )
    return (
        f'<li class="content-card glossary-card" '
        f'data-type="glossary" data-name="{esc(search_name)}" '
        f'data-tags="{esc(tags)}" data-slug="{esc(slug)}">'
        f'<a href="content/glossary/{esc(item["_file"])}" class="card-inner">'
        f'<h3 class="card-title">{esc(term)}</h3>'
        f'{alias_html}'
        f'</a></li>'
    )


def render(items):
    items = sorted(items, key=lambda i: i["term"].lower())
    return "\n".join("    " + _card(i) for i in items)
