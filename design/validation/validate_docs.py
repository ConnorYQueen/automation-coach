"""Validate the schemas themselves, then every JSON example and fixture in the design docs.

Exit code 0 when everything validates, 1 otherwise.
"""
import collections
import sys

from jsonschema import Draft202012Validator

from common import S, V, json_blocks, load

counts = collections.Counter()
fails = collections.OrderedDict()


def check(cat, label, inst, key, pointer=""):
    counts[cat + " total"] += 1
    errs = sorted(V(key, pointer).iter_errors(inst), key=lambda e: list(e.absolute_path))
    if errs:
        counts[cat + " FAIL"] += 1
        fails.setdefault(cat, []).append(
            (
                label,
                [("/".join(map(str, e.absolute_path)) or "<root>", e.message[:150]) for e in errs[:3]],
                len(errs),
            )
        )
    else:
        counts[cat + " ok"] += 1


# 1 meta-validation of the schemas and of the coach tool parameter schemas
for k, s in S.items():
    try:
        Draft202012Validator.check_schema(s)
        counts["meta ok"] += 1
        print("meta-schema OK:", k)
    except Exception as e:
        counts["meta FAIL"] += 1
        print("meta-schema FAIL", k, str(e)[:200])
tools = load("coach-tools.json")
tl = tools["tools"] if isinstance(tools, dict) and "tools" in tools else tools
n = 0
for t in tl:
    p = t.get("function", {}).get("parameters")
    if p is not None:
        n += 1
        try:
            Draft202012Validator.check_schema(p)
        except Exception as e:
            counts["tool params FAIL"] += 1
            print("tool params FAIL", t["function"]["name"], str(e)[:160])
print("coach tool parameter schemas checked:", n, "of", len(tl))

# 2 tool catalog seed
cat = load("tool-catalog.seed.json")
for e in cat:
    check("catalog entry", e.get("toolId", "?"), e, "blueprint", "#/$defs/toolCatalogEntry")

# 3 examples in the docs, matched by shape
for line, o in json_blocks("rules-engine.md"):
    ks = set(o) if isinstance(o, dict) else set()
    where = f"rules-engine:{line}"
    if "inputStructure" in ks and "diagnosticDelta" not in ks:
        check("diagnostic example", where, o, "blueprint", "#/$defs/diagnostic")
    elif "whyNotCode" in ks:
        check("llmJustification example", where, o, "blueprint", "#/$defs/llmJustification")
    elif "fromRungId" in ks:
        check("graduation example", where, o, "blueprint", "#/$defs/graduationProposal")
    elif {"schemaVersion", "steps"} <= ks or ("auditLog" in ks and "deployPlan" in ks):
        check("Blueprint example", where, o, "blueprint")
for line, o in json_blocks("settings-catalog.md"):
    if not isinstance(o, dict):
        continue
    if "settings" in o and "orgId" in o:
        check("policy example", f"settings-catalog:{line}", o, "policy")
    else:
        for k, v in o.items():
            if isinstance(v, dict):
                check("connection example", f"settings-catalog:{line}:{k}", v, "connection")

for line, o in json_blocks("coach-spec.md"):
    if not isinstance(o, dict):
        continue
    where = f"coach-spec:{line}"
    if "sessionId" in o:
        check("SessionState example", where, o, "coach-session")
    elif "questionId" in o:
        check("LiteExtract example", where, o, "coach-session", "#/$defs/liteExtract")
for line, o in json_blocks("model-certification.md"):
    if isinstance(o, dict) and "probeVersion" in o:
        check("CapabilityReport example", f"model-certification:{line}", o, "capability-report")

# A block that disappears from a doc must not pass silently.
MUST_FIND = {"SessionState example": 1, "LiteExtract example": 3, "CapabilityReport example": 1, "Blueprint example": 2,
             "graduation example": 1, "llmJustification example": 1, "diagnostic example": 1, "policy example": 2}
