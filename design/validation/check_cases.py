"""Accept/reject cases for the schemas: each case states whether the instance must validate.

Exit code 0 when every expectation holds, 1 otherwise. Some cases pin down behavior that is
deliberate: unknown audit actions and unknown policy setting keys are accepted so that older
clients keep working when a newer one adds a name.
"""
import sys

from common import V, connection_examples, copy, example_blueprint, json_blocks, mod, policy_examples

bp = example_blueprint()
bpv, polv, conv = V("blueprint"), V("policy"), V("connection")
rows = []
NOW = "2026-10-26T09:00:00Z"


def expect(name, inst, validator, want_valid):
    errs = list(validator.iter_errors(inst))
    got = not errs
    rows.append((name, want_valid, got, "" if got else errs[0].message[:90]))


# ---- Blueprint audit log
audit0 = bp["auditLog"][0]


def with_audit(action, details, actor=None):
    def f(c):
        e = copy.deepcopy(audit0)
        e["id"] = "aud_01M5S3EXR0M8MZCV3K50EP45SZ"
        e["action"] = action
        e["details"] = details
        if actor:
            e["actor"] = actor
        c["auditLog"].append(e)

    return mod(bp, f)


coach = {"type": "coach"}
expect("audit sensitivity_tightened internal->confidential", with_audit("sensitivity_tightened", {"from": "internal", "to": "confidential", "turnId": "t_1"}, coach), bpv, True)
expect("audit sensitivity_tightened confidential->internal (loosening)", with_audit("sensitivity_tightened", {"from": "confidential", "to": "internal", "turnId": "t_1"}, coach), bpv, False)
expect("audit sensitivity_tightened same class", with_audit("sensitivity_tightened", {"from": "internal", "to": "internal", "turnId": "t_1"}, coach), bpv, False)
expect("audit unknown action is accepted (x-actions is documentation; forward compatible)", with_audit("bogus_action", {}), bpv, True)
expect("audit blueprint_backup_deleted with counts", with_audit("blueprint_backup_deleted", {"revisionCount": 4, "includesHistory": True}, {"type": "user"}), bpv, True)
expect("audit blueprint_backup_deleted missing includesHistory", with_audit("blueprint_backup_deleted", {"revisionCount": 4}, {"type": "user"}), bpv, False)
expect("audit confirmations_reset without counts", with_audit("confirmations_reset", {}), bpv, False)

# ---- ApprovalRecord carries the issuing tenant inside the signed bytes
arv = V("blueprint", "#/$defs/approvalRecord")
rec = {"recordId": "rec_0001abcd", "tenantId": "tnt_acme_0001", "blueprintId": bp["id"], "rev": 3,
       "contentHash": "ab" * 32, "reviewerId": "usr_reviewer", "decision": "approved", "at": NOW,
       "kid": "kid-2026-10", "signature": "A" * 86}
expect("approval record with a tenantId", rec, arv, True)
expect("approval record, rejected decision, with a tenantId", mod(rec, lambda c: c.update(decision="rejected")), arv, True)
expect("approval record without a tenantId", mod(rec, lambda c: c.pop("tenantId")), arv, False)
expect("approval record, tenantId of 7 characters", mod(rec, lambda c: c.update(tenantId="a" * 7)), arv, False)
expect("approval record, tenantId of 8 characters", mod(rec, lambda c: c.update(tenantId="a" * 8)), arv, True)
expect("approval record, tenantId of 64 characters", mod(rec, lambda c: c.update(tenantId="a" * 64)), arv, True)
expect("approval record, tenantId of 65 characters", mod(rec, lambda c: c.update(tenantId="a" * 65)), arv, False)
expect("approval record, tenantId with a space", mod(rec, lambda c: c.update(tenantId="tnt acme 0001")), arv, False)
expect("approval record, tenantId as a number", mod(rec, lambda c: c.update(tenantId=12345678)), arv, False)
syv = V("blueprint", "#/$defs/syncState")
sy = {"state": "synced", "tenantId": "tnt_acme_0001", "deviceId": "dev-1", "baseRev": 3, "lastSyncedRev": 3, "lastSyncedAt": NOW}
expect("sync state with a tenantId", sy, syv, True)
expect("sync state, local only, tenantId null", {"state": "local_only", "tenantId": None}, syv, True)
expect("sync state, local only, no tenantId", {"state": "local_only"}, syv, True)
expect("sync state, tenantId too short", mod(sy, lambda c: c.update(tenantId="a" * 7)), syv, False)
expect("sync state, tenantId with a space", mod(sy, lambda c: c.update(tenantId="tnt acme 0001")), syv, False)
expect("sync state, unknown property", mod(sy, lambda c: c.update(tid="x" * 12)), syv, False)
expect("audit details key modelKey, longest valid key", with_audit("bogus_action", {"modelKey": "a" * 64 + "/" + "b" * 128}), bpv, True)
expect("audit details key modelKey, over the length limit", with_audit("bogus_action", {"modelKey": "a" * 64 + "/" + "b" * 136}), bpv, False)

