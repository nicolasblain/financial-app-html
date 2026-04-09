# Financial App — Architecture Guide

## Purpose

A single-file, self-contained financial planning app delivered as one `index.html`, built from plain markdown source files by a modular Python build pipeline. No backend, no database, no framework — the generated HTML is opened directly in a browser (or hosted on any static host) and contains everything it needs.

This is the same philosophy as the recipes app: **markdown in, one HTML out**. The difference is that a financial planning tool has more content types (modules, case studies, calculators, plan sections, client-facing explanations) and richer interactions than a recipe index, so the build step is broken into modules instead of living in a single `build.py` script.

---

## Guiding Principles (inherited from the recipes app)

1. **Markdown is the source of truth.** Every piece of content — a module, a case study chapter, a definition, a plan section — is authored as a markdown file with YAML frontmatter. Nothing important lives only in code or only in the template.
2. **One build command, one output file.** Running `python build.py` regenerates `index.html` from the current state of the content directory. No watchers, no dev servers required to iterate.
3. **No dependencies unless justified.** The recipes app uses zero Python dependencies and one CDN script (`marked.js`) at runtime. The financial app follows the same rule: stdlib-only Python, and any runtime JS comes from a small, pinned CDN list.
4. **Client-side rendering of long-form content.** Cards, navigation, and indexes are baked into the HTML at build time. Full article/module bodies are loaded on demand and rendered from the original markdown in the browser — so the HTML stays small and the markdown stays the canonical form.
5. **Frontmatter is the schema.** Filtering, grouping, ordering, and routing all come from frontmatter fields. The build script should never hardcode lists of files.

---

## Repository Layout

```
financial-app-html/
├── ARCHITECTURE.md              ← this file
├── README.md
├── build.py                     ← thin entrypoint: wires the pipeline
├── builder/                     ← modular build pipeline (the main difference vs recipes)
│   ├── __init__.py
│   ├── frontmatter.py           ← YAML-ish parser (stdlib only, like recipes build.py)
│   ├── content.py               ← loads + validates markdown files by content type
│   ├── registry.py              ← central registry of content types and their renderers
│   ├── renderers/
│   │   ├── __init__.py
│   │   ├── module_card.py       ← one renderer per card/index type
│   │   ├── plan_section.py
│   │   ├── case_study.py
│   │   ├── glossary.py
│   │   └── calculator.py        ← calculators are declared in markdown, rendered to JSON+HTML
│   ├── navigation.py            ← builds the top-level nav and cross-links
│   ├── search_index.py          ← builds a lightweight JSON search index embedded in the HTML
│   └── template.py              ← template loading + placeholder substitution
├── content/
│   ├── modules/                 ← planning modules (Home Purchase, Retirement, Protection, …)
│   │   ├── _template.md
│   │   └── home-purchase.md
│   ├── plan-sections/           ← reusable sections of a generated plan
│   ├── case-studies/            ← long-form narrative examples
│   ├── glossary/                ← one term per file, short
│   └── calculators/             ← markdown + declarative formula block
├── assets/
│   ├── style.css
│   ├── app.js                   ← client-side: search, nav, overlay, markdown render
│   └── calculators.js           ← client-side calculator runtime
├── template.html                ← single HTML shell with {{...}} placeholders
└── index.html                   ← generated output (gitignored or committed, your call)
```

The `content/` directory is the only place a non-developer should need to touch. Everything under `builder/` exists to turn that directory into `index.html`.

---

## Content Types

Unlike the recipes app (which has essentially one type: `recipe`, with an optional `group` variant), the financial app has several first-class content types. Each one lives in its own subfolder under `content/` and has a dedicated renderer under `builder/renderers/`.

| Type | Folder | Purpose | Key frontmatter |
|---|---|---|---|
| Module | `content/modules/` | A planning module the user can work through (Home Purchase, Retirement, Protection, …) | `title`, `stage`, `status`, `order`, `tags`, `prerequisites` |
| Plan section | `content/plan-sections/` | A reusable section that appears in a generated financial plan | `title`, `section_id`, `applies_to` |
| Case study | `content/case-studies/` | Narrative walkthrough of a real or illustrative client scenario | `title`, `persona`, `modules`, `published` |
| Glossary term | `content/glossary/` | A single definition, one per file | `term`, `aliases`, `see_also` |
| Calculator | `content/calculators/` | A small interactive calculator declared in markdown | `title`, `inputs`, `formula`, `output` |

