---
name: domain-canvas
description: Build or update a single-source interactive domain canvas from project docs and code. Use for screen-to-domain maps, conceptual models, ER diagrams, state transitions, processing sequences, service blueprints, data lineage, and KPI decomposition, or when choosing diagrams for engineers, beginners, and business decision makers.
---

# Domain Canvas

Generate eight complementary views from one canonical model. Choose the view by the reader's question, then show the smallest useful scope with its assumptions intact.

## Outputs

Maintain `.domain-canvas/model.json`, generated `.domain-canvas/index.html`, and `.domain-canvas/README.md` for sources, unresolved assumptions, and the refresh command. Preserve user-specified locations. Change the model or bundled template, then regenerate; never hand-edit generated HTML.

## Workflow

1. **Inspect before asking.** Read an existing model first. Search migrations/ORM, typed models/API schemas, specifications/ADRs, routes/components, and user-provided prototypes. Read `references/extraction-rules.md` for which source supports which claim. Preserve stable IDs and confirmed labels.
2. **Choose the question and scope.** Read `references/diagram-selection.md`. Use one screen, entity neighborhood, process, cohort, or decision at a time. Beginners need concrete names and actions; engineers need constraints and exceptions; business readers need definitions and comparison conditions. Do not fill every view merely because it exists.
3. **Build one canonical model.** Read `references/model-schema.md`. Keep entities, screens, and relationships shared; extend them with stable references in `state_machines`, `scenarios`, `journeys`, `lineage`, and `outcomes` only when the required information exists. Version 1 models remain accepted. Omitted extensions display an honest empty state.
4. **Preserve evidence.** Mark `confirmed`, `inferred`, `illustrative`, or `unknown`. Keep evidence next to each claim. An enum type does not establish transitions; a screen binding does not establish API order; an FK does not establish a business metric. Use `illustrative` and `is_example: true` for constructed samples. Do not turn unknown real values into zero.
5. **Refine the view.** Read `references/visual-design.md`. Show names and primary relationships first. Put full attributes, conditions, formulas, and evidence in the inspector. Keep units, population, observation window, boundaries, and material exceptions visible or directly accessible. Use specialized sequence/matrix layouts where order or alignment carries meaning.
6. **Attach actual screen evidence.** Use `preview_image` or self-contained `preview_html` relative to the model directory. Missing supplied assets are errors; absent assets produce “プレビュー未登録”. HTML previews are sandboxed. Do not invent screenshots.
7. **Generate and validate.** Run the command below. Check references, nullable/FK consistency, transition conditions, message order, blueprint alignment, lineage grain, and metric arithmetic. Review at least one representative view per added family, a long label, detail selection, and a narrow screen when browser access is available. State any unverified rendering rather than claiming a visual pass.

```bash
python .claude/skills/domain-canvas/scripts/generate_canvas.py \
  --model .domain-canvas/model.json \
  --out .domain-canvas/index.html
```

Resolve the script relative to this skill when installed elsewhere. Python 3.9+ is required; copy the entire skill directory, including `assets/canvas.html`. The generated canvas needs no JavaScript dependencies or server.

## View semantics

| Group | View | Meaning of a connection |
|---|---|---|
| Structure | Design | Screen displays, creates, or updates an entity |
| Structure | Concept | Business relationship between entities |
| Structure | ER | Data relationship with cardinality and keys |
| Behavior | Lifecycle | Permitted state change caused by an event |
| Behavior | Sequence | Message from one participant to another, in order |
| Behavior | Service | Same process stage across customer, frontstage, backstage, and support |
| Measurement | Lineage | Dataset input/output of a transformation |
| Measurement | Outcome | Arithmetic decomposition of a metric, not a causal effect |

A generic arrow must not blur those meanings. Concept and ER are different projections of shared relationships; domain-only relationships are omitted from ER.

## Updating and completion

Reconcile changes into the existing model, preserving confirmed IDs and user labels. Resolve conflicting evidence and report ambiguous removals before deleting them. Regenerate all affected projections together.

Report the sources used, views updated, validation performed, unresolved assumptions, and refresh command. Do not claim authority beyond the evidence. For KPI samples, independently check arithmetic and conditional denominators; never link a cohort metric to a period aggregate without a supported mapping.
