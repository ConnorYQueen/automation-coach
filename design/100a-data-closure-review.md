# 100a Data closure review (second round, data and contract consistency)

Reviewer: independent, fresh context; I wrote and patched none of the files. Date: 2026-10-25.
Source of truth: `design/00-shared-contract.md` (contract v2). First round: `design/99a-data-contract-review.md` (F-01 to F-52, owner decisions D1 to D8).
No existing file was edited. This is the only file written. Nothing was installed or downloaded.

## 0. Verdict

| Result | Count | Findings |
|---|---|---|
| Closed | 47 | all others |
| Partially closed | 4 | F-04, F-13, F-14, F-46 |
| Open | 1 | F-07 |
| Regressed | 0 | none |

New defects introduced or exposed by the patch round: 12 (1 High, 4 Medium, 7 Low), section 8.

All embedded examples validate (section 2). Policy keys agree both ways (93 and 93). Every tool call built with maximal valid arguments produced a valid Blueprint except one length overflow (NEW-5). The pattern library's 41 fixtures are consistent with the engine rules and the ladder order; the only fixture problem is under-assertion (NEW-12).

The single most serious problem is new: the `contentHash` that approval and the AutoMate handoff gate bind to still covers values that change after approval (NEW-1).

## 1. Method and the validator caveat

`jsonschema` is not installed and I did not install it. I wrote my own JSON Schema 2020-12 validator (`mv.py`, in the scratchpad) and attached controls so its verdicts can be trusted:

- It implements: type, enum, const, pattern, numeric and length bounds, items, properties, patternProperties, additionalProperties, unevaluatedProperties, required, propertyNames, dependentRequired, contains, uniqueItems, allOf, anyOf, oneOf, not, if/then/else, `$ref` and `$defs` (with sibling keywords), and the formats date, date-time and uri.
- Validator self-test: 50 cases, 0 failures (each keyword has a passing and a failing instance).
- Meta-validation of schemas: my own structural check (unknown keyword, bad type, bad pattern regex, unresolved `$ref`, enum value that violates its type, minimum greater than maximum). 7 negative controls, 0 failures. It is not the official Draft 2020-12 metaschema, which is not available offline; a CI run with the real `jsonschema` is still advised (99a section 10 item 1).
- Every example check below includes negative controls (a deliberately broken instance that must be rejected).