A new content type is added by:
1. Creating a new folder under `content/`.
2. Adding a renderer module under `builder/renderers/`.
3. Registering it in `builder/registry.py` (one line: folder → renderer → template placeholder).

That registration step is the whole reason the builder is modular. The recipes app hardcodes `RECIPES_DIR` and a single card format. Here, `registry.py` holds the mapping so `build.py` stays short.

---

## The Build Pipeline

`build.py` is a thin entrypoint. The real work happens in `builder/` and proceeds in clearly separated phases. Each phase consumes the output of the previous one and produces a plain Python data structure — no phase writes files except the final one.

```
  ┌──────────────────┐
  │ 1. Discover      │  walk content/, group by content type
  └────────┬─────────┘
           ▼
  ┌──────────────────┐
  │ 2. Parse         │  read each .md, split frontmatter + body
  └────────┬─────────┘
           ▼
  ┌──────────────────┐
  │ 3. Validate      │  per-type schema check (required fields, enums)
  └────────┬─────────┘
           ▼
  ┌──────────────────┐
  │ 4. Transform     │  resolve cross-links, sort, group, build nav
  └────────┬─────────┘
           ▼
  ┌──────────────────┐
  │ 5. Render        │  each type → HTML fragment via its renderer
  └────────┬─────────┘
           ▼
  ┌──────────────────┐
  │ 6. Assemble      │  inject fragments + search index into template
  └────────┬─────────┘
           ▼
  ┌──────────────────┐
  │ 7. Write         │  index.html
  └──────────────────┘
```

### Phase details

1. **Discover** (`builder/content.py`): walks `content/`, returns `{content_type: [Path, …]}`. Files starting with `_` are ignored, matching the recipes app convention (`_template.md`, `_index.md`).
2. **Parse** (`builder/frontmatter.py`): the same regex-based YAML-subset parser used in the recipes `build.py`, lifted into its own module so every content type parses the same way. Handles strings, bools, and `[a, b, c]` lists. No PyYAML dependency.
3. **Validate** (`builder/content.py`): each content type declares required fields and allowed values. A missing `title` or an unknown `stage` fails the build loudly instead of silently producing a broken card.
4. **Transform** (`builder/navigation.py`, per-renderer helpers): resolves prerequisites between modules, sorts by `order` then title, groups case studies by persona, expands glossary aliases. This is where the recipes app's `group_map` logic lives, generalized.
5. **Render** (`builder/renderers/*`): every renderer exports a single `render(items) -> str` function that returns an HTML fragment. The fragments are the HTML equivalent of the recipes `<li class="recipe-card">` blocks.
6. **Assemble** (`builder/template.py`): loads `template.html` and substitutes placeholders — `{{MODULE_LIST}}`, `{{PLAN_SECTION_NAV}}`, `{{CASE_STUDY_LIST}}`, `{{GLOSSARY_JSON}}`, `{{CALCULATORS_JSON}}`, `{{SEARCH_INDEX}}`. Same `str.replace` approach as the recipes app — no Jinja.
7. **Write**: `OUTPUT.write_text(output, encoding="utf-8")` and print a summary line per content type, the same way the recipes build prints `Built index.html with N entries`.

### Why modular and not one big script

The recipes `build.py` is ~180 lines and does everything inline. That works because there is one content type and three tags. In this app:

- Content types will grow (modules, sections, case studies, glossary, calculators — and almost certainly more later).
- Validation matters more: a malformed recipe produces an ugly card, a malformed plan section produces wrong financial advice.
- Renderers will need to share helpers (escaping, slug, meta blocks) without copy-paste.
- The search index and the nav are cross-cutting — they touch every content type — so they need a structured intermediate representation to build from.

