# financial-app-html

Single-file financial planning app, generated from markdown by a stdlib-only Python pipeline. See `ARCHITECTURE.md` for the full design.

## Build

```
python3 build.py
```

Produces `index.html`. Open it in a browser — no server needed for card/index views. Detail views `fetch()` the original markdown, so if you want those to work over `file://` your browser must allow local fetches; otherwise serve with:

```
python3 -m http.server
```

## Add content

- Module: create `content/modules/<slug>.md` from `_template.md`, then rebuild.
- Plan section, case study, glossary term, calculator: same pattern in the matching folder.

## Add a new content type

1. New folder under `content/`.
2. New renderer under `builder/renderers/`.
3. One entry in `builder/registry.py`.
4. Placeholder in `template.html`.
5. Rebuild.
