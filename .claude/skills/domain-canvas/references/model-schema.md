# Canonical model schema

`.domain-canvas/model.json` is the single source of truth.

```json
{
  "title": "Product domain canvas",
  "version": 1,
  "entities": [
    {
      "id": "customer",
      "name": "Customer",
      "description": "A person or organization receiving the service.",
      "group": "crm",
      "attributes": [
        {
          "name": "id",
          "type": "uuid",
          "pk": true,
          "nullable": false
        },
        {
          "name": "name",
          "type": "text",
          "nullable": false
        }
      ]
    }
  ],
  "relationships": [
    {
      "id": "customer-contracts",
      "from": "customer",
      "to": "contract",
      "label": "has contracts",
      "from_cardinality": "1",
      "to_cardinality": "0..*",
      "kind": "domain",
      "confidence": "confirmed",
      "evidence": "contracts.customer_id -> customers.id"
    }
  ],
  "screens": [
    {
      "id": "contract-detail",
      "name": "Contract detail",
      "route": "/contracts/:id",
      "description": "Review contract status and related documents.",
      "preview_image": "assets/contract-detail.png",
      "preview_html": null,
      "bindings": [
        {"entity": "contract", "role": "primary"},
        {"entity": "customer", "role": "context"},
        {"entity": "document", "role": "collection"}
      ]
    }
  ],
  "concept_groups": [
    {
      "id": "crm",
      "name": "CRM",
      "description": "People and commercial relationships."
    }
  ]
}
```

## Required fields

### Root

- `title`: string
- `version`: integer
- `entities`: array
- `relationships`: array
- `screens`: array
- `concept_groups`: array, may be empty

### Entity

- `id`: stable unique string
- `name`: display label
- `description`: concise business meaning
- `attributes`: array, may be empty in early conceptual modeling
- `group`: optional concept group id

### Attribute

- `name`: field/column name
- `type`: display type
- `pk`: optional boolean
- `fk`: optional object `{ "entity": "...", "attribute": "id" }`
- `nullable`: optional boolean
- `description`: optional string

### Relationship

- `id`: stable unique string
- `from`, `to`: entity ids
- `label`: business-readable meaning
- `from_cardinality`, `to_cardinality`: `1`, `0..1`, `1..*`, or `0..*`
- `kind`: `domain`, `database`, or `both`
- `confidence`: `confirmed` or `inferred`
- `evidence`: optional concise source note

### Screen

- `id`: stable unique string
- `name`: display label
- `route`: optional route or screen identifier
- `description`: optional
- `preview_image`: optional relative asset path
- `preview_html`: optional relative local HTML path
- `bindings`: array of `{ "entity": "...", "role": "primary|context|collection|edit|create" }`

## Invariants

- Entity ids are unique.
- Screen ids are unique.
- Relationship endpoints must exist.
- Binding entity ids must exist.
- A screen can have at most one `primary` binding unless the UI genuinely represents a composite object.
- `preview_image` and `preview_html` may both be absent; if both are present, the generator prefers `preview_html`.