Splitting by phase keeps each module small and individually testable. The phases are pure functions of their inputs; only phase 7 touches the filesystem.

---

## Runtime Architecture (the generated HTML)

`index.html` is a single file containing:

- The page shell (header, nav tabs, search, main content container, detail overlay).
- Baked-in HTML fragments for every index/card view.
- An embedded JSON search index (`<script type="application/json" id="searchIndex">…</script>`).
- An embedded JSON calculators manifest.
- A link to `assets/style.css` and `assets/app.js` (and the `marked.js` CDN script, same as recipes).

When the user clicks a module or case study card, `app.js` fetches the original markdown file from `content/…/foo.md` and renders it into the overlay using `marked.js`. This mirrors the recipes app's `recipe-overlay` flow exactly — the HTML stays small because long bodies are not baked in.

Calculators are the one place the financial app goes beyond the recipes pattern. Each calculator's frontmatter declares its inputs, a formula (as a restricted expression), and an output format. At build time those are serialized into the `{{CALCULATORS_JSON}}` block. At runtime, `calculators.js` reads that block, builds the input form, evaluates the expression in a sandboxed scope, and renders the result. Formulas stay in the markdown file so planners can edit them without touching JS.

---

## Frontmatter Conventions

Shared across all types (mirroring the recipes convention of stable, documented keys):

```yaml
---
title: Human-readable title
slug: optional-override         # default: filename without .md
tags: [tag-a, tag-b]            # used for filtering, like recipe categories
order: 10                       # sort within its type; lower first
status: draft | published       # draft is excluded from the default build
---
```

Per-type additions are documented in each type's `_template.md` file inside its folder. That template file is the authoritative schema — same pattern as `recipes/_template.md` in the recipes app.

---

## Adding a New Module (worked example)

1. Copy `content/modules/_template.md` to `content/modules/retirement-readiness.md`.
2. Fill in frontmatter: `title`, `stage`, `order`, `tags`, `prerequisites`.
3. Write the module body in markdown.
4. Run `python build.py`.
5. Open `index.html`.

No code changes. This is the single most important property to preserve as the app grows: **content work does not touch Python**.

## Adding a New Content Type (worked example)

1. Create `content/checklists/` with a `_template.md`.
2. Create `builder/renderers/checklist.py` exporting `render(items) -> str`.
3. Add one entry to `builder/registry.py` mapping `"checklists"` → the new renderer and a template placeholder name (e.g. `{{CHECKLIST_LIST}}`).
4. Add `{{CHECKLIST_LIST}}` somewhere in `template.html`.
5. Run `python build.py`.

Four touch points, all small, all obvious. That is the payoff of the modular builder.

---

## What This Architecture Is Not

- **Not a CMS.** There is no admin UI. Content is edited in a text editor and committed.
- **Not a SPA framework.** There is no React/Vue/etc. `app.js` is hand-written vanilla JS, same as the recipes app.
- **Not a static site generator.** No Jekyll/Hugo/Eleventy. The build is a ~few-hundred-line Python package with zero dependencies, so the whole pipeline is readable in one sitting.
- **Not multi-page.** One HTML file, one overlay for detail views. Routing is done with URL fragments (`#module=retirement-readiness`) so deep links still work.
- **Not a backend for client data.** This app renders planning *content*. Any eventual client-specific data (intake forms, saved plans) is out of scope for this repo and would belong in a separate service.

---

## Open Questions to Resolve Before Implementation

1. Where does client-entered calculator state live between sessions? (Probably `localStorage`, matching the no-backend stance — worth confirming.)
2. Do we need i18n from day one (French + English)? If yes, `lang` becomes a frontmatter field and renderers emit per-language fragments. Easier to build in now than retrofit.
3. Should `index.html` be committed or gitignored? The recipes repo commits it so GitHub Pages can serve it — same call probably applies here.
4. Print/PDF export of a generated plan: do we need it, and if so, is it a second build target (`build.py --pdf`) or a browser `window.print()` stylesheet?

These are decisions to make at implementation time, not now. Recording them here so they are not forgotten.