Scripts (read-only against the project) live in the session scratchpad directory `rev100a`:
`C:\Users\Autom\AppData\Local\Temp\claude\C--Users-Autom-AppData-Local-Claude-Data-claude-pzs8sxrjxfjjc-scratch-workspaces-d309879a-4de6-467e-8e59-ff7b210e65a1-557653da-9b77-4d47-82d3-cc73af62112c-scratch-2026-10-25-089e3c\a11be073-c407-4a6d-ba66-ef5202e1339d\scratchpad\rev100a\`
(`mv.py`, `selftest.py`, `meta.py`, `examples.py`, `conn.py`, `roundtrip.py`, `patterns.py`, `keyaudit.py`, `unref.py`, `refkeys.py`, `defs_diff.py`, `toolsum.py`, `targets.py`; the helper `drift_check.py` is in the parent scratchpad directory). Run as `python -I <script> <project_root>`.

## 2. Mechanical checks

| Check | Result |
|---|---|
| Parse all JSON | 5 of 5 parse: `blueprint.schema.json`, `policy.schema.json`, `connection.schema.json`, `coach-tools.json`, `tool-catalog.seed.json` |
| Meta-validation | blueprint 0 problems, policy 0 problems, connection 0 problems |
| `$ref` resolution | blueprint 209 refs (72 distinct), policy 169 (42), connection 12 (11); 0 unresolved |
| Example Blueprint (`rules-engine.md` section 19, block at L2738) | 0 errors; also 0 errors with `status` set to `approved`; 9 negative controls rejected (bad status, extra root property, bad rung, missing `createdAt`, `schemaVersion` 2.0, bad `kind`, step without `createdBy`, hyphenated `toolId`, 14-character override reason) |
| Example policy bundles (`settings-catalog.md` blocks at L290 and L1075) | 0 errors each; negative controls rejected: `user_choice` with a value, `locked` without a value, `coach.aiMode` = bogus, missing `schemaVersion`, junk signature, `coach.override.mode` = disabled |
| Connection examples (`settings-catalog.md` section 9.3) | 5 of 5 valid (managed, byok_openrouter, byok_provider, custom_openai_compat for Azure, local for Ollama) against `connection.schema.json` |
| Tool catalog seed (29 entries) against `$defs/toolCatalogEntry` | 0 errors; negative controls rejected: `dataFlow` = mars, `skillLevel` = beginner, `toolId` = x.y.z |
| Seed internal references | every `hostToolIds` entry resolves (0 dangling) |
| Tool write targets | the 158 Blueprint paths that `coach-tools.json` names as write targets (for example `steps[].diagnostic.attractorCheck`) all resolve in the Blueprint schema (`targets.py`; its negative controls reject unknown paths) |
| Pattern-library fixtures (41 blocks) | 41 parse, no duplicate ids, 0 schema errors in their `diagnosticDelta` and `systems`, every `expect.toolId` exists in the seed on the stated rung; 10 card sketches use valid `validator.kind` and `fallback.kind` values and 10 to 300 character descriptions |

One negative control is deliberately not rejected: an unknown non-`x-` setting key in a policy bundle is accepted. That is the intended F-08 behaviour (`$defs/unknownSetting`), not a validator weakness.

### 2.1 Shared enums and patterns, compared textually

| Item | Result |
|---|---|
| `toolId` pattern (`^[a-z][a-z0-9_]*\.[a-z0-9][a-z0-9_]*$`, max 80) | identical in Blueprint, policy, contract L32 and the `coach-tools.json` copies |
| `orgToolId` (`^org\.[a-z0-9][a-z0-9_]{0,59}$`) | identical in Blueprint and policy |
| `slug` (`^[a-z][a-z0-9_-]{1,62}$`) | identical in Blueprint and policy |
| `connectionId` (`^[a-z0-9][a-z0-9_-]{0,63}$`) | identical in Blueprint, policy and connection schema |
| `operationTag` (36 values), `skillLevel`, `rungId`, `certification`, `role` | identical enums |
| `modelKey` | policy and connection identical (pattern, maxLength 200); the Blueprint copy differs (pattern looser, maxLength 160). See F-13 |
| Probes from 99a: `org.acme-erp`, `org.acme.erp` | rejected by both `toolId` patterns; `org.1password`, `org.acme_erp` accepted by both |
| Probes from 99a: `corp_default`, `sap_prod` | accepted by both slug patterns; `corp.default`, `2024-profile`, a one-character id rejected by both |

`drift_check.py` reports 15 enum flags. I judged each; all are legitimate subsets or supersets, none is drift:

- 2 flags: `diagnostic.dataSensitivity` (and the tool copy) add `unknown` to the sensitivity classes, on purpose.
- 1 flag: `governance.intake.gateStage` allows only the three stages an intake gate can sit at.
- 5 flags: connection-type `if` conditions in `connection.schema.json` and `policy.schema.json` `orgConnection` (an org connection cannot be `local` or `managed`; conditional branches name one type each).
- 4 flags: `serverKind` subsets inside per-type `then` branches.
- 2 flags: `export_blueprint.kind` and `fileFormat` lack `automate_flow_draft` and `automate_draft`, which only `apply_automate_draft` writes.
- 1 flag: the Blueprint `status` condition names only the statuses it needs.

## 3. Status of F-01 to F-52

Evidence cites file and JSON path or line. "bp" is `blueprint.schema.json`, "po" is `policy.schema.json`, "ct" is `coach-tools.json`, "re" is `rules-engine.md`.

| ID | Status | Evidence |
|---|---|---|
| F-01 | Closed | bp `$defs/rungId` (description L427) and po `$defs/rungId` both equal the 9-value ladder with `human_checkpoint` before `llm_agent`. ct rung enums at `/tools/2` (search_catalog), `/tools/10` (add_steps asBuilt), `/tools/11` (update_step asBuilt) and `/tools/18` (record_override chosenRungId) are identical. Contract L27, re C1 L13 and L372 state the same order. No file lists the pair reversed (text search). Owner deviation (human before agent) applied everywhere; see D1 |
| F-02 | Closed | bp `$defs/engineEnvironment/properties/policy/properties/llmAgentMode` (L4522) enum allowed_with_justification, approval_required, forbidden. re section 3.2 row `policy.llmAgentMode` (L236) maps `coach.llmAgent.mode` and says `forbidden` removes the rung. No `disabled` left in bp or re |
| F-03 | Closed | bp `engineEnvironment.sensitivityRules.*.llmContentMode` (L4375, L4415, L4455, L4495) enum full, redacted, none, with `none` described as making llm_node and llm_agent unavailable. po `$defs/sensitivityClassRule.llmContentMode` (L4819) has the same three values |
| F-04 | Partially closed | Scale unified to none, basic, intermediate, advanced: bp and po `$defs/skillLevel`, po `prefs.skillLevel`, ct `record_environment_facts.builderSkill` (`/tools/17`), all 29 seed entries, contract L33; `prefs.skillLevel` default `basic` (settings-catalog L176). Gap: the agreed rule was that an unset `builderSkill` defaults to `prefs.skillLevel`. re L187 and L804 still say the default is `intermediate`, and bp `stepEnvironment.builderSkill` carries no default or description. A new user (pref basic) with an unset step is evaluated as intermediate by `T-SKILL` (re L424). Fix: say in re L187 and L804 and in the bp description that an unset `builderSkill` takes `prefs.skillLevel`, and make the fixtures set it explicitly |
| F-05 | Closed | model-certification.md section 2.4 L104 `"value": "works"`; po `$defs/certification` lowercase; ct `x-minLabel` lowercase. No capitalised label remains |
| F-06 | Closed (D3 A) | bp `diagnostic.interfaceAvailability` enum unchanged (api_available, file_exchange, ui_only, unknown); the `paper_or_phone` exemption stays in re C6 L18 |
| F-07 | Open | re section 11.1 (L611 to L626) still lists only yes, no (and the partly and mostly sets) and has no note that `unknown` counts as missing and yields `needs_info`. bp `$defs/triageAnswers` (7 properties) and ct `record_triage_answers` all allow `unknown`. Only the diagnostic path is covered (re V-MISSING L112). Fix: add the sentence to 11.1 and add `unknown` to the table |
| F-08 | Closed | po `properties/settings/additionalProperties` is `$ref $defs/unknownSetting` (state required, value allowed, `stateValueRule` applied) plus a `propertyNames` pattern; contract L37 says clients ignore unknown non-`x-` keys. Confirmed by the negative control in section 2 |
| F-09 | Closed | Identical `toolId` pattern in bp `$defs/toolId` and po `$defs/toolId` (po L3445 adds the publish-time check); `orgToolId` in both; probes in section 2.1 behave identically |
| F-10 | Closed | Identical `slug` in bp and po; the 99a probes pass or fail identically in both |
| F-11 | Closed | po `orgToolEntry.properties.capabilities.items` is `$ref $defs/operationTag`; the 36-value enum equals bp's |
| F-12 | Closed | po `orgToolEntry` has the 12 extension fields of bp `toolCatalogEntry` (dataFlow, unattendedSupport, systemKinds, accessModes, connectionTypes, language, hostToolIds, locatorKinds, requiresTrainingData, maxInputVariability, limits, handoff) plus description; defaults stated in re section 3.4 hard-cap paragraph (L275) and re section 17.2 item 9 (L2718): `dataFlow` absent is `vendor_cloud`, `unattendedSupport` absent is `no` |
| F-13 | Partially closed | The convention is adopted: contract L35; po `$defs/modelKey` and connection `$defs/modelKey` are identical (pattern, maxLength 200); `models.allowlist` text names the namespaces. Gap: bp `$defs/modelKey` (L400, used by `auditDetails.modelId`, L3652) is a different, looser pattern with maxLength 160, while a legal key can be 64 + 1 + 128 = 193 characters. A long local or custom key passes policy and fails when written to the audit log. Fix: copy the po pattern and maxLength 200 into bp |
| F-14 | Partially closed | 30 of the 68 id-like tool parameters carry the Blueprint patterns (`stp_`, `exc_`, `tst_` ULID patterns, toolId, slug, connection id). The other 38 are enums (rungId), host-issued ids with length limits (turnId, docId, requestId, templateId, flowRef) or free strings. One real gap remains: `search_catalog.toolId` (`/tools/2`) has maxLength 80 and no pattern. Fix: add the `toolId` pattern there |
| F-15 | Closed | `builtin.spreadsheet_formulas` appears nowhere; po toolId description (L3445) states the publish-time membership check for `providesToolIds`, `permittedToolIds`, `forbiddenToolIds`; all seed `hostToolIds` resolve. `ocr.tesseract_local` is still named only in the seed (it is reachable by capability match; 99a asked only to confirm intent) |
| F-16 | Closed | bp root `deployPlan` -> `$defs/deployPlan` (backupOwner, failureSignals[], manualFallback, changeTriggers[], reviewAfterDays, createdBy, confirmationState, confirmedBy, confirmedAt; required createdBy, confirmationState). ct `record_deploy_plan` parameters map one to one; round trip valid |
| F-17 | Closed | bp `step`, `exception`, `test`, `deployPlan` all carry createdBy, confirmationState, confirmedBy, confirmedAt; step, exception and test also carry `provenance` (Evidence). `createdBy` and `confirmationState` are required on all four. Negative control: a step without `createdBy` is rejected. Round trip of `add_steps` with host-written fields valid |
| F-18 | Closed | bp `test` has exampleData (max 400), lastRunId, lastRunDetail (max 500), then, status, lastRunAt. ct `generate_test_cases_from_exceptions` with a maximal call (40 plus 25 cases) produced 67 valid tests |
| F-19 | Closed | bp `processInfo.provenance` (property names limited to the 6 process fields) and `triageBlock.provenance` (the 7 answers), values `$ref $defs/provenance` |
| F-20 | Closed | bp `$defs/provenance` = `{origin: user_stated, coach_inferred, engine_derived; evidence?}`; `diagnostic.provenance` covers 22 fields; re section 2.1 (L98) states the engine reads the value, not the provenance |
| F-21 | Closed | bp root `x-virtualFields` registers `step.derived.domains[]`; po rule-condition path description (L4383) states the publish-time path check against the Blueprint field registry and `x-virtualFields` |
| F-22 | Closed | bp `triageBlock` properties verdict, rationale, conditions, warnings, ruleTrace and engine carry `x-derived`; answers, overrideDecisionId and provenance do not; `recommendation` and `roiEstimate` are marked at definition level. Residual: root `engine` is unmarked (NEW-10) |
| F-23 | Closed | bp `$defs/asBuilt` exists; root `x-actions` registers 45 audit actions; a scan of every snake_case action-like token in ct finds no unregistered action (the 3 hits are error codes). Caveat: no self-attestation action (NEW-2) |
| F-24 | Closed | bp `$defs/auditDetails` registers callId, connectionId, modelId, tool, entityIds, evidenceRef (plus via, approvedVia, requestId); `auditEntry.actor.type` includes `server` |
| F-25 | Closed | ct `record_diagnostic_answers.answers` has 21 properties: the 12 contract fields plus operations, humanAuthority, necessity, requiredByControl, residualHandling, inputVariability, pathPredictability, inputSize, training; `attractorCheck` is a sibling parameter (ct L3196) and the host rule at L3342 requires it for the three conditions. Maximal round trip valid |
| F-26 | Closed | ct `record_environment_facts.systems[]` (maxItems 8) items carry name, kind, role, accessModes, accessEvidence, uiLocator, authModel, profileSystemId, the same 8 keys as bp `$defs/stepSystem`; host forces `accessEvidence` = claimed (re L2661). Round trip with 8 systems and 20 tools valid |
| F-27 | Closed | ct `record_override` required = stepId, chosenRungId, reason, evidence; `chosenToolId` required unless the rung is `eliminate` (description plus host rule, since the flat tool schema cannot express it); bp `decisionOverride` allOf requires it; re OV-1 (L702) |
| F-28 | Closed (D4 A) | bp `override.reason` and `decisionOverride.reason` minLength 15; po `coach.override.reasonMinChars` minimum 15; tool floor stays 1 with host rule `record_override.13` (`reason_too_short`, max of 15 and policy). Residual: policy maximum 500 exceeds the reason maximum 400 (NEW-6) |
| F-29 | Closed | bp `exportRecord` has `kind` (5 values) and `fileFormat`; po `exportKind` enum has the same 5 kinds and `data.exports.allowedKinds.items` is `$ref exportKind`; ct `export_blueprint` has `kind` and `fileFormat`, with the old-value migration in its description |
| F-30 | Closed | bp `exportRecord` requires scope and sensitivityAtExport and has `stepIds` (allOf: scope steps requires stepIds) |
| F-31 | Closed | ct `generate_llm_justification_card` required = stepId, whyNotCode, validator, fallback, evidence; `citedDiagnosticFields` optional, merged with the engine's pre-fill, engine wins (re CARD-2 L730, L2664) |
| F-32 | Closed | bp root `etag` description: client-local, base64url SHA-256 of the canonical Blueprint without etag and sync, "not used for sync"; architecture L663 `If-Match: <rev>` |
| F-33 | Closed | bp `syncState` uses `baseRev` and `lastSyncedRev`, with the description "rev exists only here and in the sync envelope; version is the client edit counter"; architecture L669 to L671 |
| F-34 | Closed | Hash registry exists in three agreeing places: bp root `x-hashes`, architecture L674 to L680, contract Hashes bullet; `contentHash` excludes auditLog, status, updatedAt, version, sync and etag as asked. The exclusion list itself is too narrow for approval binding (NEW-1) |
| F-35 | Closed | bp `$defs/approvalRecord` (recordId, blueprintId, rev, contentHash, reviewerId, decision, at, kid, signature; all required); `auditEntry` allOf makes `approval_recorded` carry it in `details`; `actor.type` has `server`; architecture L695 gate |
| F-36 | Closed | bp `schemaVersion` pattern `^1\.[0-9]+$`; contract L37 (readers preserve unknown properties, writers emit schema properties only) |
| F-37 | Closed | Contract L37: Blueprint string "1.x", Policy required integer const 1 (po L17 description), tool schema semver (model-certification `toolSchemaVersion` 0.2.0) |
| F-38 | Closed | Contract L38 and settings-catalog L43: round half up of USD x 1,000,000, evaluated at reserve |
| F-39 | Closed | architecture L649 `membership.role (admin, coe_reviewer, builder, viewer)`; po `$defs/role` identical |
| F-40 | Closed (D6 A) | po `$defs/sensitivityClassRule.toolDataFlowCeiling` optional enum local, tenant, vendor_cloud, ai_cloud; bp projection requires it and the description says the projection fills the re section 3.4 defaults; re section 3.4 adds a hard cap (restricted never above tenant) |
| F-41 | Closed (D2, owner variant) | po settings key `coach.aiMode` (off, lite_only, full; Team minimum; enforced at both), `$defs/aiFlowsByMode`; coach-spec section 3.1 (L163 to L187) selects `wizard` first when off; ct `x-aiModes`. Residual: architecture gateway key list omits it (NEW-3) |
| F-42 | Closed | po root `required` includes `schemaVersion`; type integer, const 1 |
| F-43 | Closed | Contract L41 now reads `{state, value?}`; po `stateValueRule`; both negative controls pass (section 2) |
| F-44 | Closed (D7 A) | po `environmentProfile` description: first matching profile in array order, none matches gives `environment.defaultProfileId`; `groupIds` description repeats the tiebreak; tiers L19 (per-group budgets) and L364 (group-scoped policy and `scope`) defer the rest. No `scope` field was reserved (recommendation only) |
| F-45 | Closed | Contract item 7, tiers L206 and po `signature` description all say ES256 (64-byte signature, 86 base64url characters) unless Ed25519 support is verified; the pattern tail is 86 characters |
| F-46 | Partially closed | Catalog and schema agree on 93 keys (section 6) and every `coach-tools.json` key reference exists. But 42 policy keys are still referenced by no file other than the catalog and the schema (list in section 6), and the engine projection table (re section 3.2, L227 to L239) and bp L4627 still use `environmentProfile.*` and `policy.environmentProfile` instead of the key names `environment.profiles`, `environment.defaultProfileId`. Fix: name a consumer for each of the 42 and use the real key names in the projection table |
| F-47 | Closed | `connection.schema.json` exists (14 properties, 6 required, per-type allOf rules, 13 server kinds); po `$defs/orgConnection` is the same shape without `credentialRef`; contract Connection bullet; 5 catalog examples validate |
| F-48 | Closed | Single CapabilityReport definition at model-certification section 2.4 (L83 to L106), keyed by connectionId, modelKey, probeVersion, endpointHash (L81); no `capabilityProfile` on the Connection; contract CapabilityReport bullet. Note: it is prose plus an example, not a JSON Schema (Low) |
| F-49 | Closed (D5 A) | Contract L13 glossary sentence: `byok_openrouter` is the customer's own OpenRouter key and unrelated to OpenRouter's "BYOK" product |
| F-50 | Closed | `connectionId` pattern in the connection schema; `policyRef` is an `orgConnection.id` or null; po `orgConnection.id` is `connectionId` and not the constant `managed` |
| F-51 | Closed (D8, owner variant) | tiers.md section 2 (L73 to L110) gives CoE Reviewer AutoMate draft and apply as Y; ct `x-roleMatrix` and the `x-roles` of all 27 tools allow admin, coe_reviewer, builder; coach-spec L452 and L868 state it; no stale "read-only reviewer" wording remains except the quoted history in tiers L123 |
| F-52 | Closed | tiers L117 "Viewer cannot export (finding F-52)" and a Viewer column of "-" for every Coach and export row; no ct tool lists viewer; the 99a "Viewer may export review_packet" assumption is gone |

## 4. Owner decisions D1 to D8

| ID | Resolution found | Note |
|---|---|---|
| D1 | Option B (human_checkpoint before llm_agent), not the reviewer's option A | Applied in contract L27, re C1 L13 (states it reverses draft 0.1), re L372, bp and po `rungId`, ct enums. The engine side was re-derived: `RA-OPEN` is evaluated only after the human rung found nothing (re L395), `RH-AUTH` clause (d) opens the human rung for open-ended work unless volume exceeds `humanMaxItemsPerRun`. Fixtures PF-11a and PF-11b follow it (section 7) |
| D2 | A single three-valued key `coach.aiMode` (off, lite_only, full) instead of a boolean | Owner-approved deviation. Present in po, settings-catalog L120, coach-spec section 3.1, ct `x-aiModes`. Gateway enforcement is described in the po text but not in architecture L867 (NEW-3) |
| D3 | A: no enum change, `paper_or_phone` exemption kept | F-06 |
| D4 | A: policy minimum 15, tool floor 1 | F-28; max mismatch NEW-6 |
| D5 | A: name kept, glossary line added | Contract L13 |
| D6 | A: optional per-class `toolDataFlowCeiling` | F-40 |
| D7 | A: single org bundle, first matching profile, groups deferred | F-44; no reserved `scope` field |
| D8 | A with an owner extension: CoE Reviewer is Builder plus review, including AutoMate draft and apply; Admin cannot approve | tiers section 2 and its change list; ct role matrix matches; the approval gate (approver differs from owner) is a server rule, not a tool |

`coach.override.mode`, `coach.llmOverride.mode` and `coach.triageOverride.mode` all include `forbidden` (po enums). The tool-side wording for that is incomplete (NEW-4).

## 5. Tool round trip and role rules

Harness `roundtrip.py`: starts from the valid example Blueprint, builds a maximal valid call for each tool that writes to the Blueprint (18 of the 27 tools; the other 9 are reads, engine requests or the draft proposal), applies the documented host write (including host-forced fields such as `createdBy`, `confirmationState`, `accessEvidence` = claimed, ids, orders), then validates the resulting Blueprint. 20 cases (some tools have variants), plus a 40-combination export matrix.

| Result | Detail |
|---|---|
| Call schema validity | all 20 maximal calls are valid against their own tool schema |
| Resulting Blueprint valid | 18 of 20 |
| Failure 1: `apply_automate_draft` | The exported record gets `exports[1].targetId` of 105 characters; bp `exportRecord.targetId` allows 80, while ct `propose_automate_flow_draft.target.flowRef` and `request_attended_test_run.flowRef` allow 120. NEW-5 |
| Failure 2: `set_process_info` | My harness wrote `process.provenance.title`; the map only allows the six process fields. The tool does accept `title` and `sensitivity` but its spec does not say they are excluded from provenance. Not a schema defect, a spec gap. NEW-9 |
| Other checks | `add_steps` 25 steps valid (root `steps` maxItems 200); `update_step` edit and move valid; `remove_step` both modes valid; `record_environment_facts` 8 systems and 20 tools valid; `record_override` with a 400-character reason and 20 acknowledged ids valid, status enum active, incomplete, pending_approval, stale, revoked; `record_deploy_plan` valid and a confirmed plan without `confirmedBy` is rejected; `advance_stage` with a maximal triage override valid |
| Export matrix | `kind` x `fileFormat` x `scope` = 40 combinations. The flat tool schema accepts all 40; the Blueprint schema rejects the 8 where `blueprint_json` has a non-json format; the 10 further combinations that the `x-kindFileFormats` matrix forbids (for example `handoff_brief` as json) are rejected only by host rule `export_blueprint` (the matrix is marked ASSUMPTION). No invalid Blueprint results if the host enforces the rule |

Role rules against `tiers.md` section 2 (L73 to L110): all 27 tools carry `x-roles.allowed` = admin, coe_reviewer, builder; viewer has no tool; `export_blueprint` marks builder as own-Blueprint only, matching "Export: Y, Y, own, -"; AutoMate draft, apply and the attended test run allow all three (matrix L106 to L108). Tools are generated from the matrix rows (`x-roleMatrix.classes`), so they cannot drift independently. No tool grants approval: approving a Blueprint or an override is a CoE Reviewer action in the review queue and Admin has no approval right (tiers L113). The per-Blueprint conditions (own, edit grant, in review, break-glass for Admin) are host checks, outside the role list, and are described in coach-spec L452.

## 6. Policy key audit, both ways

- Schema to catalog: `policy.schema.json` `settings.properties` has 93 keys; `settings-catalog.md` has 93 policy rows plus 20 `tenant.*` rows (tenant settings are a separate group, not policy keys). Missing in either direction: 0. All 93 schema keys carry `x-group`, `x-minTier`, `x-enforcedAt`, `x-default` and `x-phase`.
- Tool layer: `coach-tools.json` `x-meta.policyKeysUsed` lists 20 keys; all exist in the schema; `policyKeysToVerify` is empty.
- Consumers: 42 keys have no reference in any design file other than the catalog and the schema (so no document says who reads them): `connections.byokOpenrouter.enabled`, `connections.byokProvider.enabled`, `connections.byokProvider.allowedProviders`, `connections.customOpenaiCompat.enabled`, `connections.endpointHostAllowlist`, `connections.orgConnections`, `connections.proxy`, `connections.requireTls`, `data.redaction.customPatterns`, `data.redaction.defaultAction`, `data.redaction.surfaces`, `environment.defaultProfileId`, `environment.profiles`, `environment.userMayDeclareSoftware`, `governance.approval.minReviewers`, `governance.approval.mode`, `governance.approval.requiredBefore`, `governance.approval.reviewSlaDays`, `governance.intake.enabled`, `governance.intake.gateStage`, `governance.intake.requiredFields`, `governance.orgRules`, `governance.templates.allowPersonal`, `governance.templates.required`, the 8 `prefs.*` UI keys (`coachingStyle`, `verbosity`, `skillLevel`, `showEngineTrace`, `locale.*`, `accessibility.*`, `alerts.*`), `retention.localLogs.days`, `retention.transcripts.storage`, `spend.byokEstimatedMonthlyCapUsd`, `spend.personalMonthlyCapUsd`, `sync.transcripts.enabled`. Most are client UI or portal keys and need only a one-line consumer note (F-46).
- Keys named in documents but absent from the catalog: `tenant.region` and `tenant.tier` (architecture L1079, L1096, L374). The catalog names are `tenant.dataRegion` and `org.tier` (NEW-3). The removed key `governance.approval.allowSelfApproval` appears only in removal notes (tiers L113, settings-catalog L262 and L1190), as intended.

## 7. Pattern library against the engine

41 fixtures in 11 patterns (PL-01 to PL-11; per pattern counts 6, 3, 4, 5, 4, 4, 2, 3, 3, 4, 3). I traced every fixture's chosen rung against the ladder and the rung predicates of re sections 6 to 8; there is no execution engine in the deliverable, so the trace is by hand against the written rules, and the 41 expected tool ids and rungs were mechanically cross-checked against the seed. The chosen rung is always the first ladder rung whose predicates hold, and no fixture needs a reversed `human_checkpoint` or `llm_agent` order other than as intended. Fourteen traces, chosen from the variant table (section 5.1 of the library):

| Fixture and variant | Rules that decide it | Library result | Match |
|---|---|---|---|
| PF-09a unattended, high cost, irreversible | risk table high x irreversible = D (re 7.1); `W-TIER-D-CODE` for a code rung, unattended (7.2) | script, tier D, review queue, W-TIER-D-CODE | yes |
| PF-11a base | `RH-AUTH` (d) opens the human rung for open-ended work; ladder puts it before the agent (C1) | human_checkpoint, human.manual_task, tier A | yes |
| PF-11a 120 items per run | `RH-AUTH` (d) fails above `humanMaxItemsPerRun`; `RA-OPEN` then opens the agent; `RK-C` for agent at tier A or B | llm_agent, review queue, card, W-AGENT-DISCOURAGED | yes |
| PF-11a cost of error high | tier C; `RA-RISK` rejects the agent at C or D; human rung still fits | human_checkpoint, tier C | yes |
| PF-11a must run unattended | agent fails `RA-ATT`; human tools have `unattendedSupport` no (`T-EXEC`); rung rejected with `T-COVER` (re L456) | no_fit | yes |
| PF-11b person forbidden | human tools removed by policy; agent reachable by `RA-OPEN` | llm_agent, W-ENV-DOWNGRADE | yes (D1) |
| PF-07a cost of error medium | tier C for medium x partly or irreversible; `RK-C` for llm_node | llm_node, review queue, card | yes |
| PF-07a data restricted | restricted allows connection type local only and `toolDataFlowCeiling` local (re 3.4); `T-FLOW` fails the model rungs, no downgrade (G5) | no_fit, blocked by T-FLOW | yes |
| PF-03b and PF-04c no model connection | `llm.availableConnectionTypes` empty, `T-FLOW` fails for model tools (G5: never fall to an LLM, never invent a human) | no_fit | yes |
| PF-08a 100 examples for 6 labels, and 400 with an unstable label set | `T-TRAIN` / `RP-PARSE` classify path needs enough stable labelled examples; both fail | llm_node (not parser) | yes |
| PF-05b org forbids UI automation | `ORG-no-ui` removes the rung; read cannot move to a lower rung | no_fit, blocked_by_policy | yes |
| PF-05b unattended with attended-only runners, then with an unattended runner | `T-EXEC` runner part; with a runner, `W-HOST-UNATTENDED` | no_fit, then ui.automate with warning | yes |
| PF-04e scripting switched off, and connector rung forbidden | `T-SCRIPT` removes script (api_connector precedes it anyway); `forbiddenRungIds` removes api_connector, script follows with `W-ENV-DOWNGRADE` | api_connector tier B, then script | yes |
| PF-10a JavaScript pages, PF-10b fixed layout | `RP-ACC-4`/`ui.playwright_browser` with `W-SCRAPE-TERMS`; extract path of `RP-PARSE` for `parser.regex_template` | ui_automation; parser_ocr_ml | yes |

Ladder-order check: no text in any design file lists `llm_agent` before `human_checkpoint`; the library's coverage paragraph and index list rungs in ladder order; `llm_agent` appears only in PL-11, where the deviation is exercised.

Findings from this section: 12 fixtures do not pin their recommendation (NEW-12), and the spec gaps NEW-8 and F-07. The fixtures themselves are consistent.

## 8. New defects

| ID | Severity | Where | Defect | Fix |
|---|---|---|---|---|
| NEW-1 | High | bp root `x-hashes.contentHash`; architecture L676 and L695; contract Hashes bullet | `contentHash` excludes only auditLog, status, updatedAt, version, sync and etag. It therefore still covers `exports[]`, the root `engine` (computedAt), every `recommendation.engine.computedAt` and `roiEstimate.engine` / `triage.engine` (all `x-derived`), and the run results in `tests[]` (status, lastRunAt, lastRunId, lastRunDetail). The AutoMate gate (architecture L695) recomputes the hash and compares it with the approval record. Consequences: (a) the handoff itself appends an `automate_flow_draft` `ExportRecord` after approval, so the hash no longer matches; (b) architecture L613 says derived values are dropped from a merge and recomputed under the merging device's catalog and rules versions, so two devices holding identical content get different hashes and an approval signed on one fails on the other; (c) an attended test run after approval changes `tests[]` | Define `contentHash` over content only: exclude `exports`, root `engine`, every property marked `x-derived` (recommendation, roi, triage derived properties and their engine meta), and the run-result fields of `tests[]`, in addition to the current list. Generate the exclusion list from the `x-derived` markers so it cannot drift; publish it once as machine-readable `x-hashes.contentHash.exclude` in bp and copy it into the contract and architecture L676 |
| NEW-2 | Medium | tiers L102 and L115; architecture L381; bp `x-actions`, `auditEntry` allOf | The Individual-tier advisory self-attestation (who, when, content hash, statement) has no wire shape. `x-actions` has no attestation action, `approvalRecord` requires `kid` and a server signature (so a client-made record cannot use it), and the `auditEntry` allOf covers only `approval_recorded`. The matrix also gives the row to Admin and Builder only, not to the owner role generally | Add action `self_attested` to `x-actions`; add `$defs/selfAttestation` {blueprintId, contentHash, attestedBy, at, statement max 400} required in `details` for that action; state in the contract that it never sets `approved`; align the matrix wording to "owner" |
| NEW-3 | Medium | architecture L867 (section 4.2), L374, L1079, L1096 | The "Keys the gateway reads" list omits `coach.aiMode`, although po says managed calls are refused by the gateway when the org mode is `off` (hard enforcement). Also two key names do not exist in the catalog: `tenant.region` (catalog: `tenant.dataRegion`) and `tenant.tier` (catalog: `org.tier`) | Add `coach.aiMode` to the list with the refusal behaviour (off refuses all managed calls with a policy error, no downgrade); rename `tenant.region` to `tenant.dataRegion` and `tenant.tier` to `org.tier` |
| NEW-4 | Medium | ct `record_override`, rule `record_override.12` (L3923) | For any rung other than llm_node and llm_agent the rule lists `coach.override.mode` with the values advisory and approval_required only, but the policy enum (owner-approved) also has `forbidden`. An implementer working from the tool file alone records the override instead of failing with `blocked_by_policy` | List `coach.override.mode` as advisory, approval_required, forbidden and state that `forbidden` fails with `blocked_by_policy` and stores nothing, as coach-spec L146 says |
| NEW-5 | Medium | ct `propose_automate_flow_draft.target.flowRef` and `request_attended_test_run.flowRef` (maxLength 120) against bp `exportRecord.targetId` (maxLength 80) | A valid 105-character flow reference makes `apply_automate_draft` write an invalid Blueprint (roundtrip failure 1); the save or sync is then rejected after the user already approved the apply | One length: raise `exportRecord.targetId` to 120 (or lower both flowRef limits to 80) and record it in the contract conventions |
| NEW-6 | Low | po `coach.override.reasonMinChars` (integer 15 to 500) against bp `override.reason`, `decisionOverride.reason` and ct `record_override.reason` (maxLength 400) | An admin value from 401 to 500 makes every override impossible | Set the policy maximum to 400 |
| NEW-7 | Low | re OV-2 and OV-5 and "Resulting states" (L702 to L709) against bp `decisionOverride.status` and coach-spec L146 | The engine spec lists a `rejected` override state; the Blueprint status enum has no `rejected`, and coach-spec says a `forbidden` outcome stores nothing. A reviewer's rejection of a `pending_approval` override has no stated state | Say OV-2 and `forbidden` return a failure without storing; remove `rejected` from the states list; state that a reviewer rejection sets `revoked` (or add `rejected` to the enum, the ct status list and `x-actions`) |
| NEW-8 | Low | re `T-SYS` and `T-ACCESS` (L419, L420); seed | 13 of 29 seed tools, including `human.manual_task`, `llm.cloud_model` and `parser.regex_template`, have empty `systemKinds` and `accessModes`. Read literally, "effective access modes intersect the tool's `accessModes`" fails for every one of them, contradicting the fixtures that recommend them | Add: an empty or absent list means the tool does not depend on a system kind or access mode and the predicate passes. Repeat in the bp catalog field descriptions |
| NEW-9 | Low | ct `set_process_info` (parameters `title`, `sensitivity`, valueEvidence field list); bp `processInfo.provenance` | The tool accepts `title` and `sensitivity`, but provenance names are limited to the six process fields, and the rule "writes the value with provenance" does not say title and sensitivity are exempt. A host that records provenance for every accepted field writes an invalid Blueprint | State "title and sensitivity are not recorded in process.provenance", or add them to the `propertyNames` enum |
| NEW-10 | Low | bp root `properties/engine` | The root `engine` meta (computedAt, inputsHash) is not `x-derived`, though architecture L613 says derived values are dropped from a merge and recomputed. A merge can keep a stale root `engine` | Mark root `engine` `x-derived` (and exclude it from `contentHash`, NEW-1) |
| NEW-11 | Low | po `data.exports.allowedKinds` (lists `automate_flow_draft`); ct `propose_automate_flow_draft` and `apply_automate_draft` (rule 9) | The two AutoMate tools check `automate.actions.mode` and `automate.actions.allowedKinds` only, never `data.exports.allowedKinds`, yet `apply_automate_draft` writes an `ExportRecord` of kind `automate_flow_draft`. An admin who sets `allowedKinds` to none does not stop draft exports | Add the check to `apply_automate_draft`, or drop `automate_flow_draft` from the policy enum and state that `automate.actions.mode` governs it |
| NEW-12 | Low | `pattern-library.md` section 5.2 fixtures PF-03a, PF-04a, PF-04e, PF-05b, PF-05c, PF-05d, PF-06c, PF-06d, PF-07b, PF-08c, PF-09a, PF-10c | These 12 fixtures state `outcome: recommended` and the tier, but no `rungId` or `toolId`, while the results table in section 5.1 states a tool for each. A regression in the engine could pass them | Add `expect.rungId` and `expect.toolId` to the 12 from the table (for example PF-09a: builtin_feature, builtin.excel_formulas) |

Residuals of partially closed findings (not counted again): F-04 builderSkill default, F-07 `unknown` note, F-13 Blueprint `modelKey`, F-14 `search_catalog.toolId`, F-46 consumers and projection key names.

## 9. Worst remaining problems

1. NEW-1 (High): approval is bound to a hash that changes after approval.
2. NEW-5 (Medium): a valid AutoMate flow reference longer than 80 characters makes the apply write an invalid Blueprint.
3. NEW-4 (Medium): the tool spec does not implement `coach.override.mode = forbidden`.
4. NEW-2 (Medium): Individual-tier self-attestation has no schema home or audit action.
5. NEW-3 (Medium): the gateway key list omits `coach.aiMode`, so the hard "AI off" enforcement is not in the architecture; two other key names are wrong.

Also open: F-07 (`unknown` triage answers undefined in the engine) and F-04 (`builderSkill` default conflicts with `prefs.skillLevel`).

## 10. Re-run notes

- Re-run the scripts in section 1 after any patch; `examples.py`, `roundtrip.py` and `patterns.py` are the three that catch regressions.
- Install the real `jsonschema` in CI and repeat checks 1 to 4 of 99a section 10 as the independent confirmation of my validator.
- After NEW-1 is fixed, add a test that appends an export, bumps a test result and re-runs the engine on a copy of an approved Blueprint and expects an unchanged `contentHash`.