# ---- reopen marker only on drafts
expect("reopen on in_review Blueprint", mod(bp, lambda c: c.update(reopen={"via": "import", "at": NOW, "pending": ["triage"]})), bpv, False)


def draftify(c):
    c["status"] = "draft"
    c["reopen"] = {"via": "import", "at": NOW, "pending": ["triage"]}
    for k in ("approvals", "selfAttestation"):
        c.pop(k, None)


r = list(bpv.iter_errors(mod(bp, draftify)))
rows.append(("reopen on draft Blueprint (info only; other draft rules may add errors)", None, not r, r[0].message[:90] if r else ""))

# ---- tests, sensitivity, step confirmation
expect("test status passed (run result belongs in lastRunOutcome)", mod(bp, lambda c: c["tests"][0].update(status="passed")), bpv, False)
expect("test lastRunOutcome passed", mod(bp, lambda c: c["tests"][0].update(lastRunOutcome="passed", lastRunAt=NOW)), bpv, True)
expect("sensitivity secret", mod(bp, lambda c: c.update(sensitivity="secret")), bpv, False)
expect("confirmed step without confirmedBy", mod(bp, lambda c: (c["steps"][0].update(confirmationState="confirmed"), c["steps"][0].pop("confirmedBy", None), c["steps"][0].pop("confirmedAt", None))), bpv, False)
expect("proposed step carrying confirmedBy", mod(bp, lambda c: c["steps"][0].update(confirmationState="proposed", confirmedBy="usr_x", confirmedAt=NOW)), bpv, False)

# ---- whyNotCode card: a confirmed card needs the user's own words
card = {
    "whyNotCode": "A formula cannot read the supplier's free wording; the note has to explain the mismatch in plain words.",
    "citedDiagnosticFields": ["languageUnderstanding"],
    "validator": {"kind": "human_review", "description": "The clerk reads every draft."},
    "fallback": {"kind": "human_checkpoint", "description": "The clerk writes the note by hand."},
    "costPerRun": {"value": 0.01, "currency": "USD", "basis": "price_table"},
}
EV = {"source": "user_turn", "turnId": "t_1", "quote": "just describe the total in words"}


def with_card(prov, state, step_index=0):
    def f(c):
        k = copy.deepcopy(card)
        k["cardState"] = state
        if prov is not None:
            k["provenance"] = {"whyNotCode": dict({"origin": prov}, **({"evidence": EV} if prov == "coach_inferred" else {}))}
        c["steps"][step_index]["llmJustification"] = k

    return mod(bp, f)


expect("confirmed card, whyNotCode user_stated", with_card("user_stated", "confirmed"), bpv, True)
expect("confirmed card, whyNotCode coach_inferred", with_card("coach_inferred", "confirmed"), bpv, False)
expect("confirmed card, whyNotCode engine_derived", with_card("engine_derived", "confirmed"), bpv, False)
expect("confirmed card, no provenance", with_card(None, "confirmed"), bpv, False)
expect("proposed card, whyNotCode coach_inferred", with_card("coach_inferred", "proposed"), bpv, True)
expect("proposed card, no provenance", with_card(None, "proposed"), bpv, True)

# ---- approved / built / deployed Blueprints need every step confirmed and a confirmed card on model steps
model_steps = [i for i, s in enumerate(bp["steps"]) if (s.get("recommendation") or {}).get("rungId") in ("llm_node", "llm_agent")]
if model_steps:
    i = model_steps[0]

    def approved(extra=None):
        def f(c):
            c["status"] = "approved"
            if extra:
                extra(c)

        return mod(bp, f)

    expect("approved Blueprint as published in the example", approved(), bpv, True)
    expect("approved, model step has no card", approved(lambda c: c["steps"][i].pop("llmJustification", None)), bpv, False)
    expect("approved, model step card still proposed", approved(lambda c: c["steps"][i]["llmJustification"].update(cardState="proposed")), bpv, False)
    expect("approved, a step still proposed", approved(lambda c: (c["steps"][i].update(confirmationState="proposed"), c["steps"][i].pop("confirmedBy", None), c["steps"][i].pop("confirmedAt", None))), bpv, False)
    expect("in_review, model step has no card (allowed before approval)", mod(bp, lambda c: c["steps"][i].pop("llmJustification", None)), bpv, True)
    # the attractor check is required before approval, not while the interview is still running
    attr_steps = [j for j, s in enumerate(bp["steps"]) if "attractorCheck" in s["diagnostic"]]
    if attr_steps:
        j = attr_steps[0]
        expect("approved, step that triggers the attractor check lacks it", approved(lambda c: c["steps"][j]["diagnostic"].pop("attractorCheck")), bpv, False)
        expect("in_review, same step lacks the attractor check (allowed mid-interview)", mod(bp, lambda c: c["steps"][j]["diagnostic"].pop("attractorCheck")), bpv, True)
