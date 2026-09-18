# Diagram design rules

Use these rules when choosing content, layout, emphasis, and interaction for a Domain Canvas.

## 1. One node, one reviewable concept

A node should answer a clear question: “What object is this?” or “What screen is this?”

Merge two labels when they always appear together and reviewing them separately would not change a decision. Keep them separate when they have distinct lifecycle, ownership, constraints, or relationships.

## 2. Make every edge earn its ink

An edge must communicate something that placement, grouping, or a label cannot already express.

- Do not add membership edges when a group lane already shows membership.
- Do not draw every screen binding. In Design, show `context` and `collection` as metadata by default.
- Keep semantic/database relationship edges because their label, confidence, or cardinality is substantive.
- Prefer fewer labeled edges over a dense web of unlabeled lines.

## 3. Limit emphasis

Use emphasis for the current review question, not as decoration.

- Highlight no more than two entities.
- Use one accent family for focus.
- Do not give every node a colored border, badge, or background.
- Use dashed lines plus text for inferred relationships; do not rely on color alone.

## 4. Control density

Target roughly 4/10 visual density: enough structure to scan, enough whitespace to trace relationships.

- Up to 9 entity-level nodes: a single detail view is usually acceptable.
- More than 9: begin with an overview grouped by concept, then allow detail.
- If a section becomes unreadable at “Fit”, split by scope instead of shrinking text indefinitely.

## 5. Prefer static explanation

Static output is the default. Pan, zoom, tabs, and overview/detail toggles support navigation; they should not animate information merely to look dynamic.

Only introduce time-based animation when the sequence itself is the subject of explanation. Always provide an equivalent static state and honor reduced-motion preferences.

## 6. Brand as a system, not per-node decoration

Use the optional presentation theme to coordinate background, surface, text, lines, and a single accent. Keep contrast readable and retain meaning without color.

Do not independently recolor each diagram or each node. Consistency across views is more useful than novelty.

## 7. Re-layout imported diagrams

When Mermaid, draw.io, or an older architecture diagram exists:

1. Extract candidate concepts, labels, and relationships.
2. Cross-check them against stronger code/schema/spec evidence.
3. Rebuild the canonical model.
4. Generate a new layout based on reader task, density, and grouping.

Do not treat old coordinates, line routing, or styling as source-of-truth data.

## 8. Accessibility and static delivery

Generated output should:

- expose view controls as labeled tabs/buttons,
- include an accessible SVG title and description,
- distinguish inferred relationships with dashed lines and text,
- avoid remote fonts/scripts/styles by default,
- remain usable with reduced motion,
- keep local preview assets explicitly referenced.

Run `scripts/self_check.py` before delivery.
