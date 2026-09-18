# Canonical model schema

`.domain-canvas/model.json` is the single source of truth.

```json
{
  "title": "Product domain canvas",
  "version": 1,
  "presentation": {
    "focus_entities": ["contract", "document"],
    "theme": {
      "background": "#f3f4ef",
      "surface": "#ffffff",
      "ink": "#20231c",
      "muted": "#667064",
      "line": "#cfd2c7",
      "accent": "#9b6200",
      "accent_soft": "#fbf3ce",
      "warning": "#9a5a00"
    }
  },
  "entities": [
    {
      "id": "customer",
      "name": "Customer",
      "description": "A person or organization receiving the service.",
      "group": "crm",
      "attributes": [
        {"name": "id", "type": "uuid", "pk": true, "nullable": false},
        {"name": "name", "type": "text", "nullable": false}
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
    {"id": "crm", "name": "CRM", "description": "People and commercial relationships."}
  ]
}
```

## Required root fields

- `title`: string
- `version`: integer
- `entities`: array
- `relationships`: array
- `screens`: array
- `concept_groups`: array; may be empty

`presentation` is optional.

## Entity

- `id`: stable unique string
- `name`: display label
- `description`: concise business meaning
- `attributes`: array; may be empty during early conceptual modeling
- `group`: optional concept-group id

## Attribute

- `name`: field/column name
- `type`: display type
- `pk`: optional boolean
- `fk`: optional object `{ "entity": "...", "attribute": "id" }`
- `nullable`: optional boolean
- `description`: optional string

## Relationship

- `id`: stable unique string
- `from`, `to`: entity ids
- `label`: business-readable meaning
- `from_cardinality`, `to_cardinality`: `1`, `0..1`, `1..*`, or `0..*`
- `kind`: `domain`, `database`, or `both`
- `confidence`: `confirmed` or `inferred`
- `evidence`: optional concise source note

## Screen

- `id`: stable unique string
- `name`: display label
- `route`: optional route or screen identifier
- `description`: optional
- `preview_image`: optional local relative asset path
- `preview_html`: optional local relative HTML path
- `bindings`: array of `{ "entity": "...", "role": "primary|context|collection|edit|create" }`

## Presentation

Presentation affects reading, not domain meaning.

### `focus_entities`

Optional array of zero to two entity IDs. Use it to emphasize the current review question. Do not add more than two; if more items are important, reduce scope or use overview/detail instead.

### `theme`

Optional restrained brand palette. Supported keys:

- `background`
- `surface`
- `ink`
- `muted`
- `line`
- `accent`
- `accent_soft`
- `warning`

Values must be hex colors (`#RGB`, `#RRGGBB`, or `#RRGGBBAA`). The generator falls back to its accessible editorial palette for missing keys.

## Invariants

- Entity IDs are unique.
- Screen IDs are unique.
- Relationship endpoints must exist.
- Binding entity IDs must exist.
- Focus entity IDs must exist and total no more than two.
- A screen can have at most one `primary` binding unless the UI genuinely represents a composite object.
- `preview_image` and `preview_html` must be local relative paths; remote URLs and parent traversal are rejected.
- If both previews are present, the generator prefers `preview_html`.