else:
    rows.append(("example Blueprint has no model step; approved-card cases skipped", None, True, ""))

# ---- policy
P = policy_examples()[0]


def setting(key, val):
    return mod(P, lambda c: c["settings"].update({key: val}))


expect("policy: aiMode locked full", setting("coach.aiMode", {"state": "locked", "value": "full"}), polv, True)
expect("policy: aiMode locked bogus", setting("coach.aiMode", {"state": "locked", "value": "bogus"}), polv, False)
expect("policy: aiMode locked without value", setting("coach.aiMode", {"state": "locked"}), polv, False)
expect("policy: aiMode user_choice with value", setting("coach.aiMode", {"state": "user_choice", "value": "full"}), polv, False)
expect("policy: breakGlass timeBoxHours default 4", setting("governance.breakGlass.timeBoxHours", {"state": "locked", "value": 4}), polv, True)
expect("policy: breakGlass timeBoxHours 5", setting("governance.breakGlass.timeBoxHours", {"state": "locked", "value": 5}), polv, False)
expect("policy: breakGlass timeBoxHours 0", setting("governance.breakGlass.timeBoxHours", {"state": "locked", "value": 0}), polv, False)
expect("policy: requiredBefore valid gates", setting("governance.approval.requiredBefore", {"state": "locked", "value": ["handoff_brief", "automate_flow_draft"]}), polv, True)
expect("policy: requiredBefore bogus gate", setting("governance.approval.requiredBefore", {"state": "locked", "value": ["sensitivity_class"]}), polv, False)
expect("policy: schemaVersion as string", mod(P, lambda c: c.update(schemaVersion="1")), polv, False)
expect("policy: managed enabled locked false", setting("connections.managed.enabled", {"state": "locked", "value": False}), polv, True)
expect("policy: unknown setting key is ignored by design (clients ignore unknown keys)", setting("identity.sso.enabled", {"state": "locked", "value": True}), polv, True)

# ---- connection
C = dict(connection_examples())
loc, byo = C["local (Ollama)"], C["byok_openrouter"]
expect("conn: local over loopback http", loc, conv, True)
expect("conn: local to non-loopback http", mod(loc, lambda c: c.update(endpoint="http://example.com:11434/v1")), conv, False)
expect("conn: byok_openrouter over http", mod(byo, lambda c: c.update(endpoint="http://openrouter.ai/api/v1")), conv, False)
expect("conn: bad type", mod(byo, lambda c: c.update(type="bogus")), conv, False)
expect("conn: byok_openrouter with ollama serverKind", mod(byo, lambda c: c.update(serverKind="ollama")), conv, False)
expect("conn: id with spaces", mod(byo, lambda c: c.update(id="My Conn")), conv, False)

# ---- CapabilityReport (model-certification.md 2.4)
capv = V("capability-report")
cap = next(o for _, o in json_blocks("model-certification.md") if isinstance(o, dict) and "probeVersion" in o)


def cap_with(label=None, mode=None, eligibility=None, **top):
    def f(c):
        c["label"].update(label or {})
        if mode:
            c["mode"] = mode
        c["eligibility"].update(eligibility or {})
        c.update(top)

    return mod(cap, f)


