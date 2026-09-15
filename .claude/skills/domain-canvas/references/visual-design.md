# Visual design and information selection

## Start with a question

Use a title that states what the reader can understand or decide. Separate structure, behavior, and measurement in navigation. Use one shared vocabulary and stable entity IDs across views; a technical ID belongs in details unless it is necessary to identify the object.

## Information hierarchy

| Layer | Show |
|---|---|
| First glance | Question, selected scope, names, primary connections, units and material assumptions |
| Selected item | Full description, attributes, conditions, actors, formula inputs, references and evidence |
| Another scope | Other screens, processes, cohorts, or entity neighborhoods |

Keep the full model available. A filtered view must show its selected scope and visible count. Do not delete evidence to make a diagram smaller. Missing information must say unknown or undefined rather than appearing as a confirmed absence.

## Layout by meaning

- **Concept / ER:** stable layers; keep cycles together; business labels on edges. ER prioritizes keys and shows at most six attribute rows, with a visible count of additional attributes and full details on selection. Endpoint cardinalities are stated in source-to-target order.
- **State:** label edges with events; distinguish initial and terminal states in text as well as styling. Preserve return paths. Conditions and actors belong in state details. Separate unusually large processes into meaningful machines, not arbitrary page chunks.
- **Sequence:** participant headers, aligned lifelines, numbered message order. Solid calls, dashed returns, open arrows for asynchronous messages. Separate materially different success/failure/retry scenarios. This renderer does not implement UML `alt`, parallel, or activation frames: describe the supported path honestly.
- **Service:** columns are stages and rows are roles; preserve their intersection. Mark interaction/visibility boundaries explicitly. A stage's width is not elapsed time. Blank cells mean unspecified unless the model explicitly documents no action.
- **Lineage:** distinguish data and transformations by text and treatment. Show each dataset's grain; put join, filtering, deduplication, and time rules in details. DAGs represent a specific data version; model recurrent processing as distinct versioned datasets.
- **KPI:** emphasize the outcome value and its unit. Show population and observation window outside the graph. Show derived values from formula inputs, never a separately typed total. The inspector names each input and denominator. Arithmetic dependence is not evidence of a causal effect.

## Readability and interaction

Use restrained color: one accent for focus, neutral surfaces for structure, and a labeled treatment for assumptions. Do not encode state only by color. Maintain visible keyboard focus and descriptive control names. Respect reduced motion and light/dark preferences.

Prefer 16px node names and 13px supporting text at normal scale. Wrap names; restrict secondary descriptions to a short preview with full text in details. Increase space or filter scope before shrinking everything. Default scale preserves legibility; “全体表示” offers an overview and “読みやすく” restores readable sizing. Dense graphs may require panning. On small screens, keep the page within the viewport and allow the graph or matrix to move inside its own surface.

Selection highlights immediate context and exposes evidence. Recenter a selected node when a side inspector reduces canvas width. Do not make unrelated nodes look deleted. Empty extensions retain a clearly labeled empty state.

## Review before delivery

Verify names are readable, edge direction is correct, cycle labels are distinct, and graph labels do not cover cards. Check a long Japanese label, the widest matrix, mobile navigation, a detail panel, and keyboard access. Compare the model counts and KPI results to the generated output. If a renderer cannot express a key exception, use another scenario or explicitly state the limit instead of drawing a misleading approximation.
