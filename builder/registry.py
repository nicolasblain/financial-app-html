"""Central registry of content types.

Adding a new content type = adding one entry here + writing its renderer.
"""

from .renderers import module_card, plan_section, case_study, glossary, calculator

# Each entry:
#   folder       — subfolder under content/
#   placeholder  — template token replaced by this type's rendered HTML
#   renderer     — module exposing render(items) -> str
#   schema       — required fields, enums, types for validation
#   nav_label    — human label shown in the top nav

TYPES = [
    {
        "key": "modules",
        "folder": "modules",
        "placeholder": "{{MODULE_LIST}}",
        "renderer": module_card,
        "nav_label": "Modules",
        "schema": {
            "required": ["title", "stage"],
            "enums": {
                "stage": [
                    "Intake",
                    "Goals",
                    "Analysis",
                    "Plan Drafting",
                    "Plan Delivery",
                    "Monitoring",
                ],
            },
            "types": {"order": int},
        },
    },
    {
        "key": "plan-sections",
        "folder": "plan-sections",
        "placeholder": "{{PLAN_SECTION_LIST}}",
        "renderer": plan_section,
        "nav_label": "Plan Sections",
        "schema": {
            "required": ["title", "section_id"],
            "types": {"order": int},
        },
    },
    {
        "key": "case-studies",
        "folder": "case-studies",
        "placeholder": "{{CASE_STUDY_LIST}}",
        "renderer": case_study,
        "nav_label": "Case Studies",
        "schema": {
            "required": ["title", "persona"],
        },
    },
    {
        "key": "glossary",
        "folder": "glossary",
        "placeholder": "{{GLOSSARY_LIST}}",
        "renderer": glossary,
        "nav_label": "Glossary",
        "schema": {
            "required": ["term"],
        },
    },
    {
        "key": "calculators",
        "folder": "calculators",
        "placeholder": "{{CALCULATOR_LIST}}",
        "renderer": calculator,
        "nav_label": "Calculators",
        "schema": {
            "required": ["title", "inputs", "formula"],
        },
    },
]


def by_key(key):
    for t in TYPES:
        if t["key"] == key:
            return t
    raise KeyError(key)
