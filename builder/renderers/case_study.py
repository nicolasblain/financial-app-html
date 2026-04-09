"""Renders narrative case studies."""

from . import esc, tag_attr


def _card(item):
    tags = tag_attr(item.get("modules", []))
    title = item["title"]
    persona = item["persona"]
    slug = item["_slug"]
    summary = item.get("summary", "")
    desc_html = f'<p class="card-desc">{esc(summary)}</p>' if summary else ""
    return (
        f'<li class="content-card case-study-card" '
        f'data-type="case-study" data-name="{esc(title)}" '
        f'data-tags="{esc(tags)}" data-persona="{esc(persona)}" data-slug="{esc(slug)}">'
        f'<a href="content/case-studies/{esc(item["_file"])}" class="card-inner">'
        f'<span class="card-stage card-stage--case">{esc(persona)}</span>'
        f'<h3 class="card-title">{esc(title)}</h3>'
        f'{desc_html}'
        f'</a></li>'
    )


def render(items):
    items = sorted(items, key=lambda i: (i.get("persona", ""), i["title"].lower()))
    return "\n".join("    " + _card(i) for i in items)