H = "sha256:" + "ab" * 32
expect("cap: the example in model-certification.md", cap, capv, True)
expect("cap: experimental, no source, not yet evaluated (S1 default)", cap_with(label={"value": "experimental", "source": "none", "reason": "not_yet_evaluated", "registryVersion": None, "testedAt": None}), capv, True)
expect("cap: not_yet_evaluated on a works label", cap_with(label={"reason": "not_yet_evaluated"}), capv, False)
expect("cap: source none but reason null", cap_with(label={"value": "experimental", "source": "none", "reason": None}), capv, False)
expect("cap: uncertified with source none (uncertified means evaluated)", cap_with(label={"value": "uncertified", "source": "none"}), capv, False)
expect("cap: uncertified from the registry, lite mode", cap_with(label={"value": "uncertified"}, mode="lite"), capv, True)
expect("cap: guided mode on an uncertified label", cap_with(label={"value": "uncertified"}, mode="guided"), capv, False)
expect("cap: low fingerprint confidence on a works label", cap_with(label={"fingerprintConfidence": "low"}), capv, False)
expect("cap: low fingerprint confidence on an experimental label", cap_with(label={"fingerprintConfidence": "low", "value": "experimental"}), capv, True)
expect("cap: degraded compatibility layer on a certified label", cap_with(label={"capReason": "degraded_compatibility", "value": "certified"}), capv, False)
expect("cap: degraded compatibility layer on a works label", cap_with(label={"capReason": "degraded_compatibility"}), capv, True)
expect("cap: guided mode without full eligibility", cap_with(eligibility={"full": False}), capv, False)
expect("cap: lite mode without lite eligibility", cap_with(mode="lite", eligibility={"lite": False}), capv, False)
expect("cap: wizard mode, nothing eligible", cap_with(mode="wizard", eligibility={"full": False, "lite": False}), capv, True)
expect("cap: P6 not run but a source is named", mod(cap, lambda c: c["adversarial"].update(p6="not_run", source="local_run")), capv, False)
expect("cap: P6 not run, source none", mod(cap, lambda c: c["adversarial"].update(p6="not_run", source="none")), capv, True)
expect("cap: P6 graded A with source none", mod(cap, lambda c: c["adversarial"].update(source="none")), capv, False)
expect("cap: grade D", mod(cap, lambda c: c["results"][0].update(grade="D")), capv, False)
expect("cap: probe P7", mod(cap, lambda c: c["results"][0].update(probe="P7")), capv, False)
expect("cap: latency tier Medium", mod(cap, lambda c: c["latency"].update(tier="Medium")), capv, False)
expect("cap: structuredOutput yaml", mod(cap, lambda c: c["features"].update(structuredOutput="yaml")), capv, False)
expect("cap: hosted model with no digest or quantization", mod(cap, lambda c: c.update(modelDigest=None, quantization=None, serverVersion=None)), capv, True)
expect("cap: digest without the sha256: prefix", mod(cap, lambda c: c.update(modelDigest="ab" * 32)), capv, False)
expect("cap: unknown top-level key (reports hold no user content)", mod(cap, lambda c: c.update(transcriptSample="hello")), capv, False)
expect("cap: contextProbe not a server kind", mod(cap, lambda c: c.update(contextProbe="ollama2")), capv, False)
expect("cap: missing quirks", mod(cap, lambda c: c.pop("quirks")), capv, False)

# ---- SessionState (coach-spec.md 8.1)
sesv = V("coach-session")
sess = next(o for _, o in json_blocks("coach-spec.md") if isinstance(o, dict) and "sessionId" in o)
STEP = sess["askedQuestions"][0]["subjectId"]
expect("session: the example in coach-spec.md", sess, sesv, True)
expect("session: no open question", mod(sess, lambda c: c.pop("openQuestion")), sesv, True)
expect("session: wizard-only session has no lastModel", mod(sess, lambda c: (c.pop("lastModel"), c.update(mode="wizard"))), sesv, True)
expect("session: outcome maybe", mod(sess, lambda c: c["askedQuestions"][0].update(outcome="maybe")), sesv, False)
expect("session: outcome skipped", mod(sess, lambda c: c["askedQuestions"][0].update(outcome="skipped")), sesv, True)
expect("session: stage deploy (the stage is deploy_monitor)", mod(sess, lambda c: c.update(stage="deploy")), sesv, False)
expect("session: subjectId that is no entity id", mod(sess, lambda c: c["askedQuestions"][0].update(subjectId="<stepId>")), sesv, False)
expect("session: questionId from an unknown family", mod(sess, lambda c: c["askedQuestions"][0].update(questionId="Q-XYZ-01")), sesv, False)
expect("session: questionId with a letter suffix", mod(sess, lambda c: c["askedQuestions"][0].update(questionId="Q-CLS-02a")), sesv, True)
expect("session: sessionId without the ses_ prefix", mod(sess, lambda c: c.update(sessionId="01M5S4N2Q8T6W0XJ9D4F7H3B5A")), sesv, False)
expect("session: mode rescue (rescue is a flow on top of guided or lite)", mod(sess, lambda c: c.update(mode="rescue")), sesv, False)
expect("session: locale pt-BR", mod(sess, lambda c: c["prefs"].update(locale="pt-BR")), sesv, True)
expect("session: locale with underscore", mod(sess, lambda c: c["prefs"].update(locale="en_US")), sesv, False)
expect("session: transcript does not belong in SessionState", mod(sess, lambda c: c.update(transcript=[])), sesv, False)
expect("session: pending approval for a real gate", mod(sess, lambda c: c["pendingApprovals"].append({"gate": "automate_apply", "subjectId": STEP, "requestedAt": NOW})), sesv, True)
expect("session: pending approval for an unknown gate", mod(sess, lambda c: c["pendingApprovals"].append({"gate": "sensitivity_class", "subjectId": STEP, "requestedAt": NOW})), sesv, False)
expect("session: lastModel label offered as a number", mod(sess, lambda c: c["lastModel"].update(label=3)), sesv, False)

