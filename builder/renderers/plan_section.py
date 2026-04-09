"""Renders plan sections — reusable sections that compose a generated financial plan."""

from . import esc, tag_attr


def _card(item):
    tags = tag_attr(item.get("applies_to", []))
    title = item["title"]
    sid = item["section_id"]
    slug = item["_slug"]
    summary = item.get("summary", "")
    desc_html = f'<p class="card-desc">{esc(summary)}</p>' if summary else ""
    return (
        f'<li class="content-card plan-section-card" '
        f'data-type="plan-section" data-name="{esc(title)}" '
        f'data-tags="{esc(tags)}" data-slug="{esc(slug)}">'
        f'<a href="content/plan-sections/{esc(item["_file"])}" class="card-inner">'
        f'<span class="card-stage card-stage--section">§ {esc(sid)}</span>'
        f'<h3 class="card-title">{esc(title)}</h3>'
        f'{desc_html}'
        f'</a></li>'
    )


def render(items):
    items = sorted(items, key=lambda i: (i.get("order", 99), i["title"].lower()))
    return "\n".join("    " + _card(i) for i in items)
