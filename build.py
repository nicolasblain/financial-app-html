#!/usr/bin/env python3
"""Thin entrypoint. Wires the modular builder pipeline — see ARCHITECTURE.md."""

from pathlib import Path

from builder import content, navigation, registry, search_index, template
from builder.renderers import calculator as calc_renderer
from builder.renderers import plan_view as plan_renderer

ROOT = Path(__file__).parent
CONTENT_ROOT = ROOT / "content"
TEMPLATE_PATH = ROOT / "template.html"
OUTPUT_PATH = ROOT / "index.html"


def main():
    # Phases 1-3: discover + parse + validate per content type
    items_by_type = {}
    for t in registry.TYPES:
        items = content.load_type(CONTENT_ROOT, t["folder"], t["schema"])
        items_by_type[t["key"]] = items

    # Phases 4-5: transform + render
    placeholders = {}
    counts = {}
    for t in registry.TYPES:
        items = items_by_type[t["key"]]
        placeholders[t["placeholder"]] = t["renderer"].render(items)
        counts[t["key"]] = len(items)

    # Cross-cutting: navigation, search index, calculator data
    placeholders["{{NAV_TABS}}"] = navigation.render(counts)
    placeholders["{{SEARCH_INDEX}}"] = search_index.build(items_by_type)
    placeholders["{{CALCULATOR_DATA}}"] = calc_renderer.build_data(
        items_by_type.get("calculators", [])
    )
    placeholders["{{PLAN_DATA}}"] = plan_renderer.build_data(
        items_by_type.get("plans", [])
    )

    # Phase 6-7: assemble + write
    tmpl = template.load(TEMPLATE_PATH)
    output = template.substitute(tmpl, placeholders)
    template.write(OUTPUT_PATH, output)

    print("Built index.html")
    for t in registry.TYPES:
        print(f"  - {t['nav_label']:<15} {counts[t['key']]:>3} items")


if __name__ == "__main__":
    main()
