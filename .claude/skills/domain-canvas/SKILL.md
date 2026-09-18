---
name: domain-canvas
description: Build or update evidence-grounded, single-source domain canvases that connect product screens, domain concepts, and ER/data relationships. Use when the user asks to map a feature or system from UI to business objects to data, create or revise an object/domain map or ER view tied to screens, re-layout an existing Mermaid or draw.io diagram into a clearer canvas, or maintain a generated interactive canvas from project docs and code.
---

# Domain Canvas

Create or update one canonical model and generate multiple review views from it. Optimize for reader understanding, not for the number of boxes or lines drawn.

## Outputs

Maintain these files unless the user specifies another location:

- `.domain-canvas/model.json` — canonical source of truth
- `.domain-canvas/index.html` — generated static interactive canvas
- `.domain-canvas/README.md` — evidence, unresolved assumptions, and refresh commands

Never hand-edit generated HTML. Change `model.json`, then regenerate.

## Workflow

### 1. Inspect evidence before asking questions

Search strongest sources first:

1. Database schema, migrations, ORM models
2. Typed domain/API schemas, GraphQL, OpenAPI
3. PRDs, specs, ADRs, design docs
4. UI routes, page components, Storybook, prototype HTML
5. Mermaid, draw.io, architecture diagrams, or screenshots supplied by the user

Treat existing diagrams as evidence of intended concepts and relationships, not as authoritative geometry. Re-layout them from semantics instead of preserving coordinates or merely changing colors.

Ask only for information that materially changes the model and cannot be derived from available evidence.

### 2. Decide whether a diagram earns its place

Before adding a view, ask whether the reader learns more from a diagram than from a sentence or table. If not, keep the fact in notes instead of drawing it.

Use `references/diagram-design-rules.md` for visual constraints. Key defaults:

- One node represents one clear concept.
- Merge concepts that always travel together and have no independent review value.
- Every visible edge must carry information; do not draw a line when grouping or layout already expresses the relationship.
- Emphasize at most one or two focal entities.
- Target moderate visual density. Above 9 entity-level nodes, provide an overview before detail.
- Keep output static by default; use interaction for navigation, not decorative motion.

### 3. Build the canonical model

Use `references/model-schema.md`.

Separate:

- **Entities** — stable domain objects
- **Attributes** — data carried by entities
- **Relationships** — semantic and/or database relationships
- **Screens** — UI views and which entities they expose or mutate
- **Concept groups** — business-level groupings used for overview and layout
- **Presentation** — optional focus and restrained brand colors; never use it to override evidence

Prefer stable IDs such as `customer`, `contract`, `property` over display names.

Never invent a database relationship because concepts are adjacent in UI or an old diagram. Mark uncertain relationships `confidence: "inferred"` and record the evidence in `.domain-canvas/README.md`.

### 4. Preserve one source of truth

Generate all projections from the same `.domain-canvas/model.json`:

- Design: screens and entity bindings
- Concept: entity meanings and semantic relationships
- ER: attributes, keys, database relationships, and cardinalities

If a relationship changes, edit it once in the model and regenerate.

### 5. Attach real design data when available

For each screen, prefer:

- `preview_image`: relative PNG/JPG/WebP path
- `preview_html`: relative local HTML path

If neither exists, show a labeled placeholder. Do not fabricate a pixel-perfect UI.

Keep preview paths local and relative so the generated output remains self-contained and reviewable.

### 6. Generate and validate

Run:

```bash
python .claude/skills/domain-canvas/scripts/generate_canvas.py \
  --model .domain-canvas/model.json \
  --out .domain-canvas/index.html

python .claude/skills/domain-canvas/scripts/self_check.py \
  --model .domain-canvas/model.json \
  --html .domain-canvas/index.html
```

If the skill is installed elsewhere, resolve both scripts from this skill directory.

Validate that:

- JSON parses and IDs are unique.
- Relationship endpoints and screen bindings exist.
- Focus entities exist and there are no more than two.
- Preview paths are local.
- Primary/foreign-key flags do not contradict available schema evidence.
- The generator completes without errors.
- The self-check passes accessibility, static-output, and remote-resource checks.
- If possible, visually inspect view switching, overview/detail behavior for large models, and fit/zoom.

## Modeling rules

Use `references/extraction-rules.md` for evidence and ambiguity handling.

Additional defaults:

- Keep Concept smaller and more business-readable than ER.
- Use group placement to express membership instead of extra membership edges.
- In Design, draw direct edges only for `primary`, `edit`, and `create` bindings; keep `context` and `collection` as labeled metadata unless an edge is necessary to answer the review question.
- Use relationship labels with business meaning (`owns`, `applies to`, `has documents`) instead of only FK names.
- Use `presentation.focus_entities` only for the current review question, never to make every node look important.

## Update behavior

When `.domain-canvas/model.json` already exists:

1. Read it first.
2. Preserve confirmed IDs and user-authored labels unless evidence changed.
3. Reconcile repo changes into the model.
4. Preserve presentation choices that still fit the review question; remove stale focus.
5. Report ambiguous removed or renamed entities before deleting them.
6. Regenerate HTML and run `self_check.py`.

## Completion

Report:

- evidence used,
- files generated or updated,
- unresolved inferred relationships,
- any overview/detail split introduced for density,
- the refresh and self-check commands.

Do not claim the model is authoritative beyond its evidence.