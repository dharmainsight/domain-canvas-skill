# Domain Canvas Skill

An evidence-grounded skill for building a **single-source domain canvas** that connects three views of the same product or system model:

- **Design** — screens and the objects they directly act on
- **Concept** — business/domain objects and semantic relationships
- **ER** — attributes, keys, foreign keys, and cardinalities

All views are generated from one `model.json`, so a relationship is maintained once and projected consistently.

## What changed in this version

The renderer now treats diagram design as a constraint system instead of “draw every box and every line”:

- one node represents one reviewable concept,
- Design draws direct `primary` / `edit` / `create` edges and keeps context/collection as labels,
- concept groups are expressed through layout lanes rather than extra membership lines,
- focus is limited to two entities,
- models above 9 entities open in an overview-first mode with a Detail toggle,
- the output is static by default and honors reduced-motion preferences,
- an optional presentation theme keeps background, text, lines, and one accent consistent,
- Mermaid/draw.io diagrams can be treated as input evidence and re-laid out from semantics rather than copied geometrically,
- generated HTML includes accessible view controls and an accessible relationship SVG,
- `self_check.py` verifies self-contained output, accessibility markers, embedded-model integrity, static behavior, and unsafe/remote resource patterns.

These rules are documented in [`references/diagram-design-rules.md`](.claude/skills/domain-canvas/references/diagram-design-rules.md).

## Live demo

**https://dharmainsight.github.io/domain-canvas-skill/**

The demo uses the real-estate CRM model in [`example/model.json`](example/model.json). It supports:

- Design / Concept / ER switching
- group-aware layout
- restrained focus highlighting
- pan, wheel zoom, fit-to-viewport, and keyboard panning
- relationship confidence (`confirmed` vs `inferred`)
- PK / FK display in ER
- overview/detail behavior for larger models

## Install in Claude Code

Copy this directory into your repository:

```text
.claude/skills/domain-canvas/
```

Then invoke it directly:

```text
/domain-canvas contracts
```

Or ask naturally:

```text
契約まわりの画面・概念モデル・ER図を同じキャンバスにまとめて
```

The skill folder also includes `agents/openai.yaml` and portable `name` / `description` frontmatter so it can be packaged as a ChatGPT Skill without maintaining a second instruction set.

## What the skill creates

```text
.domain-canvas/
├── model.json      # canonical source of truth
├── index.html      # generated static interactive canvas
└── README.md       # evidence / assumptions / refresh notes
```

## Generate and check

The bundled tools use only Python 3 standard-library modules.

```bash
python .claude/skills/domain-canvas/scripts/generate_canvas.py \
  --model .domain-canvas/model.json \
  --out .domain-canvas/index.html

python .claude/skills/domain-canvas/scripts/self_check.py \
  --model .domain-canvas/model.json \
  --html .domain-canvas/index.html
```

Try the included example:

```bash
python .claude/skills/domain-canvas/scripts/generate_canvas.py \
  --model example/model.json \
  --out docs/index.html

python .claude/skills/domain-canvas/scripts/self_check.py \
  --model example/model.json \
  --html docs/index.html
```

## Repository layout

```text
.
├── .claude/skills/domain-canvas/
│   ├── SKILL.md
│   ├── agents/
│   │   └── openai.yaml
│   ├── references/
│   │   ├── diagram-design-rules.md
│   │   ├── extraction-rules.md
│   │   └── model-schema.md
│   └── scripts/
│       ├── generate_canvas.py
│       └── self_check.py
├── .github/workflows/
├── docs/
│   ├── .nojekyll
│   └── index.html
├── example/
│   └── model.json
└── README.md
```

## Design principle

The value is not three separate diagrams. It is one evidence-backed model projected at three levels:

```text
UI screens  ↔  domain objects  ↔  data model
```

The canvas should help a reviewer answer a question faster. If a sentence or table communicates a fact more clearly than another node or edge, do not draw it.