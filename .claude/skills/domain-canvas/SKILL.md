---
description: Build or update a single-source interactive domain canvas that connects UI screens, a conceptual model, and an ER diagram. Use when the user wants to understand how product objects relate across design data and database structure, asks for an object map/domain map/ER view tied to screens, or wants a navigable design-system canvas generated from project docs and code.
argument-hint: "[scope or feature name]"
---

# Domain Canvas

Create or update an interactive canvas where **Design**, **Concept**, and **ER** views are all generated from the same canonical model.

The goal is not merely to draw three diagrams. The goal is to make object relationships reviewable from multiple levels without duplicating the source of truth.

## Outputs

Maintain these files in the project unless the user specifies another location:

- `.domain-canvas/model.json` — canonical source of truth
- `.domain-canvas/index.html` — generated interactive canvas
- `.domain-canvas/README.md` — short notes on sources, unresolved assumptions, and refresh command

Do not hand-edit generated `index.html`. Update `model.json`, then regenerate.

## Workflow

### 1. Inspect the project before asking questions

Search for the strongest available sources in this order:

1. Database schema / migrations / ORM models
2. Typed domain models, API schemas, GraphQL schema, OpenAPI
3. PRDs, specs, ADRs, design docs
4. UI routes, page components, storybook, prototype HTML
5. Screenshots or image assets explicitly provided by the user

Only ask the user for information that materially changes the model and cannot be derived from the repo.

### 2. Build the canonical model

Use `references/model-schema.md`.

The canonical model must separate:

- **Entities** — stable domain objects
- **Attributes** — data carried by entities
- **Relationships** — semantic or database relationships
- **Screens** — UI views and which entities they expose or mutate
- **Concept groups** — optional business-level groupings for a cleaner conceptual view

Prefer stable IDs (`customer`, `contract`, `property`) over display names.

Never invent a database relationship because two concepts appear near each other in UI. Mark uncertain relationships with `confidence: "inferred"` and explain the evidence in `.domain-canvas/README.md`.

### 3. Preserve one source of truth

All three views must be projections of the same `.domain-canvas/model.json`.

- Design view: screens + entity bindings
- Concept view: entity meanings + semantic relationships
- ER view: attributes + keys + cardinalities

If a relationship is changed, change it once in `model.json` and regenerate all views.

### 4. Attach real design data when available

For each screen, prefer one of:

- `preview_image`: relative path to a PNG/JPG/WebP screenshot
- `preview_html`: relative path to a local HTML prototype

If neither exists, generate a labeled placeholder card. Do not fabricate a pixel-perfect screen.

When screenshots or HTML prototypes are available, map the screen to entities through `bindings`.

### 5. Generate the canvas

Run:

```bash
python .claude/skills/domain-canvas/scripts/generate_canvas.py \
  --model .domain-canvas/model.json \
  --out .domain-canvas/index.html
```

If the project skill is installed at a different path, resolve the script path from this skill directory.

### 6. Validate before presenting

Check all of the following:

- JSON parses successfully.
- Every relationship endpoint references an existing entity.
- Every screen binding references an existing entity.
- Primary/foreign-key flags do not contradict the available schema.
- The generator completes without errors.
- `index.html` contains the same count of entities and screens as `model.json`.
- If a preview path is supplied, the referenced file exists.

If possible, open the generated HTML in a browser and visually inspect at least one view switch and one pan/zoom action.

## Modeling rules

Use `references/extraction-rules.md` for evidence and ambiguity handling.

Important defaults:

- Concept view should be understandable by product/design stakeholders; omit implementation-only fields.
- ER view may show implementation details, but do not promote inferred fields to confirmed schema.
- UI bindings are many-to-many: one screen may expose several entities and one entity may appear on many screens.
- Keep the conceptual graph smaller than the ER graph when possible.
- Use relationship labels that describe business meaning (`owns`, `applies to`, `has documents`) instead of only technical FK names.

## Update behavior

When `.domain-canvas/model.json` already exists:

1. Read it first.
2. Preserve confirmed IDs and user-authored labels unless the source has changed.
3. Reconcile repo changes into the model.
4. Report any removed or renamed entities explicitly before deleting them from the canonical model when the evidence is ambiguous.
5. Regenerate `index.html` after model changes.

## Completion format

State:

- what sources were used,
- what was generated or updated,
- any unresolved inferred relationships,
- the command to refresh the canvas.

Do not claim the model is authoritative beyond the evidence in the project.
