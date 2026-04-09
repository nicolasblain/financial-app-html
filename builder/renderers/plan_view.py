"""Renders customer plan cards for the index, and builds a JSON data
block with frontmatter numbers so the client-side plan view can display
key metrics without parsing markdown."""

import json

from . import esc


# Metric keys we pull from frontmatter and display in the key-metrics panel.
# (key, label, format)  — format: "$" = dollar, "%" = percent, "" = plain
METRIC_DEFS = [
    ("gross_income", "Gross Income", "$"),
    ("net_income", "Net Income", "$"),
    ("savings_rate", "Savings Rate", "%"),
    ("monthly_savings", "Monthly Savings", "$"),
    ("emergency_fund", "Emergency Fund", "$"),
    ("total_assets", "Total Assets", "$"),
    ("rrsp_balance", "RRSP", "$"),
    ("tfsa_balance", "TFSA", "$"),
    ("non_registered", "Non-Registered", "$"),
    ("total_debt", "Total Debt", "$"),
    ("mortgage_balance", "Mortgage Balance", "$"),
    ("net_worth", "Net Worth", "$"),
    ("retirement_age", "Target Retirement Age", ""),
    ("retirement_gap", "Retirement Gap", "$"),
    ("life_insurance", "Life Insurance", "$"),
    ("disability_coverage", "Disability Coverage", "$"),
    ("monthly_housing", "Monthly Housing Cost", "$"),
]


def _card(item):
    title = item["title"]
    slug = item["_slug"]
    client = item.get("client", title)
    summary = item.get("summary", "")
    status = item.get("plan_status", "")
    desc_html = f'<p class="card-desc">{esc(summary)}</p>' if summary else ""
    status_html = (
        f'<span class="card-stage card-stage--plan-{esc(status.lower())}">{esc(status)}</span>'
        if status else ""
    )
    return (
        f'<li class="content-card plan-view-card" '
        f'data-type="plan" data-name="{esc(title)} {esc(client)}" '
        f'data-slug="{esc(slug)}">'
        f'<button type="button" class="card-inner" data-plan-slug="{esc(slug)}">'
        f'{status_html}'
        f'<h3 class="card-title">{esc(title)}</h3>'
        f'{desc_html}'
        f'</button></li>'
    )


def render(items):
    items = sorted(items, key=lambda i: i.get("client", i["title"]).lower())
    return "\n".join("    " + _card(i) for i in items)


def build_data(items):
    """JSON blob mapping slug → {title, client, metrics: [...], body}."""
    out = {}
    for item in items:
        metrics = []
        for key, label, fmt in METRIC_DEFS:
            val = item.get(key)
            if val is None or val == "":
                continue
            metrics.append({"key": key, "label": label, "value": val, "format": fmt})
        out[item["_slug"]] = {
            "title": item["title"],
            "client": item.get("client", ""),
            "plan_status": item.get("plan_status", ""),
            "date": item.get("date", ""),
            "metrics": metrics,
            "body": item.get("_body", ""),
        }
    return json.dumps(out, ensure_ascii=False)
