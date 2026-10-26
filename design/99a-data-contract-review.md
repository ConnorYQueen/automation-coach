# 99a: Data-contract consistency review

Reviewer: independent (fresh context; wrote none of the files reviewed). Date: 2026-10-25.
Scope: field names, enums, id patterns, rung ids, stages, sensitivity, roles, connection types, tool ids, `Step.override` vs `decisions[]`, policy keys, and the writable surface of `coach-tools.json` against `blueprint.schema.json`.
Rule followed: no existing file was edited. This is the only file written. Scratch scripts live in the session scratchpad, not the project.

Paths below are relative to the project root. `L123` means line 123 of the cited file; `§` means section. Where I could not pin a line I cite the section or `$defs` name.

---

## 0. Result at a glance

| Severity | Count | Meaning |
|---|---|---|
| Critical | 5 | A normal in-contract flow produces a document or bundle that another file's schema rejects, or a tool cannot persist what it exists to persist |
| High | 11 | Semantic conflict or unmapped enum that will cause wrong behaviour or a hard validation failure in a launch feature |
| Medium | 22 | Shape or naming drift that needs a mapping layer, or an undefined rule |
| Low | 14 | Documentation, casing, or latent issues |
| Total | 52 | Findings F-01 to F-52 (section 3) |

The 5 worst:

1. F-25 `record_diagnostic_answers` cannot set the 9 diagnostic fields the engine needs (`operations` first), so every step reached through the Coach returns `needs_info`.
2. F-29 Export vocabulary is defined three ways (tools, Blueprint `exportRecord.format`, policy `allowedKinds`); an export made by the tool cannot be stored, and the admin allow-list can never match.
3. F-09 and F-10 `toolId` and `slug` patterns differ between `policy.schema.json` and `blueprint.schema.json`; valid org tools and environment profile ids produce invalid Blueprints.
4. F-16 and F-17 `record_deploy_plan`, `evidence`, `provenance` and `confirmation` have no home in the Blueprint (root and entities are `additionalProperties:false`).
5. F-01 `llm_agent` sits at a different ladder position in two files than in four others, which changes "first rung that fits" behaviour (OWNER DECISION D1).

Examples validate: yes, with caveats on the validator (section 1). Both embedded examples produce 0 errors, and the 29 seed catalog entries produce 0 errors.

---

## 1. Method and validator caveat

| Item | Detail |
|---|---|
| `jsonschema` library | Not importable in the Python 3.12 install or in `python`. I did not install or download anything. |
| Validator used | A small 2020-12 subset validator I wrote (scratch only): `type`, `enum`, `const`, `pattern`, length and range keywords, `required`, `properties`, `patternProperties`, `additionalProperties`, `items`, `prefixItems`, `contains`, `uniqueItems`, `dependentRequired`, `allOf`, `anyOf`, `oneOf`, `not`, `if/then/else`, `$ref` to `#/...`, and `format` for `date-time`, `date`, `uri`. It does not implement `unevaluatedProperties`, `$dynamicRef`, or remote refs (none are used). |
| Negative controls | Run and rejected as expected: bad `status`, bad `rungId`, extra root property, `user_choice` carrying a `value`, `locked` without a `value`. |
| What to do before release | Re-run both examples and the catalog with the real `jsonschema` (Draft 2020-12 with format checking) in CI. My result is strong evidence, not proof. |
| Probes | I ran real values through both schemas' regexes to confirm the pattern mismatches in F-09 and F-10 (section 3, area B). |

---

## 2. Validation results

| Check | Result |
|---|---|
| Parse `00-shared-contract.md` fenced data, `blueprint.schema.json`, `policy.schema.json`, `tool-catalog.seed.json`, `coach-tools.json` | All JSON files parse |
| Meta-check `blueprint.schema.json` (`$schema` 2020-12, `$id urn:coach:schema:blueprint:1`) | No unknown keywords (only `x-` extensions), all patterns compile, all `$ref` resolve. One informational line: `allOf/0/then/properties/steps/items` has `required: ["recommendation"]` with no sibling `properties`. This is a deliberate "approved Blueprints need a recommendation" constraint, not an error. |
| Meta-check `policy.schema.json` (`$id urn:coach:schema:policy:1`) | Clean |
| Example Blueprint, `rules-engine.md` §19 (block starts L2546) | 0 errors. Also 0 errors with `status` forced to `approved`. |
| Example policy, `settings-catalog.md` §8 (block starts L237) | 0 errors |
| `tool-catalog.seed.json` against `blueprint.schema.json#/$defs/toolCatalogEntry` | 29 entries, 0 errors, 0 duplicate ids |
| Counts cross-checked | 82 policy settings (matches the section counts 17+8+18+8+5+13+6+7 in `settings-catalog.md`); 36 `operationTag` values (matches `rules-engine.md`); 27 tools in `coach-tools.json` |
| `x-meta.policyKeysUsed` in `coach-tools.json` | 18 keys, all exist in `policy.schema.json` |
| Embedded examples vs the other direction | The example Blueprint was not run through `coach-tools.json` write schemas (the tools write through the host, not as whole documents). The tool-to-Blueprint mapping is checked by reading, in section 4. |

What validation does not catch (and this review does): the examples pass because each stays inside its own file's vocabulary. For instance, the example policy uses `builtin.spreadsheet_formulas` in `providesToolIds`, which the policy schema accepts but which is not in the catalog (F-15).

---

## 3. Cross-reference findings

Columns: ID, file A (path and location), file B (path and location), issue, severity, proposed canonical fix. Enum lists use commas (no pipe characters) so the tables stay valid.

### Area A: Vocabulary and enums

