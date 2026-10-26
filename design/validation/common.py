"""Shared loader for the design-folder validators.

DESIGN_DIR (env) points at the folder that holds the three *.schema.json files and the
markdown/JSON design documents. It defaults to the parent of this validation folder.
"""
import copy
import json
import os
import re
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

HERE = Path(__file__).resolve().parent
D = Path(os.environ.get("DESIGN_DIR", HERE.parent))

SCHEMA_KEYS = ["blueprint", "connection", "policy", "capability-report", "coach-session"]


def load(name):
    return json.loads((D / name).read_text(encoding="utf-8"))


def text(name):
    return (D / name).read_text(encoding="utf-8")


S = {k: load(f"{k}.schema.json") for k in SCHEMA_KEYS}
ID = {k: s["$id"] for k, s in S.items()}
REG = Registry()
for _s in S.values():
    REG = REG.with_resource(_s["$id"], Resource.from_contents(_s))
FORMAT_CHECKER = Draft202012Validator.FORMAT_CHECKER


def V(key, pointer=""):
    """Validator for a whole schema, or for one fragment such as '#/$defs/step'."""
    return Draft202012Validator(
        {"$ref": ID[key] + pointer}, registry=REG, format_checker=FORMAT_CHECKER
    )


def json_blocks(filename):
    """Yield (line_number, parsed_json) for every ```json fence in a markdown file."""
    t = text(filename)
    for m in re.finditer(r"```json\r?\n(.*?)```", t, flags=re.S):
        yield t[: m.start()].count("\n") + 1, json.loads(m.group(1))


def example_blueprint():
    """The full worked Blueprint in rules-engine.md: the complete one with the longest audit log.

    The MINI Blueprint used by the reopen fixtures is also complete but has an empty audit log
    and a single step, so it loses to the worked example.
    """
    found = [
        o
        for _, o in json_blocks("rules-engine.md")
        if isinstance(o, dict) and {"schemaVersion", "steps", "auditLog"} <= set(o)
    ]
    if not found:
        raise SystemExit("no full example Blueprint found in rules-engine.md")
    return max(found, key=lambda o: (len(o["auditLog"]), len(o["steps"])))


def policy_examples():
    return [
        o
        for _, o in json_blocks("settings-catalog.md")
        if isinstance(o, dict) and "orgId" in o
    ]


def connection_examples():
    return [
        (k, v)
        for _, o in json_blocks("settings-catalog.md")
        if isinstance(o, dict) and "orgId" not in o
        for k, v in o.items()
        if isinstance(v, dict)
    ]


def mod(obj, fn):
    """Deep-copy obj, apply fn to the copy, return the copy."""
    c = copy.deepcopy(obj)
    fn(c)
    return c
