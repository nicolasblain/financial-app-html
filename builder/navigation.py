"""Builds the top-level nav (one tab per content type)."""

import html as _html

from . import registry


def render(counts):
    """counts = {type_key: int}. Returns HTML for the nav container."""
    tabs = ['<button class="nav-tab active" data-type="all">All</button>']
    for t in registry.TYPES:
        n = counts.get(t["key"], 0)
        label = _html.escape(t["nav_label"])
        tabs.append(
            f'<button class="nav-tab" data-type="{t["key"]}">{label} '
            f'<span class="nav-count">{n}</span></button>'
        )
    return "\n      ".join(tabs)
