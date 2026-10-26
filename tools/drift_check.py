"""Cross-file drift check for the Coach design JSON files (no third-party packages).

Usage: python drift_check.py <project_root>
Reports: JSON parse errors, unresolved $ref, shared-enum drift against the v2 contract,
ladder order, and conflicting id patterns.
"""
import glob
import json
import os
import re
import sys

root = sys.argv[1]
design = os.path.join(root, "design")

CANON = {
    "rungs": ["eliminate", "builtin_feature", "api_connector", "script", "ui_automation",
              "parser_ocr_ml", "llm_node", "human_checkpoint", "llm_agent"],
    "skill": ["none", "basic", "intermediate", "advanced"],
    "sensitivity": ["public", "internal", "confidential", "restricted"],
    "stages": ["triage", "capture", "decompose", "classify", "environment_fit", "design",
               "build_handoff", "test_plan", "deploy_monitor"],
    "roles": ["admin", "coe_reviewer", "builder", "viewer"],
    "labels": ["certified", "works", "experimental", "uncertified"],
    "connection_types": ["managed", "byok_openrouter", "byok_provider",
                         "custom_openai_compat", "local"],
    "export_kinds": ["handoff_brief", "process_document", "review_packet", "blueprint_json",
                     "automate_flow_draft"],
    "export_formats": ["md", "json", "pdf", "docx", "csv", "automate_draft"],
    "status": ["draft", "in_review", "approved", "built", "deployed", "retired"],
    "verdict": ["automate", "fix_process_first", "dont_automate"],
    "server_kind": ["ollama", "lmstudio", "foundry_local", "llamacpp", "vllm", "litellm",
                    "azure_openai", "bedrock", "vertex_openai", "anthropic_compat", "openai",
                    "openrouter", "generic"],
    "ai_mode": ["off", "lite_only", "full"],
}
EXPECTED_PATTERNS = {
    "toolId": r"^[a-z][a-z0-9_]*\.[a-z0-9][a-z0-9_]*$",
}

problems = []
docs = {}
for path in sorted(glob.glob(os.path.join(design, "*.json"))):
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as fh:
            docs[name] = json.load(fh)
    except Exception as exc:  # noqa: BLE001
        problems.append(("PARSE", name, str(exc)))


def walk(node, path=""):
    yield path, node
    if isinstance(node, dict):
        for key, val in node.items():
            yield from walk(val, f"{path}/{key}")
    elif isinstance(node, list):
        for idx, val in enumerate(node):
            yield from walk(val, f"{path}/{idx}")


def resolve(doc, pointer):
    cur = doc
    for part in pointer.lstrip("/").split("/"):
        if part == "":
            continue
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return False
    return True


# 1. $ref resolution
for name, doc in docs.items():
    for path, node in walk(doc):
        if isinstance(node, dict) and isinstance(node.get("$ref"), str):
            ref = node["$ref"]
            target_file, _, frag = ref.partition("#")
            if target_file == "":
                ok = resolve(doc, frag)
            else:
                other = docs.get(os.path.basename(target_file))
                ok = other is not None and (frag == "" or resolve(other, frag))
            if not ok:
                problems.append(("REF", name, f"{path}: unresolved {ref}"))

# 2. enum drift
enums = []
for name, doc in docs.items():
    for path, node in walk(doc):
        if isinstance(node, dict) and isinstance(node.get("enum"), list):
            vals = node["enum"]
            if vals and all(isinstance(v, str) for v in vals):
                enums.append((name, path, vals))

for cname, canon in CANON.items():
    cset = set(canon)
    for name, path, vals in enums:
        vset = set(vals)
        if len(vset) < 3:
            continue
        overlap = len(vset & cset) / min(len(vset), len(cset))
        if overlap < 0.6:
            continue
        if vset == cset:
            if cname == "rungs" and vals != canon:
                problems.append(("ORDER", name, f"{path}: rung order {vals}"))
            continue
        missing = sorted(cset - vset)
        extra = sorted(vset - cset)
        problems.append(("ENUM", name, f"{path} vs {cname}: missing={missing} extra={extra}"))

# 3. id patterns
patterns = {}
for name, doc in docs.items():
    for path, node in walk(doc):
        if isinstance(node, dict) and isinstance(node.get("pattern"), str):
            key = path.rsplit("/", 2)
            owner = key[-3] if len(key) >= 3 else ""
            for label in EXPECTED_PATTERNS:
                if path.endswith(f"/{label}") or path.endswith(f"/{label}/pattern"):
                    patterns.setdefault(label, set()).add((name, node["pattern"]))
for label, pset in patterns.items():
    distinct = {p for _, p in pset}
    if distinct != {EXPECTED_PATTERNS[label]}:
        problems.append(("PATTERN", label, f"{sorted(pset)}"))

# 4. banned/obsolete words in policy enums
for name, path, vals in enums:
    if "disabled" in vals and "forbidden" not in vals and name.startswith("policy"):
        problems.append(("WORD", name, f"{path}: uses 'disabled' ({vals})"))

print(f"files parsed: {len(docs)}; enums scanned: {len(enums)}")
if not problems:
    print("OK: no drift found")
else:
    by_kind = {}
    for kind, name, msg in problems:
        by_kind.setdefault(kind, []).append((name, msg))
    for kind, items in sorted(by_kind.items()):
        print(f"\n[{kind}] {len(items)}")
        for name, msg in items[:40]:
            print(f"  {name}: {msg}")
sys.exit(1 if problems else 0)
