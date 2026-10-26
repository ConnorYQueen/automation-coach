"""Strictness probe: how many leaves of each example can be deleted or retyped and still validate.

Informational only (always exits 0). A leaf that survives a type change is a field the schema
does not type, which is worth knowing about but is not always a defect.
"""
import collections

from common import V, connection_examples, copy, example_blueprint, json_blocks, policy_examples

DEL = object()


def paths(o, p=()):
    yield p, o
    if isinstance(o, dict):
        for k, v in o.items():
            yield from paths(v, p + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from paths(v, p + (i,))


def setp(o, p, v):
    c = copy.deepcopy(o)
    t = c
    for k in p[:-1]:
        t = t[k]
    if v is DEL:
        del t[p[-1]]
    else:
        t[p[-1]] = v
    return c


def run(name, inst, key):
    v = V(key)
    assert not list(v.iter_errors(inst)), f"{name}: base example is not valid"
    res = collections.Counter()
    accepted = []
    for p, val in paths(inst):
        if not p:
            continue
        if isinstance(p[-1], str):
            ok = not list(v.iter_errors(setp(inst, p, DEL)))
            res["delete accepted" if ok else "delete rejected"] += 1
        if not isinstance(val, (dict, list)):
            wrong = 12345 if isinstance(val, str) else "__x__"
            ok = not list(v.iter_errors(setp(inst, p, wrong)))
            res["retype accepted" if ok else "retype rejected"] += 1
            if ok:
                accepted.append("/".join(map(str, p)))
    print(f"{name}: {dict(res)}")
    print("  leaves whose type is not enforced (first 25):", accepted[:25], "... total", len(accepted))


def run_fragment(name, inst, key, pointer):
    """Like run, for an example that validates against a fragment of a schema."""
    global V
    real_V = V
    V = lambda k, ptr="": real_V(key, pointer)
    try:
        run(name, inst, key)
    finally:
        V = real_V


run("Blueprint example", example_blueprint(), "blueprint")
for _, o in json_blocks("coach-spec.md"):
    if isinstance(o, dict) and "sessionId" in o:
        run("SessionState example", o, "coach-session")
    elif isinstance(o, dict) and "questionId" in o:
        run_fragment("LiteExtract example " + ("answer" if "value" in o else "steps" if "steps" in o else "exceptions"), o, "coach-session", "#/$defs/liteExtract")
for _, o in json_blocks("model-certification.md"):
    if isinstance(o, dict) and "probeVersion" in o:
        run("CapabilityReport example", o, "capability-report")
for i, p in enumerate(policy_examples()):
    run(f"Policy example {i}", p, "policy")
for k, c in connection_examples():
    run(f"Connection example {k}", c, "connection")
