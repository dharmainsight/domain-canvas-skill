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

## Confirmed vs inferred

Mark `confidence: "confirmed"` when the relationship is directly supported by a schema constraint, explicit domain specification, or unambiguous typed model.

Mark `confidence: "inferred"` when the relationship is deduced from naming, UI co-occurrence, API shape, or partial code evidence.

Never silently convert an inferred relationship into a confirmed one.

## Cardinality

Prefer database constraints when present, but distinguish database cardinality from business cardinality if they differ.

Examples:

- Non-null FK from `contracts.customer_id` to `customers.id` generally supports `contract -> customer = 1`.
- A uniqueness constraint on a FK may reduce `0..*` to `0..1` on the reverse side.
- Soft-deleted rows, versioning tables, and polymorphic references need explicit notes.

## Concept view simplification

The concept view is not a dump of the schema.

Hide or collapse:

- join tables that have no business identity of their own,
- audit/version tables,
- implementation-only lookup tables,
- technical IDs and timestamps.

Promote a join table to a concept only when it carries meaningful domain state or behavior.

## UI binding

A screen is bound to an entity when the screen materially displays, edits, creates, filters by, or navigates through that entity.

Do not bind every entity that appears indirectly in a payload.

Roles:

- `primary`: object the screen is chiefly about
- `context`: related object needed to interpret the primary object
- `collection`: repeated related objects
- `edit`: object directly mutated by the screen
- `create`: object instantiated from the screen

## Naming

Use business-facing labels in `name` and relationship `label`.
Keep code/schema identifiers in IDs or evidence notes.

## Evidence for additional views

| Claim | Preferred evidence | Do not infer it from |
|---|---|---|
| Allowed transition / actor / guard | state machine code, workflow specification, authorization checks | a status column or enum type alone |
| Message order / commit / reply | handler implementation, trace, explicit sequence specification | screen bindings or an FK |
| Customer and backstage stages | documented process, role ownership, observed handoffs | UI order alone |
| Dataset grain and transformations | SQL, model definitions, orchestration configuration | similar column names |
| Metric definition and denominator | agreed metric contract, query, cohort inclusion rules | labels such as “conversion rate” |

`illustrative` marks an invented teaching example. `unknown` means evidence is missing. Neither is `inferred`: a sample number is not an estimate supported by data. Preserve confidence and evidence at the bundle and item levels; report conflicts rather than choosing the more convenient source.

For lineage, record the meaning of one row before and after each transform, join keys and multiplicities, duplicate handling, and date basis. A declared FK is not a complete transformation specification.

For outcomes, establish population, observation window, unit, numerator and denominator, maturity of the observation window, and missing-data handling. Do not divide one calendar month's contracts by that month's applications and describe it as cohort conversion without a valid individual mapping.

The repository example has no application-to-contract key. Its 90-day conversion model is illustrative and separate from the contract-start-month lineage. Adding that connection requires supported linkage and aligned population/time semantics.
