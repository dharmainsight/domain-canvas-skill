#!/usr/bin/env python3
"""Static quality checks for Domain Canvas model and generated HTML."""
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.remote = []
        self.script_src = []
        self.svg_role = False
        self.svg_title = False
        self.svg_desc = False
        self._in_svg = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src"):
            self.script_src.append(attrs["src"])
        for key in ("src", "href"):
            value = attrs.get(key, "")
            if isinstance(value, str) and value.lower().startswith(("http://", "https://", "//")):
                self.remote.append((tag, key, value))
        if tag == "svg":
            self._in_svg = True
            if attrs.get("role") == "img" and attrs.get("aria-labelledby"):
                self.svg_role = True
        elif self._in_svg and tag == "title":
            self.svg_title = True
        elif self._in_svg and tag == "desc":
            self.svg_desc = True

    def handle_endtag(self, tag):
        if tag == "svg":
            self._in_svg = False


def fail(message, errors):
    errors.append(message)


def main():
    parser = argparse.ArgumentParser(description="Check Domain Canvas static output")
    parser.add_argument("--model", required=True)
    parser.add_argument("--html", required=True)
    args = parser.parse_args()

    model_path = Path(args.model)
    html_path = Path(args.html)
    errors = []

    try:
        model = json.loads(model_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL: model JSON could not be read: {exc}", file=sys.stderr)
        raise SystemExit(2)

    text = html_path.read_text(encoding="utf-8")
    scan = Scan()
    scan.feed(text)

    if scan.remote:
        for item in scan.remote:
            fail(f"remote resource found: {item[0]} {item[1]}={item[2]}", errors)
    if scan.script_src:
        fail("generated HTML must not load external script files", errors)
    if not scan.svg_role or not scan.svg_title or not scan.svg_desc:
        fail("relationship SVG must have role=img, aria-labelledby, title, and desc", errors)
    if "prefers-reduced-motion:reduce" not in text:
        fail("missing reduced-motion fallback", errors)
    if re.search(r"\banimation\s*:\s*(?!none\b)", text, re.I):
        fail("time-based CSS animation found; static output is the default", errors)
    for dangerous in (r"\beval\s*\(", r"\bnew\s+Function\s*\(", r"javascript:"):
        if re.search(dangerous, text, re.I):
            fail(f"dangerous script pattern found: {dangerous}", errors)

    payload_match = re.search(r'<script id="model" type="application/json">(.*?)</script>', text, re.S)
    if not payload_match:
        fail("embedded canonical model not found", errors)
    else:
        try:
            embedded = json.loads(payload_match.group(1).replace("<\\/", "</"))
            if embedded != model:
                fail("embedded model differs from input model", errors)
        except Exception as exc:
            fail(f"embedded model is invalid JSON: {exc}", errors)

    focus = ((model.get("presentation") or {}).get("focus_entities") or [])
    if len(focus) > 2:
        fail("more than two focus entities", errors)

    if errors:
        print("Domain Canvas self-check failed:", file=sys.stderr)
        for error in errors:
            print(" - " + error, file=sys.stderr)
        raise SystemExit(2)

    mode = "overview-first" if len(model.get("entities", [])) > 9 else "detail"
    print(
        f"PASS: self-contained static HTML, accessible relationship SVG, model embedded unchanged, "
        f"focus={len(focus)}, density-mode={mode}"
    )


if __name__ == "__main__":
    main()
