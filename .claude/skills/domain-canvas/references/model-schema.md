# Canonical model schema

`model.json` is the source of truth. The generator accepts versions `1` and `2`; all five extension arrays are optional. Version 2 identifies models using these extensions. Generated `computed_outcomes` and `embedded_preview` are output fields, not authored inputs.

## Root and shared objects

Required root fields: `title` (nonempty string), `version` (1 or 2), and arrays `entities`, `relationships`, `screens`, `concept_groups`. The arrays may be empty. Optional `is_example: true` labels the entire canvas as an example.

| Object | Fields |
|---|---|
| Entity | `id`, `name`, `description`, `attributes`; optional `group` referencing a concept group |
| Attribute | `name`, `type`; optional booleans `pk`, `nullable`, optional `description`, and `fk: {entity, attribute}` |
| Relationship | `id`, `from`, `to` (entity IDs), `label`, `from_cardinality`, `to_cardinality`, `kind` (`domain`, `database`, `both`) |
| Screen | `id`, `name`, `bindings: [{entity, role}]`; optional `description`, `route`, `preview_html`, `preview_image` |
| Concept group | `id`, `name`; optional `description` |

Cardinalities: `1`, `0..1`, `1..*`, `0..*`. Each describes its named endpoint. For `customer → contract`, `from_cardinality: "1"` means one customer per contract; `to_cardinality: "0..*"` means zero or more contracts per customer. A nullable FK requires optionality at its target endpoint unless a separately evidenced business constraint is being modeled.

Binding roles: `primary`, `context`, `collection`, `edit`, `create`. Prefer one primary object unless the screen genuinely represents a composite. Preview paths must remain within the model directory, including after resolving symlinks. HTML is preferred if both are supplied; provide inline styles/scripts/assets for a portable HTML preview. PNG/JPEG/WebP images and HTML content are embedded in the generated canvas. Remote or parent-directory preview paths are rejected.

IDs are nonempty strings and unique within each collection. Referenced entities, attributes, groups, and screens must exist. Primary keys cannot be nullable. Use distinct participant/message IDs within a scenario and dataset/job IDs within a lineage bundle.

## Evidence shared by all extensions

Bundles and their items can carry `name`, `description`, `evidence`, and `confidence`:

- `confirmed`: direct support from a cited source.
- `inferred`: reasoned interpretation of partial evidence.
- `illustrative`: constructed example, not observed behavior or performance.
- `unknown`: not established; this is the default when absent.

Bundles can include `entity_ids` and `note`. Give every displayed object a human-readable name. A bundle's confidence provides context for its items; specify exceptions at item level. Evidence is a concise string naming a source and the supported claim.

## `state_machines`

Each bundle: `id`, `name`, `entity_id`, `initial` (state ID), `states`, `transitions`.

- State: `id`, `name`, optional `description`, `terminal` boolean.
- Transition: `id`, `from`, `to` (state IDs), `label` (event), optional `condition`, `actor`, evidence.

Cycles and self-transitions are supported. A terminal state cannot have outgoing transitions. Do not infer a transition from an attribute typed `enum`.

## `scenarios`

Each bundle: `id`, `name`, `participants`, `messages`; optional `screen_id`, `entity_ids`, `note`.

- Participant: `id`, `name`, optional `kind`, `description`, `entity_id`.
- Message: `id`, `from`, `to` (participant IDs), `label`, optional `kind` (`call`, `return`, `async`; default `call`), `condition`, `description`, evidence.

The array order is message order. At least one participant is required. A condition annotates a message; it does not create an alternative branch. Express distinct execution paths as separate scenarios, and document transactional, failure, and retry boundaries in `note`.

## `journeys`

Each bundle: `id`, `name`, `steps`, `lanes`, `cells`.

- Step: `id`, `name`; array order is stage order.
- Lane: `id`, `name`, optional `boundary_before` label; array order is role order.
- Cell: `id`, `step`, `lane`, `name`, optional `description`, `note`, `entity_ids`, `screen_ids`, evidence.

At least one step and lane are required. Multiple cells can occupy an intersection. Typical lanes: customer action, frontstage contact, backstage work, support, and physical/digital evidence. An omitted cell is unspecified, not proof that no activity occurs.

## `lineage`

Each bundle: `id`, `name`, `datasets`, `jobs`.

- Dataset: `id`, `name`, `grain` (meaning of one row), optional `description`, `entity_id`, evidence.
- Job: `id`, `name`, `inputs` and `outputs` (nonempty arrays of dataset IDs), `description`, `rule`, evidence.

The combined dataset → job → dataset graph must be acyclic. Each job should explain join keys, row multiplication, filters, deduplication, and time basis where applicable. This is design lineage, not a claim that a job ran successfully; run status and column-level lineage are not implemented.

## `outcomes`

Each bundle: `id`, `name`, `root` (metric ID), nonempty `population`, nonempty `window`, `metrics`.

- Every metric: `id`, `name`, `unit`, optional `description`, `entity_ids`, evidence.
- Leaf: finite numeric `value`. For unit `%`, store a fraction between 0 and 1 (`0.8` displays `80%`). Never use zero to stand for missing data.
- Derived: `operator` and `inputs` (metric IDs); do **not** provide a stored `value`.
- Operators: `product` (multiply all inputs), `sum` (add all inputs), `ratio` (exactly two inputs, numerator then denominator).

Inputs must form a DAG; cycles, duplicate references, non-finite values, and zero denominators are rejected. Derived percentages may exceed 100% when a ratio's definition permits it. The generator computes every metric; the canvas displays the root and reachable inputs. No JavaScript/Python expression evaluation is used.

For conversion decomposition, rates must be conditional on the previous stage within one cohort and observation window. The sample is `1,000 × 0.8 × 0.75 × 0.6 = 360`; these are illustrative values. Its contract-start-month lineage and 90-day application cohort measure different populations and are intentionally not joined.

## Minimal valid model

```json
{
  "title": "申込の理解",
  "version": 2,
  "entities": [{"id": "application", "name": "申込", "description": "審査の対象", "attributes": []}],
  "relationships": [],
  "screens": [],
  "concept_groups": [],
  "state_machines": [{
    "id": "review", "name": "申込の審査", "entity_id": "application",
    "confidence": "illustrative", "evidence": "説明用に構成した審査例",
    "initial": "draft",
    "states": [{"id": "draft", "name": "下書き"}, {"id": "reviewing", "name": "審査中"}],
    "transitions": [{"id": "submit", "from": "draft", "to": "reviewing", "label": "提出する", "condition": "必須項目がそろう", "actor": "申込者"}]
  }]
}
```

The repository's `example/model.json` is a complete, executable sample of all eight projections.
