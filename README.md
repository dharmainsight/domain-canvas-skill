# Domain Canvas Skill

A Claude Code skill that generates eight interactive views from one canonical model, connecting product structure, behavior, and measurement.

| Group | View | Question |
|---|---|---|
| Structure | Design | Which business objects does a screen expose or change? |
| Structure | Concept | What are the objects and their business relationships? |
| Structure | ER | What are the keys, references, and cardinalities? |
| Behavior | Lifecycle | Which event and condition allow a state change? |
| Behavior | Sequence | In what order do saving, replying, and notification occur? |
| Behavior | Service blueprint | How do customer actions connect to frontstage and backstage work? |
| Measurement | Lineage | Which data and transformations produce this dataset? |
| Measurement | KPI | How does the result decompose into defined metric inputs? |

The generator uses Python 3.9+ standard libraries. Its standalone HTML has no external JavaScript or CSS dependencies. Existing version 1 models remain supported; missing extensions show an undefined state.

## Demo

[Open the GitHub Pages demo](https://dharmainsight.github.io/domain-canvas-skill/). The published demo tracks `main`; proposed branch changes appear after merge and Pages deployment.

The [example model](example/model.json) contains five entities, three screens, an application state machine, two processing scenarios, a service blueprint, dataset lineage, and a KPI decomposition. Business rules and metric values are explicitly illustrative. The KPI's application cohort and the lineage's contract-start-month aggregate are different measures, with no unsupported application-to-contract join.

## Readable by default

- Navigation separates structure, behavior, and measurement.
- Select a screen, process, or entity neighborhood to focus the question.
- Names and primary relationships appear first; full attributes, conditions, formulas, and evidence appear when selected.
- State, sequence, matrix, lineage, and KPI views preserve their distinct meanings.
- Pan by dragging or scrolling; zoom with Ctrl/Command + wheel or the buttons. “全体表示” fits the whole graph; “読みやすく” restores readable sizing. Dense graphs may require panning.
- Keyboard controls, mobile navigation, dark mode, and reduced-motion support are included.

[Diagram selection](.claude/skills/domain-canvas/references/diagram-selection.md) catalogs 36 use cases for beginners, engineering roles, and business decisions, and distinguishes supported views from future candidates. [Visual design rules](.claude/skills/domain-canvas/references/visual-design.md) explain how to select information without dropping material conditions.

## Install

Copy the **entire** `.claude/skills/domain-canvas/` directory, including `assets/canvas.html`, into your project. Invoke:

```text
/domain-canvas contracts
```

For example: “契約まわりの画面・概念・ERに、状態遷移と顧客対応の流れを加えて”。

The skill maintains `.domain-canvas/model.json`, generated `index.html`, and a README with evidence and refresh notes. [Model schema](.claude/skills/domain-canvas/references/model-schema.md) documents the optional extensions; [extraction rules](.claude/skills/domain-canvas/references/extraction-rules.md) explain confidence and evidence.

## Generate and validate

From this repository root:

```bash
python .claude/skills/domain-canvas/scripts/generate_canvas.py \
  --model example/model.json \
  --out docs/index.html
python -m unittest discover -s tests -v
node tests/check-canvas.mjs
```

Open `docs/index.html` in a browser. Update the model or `assets/canvas.html`, then regenerate; do not edit generated HTML by hand. Local image and self-contained HTML previews are embedded in the output. Supplied missing assets, dangling references, cyclic lineage/formulas, and invalid metric values fail generation with a diagnostic.

The automated checks cover model validation, legacy compatibility, preview portability, safe embedding, formula arithmetic, and graph layout logic. They do not substitute for checking actual browser typography, overlap, and interaction.
