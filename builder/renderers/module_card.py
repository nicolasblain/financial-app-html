"""Renders planning modules as cards, grouped by stage."""

from . import esc, tag_attr

STAGE_ORDER = [
    "Intake",
    "Goals",
    "Analysis",
    "Plan Drafting",
    "Plan Delivery",
    "Monitoring",
]

STAGE_CSS = {
    "Intake": "intake",
    "Goals": "goals",
    "Analysis": "analysis",
    "Plan Drafting": "drafting",
    "Plan Delivery": "delivery",
    "Monitoring": "monitoring",
}


def _pill(stage):
    css = STAGE_CSS.get(stage, "other")
    return f'<span class="card-stage card-stage--{css}">{esc(stage)}</span>'


def _card(item):
    tags = tag_attr(item.get("tags", []))
    title = item["title"]
    slug = item["_slug"]
    stage = item.get("stage", "")
    desc = item.get("summary", "")
    order = item.get("order", 99)

    prereqs = item.get("prerequisites", [])
    if isinstance(prereqs, str):
        prereqs = [prereqs] if prereqs else []
    prereq_html = ""
    if prereqs:
        prereq_html = (
            '<div class="card-prereqs">Prereqs: '
            + ", ".join(esc(p) for p in prereqs)
            + "</div>"
        )
    desc_html = f'<p class="card-desc">{esc(desc)}</p>' if desc else ""

    return (
        f'<li class="content-card module-card" '
        f'data-type="module" data-name="{esc(title)}" data-stage="{esc(stage)}" '
        f'data-tags="{esc(tags)}" data-slug="{esc(slug)}" data-order="{esc(order)}">'
        f'<a href="content/modules/{esc(item["_file"])}" class="card-inner">'
        f'{_pill(stage)}'
        f'<h3 class="card-title">{esc(title)}</h3>'
        f'{desc_html}'
        f'{prereq_html}'
        f'</a></li>'
    )


def _stage_key(item):
    s = item.get("stage", "")
    try:
        return (STAGE_ORDER.index(s), item.get("order", 99), item["title"].lower())
    except ValueError:
        return (len(STAGE_ORDER), item.get("order", 99), item["title"].lower())


def render(items):
    items = sorted(items, key=_stage_key)
    return "\n".join("    " + _card(i) for i in items)
