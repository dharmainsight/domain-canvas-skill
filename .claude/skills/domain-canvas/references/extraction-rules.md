# Extraction and evidence rules

## Evidence priority

Use the strongest source available for each claim rather than choosing one document as globally authoritative.

| Claim | Preferred evidence |
|---|---|
| Table/column exists | migration/schema/ORM |
| FK/cardinality | migration/schema/ORM + constraints |
| Domain meaning | PRD/spec/domain docs |
| Screen exists | router/page/component/prototype |
| Screen-to-entity binding | visible fields/actions + API/model usage |
| Business relationship label | domain docs, then code semantics |
| Candidate concept/relationship from old diagram | Mermaid/draw.io/architecture diagram, then cross-check stronger sources |

## Confirmed vs inferred

Mark `confidence: "confirmed"` when a relationship is directly supported by a schema constraint, explicit domain specification, or unambiguous typed model.

Mark `confidence: "inferred"` when it is deduced from naming, UI co-occurrence, API shape, partial code evidence, or an imported diagram that has not been corroborated.

Never silently convert an inferred relationship into a confirmed one.

## Imported diagrams

Treat Mermaid, draw.io, and older diagrams as evidence, not geometry to preserve.

- Reuse meaningful labels and candidate relations after verification.
- Ignore old coordinates and line routing unless they encode a documented grouping.
- Do not promote a line in a diagram to a database relationship without schema evidence.
- Re-layout from the current reader question and the diagram design rules.

## Cardinality

Prefer database constraints when present, but distinguish database cardinality from business cardinality if they differ.

Examples:

- A non-null FK from `contracts.customer_id` to `customers.id` generally supports `contract -> customer = 1`.
- A uniqueness constraint on an FK may reduce `0..*` to `0..1` on the reverse side.
- Soft-deleted rows, versioning tables, and polymorphic references need explicit notes.

## Concept view simplification

The concept view is not a schema dump.

Hide or collapse:

- join tables with no business identity,
- audit/version tables,
- implementation-only lookup tables,
- technical IDs and timestamps.

Promote a join table to a concept only when it carries meaningful domain state or behavior.

Use concept groups to express membership visually. Do not add group-membership edges merely because the renderer can draw them.

## UI binding

A screen is bound to an entity when it materially displays, edits, creates, filters by, or navigates through that entity.

Do not bind every entity that appears indirectly in a payload.

Roles:

- `primary`: object the screen is chiefly about
- `context`: related object needed to interpret the primary object
- `collection`: repeated related objects
- `edit`: object directly mutated by the screen
- `create`: object instantiated from the screen

In the generated Design view, draw edges for `primary`, `edit`, and `create` by default. Keep `context` and `collection` visible as labels to reduce edge clutter.

## Naming

Use business-facing labels in `name` and relationship `label`.
Keep code/schema identifiers in IDs or evidence notes.
