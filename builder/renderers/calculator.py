"""Renders calculator cards. Calculator *data* (inputs + formula) is emitted
separately by build.py into the {{CALCULATOR_DATA}} placeholder as JSON."""

import json

from . import esc


def _card(item):
    title = item["title"]
    slug = item["_slug"]
    summary = item.get("summary", "")
    desc_html = f'<p class="card-desc">{esc(summary)}</p>' if summary else ""
    return (
        f'<li class="content-card calculator-card" '
        f'data-type="calculator" data-name="{esc(title)}" '
        f'data-slug="{esc(slug)}">'
        f'<button type="button" class="card-inner" data-calc-slug="{esc(slug)}">'
        f'<span class="card-stage card-stage--calc">Calculator</span>'
        f'<h3 class="card-title">{esc(title)}</h3>'
        f'{desc_html}'
        f'</button></li>'
    )


def render(items):
    items = sorted(items, key=lambda i: i["title"].lower())
    return "\n".join("    " + _card(i) for i in items)


def build_data(items):
    """Return a JSON string mapping slug → calculator definition.

    Client-side `calculators.js` consumes this to build the form and
    evaluate the formula in a sandboxed scope.
    """
    out = {}
    for item in items:
        inputs = item.get("inputs", [])
        if isinstance(inputs, str):
            inputs = [inputs]
        labels = item.get("labels", [])
        if isinstance(labels, str):
            labels = [labels]
        defaults = item.get("defaults", [])
        if isinstance(defaults, str):
            defaults = [defaults]
        out[item["_slug"]] = {
            "title": item["title"],
            "summary": item.get("summary", ""),
            "inputs": inputs,
            "labels": labels or inputs,
            "defaults": [float(d) if d not in ("", None) else 0 for d in defaults]
                        if defaults else [0] * len(inputs),
            "formula": item["formula"],
            "output": item.get("output", "Result: {result}"),
            "body": item.get("_body", ""),
        }
    return json.dumps(out, ensure_ascii=False)
