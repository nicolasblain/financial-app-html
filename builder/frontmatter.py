"""YAML-subset frontmatter parser. Stdlib only.

Supports: strings (quoted or bare), booleans, integers, floats, and `[a, b, c]` lists.
Lifted and generalized from the recipes app's build.py.
"""

import re

_FM_RE = re.compile(r"^---\r?\n([\s\S]*?)\r?\n---", re.MULTILINE)
_KV_RE = re.compile(r"^(\w[\w_]*):\s*(.*)$")


def _coerce_scalar(val):
    val = val.strip()
    if val == "" or val is None:
        return ""
    if val == "true":
        return True
    if val == "false":
        return False
    # int
    if re.fullmatch(r"-?\d+", val):
        return int(val)
    # float
    if re.fullmatch(r"-?\d+\.\d+", val):
        return float(val)
    # quoted string
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    return val


def parse(text):
    """Return (frontmatter_dict, body_string). Missing frontmatter → ({}, text)."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    data = {}
    for line in m.group(1).split("\n"):
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        kv = _KV_RE.match(line)
        if not kv:
            continue
        key, raw = kv.group(1), kv.group(2).strip()
        if raw.startswith("[") and raw.endswith("]"):
            items = [s.strip().strip("\"'") for s in raw[1:-1].split(",") if s.strip()]
            data[key] = items
        else:
            data[key] = _coerce_scalar(raw)
    body = text[m.end():].lstrip("\r\n")
    return data, body


def strip(text):
    """Return the body with frontmatter removed."""
    _, body = parse(text)
    return body