# ---- LiteExtract (coach-spec.md section 9)
lev = V("coach-session", "#/$defs/liteExtract")
lites = [o for _, o in json_blocks("coach-spec.md") if isinstance(o, dict) and "questionId" in o]
ans = next(o for o in lites if "value" in o)
stp = next(o for o in lites if "steps" in o)
exc = next(o for o in lites if "exceptions" in o)
expect("lite: answered number, from the doc", ans, lev, True)
expect("lite: step list, from the doc", stp, lev, True)
expect("lite: exception list, from the doc", exc, lev, True)
expect("lite: answered with a null value", mod(ans, lambda c: c.update(value=None)), lev, False)
expect("lite: answered with an empty-string value", mod(ans, lambda c: c.update(value="")), lev, False)
expect("lite: answered without a quote", mod(ans, lambda c: c.pop("quote")), lev, False)
expect("lite: answered with a follow-up question", mod(ans, lambda c: c.update(followUp="Which one?")), lev, False)
expect("lite: ambiguous with a follow-up", {"questionId": "Q-CLS-04", "status": "ambiguous", "value": None, "quote": None, "followUp": "Is that per run or per day?"}, lev, True)
expect("lite: ambiguous with no follow-up", {"questionId": "Q-CLS-04", "status": "ambiguous", "followUp": None}, lev, False)
expect("lite: declined but carries a value", {"questionId": "Q-CLS-04", "status": "declined", "value": 5, "quote": None, "followUp": None}, lev, False)
expect("lite: off_topic with nothing extracted", {"questionId": "Q-CLS-04", "status": "off_topic", "value": None, "quote": None, "followUp": None}, lev, True)
expect("lite: a numeric confidence (there is none by design)", mod(ans, lambda c: c.update(confidence=0.9)), lev, False)
expect("lite: status not in the list", mod(ans, lambda c: c.update(status="probably")), lev, False)
expect("lite: step list, answered with no steps", mod(stp, lambda c: c.update(steps=[])), lev, False)
expect("lite: step without a quote", mod(stp, lambda c: c["steps"][0].pop("quote")), lev, False)
expect("lite: step list, declined but lists steps", mod(stp, lambda c: c.update(status="declined", followUp=None)), lev, False)
expect("lite: step list, declined and empty", mod(stp, lambda c: c.update(status="declined", steps=[], followUp=None)), lev, True)
expect("lite: step list, answered but also asks a follow-up", mod(stp, lambda c: c.update(followUp="Anything else?")), lev, False)
expect("lite: step list, ambiguous with a follow-up", mod(stp, lambda c: c.update(status="ambiguous", steps=[], followUp="Which system do you mean?")), lev, True)
expect("lite: step list, ambiguous with no follow-up", mod(stp, lambda c: c.update(status="ambiguous", steps=[], followUp=None)), lev, False)
expect("lite: exception list, answered but also asks a follow-up", mod(exc, lambda c: c.update(followUp="Anything else?")), lev, False)
expect("lite: exception with null handling", mod(exc, lambda c: c["exceptions"][0].update(handling=None)), lev, True)
expect("lite: exception without a description", mod(exc, lambda c: c["exceptions"][0].pop("description")), lev, False)
expect("lite: one object carrying both a value and steps", mod(stp, lambda c: c.update(value=3)), lev, False)

bad = 0
for n, w, g, m in rows:
    ok = w is None or w == g
    bad += not ok
    want = "info" if w is None else ("valid" if w else "invalid")
    print(("ok       " if ok else "MISMATCH ") + f"{n}: expected {want}, got {'valid' if g else 'invalid'}" + (f"  [{m}]" if m and not ok else ""))
print(f"\nmismatches: {bad} of {len(rows)}")
print("RESULT:", "PASS" if bad == 0 else "FAIL")
sys.exit(1 if bad else 0)
