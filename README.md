# Domain Canvas Skill

A Claude Code skill that builds a **single-source interactive canvas** connecting three views of the same product/domain model:

- **Design** — screens and the objects they expose
- **Concept** — business/domain objects and semantic relationships
- **ER** — attributes, keys, foreign keys, and cardinalities

All three views are generated from the same `model.json`, so changing a relationship once updates every projection after regeneration.

## Live demo

**https://dharmainsight.github.io/domain-canvas-skill/**

The repository includes a self-contained GitHub Pages demo. It supports:

- Design / Concept / ER view switching
- pan and wheel zoom
- fit-to-viewport and zoom controls
- screen-to-entity bindings
- relationship labels and cardinalities
- PK / FK display in the ER projection

The demo uses the same real-estate CRM model stored in [`example/model.json`](example/model.json).

## Install in a project

Copy this directory into your repository:

```text
.claude/skills/domain-canvas/
```

Then in Claude Code, invoke it directly:

```text
/domain-canvas contracts
```

Or ask naturally, for example:

```text
契約まわりの画面・概念モデル・ER図を同じキャンバスにまとめて
```

## What the skill creates

```text
.domain-canvas/
├── model.json      # canonical source of truth
├── index.html      # generated interactive canvas
└── README.md       # evidence / assumptions / refresh notes
```

The bundled generator is dependency-free Python 3.

## Try the included example locally

From this repository root:

```bash
python .claude/skills/domain-canvas/scripts/generate_canvas.py \
  --model example/model.json \
  --out example/index.html
```

Then open `example/index.html` in a browser. The checked-in `docs/index.html` is the same style of generated canvas used for the GitHub Pages demo.

## Repository layout

```text
.
├── .claude/skills/domain-canvas/
│   ├── SKILL.md
│   ├── references/
│   │   ├── extraction-rules.md
│   │   └── model-schema.md
│   └── scripts/
│       └── generate_canvas.py
├── .github/workflows/pages.yml
├── docs/
│   ├── .nojekyll
│   └── index.html          # GitHub Pages demo
├── example/
│   └── model.json          # sample source model
└── README.md
```

## Design principle

The value is not three separate diagrams. It is one model projected at three levels:

```text
UI screens  ↔  domain objects  ↔  data model
```

That makes the relationship between what users see, what the business means, and what the database stores reviewable without maintaining three independent sources of truth.
