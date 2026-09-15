#!/usr/bin/env python3
"""Validate one canonical model and emit a dependency-free Domain Canvas."""
import argparse
import base64
import copy
import html
import json
import math
import re
import sys
from pathlib import Path

CONFIDENCES = ("confirmed", "inferred", "illustrative", "unknown")
CARDINALITIES = ("1", "0..1", "1..*", "0..*")
EXTENSIONS = ("state_machines", "scenarios", "journeys", "lineage", "outcomes")


def validate(model):
    """Return actionable errors; never mutate the supplied model."""
    errors = []
    if not isinstance(model, dict):
        return ["model must be an object"]

    def fail(where, message):
        errors.append(f"{where}: {message}")

    def array(obj, field, where, required=False):
        value = obj.get(field, None if required else [])
        if not isinstance(value, list):
            fail(where, f"{field} must be an array")
            return []
        result = []
        for i, item in enumerate(value):
            if not isinstance(item, dict):
                fail(f"{where}.{field}[{i}]", "must be an object")
            else:
                result.append(item)
        return result

    def ids(items, where):
        result = set()
        for item in items:
            value = item.get("id")
            if not isinstance(value, str) or not value.strip():
                fail(where, "each item needs a nonempty string id")
            elif value in result:
                fail(where, f"duplicate id {value!r}")
            else:
                result.add(value)
        return result

    def ref(value, targets, where):
        if not isinstance(value, str) or value not in targets:
            fail(where, f"unknown reference {value!r}")

    def refs(item, field, targets, where, required=False):
        values = item.get(field, None if required else [])
        if not isinstance(values, list) or not all(isinstance(x, str) for x in values):
            fail(where, f"{field} must be an array of ids")
            return []
        if len(values) != len(set(values)):
            fail(where, f"{field} contains duplicate references")
        for value in values:
            ref(value, targets, f"{where}.{field}")
        return values

    def metadata(item, where):
        if item.get("confidence", "unknown") not in CONFIDENCES:
            fail(where, "confidence must be confirmed, inferred, illustrative, or unknown")
        for field in ("name", "description", "evidence", "note", "condition", "actor", "grain", "rule"):
            if field in item and not isinstance(item[field], str):
                fail(where, f"{field} must be a string")

    def acyclic(nodes, edges, where):
        graph = {n: [] for n in nodes}
        for a, b in edges:
            if isinstance(a, str) and isinstance(b, str) and a in graph and b in graph:
                graph[a].append(b)
        state = {}
        def visit(n):
            if state.get(n) == 1:
                return False
            if state.get(n) == 2:
                return True
            state[n] = 1
            if not all(visit(child) for child in graph[n]):
                return False
            state[n] = 2
            return True
        if not all(visit(n) for n in graph):
            fail(where, "contains a cycle; use separate versioned datasets or acyclic metric inputs")

    if not isinstance(model.get("title"), str) or not model["title"].strip():
        fail("model", "title must be a nonempty string")
    if type(model.get("version")) is not int or model["version"] not in (1, 2):
        fail("model", "version must be 1 or 2")
    entities = array(model, "entities", "model", True)
    screens = array(model, "screens", "model", True)
    relations = array(model, "relationships", "model", True)
    groups = array(model, "concept_groups", "model", True)
    eids, sids = ids(entities, "entities"), ids(screens, "screens")
    gids = ids(groups, "concept_groups")
    ids(relations, "relationships")
    for group in groups:
        metadata(group, "concept_group")
    attributes = {}
    for entity in entities:
        where = f"entity {entity.get('id')}"
        metadata(entity, where)
        if "group" in entity:
            ref(entity["group"], gids, where)
        attrs = array(entity, "attributes", where, True)
        names = [a.get("name") for a in attrs]
        if not all(isinstance(n, str) and n for n in names):
            fail(where, "attributes need string names")
        elif len(names) != len(set(names)):
            fail(where, "duplicate attribute names")
        if isinstance(entity.get("id"), str):
            attributes[entity["id"]] = {n for n in names if isinstance(n, str)}
        for attr in attrs:
            for flag in ("pk", "nullable"):
                if flag in attr and type(attr[flag]) is not bool:
                    fail(where, f"attribute {attr.get('name')}.{flag} must be boolean")
            if attr.get("pk") and attr.get("nullable"):
                fail(where, f"primary key {attr.get('name')} cannot be nullable")
    for entity in entities:
        for attr in entity.get("attributes", []) if isinstance(entity.get("attributes"), list) else []:
            if not isinstance(attr, dict) or "fk" not in attr:
                continue
            fk = attr["fk"]
            where = f"entity {entity.get('id')}.{attr.get('name')}.fk"
            if not isinstance(fk, dict):
                fail(where, "must be an entity/attribute object")
                continue
            ref(fk.get("entity"), eids, where)
            target = fk.get("entity")
            ref(fk.get("attribute"), attributes.get(target, set()) if isinstance(target, str) else set(), where)
    for rel in relations:
        where = f"relationship {rel.get('id')}"
        metadata(rel, where)
        ref(rel.get("from"), eids, where)
        ref(rel.get("to"), eids, where)
        for field in ("from_cardinality", "to_cardinality"):
            if rel.get(field) not in CARDINALITIES:
                fail(where, f"invalid {field}")
        if rel.get("kind") not in ("domain", "database", "both"):
            fail(where, "invalid kind")
    for screen in screens:
        where = f"screen {screen.get('id')}"
        metadata(screen, where)
        for binding in array(screen, "bindings", where, True):
            ref(binding.get("entity"), eids, where)
            if binding.get("role") not in ("primary", "context", "collection", "edit", "create"):
                fail(where, "invalid binding role")
        for field in ("preview_html", "preview_image"):
            value = screen.get(field)
            if value is not None and (not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", value)):
                fail(where, f"{field} must be a relative asset path inside the model directory")
    extensions = {}
    for field in EXTENSIONS:
        extensions[field] = array(model, field, "model")
        ids(extensions[field], field)
        for item in extensions[field]:
            metadata(item, f"{field} {item.get('id')}")
            refs(item, "entity_ids", eids, f"{field} {item.get('id')}")
    for machine in extensions["state_machines"]:
        where = f"state_machine {machine.get('id')}"
        ref(machine.get("entity_id"), eids, where)
        states = array(machine, "states", where, True)
        state_ids = ids(states, where)
        ref(machine.get("initial"), state_ids, where)
        for state in states:
            metadata(state, where)
            if "terminal" in state and type(state["terminal"]) is not bool:
                fail(where, "terminal must be boolean")
        transitions = array(machine, "transitions", where, True)
        ids(transitions, where)
        for trans in transitions:
            metadata(trans, where)
            ref(trans.get("from"), state_ids, where)
            ref(trans.get("to"), state_ids, where)
            if not isinstance(trans.get("label"), str) or not trans["label"]:
                fail(where, "transitions need an event label")
        terminal = {s.get("id") for s in states if s.get("terminal") and isinstance(s.get("id"), str)}
        if any(isinstance(t.get("from"), str) and t["from"] in terminal for t in transitions):
            fail(where, "terminal states cannot have outgoing transitions")
    for scenario in extensions["scenarios"]:
        where = f"scenario {scenario.get('id')}"
        if "screen_id" in scenario:
            ref(scenario["screen_id"], sids, where)
        participants = array(scenario, "participants", where, True)
        pids = ids(participants, where)
        if not participants:
            fail(where, "at least one participant is required")
        if pids & ids(messages := array(scenario, "messages", where, True), where + ".messages"):
            fail(where, "participant and message ids must be distinct")
        for participant in participants:
            metadata(participant, where)
            if "entity_id" in participant:
                ref(participant["entity_id"], eids, where)
        for message in messages:
            metadata(message, where)
            ref(message.get("from"), pids, where)
            ref(message.get("to"), pids, where)
            if message.get("kind", "call") not in ("call", "return", "async"):
                fail(where, "message kind must be call, return, or async")
            if not isinstance(message.get("label"), str) or not message["label"]:
                fail(where, "messages need a label")
    for journey in extensions["journeys"]:
        where = f"journey {journey.get('id')}"
        step_items = array(journey, "steps", where, True)
        lane_items = array(journey, "lanes", where, True)
        steps = ids(step_items, where + ".steps")
        lanes = ids(lane_items, where + ".lanes")
        if not steps or not lanes:
            fail(where, "at least one step and lane are required")
        for item in step_items + lane_items:
            metadata(item, where)
        cells = array(journey, "cells", where, True)
        ids(cells, where + ".cells")
        for cell in cells:
            ref(cell.get("step"), steps, where)
            ref(cell.get("lane"), lanes, where)
            refs(cell, "entity_ids", eids, where)
            refs(cell, "screen_ids", sids, where)
            metadata(cell, where)
    for lineage in extensions["lineage"]:
        where = f"lineage {lineage.get('id')}"
        datasets = array(lineage, "datasets", where, True)
        jobs = array(lineage, "jobs", where, True)
        dids, jids = ids(datasets, where), ids(jobs, where)
        if dids & jids:
            fail(where, "dataset and job ids must be distinct")
        for dataset in datasets:
            metadata(dataset, where)
            if "entity_id" in dataset:
                ref(dataset["entity_id"], eids, where)
        edges = []
        for job in jobs:
            metadata(job, where)
            ins = refs(job, "inputs", dids, where, True)
            outs = refs(job, "outputs", dids, where, True)
            if not ins or not outs:
                fail(where, "jobs need at least one input and one output")
            edges.extend((i, job.get("id")) for i in ins)
            edges.extend((job.get("id"), o) for o in outs)
        acyclic(dids | jids, edges, where)
    for outcome in extensions["outcomes"]:
        where = f"outcome {outcome.get('id')}"
        metrics = array(outcome, "metrics", where, True)
        mids = ids(metrics, where)
        ref(outcome.get("root"), mids, where)
        for field in ("population", "window"):
            if not isinstance(outcome.get(field), str) or not outcome[field].strip():
                fail(where, f"{field} is required to interpret metrics")
        edges = []
        for metric in metrics:
            mwhere = where + f".metric {metric.get('id')}"
            metadata(metric, mwhere)
            refs(metric, "entity_ids", eids, mwhere)
            if not isinstance(metric.get("unit"), str):
                fail(mwhere, "unit is required")
            if "operator" in metric:
                if "value" in metric:
                    fail(mwhere, "derived metrics cannot also have a stored value")
                if metric["operator"] not in ("product", "sum", "ratio"):
                    fail(mwhere, "operator must be product, sum, or ratio")
                inputs = refs(metric, "inputs", mids, mwhere, True)
                if not inputs or metric["operator"] == "ratio" and len(inputs) != 2:
                    fail(mwhere, "invalid number of inputs")
                edges.extend((metric.get("id"), i) for i in inputs)
            else:
                value = metric.get("value")
                if type(value) not in (int, float) or not math.isfinite(value):
                    fail(mwhere, "leaf value must be a finite number")
                elif metric.get("unit") == "%" and not 0 <= value <= 1:
                    fail(mwhere, "percent values must be fractions between 0 and 1")
        acyclic(mids, edges, where)
    if not errors:
        try:
            for outcome in extensions["outcomes"]:
                evaluate_metrics(outcome)
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def evaluate_metrics(outcome):
    metrics = {m["id"]: m for m in outcome["metrics"]}
    values = {}
    visiting = set()
    def value(mid):
        if mid in values:
            return values[mid]
        if mid in visiting:
            raise ValueError(f"outcome {outcome['id']}: cyclic metric {mid}")
        visiting.add(mid)
        metric = metrics[mid]
        if "operator" not in metric:
            result = metric["value"]
        else:
            args = [value(i) for i in metric["inputs"]]
            if metric["operator"] == "product":
                result = math.prod(args)
            elif metric["operator"] == "sum":
                result = sum(args)
            else:
                if args[1] == 0:
                    raise ValueError(f"outcome {outcome['id']}: zero denominator for {mid}")
                result = args[0] / args[1]
        if not math.isfinite(result):
            raise ValueError(f"outcome {outcome['id']}: non-finite result for {mid}")
        values[mid] = result
        visiting.remove(mid)
        return result
    for mid in metrics:
        value(mid)
    return values


def prepare(model, model_dir):
    payload = copy.deepcopy(model)
    payload["computed_outcomes"] = {o["id"]: evaluate_metrics(o) for o in model.get("outcomes", [])}
    for screen in payload["screens"]:
        screen.pop("embedded_preview", None)
        source = screen.get("preview_html") or screen.get("preview_image")
        if not source:
            continue
        path = (model_dir / source).resolve()
        if not path.is_relative_to(model_dir.resolve()) or not path.is_file():
            raise ValueError(f"screen {screen['id']}: preview asset is missing or outside model directory: {source}")
        if screen.get("preview_html"):
            screen["embedded_preview"] = {"kind": "html", "content": path.read_text(encoding="utf-8")}
        else:
            mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(path.suffix.lower())
            if not mime:
                raise ValueError(f"screen {screen['id']}: preview image must be PNG, JPEG, or WebP")
            screen["embedded_preview"] = {"kind": "image", "content": f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"}
    return payload


def generate(model, model_dir=None):
    errors = validate(model)
    if errors:
        raise ValueError("Model validation failed:\n" + "\n".join(" - " + e for e in errors))
    payload = prepare(model, Path(model_dir or "."))
    encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = (Path(__file__).resolve().parent.parent / "assets" / "canvas.html").read_text(encoding="utf-8")
    replacements = {"TITLE": html.escape(model["title"]), "MODEL": encoded}
    return re.sub(r"__DC_(TITLE|MODEL)__", lambda m: replacements[m[1]], template)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    source, destination = Path(args.model), Path(args.out)
    try:
        model = json.loads(source.read_text(encoding="utf-8"))
        document = generate(model, source.parent)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(document, encoding="utf-8")
    except (ValueError, OSError, RecursionError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"Generated {destination} ({len(model['entities'])} entities, {len(model['screens'])} screens, "
          f"{sum(bool(model.get(k)) for k in EXTENSIONS)} extended views)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
