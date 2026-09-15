# Domain Canvas Skill

A Claude Code skill that builds a **single-source interactive canvas** connecting three views of the same product/domain model:

- **Design** — screens and the objects they expose
- **Concept** — business/domain objects and semantic relationships
- **ER** — attributes, keys, foreign keys, and cardinalities

All three views are generated from the same `model.json`, so changing a relationship once updates every projection after regeneration.

## Live demo

The included GitHub Pages workflow deploys the interactive demo here:

**https://dharmainsight.github.io/domain-canvas-skill/**

The demo is a self-contained HTML app: switch between Design / Concept / ER, pan, zoom, and fit the graph to the viewport.

## Preview

### Design view

![Design view](example/design.png)

### Concept view

![Concept view](example/concept.png)

### ER view

![ER view](example/er.png)

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

Claude Code project skills live under `.claude/skills/<skill-name>/SKILL.md`.

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

Then open `example/index.html` in a browser.

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
│   ├── index.html          # GitHub Pages demo
│   └── model.json          # demo source model
├── example/
│   ├── index.html
│   ├── model.json
│   ├── design.png
│   ├── concept.png
│   └── er.png
└── README.md
```

## Design principle

The value is not three separate diagrams. It is one model projected at three levels:

```text
UI screens  ↔  domain objects  ↔  data model
```

That makes the relationship between what users see, what the business means, and what the database stores reviewable without maintaining three independent sources of truth.
