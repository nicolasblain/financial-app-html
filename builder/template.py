"""Template loading + placeholder substitution.

Same str.replace approach as the recipes app — no templating engine.
"""

from pathlib import Path


def load(path):
    return Path(path).read_text(encoding="utf-8")


def substitute(template, placeholders):
    out = template
    for key, value in placeholders.items():
        out = out.replace(key, value)
    return out


def write(path, content):
    Path(path).write_text(content, encoding="utf-8")