| ID | File A | File B | Issue | Severity | Proposed canonical fix |
|---|---|---|---|---|---|
| F-01 | `design/00-shared-contract.md` L31 (human_checkpoint then plus llm_agent); `design/policy.schema.json` `$defs/rungId` L2949; `design/coach-tools.json` rung enums in `search_catalog`, `add_steps.asBuilt`, `update_step.asBuilt`, `record_override`; `design/coach-spec.md` §2.4 table | `design/blueprint.schema.json` `$defs/rungId` L315 (llm_node, llm_agent, human_checkpoint); `design/rules-engine.md` §0 C1 L11 | `llm_agent` position differs. JSON enum order does not affect validation, but "choose the first rung that fits" does: with agent before human the engine can pick the agent over a human checkpoint on open-ended paths (the engine's intent); with agent last it is a last resort. The engine's 46+ fixtures assume the engine's order. | High | OWNER DECISION D1 (section 9). Whatever wins, the contract states that the array order of `rungId` is the ladder order, and all files copy one list. |
| F-02 | `design/policy.schema.json` `coach.llmAgent.mode` L1707 (allowed_with_justification, approval_required, forbidden); same `forbidden` in `coach.llmOverride.mode` and `coach.triageOverride.mode` | `design/blueprint.schema.json` `$defs/engineEnvironment.policy.llmAgentMode` L3711 (..., disabled); `design/rules-engine.md` §3.2 table row "policy.llmAgentMode" | The engine input says `disabled`, the policy value is `forbidden`. The projection row only says "(disabled removes the rung)" and defines no mapping. An implementer who copies the policy value fails engine-input validation. | Medium | Canonical `forbidden` (three policy keys already use it). Change the `engineEnvironment` enum and the rules-engine wording. |
| F-03 | `design/policy.schema.json` `$defs/sensitivityClassRule.llmContentMode` L3970 (full, redacted, none) | `design/blueprint.schema.json` `engineEnvironment.sensitivityRules.*.llmContentMode` (full, redacted) | `none` has no engine representation. | Medium | Add `none` to the engine enum with the meaning "no content may go to any model for this class" (the engine then treats model-dependent rungs as unavailable). |
| F-04 | `design/blueprint.schema.json` `toolCatalogEntry.skillLevel` and `stepEnvironment.builderSkill` (none, basic, intermediate, advanced); `design/tool-catalog.seed.json`; `design/coach-tools.json` `record_environment_facts.builderSkill` | `design/policy.schema.json` `orgToolEntry.skillLevel` L3240 and `prefs.skillLevel` (beginner, intermediate, advanced); `design/settings-catalog.md` §7 L227 | Three skill scales. An org tool with `skillLevel: beginner` cannot be projected into a catalog entry. `prefs.skillLevel` has no defined mapping to the per-step `builderSkill` that `T-SKILL` compares, and `none` is unreachable from the preference. | High | One wire scale everywhere: none, basic, intermediate, advanced. UI labels are separate copy (basic is shown as "Beginner"). `prefs.skillLevel` default becomes `basic`. Rule: `Step.environment.builderSkill` defaults to `prefs.skillLevel` when unset. |
| F-05 | `design/model-certification.md` §2.4 L79 (`"value": "Works"`) | `design/policy.schema.json` `$defs/certification` (certified, works, experimental, uncertified); `design/coach-tools.json` `x-minLabel` (lowercase) | Capitalised label in the capability report, lowercase everywhere else. | Low | Wire values lowercase; capitalise only in UI. |
| F-06 | `design/00-shared-contract.md` L34 (step diagnostic) and `blueprint.schema.json` `diagnostic.interfaceAvailability` (api_available, file_exchange, ui_only, unknown) | `design/rules-engine.md` §0 C6 L16 | No value for "no interface at all" (paper or phone steps). The engine exempts steps whose systems are all `paper_or_phone`. | Low | OWNER DECISION D3. Recommended: keep the exemption, no enum change. |
| F-07 | `design/coach-tools.json` `record_triage_answers` (each answer allows `unknown`); `blueprint.schema.json` `triageAnswers` (same) | `design/rules-engine.md` §11.1 L596-606 (table lists yes/no sets only; "all seven are required, otherwise needs_info") | The answer value sets agree with the tool and schema, except the engine table omits `unknown`. The rules-engine's own VERIFY (§17.1, "enums match 11.1") is resolved: they match. | Low | State in §11.1 that `unknown` counts as missing and yields `needs_info`. |
| F-08 | `design/policy.schema.json` `settings` (`additionalProperties:false`, only `^x-` allowed) | `design/tiers.md` §4.5 (expiry behaviours); `design/architecture.md` L423 (unknown-property preservation is a stated principle for Blueprints) | A bundle signed by a newer portal that carries a new setting key fails strict validation in an older client, so the client refuses a validly signed bundle. | Medium | Clients validate known keys and ignore unknown non-`x-` keys; the schema for `settings` keeps strictness for known keys only. Breaking changes bump `schemaVersion`. |

### Area B: Ids and patterns

| ID | File A | File B | Issue | Severity | Proposed canonical fix |
|---|---|---|---|---|---|
| F-09 | `design/blueprint.schema.json` `$defs/toolId` L309: `^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`, max 80 (exactly one dot; no hyphen) | `design/policy.schema.json` `$defs/toolId` L2944: `^[a-z][a-z0-9_.-]{1,63}$`; `orgToolEntry.toolId` L3240: `^org\.[a-z0-9_.-]{1,60}$`; `softwareItem.providesToolIds` | Probe results: `org.acme-erp`, `org.acme.erp`, `org.1password` pass policy and fail the Blueprint pattern. Any of them used as `recommendation.toolId`, `alreadyHasToolIds` or `tools.permittedToolIds` makes the Blueprint or the engine input invalid. | Critical | One toolId pattern for both: `^[a-z][a-z0-9_]*\.[a-z0-9][a-z0-9_]*$` (one dot, namespace then name, digit allowed after the dot, no hyphen or extra dot), max 80. `orgToolEntry.toolId` becomes `^org\.[a-z0-9][a-z0-9_]{0,59}$`. Generate both schemas from one `$defs`. |
| F-10 | `design/blueprint.schema.json` `$defs/slug` L304: `^[a-z0-9][a-z0-9-]{0,62}$` (used by `environmentProfileRef.id`, `stepSystem.profileSystemId`, `engineEnvironment.systems[].systemId`, org rule ids) | `design/policy.schema.json` `$defs/slug` L2939: `^[a-z][a-z0-9_.-]{1,63}$` (used by `environmentProfile.id`, `profileSystem.systemId`, `orgRule.id`, `dataDomain.id`, `softwareItem.softwareId`) | Probe: `corp_default`, `corp.default`, `sap_prod` pass policy and fail the Blueprint; `2024-profile` and a one-character id pass the Blueprint and fail policy. `Blueprint.environmentProfileRef.id` must equal a policy profile id (`settings-catalog.md` §7 L223), so a legitimate pair can fail. The example policy happens to use only hyphenated ids, which is why it validates. | Critical | One slug: `^[a-z][a-z0-9_-]{1,62}$` (no dots; the dot is reserved as the toolId separator). Both schemas share it. |
| F-11 | `design/policy.schema.json` `orgToolEntry.capabilities` (items are free slugs) | `design/blueprint.schema.json` `$defs/operationTag` (36-value enum); `design/rules-engine.md` §17.2(c) | An org tool can declare a capability the engine does not know; it never matches any step. The rules-engine already requested this fix. | Medium | `orgToolEntry.capabilities` items become the same 36-tag enum, generated from one source. |
| F-12 | `design/policy.schema.json` `orgToolEntry` (toolId, name, rungId, capabilities, constraints, skillLevel, requiresInstall, platforms only) | `design/blueprint.schema.json` `toolCatalogEntry` (adds dataFlow, accessModes, unattendedSupport, hostToolIds, handoff, systemKinds, locatorKinds, connectionTypes, language, maxInputVariability, limits, requiresTrainingData); `rules-engine.md` §0 C3 L13 | The engine's hard predicates (`T-FLOW`, `T-EXEC`, `T-HOST`) read fields an org tool cannot carry; defaults are undefined, so an org tool is either never selectable or silently treated as local-safe. | Medium | Give `orgToolEntry` the same optional extension fields. Define defaults when absent: `dataFlow` = `vendor_cloud` (fail safe), `unattendedSupport` = `no`. |
| F-13 | `design/settings-catalog.md` §7 L226 (model ids are `vendor/model`; local models `local/<name>`) and `design/policy.schema.json` `$defs/modelGlob` | `research/local-and-enterprise-endpoints.md` §7.6 (`allowedModels: ["qwen3.5:9b"]`, a raw Ollama tag); `design/00-shared-contract.md` L40 `allowedModels[]` | Two model-id conventions. A policy glob `local/*` does not match the raw tag in `allowedModels`, and a raw tag collides across connections. | Medium | Canonical model key = `<namespace>/<id>`: `managed` and `byok_openrouter` use the OpenRouter id as is; `byok_provider` uses `<providerId>/<id>`; `custom_openai_compat` uses `custom/<id>` (deployment name for Azure); `local` uses `local/<id>`. `Connection.allowedModels[]`, `models.allowlist`, `prefs.preferredModel.modelId` all store the namespaced key. |
| F-14 | `design/coach-tools.json` id params (`stepId`, `stepIds`, `exceptionId`, `chosenToolId`, `alreadyHasToolIds`, `search_catalog.toolId`): strings with length limits only | `design/blueprint.schema.json` id patterns (`stp_`, `exc_`, `tst_` plus 26-character ULID; `toolId`) | The tool layer accepts malformed ids and relies on the host (`unknown_step`, `catalog_id_unknown`). Works, but small and local models get a late error instead of a schema hint. | Low | Add `pattern` copies to tool parameters (still flat, no `$ref`, per `x-meta.format`). |
| F-15 | `design/settings-catalog.md` §8 example, L712: `builtin.spreadsheet_formulas`; `design/tool-catalog.seed.json` | `design/tool-catalog.seed.json` has `builtin.excel_formulas`; `ocr.tesseract_local` is in the seed and referenced by no other file | `providesToolIds` has no membership check against the catalog, so a dangling id is silently inert. One seed entry is unreachable from every doc. | Low | Add a publish-time check ("every id in `providesToolIds`, `permittedToolIds`, `forbiddenToolIds` exists in the catalog or starts with `org.` and is defined in `environment.customTools`"). Confirm `ocr.tesseract_local` is intended to be reachable only through the engine. |

### Area C: Blueprint fields the Coach host must write

| ID | File A | File B | Issue | Severity | Proposed canonical fix |
|---|---|---|---|---|---|
| F-16 | `design/coach-tools.json` `record_deploy_plan` L3606 (backupOwner, failureSignals[{stepId, signal, notify}], manualFallback, changeTriggers[], reviewAfterDays); L10 assumption; `design/coach-spec.md` App. B ext 3 L740 | `design/blueprint.schema.json` root (`additionalProperties:false`, no `deployPlan`) | The deploy_monitor stage's only write tool has nowhere to persist. | Critical | Add `Blueprint.deployPlan` (section 8, B3). |
| F-17 | `design/coach-tools.json` G7 (evidence on every fact write), L1423 (`provenance=pasted_document`, "Suggested from SOP" group), L1458 (`createdBy=coach`, `confirmation.state=proposed`); `design/coach-spec.md` App. B ext 1 L738 | `design/blueprint.schema.json` `$defs/step` L1836 and `$defs/exception` L1944: only a flat `confirmationState`; no `provenance`, `createdBy`, `confirmedBy`, `confirmedAt`; `provenance` exists only inside `diagnostic` | Evidence verified by the host has no stored destination on steps or exceptions; the SOP group cannot be rebuilt on reload; who confirmed and when is lost (matters for approval). | High | Keep the flat `confirmationState` (the schema, the engine example and `rules-engine.md` §17.1 already use it). Add to Step, Exception, Test, DeployPlan: `createdBy` (user, coach, engine), `confirmedBy`, `confirmedAt`, and to Step and Exception `provenance` (an Evidence object). Change `coach-spec.md` and `coach-tools.json` wording from `confirmation{state,by,at}` to these flat fields. |
| F-18 | `design/coach-tools.json` `generate_test_cases_from_exceptions` L2961 (cases[]: `exceptionId`, `stepId`, `title`, `exampleData`); L3073 assumption (`expected`, `lastResult`); L3486; `design/coach-spec.md` App. B ext 4 L741 | `design/blueprint.schema.json` `$defs/test` L2856 (`stepIds[]`, `exceptionIds[]`, `given`, `when`, `then`, `status`, `lastRunAt`; no `exampleData`, `expected`, `lastResult`) | `exampleData` has no home. `expected` and `lastResult` do not exist; the schema's `then`, `status` and `lastRunAt` carry the same meaning under other names. Singular ids vs arrays. | High | Add `Test.exampleData` (string, max 400), `lastRunId`, `lastRunDetail`, plus the F-17 fields. Canonical names stay `then` (expected), `status` plus `lastRunAt` (result). Update `coach-spec.md`/`coach-tools.json` text. The host maps `cases[].stepId` to `stepIds:[x]`. |
| F-19 | `design/coach-tools.json` `set_process_info.evidence` L800 and `record_triage_answers.evidence` (required) | `design/blueprint.schema.json` `$defs/processInfo`, `$defs/triageBlock` (no provenance) | Evidence for process facts and triage answers is verified then dropped. | Medium | Add `process.provenance` and `triage.provenance`: maps from field name to Provenance (F-20). |
| F-20 | `design/rules-engine.md` §2.1 L98 ("which answers the user stated, the Coach inferred or the engine derived") | `design/blueprint.schema.json` `diagnostic.provenance` L514 block (map of field to Evidence only) | The engine describes a classification the schema cannot hold; the schema holds quotes the engine says it does not read. | Medium | `provenance[field] = {origin: user_stated, coach_inferred, engine_derived; evidence?: Evidence}`. |
| F-21 | `design/policy.schema.json` `$defs/comparison.field` pattern (root must be blueprint, step or exception, then dotted camelCase segments with optional `[*]`); `design/settings-catalog.md` §8 example L590 `step.derived.domains` and §7 L222 (assumes a published "Blueprint field registry") | `design/blueprint.schema.json` (no `derived`, no `domains`; no field registry published) | An org rule can name any path; only `step.diagnostic.attendance`-style paths exist. `step.derived.domains` is a policy-layer virtual field with no schema definition, so publish-time checking is impossible. | Medium | Publish `x-virtualFields` in `blueprint.schema.json` (`step.derived.domains[]` = data domains matched by `governance.dataDomains`) and generate the allowed-path list for the rule builder from properties plus virtual fields. |
| F-22 | `design/rules-engine.md` §17.2 L2486 ("`recommendation`, `roi`, `triage` verdict and trace; marked `x-derived`") ; `design/architecture.md` C4 L18 (2) | `design/blueprint.schema.json` `x-derived` appears only on `$defs/recommendation` L1557 and `$defs/roiEstimate` L2234; `triageBlock` has user-written `answers` beside derived `verdict`, `rationale`, `ruleTrace`, `warnings`, `conditions` | Sync drops only what is marked; triage verdict and trace are not marked, so a merge could keep a stale verdict. | Medium | Mark the derived properties of `triageBlock` individually with `x-derived`; leave `answers` and `overrideDecisionId` unmarked. |
| F-23 | `design/coach-spec.md` App. B ext 2 L739 (`Step.asBuilt`) and ext 5 L742 (auditLog action vocabulary) | `design/blueprint.schema.json` `$defs/asBuilt` L1815 (exists), `auditEntry.action` (free string, max 64) | Ext 2 is already satisfied. Ext 5 is satisfied structurally, but no action-name registry exists. | Low | Mark ext 2 resolved. Publish the action vocabulary as an `x-actions` list in the schema. |
| F-24 | `design/coach-tools.json` G12 in `x-globalRules` (`{at, actor:'coach', connectionId, modelId, tool, entity ids, evidence ref, callId}`) | `design/blueprint.schema.json` `$defs/auditEntry` L2966 (`actor{type,id}`, `entity{type,id}` single, `summary`, `details` free object) | Shapes differ; `connectionId`, `modelId`, `callId`, `tool` and entity lists have no named place. | Medium | Keep `auditEntry` shape; define `details` keys: `callId`, `connectionId`, `modelId`, `tool`, `entityIds[]`, `evidenceRef`. Add `server` to `actor.type` (F-35). |

### Area D: Tool parameters against the Blueprint

| ID | File A | File B | Issue | Severity | Proposed canonical fix |
|---|---|---|---|---|---|
| F-25 | `design/coach-tools.json` `record_diagnostic_answers` L2188: `answers` is `additionalProperties:false` with the 12 contract fields only (plus `attractorCheck`) | `design/blueprint.schema.json` `$defs/diagnostic` L514 adds `operations`, `humanAuthority`, `necessity`, `requiredByControl`, `residualHandling`, `inputVariability`, `pathPredictability`, `inputSize`, `training`; `design/rules-engine.md` §17.1 L2472 | Verified. Without `operations` every step returns `needs_info` (`V-MISSING`), so the Coach path can never reach a recommendation; only a wizard UI could set them. | Critical | Add the nine optional fields to `answers` (enums copied from the schema), each with the same `evidence` rule as other risk facts. |
| F-26 | `design/coach-tools.json` `record_environment_facts` L2454: `systemName`, `systemKind`, `builderSkill`, `alreadyHasToolIds` | `design/blueprint.schema.json` `$defs/stepSystem` L747 (`name`, `kind`, `role`, `accessModes`, `accessEvidence`, `uiLocator.kind`, `authModel`, `profileSystemId`) and `stepEnvironment.systems` (up to 8); `rules-engine.md` §17.1 L2473 | Verified. The tool writes one system and none of `role`, `accessModes`, `accessEvidence`, `uiLocator`, `authModel`, `profileSystemId`. `authModel` is mandatory for unattended steps that need a login (`V-AUTH`). | High | Replace the single system with `systems[]` (max 8) carrying those fields. The host forces `accessEvidence` to `claimed` for model writes (only an inspection result may set `verified`). |
| F-27 | `design/coach-tools.json` `record_override` L2589 (`chosenToolId` present, optional) | `design/rules-engine.md` §17.1 L2475 (make it required, `OV-1`); `blueprint.schema.json` `override.chosenToolId` and `decisionOverride.chosenToolId` (optional) | Corrects the lead's note: the parameter exists. The gap is only that it is optional in tool and schema while the engine needs it to check hard predicates. | Medium | Required in the tool; required in `decisionOverride` when `chosenRungId` is not `eliminate`. `human.manual_task` is the accepted id for a manual fallback. |
| F-28 | `design/coach-tools.json` `record_override.reason` min 1, `advance_stage.triageOverride.reason` min 1 (L2750, L3875 say policy default 20) | `design/blueprint.schema.json` `override.reason`, `decisionOverride.reason`, `decisionTriageOverride.reason`, `decisionOrgRuleWaiver.reason` all min 15 (L1567, L2363, L2560, L2614); `design/policy.schema.json` `coach.override.reasonMinChars` L1804 integer 0 to 500, default 20; `rules-engine.md` OV-2 | Floors are 1 (tool, deliberate, to return `reason_too_short` instead of a schema error), 15 (Blueprint, hard), and 0 to 500 (policy). An admin who sets 5 passes policy and tool, then the save fails the Blueprint schema. | High | OWNER DECISION D4. Recommended: policy minimum becomes 15 (equal to the Blueprint floor); tool floor stays 1. |
| F-29 | `design/coach-tools.json` `export_blueprint.format` L3511 (handoff_brief, process_document, review_packet, blueprint_json); `design/coach-spec.md` App. B L750 | `design/blueprint.schema.json` `$defs/exportRecord.format` L2922 (automate_flow_draft, spec_markdown, spec_json, spec_pdf, spec_docx, csv); `design/policy.schema.json` `data.exports.allowedKinds` L1238 (null or array of free slugs, "kinds match `Blueprint.exports[]` kind names"); `settings-catalog.md` §7 L228 | Three vocabularies. The Blueprint has `format`, not `kind`. An export triggered by the tool cannot be stored as `exports[]`, and the admin allow-list can never match any value. | Critical | Split two axes: `kind` (handoff_brief, process_document, review_packet, blueprint_json, automate_flow_draft) and `fileFormat` (md, json, pdf, docx, csv, automate_draft). `exportRecord` stores both. `allowedKinds` becomes an enum of the five kinds. Mapping of old values is in section 8, B4. |
| F-30 | `design/coach-tools.json` `export_blueprint.scope` and `stepIds` | `design/blueprint.schema.json` `exportRecord` (no `scope`, `stepIds`, sensitivity at time of export) | A scoped export cannot be recorded or audited. | Medium | Add `scope`, `stepIds`, `sensitivityAtExport` to `exportRecord`. |
| F-31 | `design/coach-tools.json` `generate_llm_justification_card.citedDiagnosticFields` (required, min 1) | `design/rules-engine.md` CARD-2 (the engine pre-fills `citedDiagnosticFields`) | If the engine pre-fills, a required model field is redundant and invites a disagreement. | Low | Make it optional in the tool; the host merges engine-prefilled and model-supplied, engine wins. |

### Area E: Sync, envelope, hashes

| ID | File A | File B | Issue | Severity | Proposed canonical fix |
|---|---|---|---|---|---|
| F-32 | `design/blueprint.schema.json` root `etag` L38-40 ("Sent as If-Match"; base64url hash of the canonical Blueprint without `etag` and `sync`) | `design/architecture.md` L431, L461 (`If-Match: <rev>`, integer `rev`) | Two different `If-Match` semantics. | High | `If-Match` carries `rev` (architecture owns the protocol). `etag` stays as a client-local change detector; fix its description. |
| F-33 | `design/architecture.md` L469 envelope (`rev`, `baseRev`) and L448 ("`updatedAt`, `version`, `rev` set by the server at push") | `design/blueprint.schema.json` `version`, `syncState.baseVersion`, `syncState.lastSyncedVersion` | Two names for revision numbers, and `version` is stamped into `auditEntry.blueprintVersion` and `exportRecord.blueprintVersion` while offline, where no server `rev` exists. | Medium | `rev` is the server revision and lives only in the envelope and `sync` (`baseRev`, `lastSyncedRev`). `version` is the client edit counter, never equal to `rev` by definition. Rename the two `sync` fields. |
| F-34 | `design/architecture.md` C4(5) L18 (`contentHash` = SHA-256 of RFC 8785 canonical minus `auditLog`, `status`, `updatedAt`, `version`) | `blueprint.schema.json` `etag`, `exportRecord.contentHash`, `engineMeta.inputsHash`, `decisionOverride.engineRecommendation.traceHash` | Five hashes, defined in four places with different exclusion sets. | Medium | Publish a hash registry in the contract (section 8, E2). `contentHash` must also exclude `sync` and `etag`. |
| F-35 | `design/architecture.md` L463 (signed approval record `blueprintId, rev, contentHash, reviewer, decision, at`, appended to `auditLog[]`; the adapter verifies signature and `contentHash`); `design/tiers.md` §2 rules | `design/blueprint.schema.json` `$defs/approval` (no signature, rev, or hash) and `$defs/auditEntry` (`details` free; `actor.type` has no server value) | The approval record the AutoMate adapter must verify has no typed shape. A hand-edited local file cannot be distinguished by schema from a real record. | High | Add `$defs/approvalRecord` (section 8, E3); `auditEntry.action = approval_recorded` carries it in `details`; add `actor.type = server`. |
| F-36 | `design/architecture.md` C4(1) L18 and L423 (preserve unknown properties; newer `schemaVersion` opens read-only) | `design/blueprint.schema.json` root `schemaVersion` `const "1.0"`, `additionalProperties:false` everywhere | The schema cannot accept the minor versions the architecture assumes; a strict validator rejects any 1.1 document. | Medium | `schemaVersion` pattern `^1\.[0-9]+$`; rule in the contract: writers emit only schema-listed properties, readers preserve unknown ones, and the strict schema is applied only to the client's own version. |
| F-37 | `design/blueprint.schema.json` `schemaVersion` string "1.0"; `design/policy.schema.json` `schemaVersion` integer; `design/architecture.md` envelope `schemaVersion` (untyped); `model-certification.md` `toolSchemaVersion` "0.1.0" | (each other) | Four version styles. | Low | Blueprint and envelope: string "major.minor". Policy: integer (separate artifact, stated). Tool schema: semver string. Write it down once in the contract. |
| F-38 | `design/architecture.md` §4.6 (integer micro-USD) | `design/policy.schema.json` `spend.*Usd` (numbers) | No rule for converting a USD cap to micros. | Low | Cap micros = round(USD x 1,000,000), half-up, evaluated at reserve. |
| F-39 | `design/architecture.md` `membership.role (Admin/CoE Reviewer/Builder/Viewer)`; `design/tiers.md` | `design/policy.schema.json` `$defs/role` (admin, coe_reviewer, builder, viewer) | Display names used where wire ids are needed. | Low | Wire ids are the policy ids; the database enum uses them. |

### Area F: Policy

| ID | File A | File B | Issue | Severity | Proposed canonical fix |
|---|---|---|---|---|---|
| F-40 | `design/blueprint.schema.json` `engineEnvironment.sensitivityRules.*.toolDataFlowCeiling` (required, local, tenant, vendor_cloud, ai_cloud); `design/rules-engine.md` §0 C8 L18 and §17.2(a) | `design/policy.schema.json` `sensitivityClassRule` L3970 (no such field) | The engine input is required to contain a value no admin can set; the engine falls back to its internal default (§3.4). | High | OWNER DECISION D6 (add the optional field per class, recommended). |
| F-41 | `design/coach-spec.md` §3 L155 ("no usable connection, or AI off: wizard"), App. B L747; `design/model-certification.md` L285 | `design/policy.schema.json` (no key) | There is no explicit "AI off" setting. It can be approximated by locking all five `connections.*.enabled` to false, but then mode selection has no single predicate and new connection types silently re-enable AI. | Medium | OWNER DECISION D2. |
| F-42 | `design/policy.schema.json` root `schemaVersion` L17 (optional) | `design/tiers.md` §4.1 L161 (added "so an offline client knows which schema applies") | An optional field cannot do the job it was added for. | Medium | Make it required. |
| F-43 | `design/00-shared-contract.md` L41 (`settings{<key>:{value,state}}`) | `design/policy.schema.json` `stateValueRule` L3028 (`locked` and `default` carry `value`; `user_choice` must not); `design/tiers.md` L161 | Documented deviation, correct, and confirmed by the negative control (a `user_choice` carrying a value is rejected). The contract text is the stale party. | Low | Amend the contract: `{state, value?}`, `value` present for `locked` and `default` only. |
| F-44 | `design/tiers.md` L13, L15, L17, L18, L20, L297 (Enterprise: group-scoped policy, per-group profiles and variants) | `design/00-shared-contract.md` L41 (one bundle per org); `design/policy.schema.json` (`environmentProfile.groupIds` is the only group-aware field; no resolution rule) | A user in two groups with two profiles has no defined result. tiers defers group-scoped policy, but the schema half-includes it. | Medium | OWNER DECISION D7. |
| F-45 | `design/tiers.md` §4.1 signature bullet (EdDSA) | `design/architecture.md` C5 L19 (ES256 or EdDSA, VERIFY); `policy.schema.json` `signature` pattern (86 character base64url tail) | The 86-character tail fits a 64-byte signature of either algorithm, so the schema is neutral, but the JWS header `alg` is open. | Low | Contract states the `alg` set accepted by clients (`EdDSA`, `ES256`) once the owner decides (architecture C5). |
| F-46 | `design/policy.schema.json` (82 keys) | all other design files | 37 keys are referenced by no file other than the catalog: `connections.{byokOpenrouter, byokProvider, customOpenaiCompat}.enabled`, `connections.byokProvider.allowedProviders`, `connections.endpointHostAllowlist`, `connections.requireTls`, `connections.proxy`, `connections.orgConnections`, `data.redaction.{customPatterns, defaultAction}`, `environment.{profiles, defaultProfileId, userMayDeclareSoftware}`, `governance.approval.{mode, requiredBefore, minReviewers, reviewSlaDays}`, `governance.auditLog.clientReportedUsage`, `governance.dataDomains`, `governance.intake.{enabled, requiredFields, gateStage}`, `governance.orgRules`, `governance.templates.{required, allowPersonal}`, `prefs.{alerts.channels, alerts.events, coachingStyle, preferredModel, showEngineTrace, skillLevel, verbosity}`, `retention.{localLogs.days, transcripts.storage}`, `spend.{byokEstimatedMonthlyCapUsd, personalMonthlyCapUsd}`, `sync.transcripts.enabled`. Some are consumed by the portal or server (no design file here), but `connections.*`, `environment.*`, `governance.orgRules` and `prefs.skillLevel` are consumed by the Coach host and the engine under other names. | Low | Name the consumer in `settings-catalog.md` for each key, and use the key names (not `environmentProfile.*`) in the engine projection table. |

### Area G: Connection and model entities

| ID | File A | File B | Issue | Severity | Proposed canonical fix |
|---|---|---|---|---|---|
| F-47 | `design/00-shared-contract.md` L40 (`id, type, endpoint, credentialRef, allowedModels[], policyRef`); `research/local-and-enterprise-endpoints.md` §0 C2 L14, C6 L18, §7.6 (adds `serverKind`, `authScheme`, `extraHeaders`, `modelIdKind`, `contextWindowOverride`, `tokenProviderRef`, `capabilityProfile`; adds `llamacpp`) | `design/policy.schema.json` `$defs/orgConnection` L4126 (`id`, `type`, `label`, `endpoint`, `providerId`, `allowedModels`, `credentialMode`; no `credentialRef`, `policyRef`, `serverKind`) | No Connection schema exists anywhere. Three shapes (contract, research, policy) of one entity. An org connection cannot say it is Azure (deployment name) or llama.cpp. `authScheme: token_provider` overlaps `credentialMode: integrated_oauth` and `org_vault`. | High | Define one Connection schema (section 8, F1); org connections in policy are the same shape minus device-local fields. |
| F-48 | `research/local-and-enterprise-endpoints.md` §7.6 (`capabilityProfile` on the Connection: toolsNative, toolChoiceForced, streamingToolCalls, contextTokens, ttftMsAt3k, decodeTps, serverVersion, modelDigest) | `design/model-certification.md` §2.4 L69-85 (capability report keyed by connection, model, endpoint hash, probe version: `features.tools`, `toolChoiceRequired`, `streaming`, `declaredContextTokens`, `effectiveContextTokens`, `latency.ttftMsP50`, `tokensPerSec`) | The same probe result is described twice with different field names, and one of them is attached to the wrong entity (a Connection has many models; results are per model). | Medium | Remove `capabilityProfile` from Connection. One `CapabilityReport` keyed by (connectionId, modelKey, probeVersion), using the certification file's names, plus the research's extra fields (`toolsInContent`, `thinkLeak`, `silentTruncation`, `toolsPlusSchemaOk`, `serverVersion`, `modelDigest`). |
| F-49 | `design/00-shared-contract.md` L17 (`byok_openrouter`); `research/openrouter-gateway-billing.md` §0 C2 L14 | OpenRouter's own "BYOK" product (provider keys stored in an OpenRouter account, with a 5% fee after a free tier) | The name collides with OpenRouter's term. The research recommends keeping the contract names and adding a glossary line; no glossary line exists in the contract. | Medium | OWNER DECISION D5. |
| F-50 | `design/00-shared-contract.md` L40 `policyRef`; `design/settings-catalog.md` §7 L226 (built-in id `managed`); `research/...` example `conn_01` | `design/policy.schema.json` `orgConnection.id` (string 1 to 64, no pattern) | `policyRef` has no defined meaning. Connection ids have no pattern. | Low | `Connection.id` pattern `^[a-z0-9][a-z0-9_-]{0,63}$`; `policyRef` = the `orgConnection.id` it was provisioned from, or null for a personal connection. |

### Area H: Roles

| ID | File A | File B | Issue | Severity | Proposed canonical fix |
|---|---|---|---|---|---|
| F-51 | `design/tiers.md` §2 matrix (rows at L67, L74, L78, L79): CoE Reviewer can create a Blueprint and run the Coach, export, and start an attended test run; cannot use AutoMate draft and apply | `design/coach-tools.json` G13 L131 ("CoE Reviewer is read-only inside the Coach"), per-tool rules (`remove_step`, `remove_exception`, `record_override`, `propose_automate_flow_draft`, `apply_automate_draft`, `request_attended_test_run`, `advance_stage`: "Builder or Admin"; `export_blueprint`: "Builder or Admin" at L3596); `design/coach-spec.md` L747 and open question 2 L757 | Direct contradiction on a security-relevant matrix. Neither side marks it as an owner decision except coach-spec's open question. | High | OWNER DECISION D8. |
| F-52 | `design/coach-tools.json` `export_blueprint` L3596 ("Viewer and CoE Reviewer may export `review_packet` if policy allows; ASSUMPTION") | `design/tiers.md` §2 L74 (Viewer: no export) | A Viewer export that the matrix denies. | Medium | Follow the tiers matrix (Viewer cannot export); remove the assumption. |

Counts by severity are in section 0; I tallied them from the IDs above.

---

## 4. Writable tool parameters against the Blueprint

For each write tool in `design/coach-tools.json`: where each parameter lands in `design/blueprint.schema.json`, and any trap. "Host" means the host writes it, not the model (G2, G6).

| Tool (line) | Parameters | Blueprint target | Gaps and traps |
|---|---|---|---|
| `set_process_info` (L800) | title, summary, trigger, frequency, volume, timePerRunMinutes, people, sensitivity, evidence | `title` (root, max 120), `process.*`, `sensitivity` | All fields exist and limits match. `evidence` has no home (F-19). Sensitivity can only rise (error `sensitivity_downgrade_blocked`). |
| `record_triage_answers` | seven answers, evidence | `triage.answers` | Enums match `triageAnswers` and `rules-engine.md` §11.1. `evidence` no home (F-19). |
| `add_steps` (L1176), `update_step` (L1468) | name, description, actor, inputs, outputs, decisionPoints, asBuilt, afterStepId, moveAfterStepId, markExceptionsReviewed, evidence | `Step.*` | Field names, lengths and enums match, including `asBuilt` and `decisionPoints.ruleStatus`. `evidence` and host fields (`provenance`, `createdBy`) have no home (F-17). `order` is host-derived. |
| `remove_step`, `remove_exception` | reason (5 to 200), disposition | audit entry only | No trap. Approval-class. |
| `add_exception`, `update_exception` | description, frequency, frequencyNote, handling, stepIds, evidence | `Exception.*` | Matches. `Exception.confirmationState` exists; no `provenance` (F-17). `Step.exceptionRefs` and `Exception.stepIds` are two sides of one link; the host keeps both in sync (not stated in either file). |
| `record_diagnostic_answers` (L2188) | 12 answers, attractorCheck, evidence | `Step.diagnostic` | Missing nine engine fields (F-25). `provenance` per field is host-written. `additionalProperties:false` on `answers` is the trap. |
| `record_environment_facts` (L2454) | systemName, systemKind, builderSkill, alreadyHasToolIds, evidence | `Step.environment` | One system only; six per-system fields missing (F-26). |
| `record_override` (L2589) | chosenRungId, chosenToolId, reason, acknowledgedRuleIds, evidence | `decisions[]` (`decisionOverride`) and denormalised `Step.override` | Host fills `by`, `at`, `engineRecommendation`, `overriddenRuleIds`, `approval`, `status`, `id`. `chosenToolId` optional (F-27). Reason floor (F-28). |
| `generate_llm_justification_card` | whyNotCode, citedDiagnosticFields, validator, fallback, evidence | `decisions[]` (`decisionLlmJustification`) and `Step.llmJustification` | Enums for `validator.kind` and `fallback.kind` match. `costPerRun`, `source`, `cardState` are host-written, correctly absent from the tool. Redundant required field (F-31). |
| `generate_test_cases_from_exceptions` (L2961) | exceptionIds, happyPathStepIds, cases[] | `tests[]` | `exampleData` no home; naming differences (F-18). `kind` is host-set (exception, happy_path). |
| `advance_stage` (L3752) | toStage, reason, triageOverride{reason, evidence} | `stage`, `decisions[]` (`decisionTriageOverride`), audit entry | Stage enum matches. `reason` (max 200) is audit-only. Reason floor (F-28). |
| `export_blueprint` (L3511) | format, scope, stepIds | `exports[]` | Vocabulary and scope fields (F-29, F-30). |
| `record_deploy_plan` (L3606) | backupOwner, failureSignals, manualFallback, changeTriggers, reviewAfterDays, evidence | none | No home (F-16). |
| `propose_automate_flow_draft`, `apply_automate_draft`, `request_attended_test_run` | target, mappings, draftId, flowRef, testCaseIds | none in the Blueprint (adapter and host state); results land in `exports[]` (`automate_flow_draft`) and `tests[]` (`attended_run`) | `draftId`, `requestId` have no pattern. Applying a draft creating an `exports[]` record depends on F-29. |

Read tools (`get_blueprint`, `get_stage_guidance`, `search_catalog`, `get_automate_capabilities`, `get_action_status`, `request_*`) write nothing; their enums (stage, rung, view) match the schemas, apart from the rung order in F-01.

### Fields the engine needs that no tool can set

| Field | Needed by | Verified |
|---|---|---|
| `diagnostic.operations` | every step (`V-MISSING`) | Yes, tool lacks it (F-25) |
| `diagnostic.humanAuthority`, `necessity`, `requiredByControl`, `residualHandling` | elimination, human-rung and residual-handling rules | Yes (F-25) |
| `diagnostic.inputVariability`, `pathPredictability`, `inputSize`, `training` | parser/ML and agent rungs | Yes (F-25) |
| `environment.systems[].role`, `accessModes`, `accessEvidence`, `uiLocator`, `authModel`, `profileSystemId` | effective access modes, `V-AUTH` | Yes (F-26) |
| `environment.systems[]` beyond the first | multi-system steps | Yes (F-26) |
| `Step.timePerRunMinutes` | nothing (`rules-engine.md` states it is not used for weighting) | Dead field; keep or drop (Low, no ID) |

The rules-engine agent's claims about the three tools are accurate: `record_diagnostic_answers` and `record_environment_facts` are as it describes, and `record_override` does not lack `chosenToolId` (it only leaves it optional).

---

## 5. Vocabulary agreement matrix (what agrees, so it is not re-checked)

| Vocabulary | Files compared | Result |
|---|---|---|
| Stages (triage, capture, decompose, classify, environment_fit, design, build_handoff, test_plan, deploy_monitor) | contract, blueprint, policy `$defs/stage`, coach-tools (`get_stage_guidance`, `advance_stage`) | Agree |
| Sensitivity (public, internal, confidential, restricted) | contract, blueprint, policy, coach-tools | Agree. `diagnostic.dataSensitivity` adds `unknown` by design. |
| Connection types (managed, byok_openrouter, byok_provider, custom_openai_compat, local) | contract, blueprint (`toolCatalogEntry.connectionTypes`, `engineEnvironment`), policy `$defs/connectionType` | Agree. `orgConnection.type` correctly excludes managed and local. Policy key names are camelCase forms (`byokOpenrouter`); the mapping is by convention only (add a line to the catalog). |
| Roles (admin, coe_reviewer, builder, viewer) | policy `$defs/role`, `require_approval.role`, `coach.llmOverride.approverRole` | Agree on ids. Permissions conflict: F-51, F-52. |
| Triage verdicts (automate, fix_process_first, dont_automate) | contract, blueprint | Agree |
| Statuses (draft, in_review, approved, built, deployed, retired) | contract, blueprint | Agree |
| Tool ids referenced in `rules-engine.md` | `tool-catalog.seed.json` | All 29 referenced ids exist. Not referenced anywhere: `ocr.tesseract_local`. |
| `Step.override` vs `decisions[]` | contract L38, rules-engine C2, blueprint | Consistent: `Step.override` and `Step.llmJustification` are the denormalised current record, `decisions[]` the append-only history, linked by `decisionId`. `override.status` includes `pending_approval`, which resolves coach-spec's open assumption (L747) about storing an override awaiting approval. The only conflict is the reason floor (F-28). |
| Policy keys referenced by other files that are missing from `policy.schema.json` | all design files | Only one real key gap beyond F-40 and F-41: the field path `step.derived.domains` (F-21). Everything else the scan flagged is either a prefix (`data.redaction`, `automate.testRuns`), a `tenant.*` key that `settings-catalog.md` §5 deliberately keeps out of the signed bundle, an engine projection name (`policy.llmAgentMode`), or a catalog field (`limits.*`). |

---

## 6. Hypotheses (a) to (f)

| Hyp | Statement | Verdict | Evidence and finding |
|---|---|---|---|
| (a) | The Coach wants `provenance`, `confirmation`, `asBuilt`, `deployPlan` and extra `tests[]` fields | Mostly confirmed; `asBuilt` is wrong | `asBuilt` already exists (`$defs/asBuilt` L1815): F-23. `provenance` and `confirmation` (as flat fields) and `deployPlan` do not exist: F-16, F-17. `tests[]` needs `exampleData`; `expected` and `lastResult` already exist as `then`, `status`, `lastRunAt`: F-18. |
| (b) | The rules-engine conflicts C1 to C9 | C1 confirmed (F-01). C2 resolved in the schema (section 5). C3 implemented in the catalog schema but not in the contract text or org tools (F-12). C4 confirmed and unresolved in the tools (F-25). C5 is behaviour, no data impact. C6 open (F-06, D3). C7 implemented (`stepResult.status`, `outcome`). C8 unresolved in policy (F-40). C9 implemented: the eight `ruleAction` types match the engine's `orgRules[].type` enum exactly. | See cited findings. |
| (c) | The local-endpoints research wants Connection fields and `llamacpp` | Confirmed | No Connection schema exists; the policy `orgConnection` is a third shape: F-47, F-48. `llamacpp` is a `serverKind` value only; it appears in no enum yet because none exists. |
| (d) | Policy added `schemaVersion` and lets `user_choice` omit `value` | Confirmed, both documented in `tiers.md` §4.1 L161 | `schemaVersion` is optional, which defeats its purpose: F-42. `user_choice` without `value` is enforced (negative control passed); the contract text is stale: F-43. |
| (e) | There is no "AI off" key | Confirmed | F-41. |
| (f) | OpenRouter "BYOK" clashes with `byok_openrouter` | Confirmed, naming only | F-49. Impact is documentation and customer copy, not data. |

---

## 7. Policy key audit

Referenced by another file but absent from `policy.schema.json`:

| Key or path | Where referenced | Disposition |
|---|---|---|
| Per-class `toolDataFlowCeiling` | `blueprint.schema.json` `engineEnvironment`; `rules-engine.md` §0 C8 | F-40, D6 |
| An "AI off" key | `coach-spec.md` §3 L155; `model-certification.md` L285 | F-41, D2 |
| `step.derived.domains` (rule field path) | `settings-catalog.md` §8 L590 | F-21 |
| Tool ids `builtin.spreadsheet_formulas` | `settings-catalog.md` §8 L712 | F-15 |

Schema keys that nobody else references: 37, listed in F-46.

---

## 8. Proposed contract v2 data amendments

Written in the contract's style (canonical entity lines, camelCase). Each item names the finding it closes. Items needing the owner are listed in section 9 with both options and are marked `OWNER DECISION` here.

### A. Cross-cutting conventions (add as a new short section)

- **A1 Ids.** `toolId`: `^[a-z][a-z0-9_]*\.[a-z0-9][a-z0-9_]*$`, max 80; org tools `^org\.[a-z0-9][a-z0-9_]{0,59}$`. `slug`: `^[a-z][a-z0-9_-]{1,62}$`. Entity ids: `bp_`, `stp_`, `exc_`, `dec_`, `tst_`, `exp_`, `aud_` plus a 26-character ULID. Both schemas use one shared definition. (F-09, F-10)
- **A2 Ladder.** `rungId` array order is the ladder order. Order: `OWNER DECISION D1`. (F-01)
- **A3 Skill.** `skillLevel` and `builderSkill`: `none, basic, intermediate, advanced` everywhere, including `prefs.skillLevel` (default `basic`). (F-04)
- **A4 Policy mode word.** The refusal value for every three-state mode key is `forbidden` (never `disabled`). (F-02)
- **A5 Model keys.** `<namespace>/<id>`: managed and byok_openrouter use the OpenRouter id as is; byok_provider `<providerId>/<id>`; custom_openai_compat `custom/<id>`; local `local/<id>`. (F-13)
- **A6 Wire casing.** Roles `admin, coe_reviewer, builder, viewer`; labels `certified, works, experimental, uncertified`. Display names are UI copy only. (F-05, F-39)
- **A7 Versions.** `Blueprint.schemaVersion` string `1.<minor>` (pattern `^1\.[0-9]+$`); readers preserve unknown properties, writers emit only schema properties. `Policy.schemaVersion` integer, required. (F-36, F-37, F-42)

### B. Blueprint

- **B1** `Blueprint`: `id`, `schemaVersion`, `version` (client edit counter), `etag` (client-local content tag, not used for sync), `title`, `owner`, `orgId`, `status`, `sensitivity`, `stage`, `triage{verdict, rationale, answers, conditions, warnings, ruleTrace, overrideDecisionId, provenance}`, `process{summary, trigger, frequency, volume, timePerRunMinutes, people[], provenance}`, `steps[]`, `exceptions[]`, `environmentProfileRef{id, policyVersion}`, `roi{}`, `decisions[]`, `tests[]`, `deployPlan{}`, `exports[]`, `auditLog[]`, `engine{}`, `sync{deviceId, baseRev, lastSyncedRev, lastSyncedAt, state}`, `createdAt`, `updatedAt`. Properties `verdict`, `rationale`, `conditions`, `warnings`, `ruleTrace` of `triage` carry `x-derived`. (F-22, F-33, F-19)
- **B2** `Provenance` (used by `diagnostic.provenance[field]`, `process.provenance[field]`, `triage.provenance[answer]`): `{origin: user_stated|coach_inferred|engine_derived, evidence?: Evidence}`. `Evidence` unchanged: `{source: user_turn|pasted_document, turnId, docId?, quote, at?}`. (F-19, F-20)
- **B3** Host-written entity fields. On `Step`, `Exception`, `Test`, `DeployPlan`: `createdBy` (user|coach|engine), `confirmationState` (proposed|confirmed), `confirmedBy`, `confirmedAt`. On `Step` and `Exception` also `provenance` (a single `Evidence`). `deployPlan{backupOwner, failureSignals[{stepId, signal, notify}], manualFallback, changeTriggers[], reviewAfterDays (7..365), createdBy, confirmationState, confirmedBy, confirmedAt}`. (F-16, F-17)
- **B4** `Test`: `id, title, kind (happy_path|exception|regression|attended_run|negative), stepIds[], exceptionIds[], given, when, then, exampleData (max 400), status (proposed|confirmed|passed|failed|skipped), lastRunAt, lastRunId, lastRunDetail, createdBy, provenance`. The names `expected` and `lastResult` used in `coach-spec.md` and `coach-tools.json` mean `then` and (`status`, `lastRunAt`, `lastRunDetail`). (F-18)
- **B5** `ExportRecord`: `id, kind (handoff_brief|process_document|review_packet|blueprint_json|automate_flow_draft), fileFormat (md|json|pdf|docx|csv|automate_draft), scope (blueprint|steps), stepIds[], targetId, blueprintVersion, contentHash, sensitivityAtExport, createdAt, createdBy`. Migration of old `format` values: `spec_markdown` becomes (process_document, md); `spec_json` becomes (blueprint_json, json); `spec_pdf` (process_document, pdf); `spec_docx` (process_document, docx); `csv` (process_document, csv); `automate_flow_draft` becomes (automate_flow_draft, automate_draft). (F-29, F-30)
- **B6** `Diagnostic`: tool-settable set equals the schema's set (the nine added fields in F-25). `Step.environment.systems[]` is tool-settable with `role, accessModes, accessEvidence (host forces claimed on model writes), uiLocator.kind, authModel, profileSystemId`. (F-25, F-26)
- **B7** `Override`/decision reasons: floor value per D4. `chosenToolId` required when `chosenRungId` is not `eliminate`. (F-27, F-28)
- **B8** `AuditEntry`: `actor.type` adds `server`; `details` keys registry: `callId, connectionId, modelId, tool, entityIds[], evidenceRef`; `action` names registered in `x-actions`. (F-23, F-24, F-35)
- **B9** `ApprovalRecord` (new): `{recordId, blueprintId, rev, contentHash, reviewerId, decision (approved|rejected), at, kid, signature}`; carried in `auditEntry.details` when `action = approval_recorded`; the adapter verifies `signature` and recomputes `contentHash`. (F-35)
- **B10** Virtual fields: the schema publishes `x-virtualFields` (`step.derived.domains[]`) and the rule builder's allowed-path list is generated from properties plus virtual fields. (F-21)

### C. Sync and hashes

- **C1** Envelope (unchanged names): `{id, tenantId, rev, baseRev, status, sensitivity, schemaVersion, contentHash, size, clientTs, deviceId, enc{mode, alg, kekVersion}}`. `If-Match: <rev>`. `rev` is the server revision and exists only in the envelope and `sync`. (F-32, F-33)
- **C2** Hash registry: `contentHash` = SHA-256 (hex) of the RFC 8785 canonical Blueprint without `auditLog`, `status`, `updatedAt`, `version`, `sync`, `etag`; `etag` = client-local base64url hash of the canonical Blueprint without `etag` and `sync`; `exportRecord.contentHash` = SHA-256 of the exported bytes; `engine.inputsHash` = SHA-256 of canonical engine inputs; `traceHash` = SHA-256 of the canonical `ruleTrace`. (F-34)
- **C3** Spend: cap micros = round half up (USD x 1,000,000). (F-38)

### D. Policy

- **D1** `Policy`: `schemaVersion` (required integer), `orgId`, `version`, `issuedAt`, `expiresAt`, `signature`, `settings{<key>:{state, value?}}` with `value` present for `locked` and `default`, absent for `user_choice`. Clients validate known keys and ignore unknown non-`x-` keys. (F-08, F-42, F-43)
- **D2** `data.exports.allowedKinds`: null (all) or an array of the five `ExportRecord.kind` values. (F-29)
- **D3** `data.sensitivityRules[class]`: add optional `toolDataFlowCeiling` (local, tenant, vendor_cloud, ai_cloud) with the engine's §3.4 defaults. `llmContentMode` keeps `none`; the engine enum gains it. `OWNER DECISION D6`. (F-03, F-40)
- **D4** `coach.override.reasonMinChars`: minimum per D4. (F-28)
- **D5** AI off: `OWNER DECISION D2`.
- **D6** `ToolCatalogEntry` extension fields (the 12 beyond the contract's 8, as in `$defs/toolCatalogEntry`) become part of the contract, optional. `environment.customTools[]` (orgToolEntry) accepts the same optional fields; defaults when absent: `dataFlow = vendor_cloud`, `unattendedSupport = no`. `capabilities` use the 36-tag enum. (F-11, F-12)

### E. Connection and capability report

- **E1** `Connection`: `id` (`^[a-z0-9][a-z0-9_-]{0,63}$`; built-in `managed`), `type`, `label`, `endpoint` (https; `http` only for loopback `local`), `serverKind` (ollama, lmstudio, foundry_local, llamacpp, vllm, litellm, azure_openai, bedrock, vertex_openai, anthropic_compat, openai, openrouter, generic), `authScheme` (none, bearer, api_key_header, token_provider), `credentialMode` (user_supplied, integrated_oauth, org_vault, none), `credentialRef` (nullable local reference such as a Credential Manager target or token-provider id; never the secret), `extraHeaders` (non-secret only), `modelIdKind` (model, deployment), `contextWindowOverride` (nullable integer), `allowedModels[]` (model keys, A5), `policyRef` (the `orgConnection.id` it came from, or null). Policy `orgConnection` uses the same shape without `credentialRef`. (F-47, F-50)
- **E2** `CapabilityReport` (new, keyed by `connectionId`, `modelKey`, `probeVersion`, endpoint hash): the field set of `model-certification.md` §2.4, plus `toolsInContent`, `thinkLeak`, `silentTruncation`, `toolsPlusSchemaOk`, `serverVersion`, `modelDigest`. Not stored on the Connection. (F-48)
- **E3** Glossary line: "`byok_openrouter` means the customer's own OpenRouter API key. It is unrelated to OpenRouter's 'BYOK' product (provider keys stored inside an OpenRouter account)." `OWNER DECISION D5` covers renaming instead.

### F. Roles

- **F1** Permission matrix source: `tiers.md` §2. `coach-tools.json` role rules are generated from it. `OWNER DECISION D8` on CoE Reviewer. (F-51, F-52)

---

## 9. Owner decisions

| ID | Question | Option A | Option B | Reviewer recommendation |
|---|---|---|---|---|
| D1 | Where does `llm_agent` sit in the ladder? (F-01) | `OWNER DECISION`: `..., llm_node, llm_agent, human_checkpoint` (rules-engine and Blueprint as written). The agent is reachable only for open-ended paths and always carries a warning and a justification card. | `..., llm_node, human_checkpoint, llm_agent` (contract listing order). The agent is a true last resort, selected only when a human checkpoint is forbidden or unfit. | A, because the engine, its fixtures and the schema already encode it and "discouraged" is enforced by the warning and card, not by position. If B, the engine's search order and fixtures need re-running. |
| D2 | How can an admin switch AI off? (F-41) | `OWNER DECISION`: no new key; "AI off" means all five `connections.*.enabled` locked to false, and the portal offers a toggle that writes all five. | Add `coach.ai.enabled` (boolean, state model as usual, Team minimum). `false` means `wizard` mode only and no model traffic. | B: one predicate for mode selection, auditable, and immune to new connection types. |
| D3 | Add a "no interface" value to `interfaceAvailability`? (F-06) | `OWNER DECISION`: keep the `paper_or_phone` exemption, no enum change. | Add `none`. | A. |
| D4 | Reason length floor for overrides (F-28) | `OWNER DECISION`: policy `reasonMinChars` minimum becomes 15 (equal to the Blueprint floor). Tool floor stays 1. | Lower the Blueprint floor to 1 and let policy alone decide (0 to 500). | A: a stored reason shorter than 15 characters defeats the audit purpose and the Blueprint schema is the last line of defence. |
| D5 | Rename `byok_openrouter`? (F-49) | `OWNER DECISION`: keep the name and add the glossary line (E3). | Rename to `own_openrouter_key` (touches the contract, the Blueprint enums, the policy keys, the research, and any shipped bundles). | A. |
| D6 | Add `toolDataFlowCeiling` to the policy? (F-40) | `OWNER DECISION`: add it as an optional per-class field, default per the engine's §3.4. | Keep the engine default only (the field is then removed from `engineEnvironment` `required`). | A: admins need to say "no cloud OCR for restricted". |
| D7 | Group-scoped policy at v1? (F-44) | `OWNER DECISION`: single org bundle. `environment.profiles[].groupIds` is the only group-aware field; per-group sensitivity rules, budgets and reviewers are deferred (matches `tiers.md` L297). Document the multi-group tiebreak: first profile in array order. | Bundles carry a `scope{kind, groupId}` and the server composes an effective bundle per user. | A for v1, reserving an optional `scope` field now. |
| D8 | CoE Reviewer permissions (F-51, F-52) | `OWNER DECISION`: `tiers.md` is authoritative. CoE Reviewer may create and run the Coach, export, and start attended test runs; AutoMate draft and apply stay Admin and Builder. Separation of duties is enforced by the approval gate (approver differs from owner). `coach-tools.json` role rules say "Builder, CoE Reviewer or Admin" except the AutoMate draft and apply tools. | CoE Reviewer is critique-only (coach-tools as written). `tiers.md` rows change to "-" for create, run, and test run. | A, since the server enforces the `tiers.md` matrix and the roles page shows reviewers who also author templates and triage intake. |

---

## 10. Re-run checklist

1. Install `jsonschema` in CI and re-run: meta-validation of both schemas (Draft 2020-12), the two embedded examples, and `tool-catalog.seed.json` against `$defs/toolCatalogEntry`.
2. After F-09, F-10, F-11 land, add a test that a policy-defined org tool and environment profile id validate in a Blueprint.
3. Generate `coach-tools.json` parameter schemas and the policy schema's shared `$defs` (ids, rung list, skill scale, operation tags) from the Blueprint schema so these drift findings cannot recur.
4. Add a round-trip test: every tool in `coach-tools.json`, called with maximal valid arguments, produces a Blueprint that validates.