for cat_name, minimum in MUST_FIND.items():
    if counts[cat_name + " total"] < minimum:
        counts["missing example FAIL"] += 1
        print(f"missing example: expected at least {minimum} '{cat_name}' block(s), found {counts[cat_name + ' total']}")

# 4 engine fixtures, each rebuilt into the pieces the schema knows about
BASE = {
    "inputStructure": "structured", "outputDeterminism": "yes", "costOfError": "low",
    "reversibility": "reversible", "interfaceAvailability": "file_exchange",
    "attendance": "attended", "credentialsRequired": "no", "dataSensitivity": "internal",
    "languageUnderstanding": "none", "judgmentRequired": "no", "frequency": "weekly",
}
cat_ids = {e["toolId"] for e in cat}
seen = 0
tool_missing = set()
for fn in ["rules-engine.md", "pattern-library.md"]:
    for line, o in json_blocks(fn):
        if not (isinstance(o, dict) and {"id", "env", "diagnosticDelta", "expect"} <= set(o)):
            continue
        seen += 1
        fid = f"{fn}:{o['id']}"
        diag = {**BASE, **o["diagnosticDelta"]}
        check("fixture diagnostic", fid, diag, "blueprint", "#/$defs/diagnostic")
        senv = {"systems": o.get("systems", [])}
        senv.update(o.get("stepEnvironment") or {})
        if senv.get("builderSkill") is None:
            senv.pop("builderSkill", None)
        check("fixture environment", fid, senv, "blueprint", "#/$defs/stepEnvironment")
        check("fixture sensitivity", fid, o["blueprintSensitivity"], "blueprint", "#/$defs/sensitivity")
        step = {
            "id": "stp_" + "0" * 26, "order": 1, "name": o["stepName"], "actor": "Analyst",
            "createdBy": "user", "confirmationState": "confirmed", "confirmedBy": "usr_test",
            "confirmedAt": "2026-10-26T09:00:00Z", "diagnostic": diag,
            "environment": {**senv, "builderSkill": senv.get("builderSkill", "intermediate")},
        }
        if o.get("decisionPoints"):
            step["decisionPoints"] = o["decisionPoints"]
        check("fixture full step", fid, step, "blueprint", "#/$defs/step")
        ex = o["expect"]
        for k, ptr in [("rungId", "#/$defs/rungId"), ("tier", "#/$defs/riskTier")]:
            if k in ex:
                check("fixture expect", fid + ":" + k, ex[k], "blueprint", ptr)
        for k in ("toolId", "hostToolId"):
            if k in ex and ex[k] is not None:
                check("fixture expect", fid + ":" + k, ex[k], "blueprint", "#/$defs/toolId")
                if ex[k] not in cat_ids and not ex[k].startswith("org."):
                    tool_missing.add((o["id"], ex[k]))
        for k in ("status", "outcome"):
            if k in ex:
                check("fixture expect", fid + ":" + k, ex[k], "blueprint", f"#/$defs/stepResult/properties/{k}")
print("fixtures found:", seen)
print("fixture toolIds not in catalog seed:", sorted(tool_missing)[:20])
print()
for k in sorted({c.rsplit(" ", 1)[0] for c in counts if c.rsplit(" ", 1)[-1] in ("total", "ok", "FAIL")}):
    print(f"{k:28s} total {counts[k + ' total']:4d}  ok {counts[k + ' ok']:4d}  FAIL {counts[k + ' FAIL']:4d}")
for cat_, items in fails.items():
    print("\n== FAILURES:", cat_, len(items))
    for label, errs, n_ in items[:6]:
        print("  ", label, f"({n_} errors)")
        for p, m in errs:
            print("      ", p, "::", m)

bad = sum(v for k, v in counts.items() if k.endswith("FAIL")) + len(tool_missing)
print("\nRESULT:", "PASS" if bad == 0 else f"FAIL ({bad} problems)")
sys.exit(1 if bad else 0)
