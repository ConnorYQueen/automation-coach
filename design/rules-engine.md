# Coach rules engine: the deterministic core

Status: draft, rules pack `0.3.0-draft` (round 3: the owner rulings R2, R3, R4, R5, R7 and the residual ruling S2 of contract section 10, on top of the contract v2 alignment). Date: 2026-10-25. Companion files: `design/blueprint.schema.json` (data shapes, JSON Schema 2020-12), `design/tool-catalog.seed.json` (29 `ToolCatalogEntry` objects) and `design/pattern-library.md` (eleven worked patterns, each proved by engine fixtures). Entity and field names follow `design/00-shared-contract.md` (v2; its section 10, the round 3 rulings, wins over everything else). "Coach" is the product name.

Markers: `ASSUMPTION:` is a guess the owner should confirm. `VERIFY:` is a fact I could not confirm from a source in this session. No price, fee or vendor limit is stated here as fact; the engine never contains a price (section 12.3, CARD-4).

## 0. Reader notes: contract v2 alignment

Contract v2 settled most of what draft 0.1 had to resolve on its own. This table says where the two now meet, and what this file still decides.

| # | Topic | State in this design |
|---|---|---|
| C1 | Ladder order | Fixed by contract v2 and implemented as `eliminate`, `builtin_feature`, `api_connector`, `script`, `ui_automation`, `parser_ocr_ml`, `llm_node`, `human_checkpoint`, `llm_agent`. This **reverses draft 0.1**, which put `llm_agent` before `human_checkpoint`. `llm_agent` is last, is discouraged, always carries `W-AGENT-DISCOURAGED` and a justification card, and is reached only where a human checkpoint is forbidden or unfit. "Unfit" is defined in `RH-AUTH` (section 6.1): a person can take an open-ended step only up to `humanMaxItemsPerRun` items per run. |
| C2 | `Step.override`, `Step.llmJustification` and `Blueprint.decisions[]` | Unchanged. The step fields are the denormalized current record; `decisions[]` is the append-only history. They are linked by `decisionId` (section 12). |
| C3 | `ToolCatalogEntry` | The 8 contract fields plus the 12 optional extension fields now in `$defs/toolCatalogEntry`. `environment.customTools[]` accepts the same fields; when an org tool omits them the engine fails safe: `dataFlow = vendor_cloud`, `unattendedSupport = no`. |
| C4 | Diagnostic | The contract's tool-settable set is the 12 contract fields, `attractorCheck` and the nine engine fields (`operations`, `humanAuthority`, `necessity`, `requiredByControl`, `residualHandling`, `inputVariability`, `pathPredictability`, `inputSize`, `training`). `provenance` is host-written (section 2.1). |
| C5 | "First rung that fits" | Unchanged: the first rung whose inherent predicates hold AND that has at least one tool passing every hard predicate in the actual environment. A blocked rule-based step never falls to a model rung (section 1.3, G5). |
| C6 | `interfaceAvailability` for paper or phone steps | There is no `none` value. Steps whose systems are all `paper_or_phone` are exempt from the question (section 2.1). |
| C7 | What the engine returns when nothing fits | Section 10. |
| C8 | Data-flow ceiling for non-model tools | `toolDataFlowCeiling` is a key of `data.sensitivityRules[class]` in the policy. This file keeps the default values (section 3.4, ASSUMPTION) and reads the policy value when present. `llmContentMode: none` is honored by `T-FLOW` for the model rungs. |
| C9 | Org rules | The policy layer resolves `when` and passes the matching actions. The engine consumes `forbid_rungs`, `forbid_tools`, `require_attended` and `require_adjacent_rung`; the others are obligations (section 3.3). |
| C10 | Org-preferred tools | `environment.preferredToolIds` (ordered) feeds a new first tie-breaker, `TB-0`. It only chooses among tools that already pass every hard predicate at the same rung; it never moves the rung (section 8.1). |
| C11 | Values the user did not state | `Provenance {origin, evidence?}` is stored per diagnostic field, and for process facts and triage answers. The engine reads the value, never the provenance. A value the user chose on a host control has `origin = user_stated` and no `evidence` (ruling S11); a value the Coach extracted from free text is `coach_inferred` and must carry the verbatim quote in `evidence`, which the schema enforces. `Step`, `Exception` and `Test` carry `createdBy`, `confirmationState`, `confirmedBy`, `confirmedAt` and a single `Evidence` as `provenance`. Only a confirmed step is evaluated (G7, gate `G0`). |
| C12 | ROI and graduation | The ROI gate (`TR-3`) is **advisory** until the owner calibrates it from design-partner data; the constants are placeholders and are echoed in the trace. Graduation (LLM to code) is **deferred to v1.x**: the rule spec stays in section 13, nothing in v1 collects run content or calls it. |
| C13 | Hashes | `engine.inputsHash` and `traceHash` are SHA-256 of canonical JSON (RFC 8785) of the inputs and of `ruleTrace` (section 4); the Blueprint-level `inputsHash` also covers the host context (C17). `Blueprint.contentHash`, the hash an approval binds to, leaves out everything this file computes: `x-hashes.contentHash.exclude` in the schema lists `auditLog`, `status`, `updatedAt`, `version`, `sync`, `etag`, `exports`, the root `engine`, `roi`, `steps[].recommendation`, `steps[].llmJustification.costPerRun` (engine-computed, ruling S2), the derived `triage` fields (`verdict`, `rationale`, `conditions`, `warnings`, `ruleTrace`, `engine`) and the run results of `tests[]` (`lastRunOutcome`, `lastRunAt`, `lastRunId`, `lastRunDetail`). The list is generated from the `x-derived` markers, so a new derived property is excluded without a second edit. Re-running the engine under a newer rules pack, appending an export or recording a test run therefore never changes an approved Blueprint's hash, while editing content or confirming a test does. A recomputed `costPerRun` never does (`CH-2`), and a reopen reset always does (section 2.5, `RO-8`). The exclude list has 21 paths; the `reopen` marker is content and is not excluded. |
| C14 | Reopened Blueprints (R3) | A Blueprint that arrives by file import, share or restore opens as `status = draft` with every `confirmationState` reset to `proposed` and `confirmedBy` and `confirmedAt` cleared; `createdBy` and `provenance` are kept as received. The engine ignores unconfirmed values as before: gate `G0` for steps, rule `V-REOPEN` and `Blueprint.reopen.pending` for the three Blueprint-level scopes (sensitivity, process facts, triage answers). The reset changes `contentHash`; a review packet is not reset; a same-owner sync pull is not a restore (the contract's ASSUMPTION). Section 2.5, fixtures `RO-1` to `RO-12`. |
| C15 | Sensitivity order and raising (R4) | `public < internal < confidential < restricted` is published as `x-order` on `$defs/sensitivity`. The engine reads the current class at once, and every evaluated result starts its trace with a `SENS` entry that names the class it used. The model may only raise; lowering is an owner panel action. Section 3.4, fixtures `SE-1` to `SE-8`. |
| C16 | `whyNotCode` provenance (R5) | A `whyNotCode` without `provenance.whyNotCode.origin = user_stated` counts as not provided, with the same consequence as a missing one: the card is incomplete and an LLM override stays `incomplete` (`OV-4`). New rule `CARD-6`. Section 12.3, fixtures `WC-1` to `WC-7`. |
| C17 | Approval-required gate (R2, R7) | One predicate for every trigger, `ApprovalGate`: met by an `approved` ApprovalRecord for the current `contentHash`, or by a SelfAttestation for the current `contentHash` while the host context allows it (plan `free` or `individual`, or `team` with exactly one billable seat; never `enterprise`). `context.plan` and `context.billableSeats` are engine inputs and are hashed into the Blueprint-level `engine.inputsHash`. Sections 3.7 and 12.4, fixtures `AG-1` to `AG-15`. A record counts only when the host has verified its signature, its `kid` and that its `tenantId` equals the Blueprint's tenant. |

## 1. Thesis, scope and guarantees

### 1.1 The model talks; the engine decides

The engine is a pure function:

```
Evaluate(step, blueprintFacts, environment, catalog, rulesPackConfig) -> EngineResult
```

No LLM, no network, no clock, no randomness, no learned weights, no probability, no confidence score. The same inputs always give the same output. The Coach model may interview, structure, explain, draft and critique, but it may only name tools that appear in an `EngineResult` (by `toolId`), and it changes the Blueprint only through narrow tool calls. The one change that takes effect without a confirmation is a sensitivity raise (ruling R4, section 3.4): it can only make the engine's answers stricter, it is audited, and the owner can undo it.

### 1.2 What the engine decides

1. Whether a step is ready to evaluate (`not_confirmed`, `needs_info`).
2. Whether a step must be split before it can be evaluated (`split_required`).
3. The rung and tool for each step, with companions, warnings and a full explanation trace.
4. The risk tier and which human checkpoints are added.
5. The triage verdict and the ROI estimate (section 11).
6. Whether an override stands (section 12).
7. Whether an approval-required gate is met, by an approval or by a self-attestation that the host context allows (section 12.4).
8. (Deferred to v1.x.) Whether an LLM step has run long enough, and stably enough, to propose moving to code (section 13).

### 1.3 Guarantees

| # | Guarantee |
|---|---|
| G1 | **Determinism and replay.** Result = f(inputs). `EngineResult.engine` stores `rulesPackVersion`, `catalogVersion`, `policyVersion` and an `inputsHash`. A different hash means the result is stale. A step result carries a step-level hash; the Blueprint-level hash also covers the facts the engine reads and the host context (section 4). |
| G2 | **No scoring.** Nothing is weighted or ranked by a number. Numbers appear in only three places: named thresholds in hard predicates (for example the minimum labeled examples and the human volume limit), the ROI arithmetic (advisory), and the deferred graduation thresholds. Each is a named constant in the rules pack (section 18.1). |
| G3 | **Auditable.** Every decision carries `ruleTrace` entries: rule id, rung, tool, result, one-sentence reason. "Why not a higher rung" is answered by `rejectedRungs[]`. |
| G4 | **Hard versus soft.** A failed hard predicate removes a tool. A soft predicate yields a `W-*` warning; warnings never remove a tool. They enter the choice only as the second tie-breaker (section 8). |
| G5 | **No downgrade by blockage.** The model rungs open only through their own predicates (`RL-NEED`, and for the agent `RA-OPEN` after the human rung has been ruled out). A rule-based step whose best tool is blocked by the environment or by policy returns `no_fit`, never an LLM. The walk may move from a blocked code rung to a lower code rung (for example `api_connector` to `script`), and records `W-ENV-DOWNGRADE` when it does. |
| G6 | **Catalog only.** `toolId` values come from the catalog. The model cannot add a tool. Off-catalog tools the user mentions are recorded as notes and are never recommended. |
| G7 | **Fail loud.** Missing or contradictory answers return `needs_info` with exact questions. The engine never fills a default for a diagnostic answer. |
| G8 | **Overrides cannot weaken hard tool predicates.** A user may choose a different rung or tool, but only a tool that passes every hard tool predicate (section 6.2). Rung predicates (section 6.1) are the engine's judgment of fit, and that judgment is exactly what an override overrides; the warnings and the justification card exist for that case (section 12). |
| G9 | **Environment is an input, not a fallback.** The engine evaluates twice, once in an open environment and once in the real one. The difference is reported (`envDelta`), so the user sees what the environment costs them. |

### 1.4 How the examples in this file were produced

The traces in sections 15 and 16 and the Blueprint in section 19 were produced by a throwaway Python reference implementation of this spec. It is not part of the deliverable. Treat the expected results as the test suite for the real implementation. The Blueprint in section 19 was validated against `blueprint.schema.json` with Python `jsonschema` 4.26.0 (Draft 2020-12), and the schema rejected 95 deliberately broken variants and accepted 32 valid ones (unknown rung, unknown property, unknown operation tag, unknown decision kind, unknown locator kind, version below 1, a 14-character override reason, an override without `chosenToolId`, a confirmed entity without `confirmedBy`, a `blueprint_json` export with the wrong file format, `schemaVersion` 2.0, the old `baseVersion` sync field, `interfaceAvailability: none`, the skill value `beginner`, and others). The same 29 catalog entries were validated against `$defs/toolCatalogEntry`. Round 3 added 44 of the rejected variants (a confirmed card whose `whyNotCode` is not `user_stated`, a proposed entity that still carries `confirmedBy`, a `reopen` marker on a Blueprint that is not a draft, a team context without `billableSeats`, a `sensitivity_tightened` entry that lowers the class, a `blueprint_backup_deleted` entry without `revisionCount`, a `coach_inferred` risk fact without a quote, an approved Blueprint whose step lacks the `attractorCheck` that `V-ATTR` asks for, a `cardRequired` step without a confirmed card, a text ROI constant, a graduation proposal that carries `kind`, an `approval_recorded` record without `tenantId`, and others) and 27 of the accepted ones (the new audit actions, risk facts and triage answers given on a control without evidence, a confirmed step still waiting for its `attractorCheck`, a card the engine has not priced yet, the decision record that wraps a graduation proposal, the new contexts and reopened copies of the example). The JSON blocks of this file (the diagnostic example, `MINI` of 16.4, the card of 16.6, the graduation proposal of 16.3 and the Blueprint of section 19) and every fixture step of sections 15 and 16 were also validated with a second Draft 2020-12 validator that resolves the schema references and checks formats, with no failure.

Suite totals. Every case passes in the reference run.

| Suite | Cases | Where |
|---|---|---|
| Step evaluation fixtures `FX-01` to `FX-51` | 51 | Section 15 |
| Triage and ROI cases `TX-01` to `TX-13` | 13 | 16.1 |
| Override cases `OV-01` to `OV-17` | 17 | 16.2 |
| Graduation cases `GX-01`, `GX-02` (deferred) | 2 | 16.3 |
| Round 3: reopen `RO-1` to `RO-12`, sensitivity `SE-1` to `SE-8`, `whyNotCode` `WC-1` to `WC-7`, approval gate `AG-1` to `AG-15`, hashes `CH-1` to `CH-4` | 46 | 16.4 to 16.8 |
| Pattern fixtures (eleven patterns) | 41 | `design/pattern-library.md` |
| Schema: broken variants rejected, valid variants accepted | 95 and 32 | Section 19 |

## 2. Inputs: the step diagnostic

All fields live under `Step.diagnostic` unless noted. `unknown` means "not answered" and behaves as missing.

### 2.1 Field registry

**Contract fields**

| Field | Values | Need | How the engine uses it |
|---|---|---|---|
| `inputStructure` | structured, semi_structured, free_text | always | Validation (`V-CONFLICT` with `ocr_text`) and explanation only. The rung decision reads `operations`, `languageUnderstanding` and `inputVariability`, because the label "semi-structured" does not say what must be done with the input. |
| `outputDeterminism` | yes, mostly, no | always | `ruleCore`, parser eligibility, hybrid patterns, attractor evidence. |
| `costOfError` | low, medium, high | always | Risk tier (section 7). |
| `reversibility` | reversible, partly, irreversible | always | Risk tier. |
| `frequency` | ad_hoc, daily, weekly, monthly, continuous | optional | Context only. The ladder does not change with how often a step runs. ROI uses the process-level frequency (section 11). |
| `volumePerRun` | integer | optional | `T-SIZE` against `limits.maxItemsPerRun`. |
| `interfaceAvailability` | api_available, file_exchange, ui_only | always, except when every system is `paper_or_phone` | Default access modes per system (section 2.4). There is no `none` value; the exemption keeps the schema honest for a phone call or a paper form. |
| `attendance` | attended, unattended, either | always | `T-EXEC`, `T-CRED`, `RA-ATT`. `either` is evaluated as attended and adds `W-ATTENDED-ONLY` if the chosen tool needs a person present. |
| `credentialsRequired` | yes, no | always | `T-CRED`; triggers the `authModel` question. |
| `dataSensitivity` | public, internal, confidential, restricted | optional | Effective class = the stricter of this and `Blueprint.sensitivity` (section 3.4). |
| `languageUnderstanding` | none, some, core | always | `needsUnderstanding`. |
| `judgmentRequired` | no, sometimes, yes | always | `ruleCore`, `RH-AUTH`, residual handling. |
| `attractorCheck` | `{ruleAttempt, whereItBreaks}` | conditional | See 2.3. |

**Engine extension fields** (all additive to the contract's diagnostic)

| Field | Values | Need | How the engine uses it |
|---|---|---|---|
| `operations` | array of operation tags (2.2) | always, at least one | The unit of tool coverage (`T-COVER`) and of splitting. |
| `humanAuthority` | none, approval_required, accountable_decision | optional, default none | A named person must approve or own the outcome: adds `approve_decision` and opens `RH-AUTH`. |
| `necessity` | required, output_unused, duplicate_of_step, available_upstream | optional, default required | `E-1` (eliminate). |
| `requiredByControl` | boolean | optional, default false | Blocks elimination when an audit or policy control needs the step. |
| `residualHandling` | human_review, fallback_rule, llm | conditional | What happens to cases the rules cannot decide (section 14). |
| `inputVariability` | fixed_layout, few_templates, many_templates, unbounded | conditional | Parser tools (`T-VAR`) and the unbounded-extraction trigger for `needsUnderstanding`. |
| `pathPredictability` | fixed, branching_known, open_ended | optional | `RA-OPEN` (agent rung). |
| `inputSize` | small, medium, large | optional | `T-SIZE` against `limits.maxInputSize`. |
| `training` | `{examples, classCount, labelSetStable}` | conditional | Trained classifier eligibility (`RP-PARSE`, `T-TRAIN`). |
| `provenance` | object: field name to `{origin, evidence?}` | optional, host-written | `origin` is `user_stated`, `coach_inferred` or `engine_derived`. **Controls and quotes (ruling S11).** A closed-choice value the user clicked on a host control (`show_control`) is `user_stated` and has no `evidence`: the model cannot forge a click. The verbatim-quote rule applies to values the model extracts from free text (numbers such as `volumePerRun` and `training`, process facts, names): they are `coach_inferred` and `evidence` is `{source, turnId, quote}`; the schema requires it (`coach_inferred` without `evidence` is rejected, with or without a risk fact). `engine_derived` needs none. Not read by the rules. A value the user never stated and the user never confirmed cannot reach the engine, because only a confirmed step is evaluated. |

**Who may set what.** `x-toolSettable` in the schema lists the diagnostic fields the Coach may help fill: the 12 contract fields, `attractorCheck` and the nine engine fields above. The model never writes a closed-choice value. It asks the question and the host shows a control (`show_control`; ruling S12 puts every closed-choice field the engine reads on controls), and the user's click is the value and the confirmation. Only the numbers the user states in words (`volumePerRun`, `training`) go through a Coach chip (`record_diagnostic_answers`) that the user accepts. `provenance` is never settable by the model; the host writes it: `user_stated` without `evidence` for a control answer, `coach_inferred` with a verbatim quote for an accepted chip (the host checks the quote against the cited turn). Writing any field returns the step to `proposed` and marks its recommendation stale.

**Required, conditional and conflict rules (validation stage)**

| Rule | Fires when | Result |
|---|---|---|
| `V-MISSING` | A required field is missing or `unknown`; `operations` is empty; a tag in `operations` is unknown. | `needs_info` with one `missing[]` item per field. |
| `V-CONFLICT` | `languageUnderstanding = none` but a language operation is listed; `outputDeterminism = yes` with `judgmentRequired` in {sometimes, yes}; `outputDeterminism = no` with `judgmentRequired = no` and `languageUnderstanding = none`; `inputStructure = structured` with `ocr_text`. | `needs_info` with `kind = conflict` and a question that names both answers. |
| `V-ATTR` | `outputDeterminism` in {mostly, no}, or `languageUnderstanding` in {some, core}, or `judgmentRequired` in {sometimes, yes}, or the step extracts fields from documents of unbounded layout; and `attractorCheck` is absent or either text is shorter than 10 characters. | `needs_info` asking "What rule did you try, and where does it give the wrong answer?" |
| `V-RESID` | (`outputDeterminism = mostly` or `judgmentRequired = sometimes`) and `languageUnderstanding = none` and `residualHandling` absent. | `needs_info`. |
| `V-VAR` | An extraction operation other than `ocr_text` is listed and `inputVariability` is absent. | `needs_info`. |
| `V-TRAIN` | `classify_text` is listed and `training` is absent. | `needs_info`. |
| `V-AUTH` | `credentialsRequired = yes`, `attendance` in {unattended, either}, and a system has no `authModel`. | `needs_info` naming the system. |
| `V-REOPEN` | `Blueprint.reopen.pending` contains `sensitivity` (section 2.5): the class that decides routing was received, not re-confirmed. | `needs_info` with one `missing[]` item, `questionId = blueprint.sensitivity`. No rung is computed. |

Validation runs before anything else is computed and reports one group at a time: (1) missing base fields and operations, (2) conflicts, (3) conditional fields. Each round of questions stays short, and a conditional question is never asked on top of contradictory answers.

### 2.2 The operation vocabulary

`operations` holds one or more of these 36 tags. The Coach proposes them from the user's narrative; the user confirms each tag value as a chip, and the engine ignores any tag still waiting in the proposal queue; the engine takes confirmed values as given. Tools declare which tags they cover in `capabilities[]` (the contract field), so a tool's coverage and a step's need are compared in one vocabulary.

| Class | Tag | Meaning |
|---|---|---|
| data | `calculate` | Arithmetic, totals, derived numbers. |
| data | `aggregate_group` | Sum, count, pivot or group records. |
| data | `lookup_join` | Look up or join values from another list or table. |
| data | `filter_sort_dedupe` | Filter, sort or remove duplicates. |
| data | `validate_rules` | Check values against explicit rules (required, range, format, cross-field). |
| data | `format_convert` | Convert formats (CSV to Excel, date or unit formats). |
| data | `transform_text_pattern` | Change text by fixed patterns (replace, split, join). |
| data | `file_operations` | Copy, move, archive, create folders. |
| data | `rename_files` | Rename files by a pattern. |
| data | `route_by_rule` | Send an item somewhere by explicit rules on its data. |
| data | `route_message_by_header` | Route email by sender, subject or headers only (the case mail rules cover). |
| data | `generate_report` | Assemble a fixed-layout report from data. |
| move | `transfer_data` | Move data from one system to another. |
| move | `sync_records` | Keep records in two systems consistent. |
| move | `call_api` | Call a documented web API or connector. |
| move | `query_database` | Run a query against a database. |
| move | `scrape_web` | Read data from web pages. |
| move | `send_message` | Send an email or chat message from a template. |
| ui | `read_from_ui` | Read values from an application screen. |
| ui | `write_to_ui` | Type or click into an application screen. |
| extract | `extract_fields_pattern` | Pull fields from text or documents by fixed position or pattern. |
| extract | `ocr_text` | Turn images or scans into text. |
| extract | `extract_fields_document` | Pull labeled fields from documents whose layout varies (invoices, forms). |
| language | `classify_text` | Assign a label to free text. |
| language | `extract_entities_freetext` | Pull names, dates, amounts from prose. |
| language | `summarize_text` | Summarize. |
| language | `generate_text` | Draft new text. |
| language | `translate_text` | Translate. |
| language | `answer_over_text` | Answer questions over documents. |
| language | `judge_quality` | Judge whether text or work meets a standard. |
| language | `plan_open_ended` | Choose the next action at run time (no fixed path). |
| human | `approve_decision` | A person approves or rejects. |
| human | `exception_review` | A person reviews flagged cases. |
| human | `physical_action` | Something done in the physical world (a call, a signature, a delivery). |
| wrapper | `schedule_trigger` | Start on a schedule. |
| wrapper | `event_trigger` | Start when something happens. |

**Wrapper tags** are not part of coverage. A tool that lacks the trigger gets a trigger companion (section 7.3).

**Derived operation.** The engine appends `approve_decision` when `humanAuthority` is `approval_required` or `accountable_decision`, or when the step is a pure judgment (2.3) and lists no human operation. The derived tag is shown in the trace so the user can see why a human tool appeared.

### 2.3 Derived flags

Computed once per step, shown in the trace.

```
languageOps          = any operation in class language
unboundedExtraction  = inputVariability = unbounded AND any of {extract_fields_document, extract_fields_pattern}
needsUnderstanding   = languageUnderstanding in {some, core} OR languageOps OR unboundedExtraction
ruleCore             = NOT needsUnderstanding AND outputDeterminism in {yes, mostly} AND judgmentRequired in {no, sometimes}
pureJudgment         = NOT needsUnderstanding AND (judgmentRequired = yes OR outputDeterminism = no)
```

`ruleCore` opens the code rungs (builtin, api, script, UI). `needsUnderstanding` opens the model rungs. `pureJudgment` opens the human rung without a model. The three are mutually reinforcing, not exclusive: a mostly-rule step with `judgmentRequired = sometimes` is `ruleCore` and gets a residual companion (section 14).

**The attractor check.** A step may reach a model rung only when the record shows what rule the user tried and where it breaks (`RL-EVID`). This is the engine's guard against reaching for an LLM first. The text is evidence, not a score: the engine checks only that both strings exist and are at least 10 characters. Whether the evidence is persuasive is a human review question (the CoE reviewer sees it in the card). The schema does not demand the check while a step is being captured: a confirmed step with `outputDeterminism = mostly` and no `attractorCheck` is the state in which `V-ATTR` answers `needs_info` (`FX-34`), so it must validate. The root rule requires `attractorCheck` on a step whose diagnostic triggers the check only once the Blueprint is `approved`, `built` or `deployed`.

### 2.4 Systems and access modes (`Step.environment`)

`Step.environment` is per step. It holds `systems[]`, `builderSkill` (none, basic, intermediate, advanced; an unset value reads as `basic`, which is also the default of `prefs.skillLevel`; the engine never reads preferences, so a host that wants the user's own level used writes it into the step; the one skill scale, shown to users with its own labels) and `alreadyHasToolIds[]`. System names come from `record_environment_facts` (each name is a chip the user accepts and is stored with `kind unknown`). `kind`, `role`, `accessModes`, `uiLocator.kind`, `authModel`, `profileSystemId`, `builderSkill` and `alreadyHasToolIds` are closed choices the user answers on host controls (`show_control`). The host forces `accessEvidence` to `claimed` on every write; only an inspection result may set `verified`.

| System field | Values |
|---|---|
| `name` | Free text; also the key for splitting. |
| `kind` | web_app, desktop_app, terminal_or_mainframe, spreadsheet_or_file, email_or_calendar, database, api_service, paper_or_phone, unknown |
| `role` | source, target, both, lookup |
| `accessModes` | Optional explicit list from `builtin`, `connector`, `api`, `scriptable`, `file_or_db`, `http_html`, `ui`, `none`. |
| `accessEvidence` | verified, claimed, unknown. The host forces `claimed` on model writes; only an inspection result may set `verified`. |
| `uiLocator.kind` | automation_id, name_or_control_type, dom_selector, image_or_coordinates, unknown |
| `authModel` | sso, service_account, shared_login, mfa_interactive, none, unknown |
| `profileSystemId` | Links the system to an entry in the org environment profile. |

**Access modes** say how a tool can reach a system. `builtin` is a feature of the application itself (a spreadsheet formula, an email rule). `connector` is a prebuilt connector in a flow tool. `api` is a documented web API. `scriptable` is an object model or command line a script can drive. `file_or_db` is a file or database a script or query can open. `http_html` is a web page readable without a browser engine. `ui` is the screen only.

**Effective access modes** (when `accessModes` is not given):

| Rule | Result |
|---|---|
| `interfaceAvailability = api_available` | `{api, connector, scriptable}` |
| `interfaceAvailability = file_exchange` | `{file_or_db, scriptable}` |
| `interfaceAvailability = ui_only` | `{ui}` |
| `kind = paper_or_phone` | `{}` (no automation access) |
| `interfaceAvailability` is not `ui_only` and `kind` is `spreadsheet_or_file` or `email_or_calendar` | add `builtin` |
| ... and `kind = spreadsheet_or_file` | add `file_or_db`, `scriptable` |
| ... and `kind = database` | add `file_or_db` |
| The linked profile system says `api = unavailable` | remove `api`, `connector` |

If a system gets `api` or `connector` access with `accessEvidence` of `claimed`, `unknown` or absent, and the tool uses those modes, the engine adds the soft warning `W-API-UNVERIFIED`. It never accepts the claim silently and never rejects it.

### 2.5 Reopened Blueprints (ruling R3)

A Blueprint that arrives by **file import**, by **share** or by **restore** from backup or history is not trusted as confirmed. The person who opens it did not confirm those values in this copy, and an approval or self-attestation made on the sender's copy is bound to a hash the opened copy no longer has. It therefore opens for editing as a draft with every confirmation reset. Two cases are not arrivals. A **review packet** (an export of kind `review_packet`) opens read-only and unmodified, so its `contentHash` equals the owner's and the reviewer's ApprovalRecord applies to it (`RO-9`). A normal **sync pull** of a newer revision of the same Blueprint onto the same owner's own devices keeps its state (`RO-10`); this is the contract's own ASSUMPTION, since otherwise every device sync would reset confirmations.

`Reopen(blueprint, via, now, actor, auditIds)` is a pure function; the reference implementation takes the clock and the two audit ids as inputs, so a test can repeat it. `via` is `import`, `share`, `restore` or `sync_pull`; `sync_pull` returns the Blueprint unchanged. For the other three it makes these changes and no others:

| Change | Detail |
|---|---|
| Status | `status = draft`; `version` plus 1; `updatedAt = now`. |
| Confirmations | Every step, exception, test and the deploy plan gets `confirmationState = proposed`, and `confirmedBy` and `confirmedAt` are removed (the schema forbids both on a `proposed` entity). A test's `status` follows. `createdBy` and `provenance` are kept as received. |
| Justification cards | A step card, or a decision of kind `llm_justification`, with `cardState = confirmed` becomes `proposed`. Its text and its provenance are kept. |
| Derived values | Every `Step.recommendation` is marked `stale`; the `triage` verdict, rationale, conditions, warnings, trace and engine meta are cleared; `roi` is dropped. They come back when the user has re-confirmed the inputs. |
| Reopen marker | `reopen {via, at, pending}` with `pending = [sensitivity, process, triage]`. The schema requires `status = draft` whenever `reopen` is present. |
| Audit | Two entries: `blueprint_imported`, `blueprint_share_received` or `blueprint_restored`, then `confirmations_reset` with `details.counts {steps, exceptions, tests, deployPlan, cards}`, the number of entities that went from confirmed to proposed. |

Overrides, decisions and exports are kept as received. An override is re-validated by `OV-1` to `OV-6` when its step is confirmed again.

**What the user re-confirms.** The ruling names two kinds of content.

| Kind | Fields | How it is confirmed |
|---|---|---|
| Engine-read values, one by one | Every `diagnostic` field of every step; the tool-settable fields of `environment.systems`; `triage.answers`; `process.frequency`, `process.volume`, `process.timePerRunMinutes` and `process.people`; `sensitivity` | The host asks again with its option controls; the answer to a closed choice is the confirmation. |
| Free-text entities, per entity | Step name and description, exception text, process summary | One action per entity: "keep this step", "keep this exception". |

`process.people` is not in the contract's list; I added it because triage and ROI read it (ASSUMPTION).

**What the engine ignores.** The contract says the engine ignores unconfirmed values, as before. The Blueprint has no per-field confirmation flag (`provenance` records where a value came from, not whether it was confirmed again), so the engine uses two signals.

- For a step, the step's own `confirmationState` (gate `G0`). A `proposed` step returns `not_confirmed` and gets no recommendation (`RO-2`). The host sets a step to `confirmed` only after the user has re-confirmed its diagnostic and system values and kept the step (ASSUMPTION: one step flag stands for all of its fields).
- For the three Blueprint-level scopes, `reopen.pending`. A pending value is treated exactly like a missing one. While `sensitivity` is pending, every confirmed step returns `needs_info` with the single item `blueprint.sensitivity` (rule `V-REOPEN`, `RO-3`). I chose this over a fail-safe class such as `restricted` because the engine never fills a default for an answer (G7), and the class decides routing and ceilings. While `triage` is pending, the seven answers are missing (`RO-5`); while `process` is pending, the four process facts are missing (`RO-6`); see 11.1.

The host removes a scope from `pending` when every value in it has been confirmed, and removes `reopen` itself when nothing is pending (`RO-4`, `RO-7`). Once a step is kept and the sensitivity is confirmed, its recommendation equals the one before the reset, because a step never reads the process or triage scopes.

**Hash effects.** The reset changes content, so `contentHash` changes (`RO-8`, `RO-12`): an approval or a self-attestation never transfers to a reopened copy. A review packet keeps its hash (`RO-9`, `RO-12`). The Blueprint-level `engine.inputsHash` includes the sorted `reopen.pending` scopes (section 4).

## 3. Environment: the `EngineEnvironment` projection

### 3.1 Why a projection

The engine never reads policy, settings or connections directly. The policy layer builds one read-only `EngineEnvironment` per evaluation (`blueprint.schema.json` `$defs/engineEnvironment`). This keeps the engine pure, makes the environment part of the `inputsHash`, and lets the same engine run client-side and in the sync server.

### 3.2 Mapping

| `EngineEnvironment` field | Built from | Predicates that read it |
|---|---|---|
| `os.softwareInstallPolicy` | `environmentProfile.os.softwareInstallPolicy` (free, request_approval, locked_down) | `T-INST` |
| `scripting.allowed`, `languages`, `powershellExecutionPolicy`, `signedScriptsOnly`, `unattendedRequiresReview` | `environmentProfile.scripting` | `T-SCRIPT` |
| `installedToolIds` | Union of `providesToolIds` over `environmentProfile.software[]` with status `installed`. ASSUMPTION: software with status `prohibited` adds its `providesToolIds` to `tools.forbiddenToolIds`. | `T-INST`, `TB-1` |
| `tools.permittedToolIds`, `forbiddenToolIds`, `permittedRungIds`, `forbiddenRungIds` | `environmentProfile.tools` (forbidden always wins; an omitted list is unrestricted; `[]` is nothing) | `T-PERM` |
| `network.internetAccess` | `environmentProfile.network.internetAccess` | `T-FLOW` |
| `llm.availableConnectionTypes` | The connection types the user or org has actually configured and that the network lets through (`Connection` records, `connections.*.enabled`, `network.llmEndpointsReachable`). | `T-FLOW` |
| `systems[]` | `environmentProfile.systems[]` (`api` available, restricted, unavailable, unknown) | Effective access modes |
| `runners[]` | `environmentProfile.automationRunners[]` (kind, platform, credentialModel, unattendedAllowed) | `T-EXEC`, `T-CRED` |
| `sensitivityRules` | `data.sensitivityRules` (`llmConnectionTypes`, `llmContentMode`, `toolDataFlowCeiling`); an unset ceiling takes the default in 3.4 | `T-FLOW` |
| `policy.llmAgentMode` | `coach.llmAgent.mode` (`forbidden`, `approval_required`, `allowed_with_justification`) | `T-PERM` (`forbidden` removes the rung) |
| `preferredToolIds` | `environmentProfile.preferredToolIds` (ordered; position is the rank) | `TB-0` |
| `customTools[]` | Org tools (`org.<id>`) with the same optional fields as a catalog entry; absent `dataFlow` is `vendor_cloud` and absent `unattendedSupport` is `no` | merged into the catalog for the real and the relaxed walk, not the ideal walk |
| `orgRules[]` | Resolved actions of org rules whose `when` matched this step | `T-PERM`, `ORG-*`, companions |

### 3.3 Org rules

The policy layer evaluates each `orgRule.when` against the step and Blueprint, and passes the matching actions as `{id, type, severity, ...}`:

| Action `type` | Engine behavior |
|---|---|
| `forbid_rungs` | Hard, policy class: `ORG-<id>` fails every tool on those rungs. |
| `forbid_tools` | Hard, policy class: `ORG-<id>` fails those tools. |
| `require_attended` | If `severity = block` (the default): hard, policy class, applies to unattended steps and to every rung except `eliminate` and `human_checkpoint`. ASSUMPTION: a rule with severity `warn` or `info` yields the warning `W-ORG-<id>` instead, because a recommendation that violates a blocking rule can never be approved. |
| `require_adjacent_rung` | Adds a companion `{role: org, rungId, placement}` with `toolId: null`. The Coach asks the user to add that step; the policy layer verifies it later. |
| `require_field`, `require_approval`, `raise_sensitivity`, `block_gate` | Not read by the engine. Obligations checked by the policy layer after the recommendation. |

### 3.4 Sensitivity classes and data flow

**Effective class** = the stricter of `Blueprint.sensitivity` and the step's `dataSensitivity`.

**Order and raising (ruling R4).** The classes are ordered `public < internal < confidential < restricted`, weakest first. The schema publishes the order as `x-order` on `$defs/sensitivity`, and "stricter" always means later in that order. The Coach model has exactly one tool that changes the class, `raise_sensitivity` in `design/coach-tools.json`, and it can only tighten: the host rejects a call whose target is not strictly stricter than the current class (error `sensitivity_not_tightening`). An accepted raise applies at once, with no chip, shows an undo notice, and is audited as `sensitivity_tightened` (`details {from, to, turnId}`). The undo, and every lowering by the owner in the panel, is audited as `sensitivity_changed` (`details {from, to, via}`). Lowering is never a model action, and it is subject to `data.sensitivityRules`.

The engine has no special path for any of this. It reads `Blueprint.sensitivity` as it stands when it evaluates, so a raise changes the next evaluation, including the `toolDataFlowCeiling` filtering of `T-FLOW` and the `llmContentMode` used for model tools (`SE-2`, `SE-3`, `SE-6`). Routing of the next model call follows from the same class (a host duty, outside the engine). A raise to `restricted` also makes the Blueprint local-only (architecture, ruling S4): new revisions stop uploading, and the owner's one-click "Delete backed-up copies" removes every server revision including the version history (ruling S6) and is audited as `blueprint_backup_deleted` (`details {revisionCount, includesHistory}`). The engine reads neither. The class is part of every step's `inputsHash` (and of the Blueprint-level one). A raise, an undo and an owner lowering therefore change the hash of every step whose effective class changes: its stored recommendation counts as `stale` because its `engine.inputsHash` no longer equals the current one, and the next evaluation recomputes from the new class (ruling S14, `SE-8`). An override recorded under the old class becomes `stale` too (`OV-6`). A step whose own `dataSensitivity` already decides the effective class keeps its hash and its result (`SE-5`, `SE-8`).

**The `SENS` trace entry.** Every evaluated result (status `ok` or `blocked_by_policy`) starts its `ruleTrace` with one `SENS` entry of result `info`. It names the effective class, which side set it (the Blueprint or the step; a tie is credited to the Blueprint), both inputs, the `toolDataFlowCeiling` (after the hard cap below) and the `llmContentMode` that apply. The Coach quotes it when it explains why a tool disappeared after a raise (`SE-1` to `SE-6`).


Default matrix. The connection-type and content-mode columns repeat the default of `data.sensitivityRules` in `design/settings-catalog.md` section 4. The ceiling column is the default of the policy key `toolDataFlowCeiling` (C8); the values are mine (ASSUMPTION) and the policy may set others. `llmContentMode` can also be `none`, which means no content of that class may be sent to any model: `T-FLOW` then fails every model tool for the class (policy failure).

| Class | `llmConnectionTypes` | `llmContentMode` | `toolDataFlowCeiling` (ASSUMPTION) |
|---|---|---|---|
| public | managed, byok_openrouter, byok_provider, custom_openai_compat, local | full | ai_cloud |
| internal | same five | full | ai_cloud |
| confidential | managed, custom_openai_compat, local | redacted | tenant |
| restricted | local | redacted | local |

The same policy matrix has columns the engine does not read. `exportAllowed` is yes for every class by default, `restricted` included, because a local export never uploads anything (ruling R2); `requireApprovalBeforeHandoff` is yes for `restricted` only. They decide whether an approval gate applies; section 12.4 decides whether it is met. The columns above match the defaults in `design/settings-catalog.md` section 4.

**Data-flow classes** (a property of each catalog tool, `dataFlow`), from most to least contained:

| Class | Meaning |
|---|---|
| `local` | Data stays on the machine that runs the tool. |
| `tenant` | Data goes to a service inside the organization's own cloud tenant or subscription. VERIFY per tool: whether a given service really keeps data inside the customer's tenant depends on how the org configures it. |
| `vendor_cloud` | Data goes to a third party's cloud service that processes it (an integration platform, for example). |
| `ai_cloud` | Data goes to an AI model provider. |

**Hard cap.** Whatever the policy says, the ceiling for `restricted` never exceeds `tenant`, so a mis-set policy cannot send restricted data to a vendor cloud through a non-model tool. The ceiling applies to org tools too, and an org tool that omits `dataFlow` is treated as `vendor_cloud`.

**Model tools** (those with `connectionTypes`) are checked differently: allowed types = the tool's `connectionTypes` that are also in the class `llmConnectionTypes` and also in `llm.availableConnectionTypes`; an `air_gapped` network allows only `local`. An empty class intersection is a **policy** failure. An empty result after intersecting with what is configured is an **environmental** failure ("no such connection is set up here").

**Hosts.** A tool that runs inside another tool (a document-extraction service called from a script, a model called from a flow) takes the larger data flow of the two (`TB-5`, and `T-FLOW` is checked for the host too).

### 3.5 Runners

`runners[]` says who or what runs finished automations. An unattended step needs a runner with `unattendedAllowed = true` on a platform the tool supports. Tools that declare `unattendedSupport = needs_host` (they need a signed-out or dedicated machine) additionally need a runner of kind `unattended_vm` or `server_scheduler`. `T-CRED` also needs an unattended runner whose `credentialModel` is `service_account` or `vaulted_secret` (section 6.2).

### 3.6 No environment profile

When `Blueprint.environmentProfileRef` is empty (typical for Individual users), the host builds the environment from answers collected at the `environment_fit` stage (can you install software, is scripting allowed, what machine would run it unattended, which model connections do you have). Anything unanswered takes the stricter value: no unattended runner, no extra connection types. ASSUMPTION: this default favors an honest `no_fit` over an optimistic recommendation the user cannot run. The engine itself does not distinguish the two cases.

### 3.7 Host context for the approval gate (rulings R2 and R7)

The engine reads two facts that belong neither to the environment profile nor to the Blueprint: the entitlement `plan` (`free`, `individual`, `team`, `enterprise`) and, for a team, the number of billable seats (Admin, CoE Reviewer or Builder; Viewers are free and are not counted). The host supplies them as `context {plan, billableSeats}`, taken from the signed entitlement and the organization roster; the engine never reads a token. They are engine inputs, so they are hashed into the Blueprint-level `engine.inputsHash` (section 4), and the context used is stored as `Blueprint.engine.context`. They are not part of any step's `inputsHash`, so a plan or seat change never makes a recommendation or an override `stale` (`OV-6`, `AG-14`), and they never enter the Blueprint's content. A missing or unknown context fails closed: no self-attestation is accepted (`AG-9`).

## 4. Output: `EngineResult`

One result per step. Shape in `blueprint.schema.json` `$defs/stepResult`; the persisted subset is `Step.recommendation`.

| Field | Meaning |
|---|---|
| `stepId`, `engine{rulesPackVersion, catalogVersion, policyVersion, inputsHash, computedAt}` | Identity and reproducibility. `inputsHash` is the SHA-256 (hex) of the RFC 8785 canonical JSON of the engine inputs. **Step level** (`Step.recommendation.engine`): the step diagnostic without `provenance`, `Step.environment`, the effective sensitivity class, the `EngineEnvironment` (including `preferredToolIds` and `customTools`), the catalog version and the rules-pack constants. **Blueprint level** (the root `Blueprint.engine`, with the host context stored beside it as `engine.context`): the step hashes with their confirmation states, `Blueprint.sensitivity`, the triage answers, the process facts, the sorted `reopen.pending` scopes and the host `context {plan, billableSeats}` (section 3.7). The step level carries no gate context, so a plan change never stales a recommendation or an override. `traceHash` (stored on an override decision) is the same hash over the canonical `ruleTrace`. |
| `status` | `ok`, `needs_info`, `blocked_by_policy`, `not_confirmed`. |
| `outcome` | `recommended`, `eliminate`, `split_required`, `no_fit`; null for `needs_info` and `not_confirmed`. |
| `rungId`, `toolId` | The recommendation (contract fields). Null unless `outcome` is `recommended` or `eliminate`. |
| `hostToolId`, `bundle[]` | The tool that runs the recommended tool; the up-to-three same-rung tools that together cover the step. |
| `companions[]` | `{role, rungId, toolId, ruleId, why}`. Roles: `trigger`, `review`, `approve`, `residual`, `org`. |
| `hybrid{pattern, spine{rungId, toolId}}` | Section 14. |
| `riskTier` | A, B, C or D (section 7). |
| `cardRequired` | True when an LLM justification card is needed (section 12.2). |
| `rationale[]` | Plain-language sentences generated from fixed templates. The Coach may rephrase them; it may not change the conclusion. |
| `alternatives[]` | `{rungId, toolId, whyNot}`: tools that also pass but lost, and later rungs that would also fit. |
| `rejectedRungs[]` | `{rungId, rule, whyNot, stage, toolId?, failedRules?}` for every rung before the chosen one. |
| `warnings[]` | `{ruleId, text}`, all `W-*` (section 6.3). |
| `policyNotes[]` | Obligations the engine knows about (for example, a reviewer must approve an `llm_agent` step). |
| `missing[]` | `{questionId, field, kind, ask}` for `needs_info`. |
| `ruleTrace[]` | `{ruleId, rungId?, toolId?, result, class?, because}` in evaluation order. |
| `proposedSplit[]` | `{name, operations, systemName?, role?, decisionPoints?}` for `split_required`. |
| `envDelta[]` | `{rungId, toolId, ideal, blockedBy[{ruleId, class, change}]}`: what in the environment separates the ideal choice from the actual result. |
| `policyRelaxedFit` | Only for `blocked_by_policy`: the tool that would fit if the policy rules were relaxed. For admins and CoE reviewers, never offered to the builder as a workaround. |
| `manualFallback` | Only for `no_fit`: `{rungId: human_checkpoint, toolId: human.manual_task}`. |

**Status and outcome matrix**

| `status` | `outcome` | When |
|---|---|---|
| `ok` | `recommended` | A rung and tool were chosen. |
| `ok` | `eliminate` | The step can be removed (`E-1`). |
| `ok` | `split_required` | A structural split is needed (section 10.1). |
| `ok` | `no_fit` | No tool fits this step here and no fit appears even with policy relaxed, or no catalog tool covers the step at all. |
| `blocked_by_policy` | `no_fit` | No tool fits here, but one would fit if policy rules were relaxed. |
| `needs_info` | null | Missing or contradictory answers. |
| `not_confirmed` | null | The user has not confirmed the step. Proposed steps are never evaluated. |


## 5. The pipeline for one step

```
Evaluate(step, blueprintFacts, env, catalog, cfg):

  G0  gate        if step.confirmationState != confirmed
                    return {status: not_confirmed}
  V   validate    missing, conflicts = Validate(step)            // 2.1, V-REOPEN (2.5)
                  if any: return {status: needs_info, missing[], ruleTrace: V-*}
  D   derive      ops   = step.operations + derived approve_decision    // 2.2
                  flags = {needsUnderstanding, ruleCore, pureJudgment}   // 2.3
                  tier  = RiskTier(costOfError, reversibility)           // 7.1
  S   split       split = CheckSplits(step)  // order: S-ACCESS, S-MIXED, S-COVER
                  // evaluated in the IDEAL environment: a split is structural,
                  // so the environment never causes one
                  if split: return {status: ok, outcome: split_required, proposedSplit[]}
  W1  ideal walk  ideal = Walk(step, IDEAL_ENV)    // policy off, environment open
  W2  real walk   fit   = Walk(step, env)         // catalog + env.customTools[] (org tools)
  C   finish      if fit.found:
                    result = recommended | eliminate
                    + alternatives, rejectedRungs, warnings
                    + W-ENV-DOWNGRADE and envDelta when ideal.rung != fit.rung
                    + companions (7.3), risk-tier rules (7.2), hybrid (14), cardRequired
                  else:
                    N  no-fit analysis (section 10.2)
```

```
Walk(step, env):
  for rung in LADDER:                              // section 9.2 order
      rp = RungPredicates(rung)                    // 6.1, inherent to the step
      if any fails: record rejection(stage = rung); continue
      for each catalog tool t at this rung:        // 6.2
          hard, soft = ToolPredicates(t, env)      // T-PERM ... T-SKILL
      passing = tools with no hard failure
      full    = passing tools covering every non-wrapper operation        // T-COVER
      if full: return choose(full) by tie-breakers TB-0..TB-7            // section 8
      bundle  = greedy cover with at most 3 passing tools at this rung
      if bundle covers all: return bundle (lead tool = the first picked)
      record rejection(stage = tool) naming the nearest miss
  return not_found
```

The ladder in `Walk` is the contract v2 order: ..., `parser_ocr_ml`, `llm_node`, `human_checkpoint`, `llm_agent`. A person is tried before the agent, and the agent is reached only when no human tool is available or the human rung does not open (`RH-AUTH`, section 6.1).

`IDEAL_ENV` switches off the policy and environmental predicates (`T-PERM`, `ORG-*`, `T-INST`, `T-PLAT`, `T-SCRIPT`, the runner part of `T-EXEC` and `T-CRED`, and `T-FLOW`) and keeps the capability predicates (`T-EXEC` support flag, `T-CRED` authModel, `T-SIZE`, `T-VAR`, `T-TRAIN`, `T-SYS`, `T-ACCESS`, `T-LOC`, `T-HOST`, `T-COVER`). It answers "what would the right tool be if nothing in this organization blocked it", which is what `envDelta` reports. Org tools from `environment.customTools[]` are added to the catalog for the real walk and the relaxed walk only; the ideal walk uses the seed catalog, so an org tool never defines "the right tool".

## 6. Predicates

Every predicate has an id used in `ruleTrace`. A **rung predicate** is inherent to the step and decides whether a rung is open at all. A **tool predicate** is checked per catalog tool in the actual environment. Classes: `capability` (a fact about the tool or the step), `environmental` (a fact about the machines, network or software estate), `policy` (something an admin can change in the Coach policy bundle), `evidence` (a doubt, always soft).

### 6.1 Rung predicates

"Step access" below means the union of the effective access modes of all the step's systems (section 2.4).

| Id | Rung | Holds when |
|---|---|---|
| `E-1` | eliminate | `necessity` in {output_unused, duplicate_of_step, available_upstream} AND NOT `requiredByControl`. The only tool is the pseudo-tool `eliminate.remove_step`. |
| `RP-CODE` | builtin_feature, api_connector, script, ui_automation | `ruleCore`. |
| `RP-ACC-1` | builtin_feature | Step access includes `builtin`, `file_or_db`, `connector` or `http_html`. |
| `RP-ACC-2` | api_connector | Step access includes `api` or `connector`. |
| `RP-ACC-3` | script | Step access includes `api`, `scriptable`, `file_or_db` or `http_html`. |
| `RP-ACC-4` | ui_automation | Step access includes `ui`. |
| `RP-PARSE` | parser_ocr_ml | **Extract path**: every non-wrapper operation is in class extract, `languageUnderstanding` in {none, some}, `outputDeterminism` in {yes, mostly}, `judgmentRequired` is not yes, `inputVariability` is not unbounded. **Classify path**: the only non-wrapper operation is `classify_text`, `outputDeterminism` in {yes, mostly}, `training.labelSetStable` is true, and `training.examples` is at least max(100, 30 x `classCount`) (ASSUMPTION, section 18.1). |
| `RL-NEED` | llm_node | `needsUnderstanding`. |
| `RL-EVID` | llm_node, llm_agent | `attractorCheck` is on record. Evaluated only when `RL-NEED` (llm_node) or `RA-OPEN` (llm_agent) holds. |
| `RA-OPEN` | llm_agent | `plan_open_ended` is an operation or `pathPredictability = open_ended`. Evaluated only after `human_checkpoint` found nothing: the agent is the last rung. |
| `RA-RISK` | llm_agent | Risk tier is A or B. |
| `RA-ATT` | llm_agent | `attendance = attended`. |
| `RH-AUTH` | human_checkpoint | (a) `humanAuthority` in {approval_required, accountable_decision}, OR (b) a human-class operation is listed, OR (c) `pureJudgment`, OR (d) the path is open-ended (`plan_open_ended` is an operation or `pathPredictability = open_ended`) and `volumePerRun` is absent or at most `humanMaxItemsPerRun` (default 50, ASSUMPTION). Clause (d) is how "the agent only where a human checkpoint is unfit" is made testable: a person can take an open-ended step of modest volume, and cannot take one of 120 items per run. |

Why `human_checkpoint` comes before `llm_agent`: contract v2 treats the agent as the rung of last resort. A person who can do open-ended work (a research task, a one-off investigation) is predictable, accountable and needs no justification card, so the engine offers the person first and names the agent as a discouraged alternative. The agent is recommended only when the person is forbidden (an org rule), when the volume is above `humanMaxItemsPerRun`, or when no human tool passes the hard predicates (for example an unattended run, because `human.manual_task` has `unattendedSupport = no`, while the agent itself needs an attended run: that combination ends in `no_fit`).

Why the code rungs come before `parser_ocr_ml`, and `parser_ocr_ml` before `llm_node`: an extraction or classification that a template, a prebuilt extractor or a trained classifier can do is cheaper to run, testable against labeled examples and cannot invent text, so the language-model rung is not even considered for it. A model rung is reached only when `needsUnderstanding` is true and the attractor check is on record.

### 6.2 Tool predicates

| Id | Class | Kind | Holds when |
|---|---|---|---|
| `T-PERM` | policy | hard | The tool is not in `forbiddenToolIds`; if `permittedToolIds` is present it is on it; its rung is not in `forbiddenRungIds`; if `permittedRungIds` is present its rung is on it; the rung is not `llm_agent` while `coach.llmAgent.mode = forbidden`. The tool lists and rung lists are not applied to `eliminate` and `human_checkpoint` tools (a manual step needs no software); to forbid a human tool an org rule `forbid_tools` (`ORG-<id>`) is used. |
| `ORG-<id>` | policy | hard | No resolved org rule forbids the tool or its rung, and no blocking `require_attended` rule applies to an unattended step (3.3). |
| `T-INST` | environmental | hard or soft | The tool is installed (`installedToolIds` or the step's `alreadyHasToolIds`) or does not need installing. If it must be installed: `locked_down` fails; `request_approval` passes with `W-INSTALL-APPROVAL`; `free` passes. |
| `T-PLAT` | environmental | hard | `platforms` includes `windows` or `cloud`. |
| `T-SCRIPT` | environmental | hard and soft | For scripting tools: `scripting.allowed` and the tool's `language` is in `scripting.languages`. Soft: PowerShell policy `restricted`, `undefined` or `unknown` gives `W-PS-POLICY`; `signedScriptsOnly` or `allsigned` gives `W-SIGN`; `unattendedRequiresReview` on an unattended step gives `W-UNATTENDED-REVIEW`. |
| `T-EXEC` | capability, then environmental | hard | Unattended steps only. Capability: `unattendedSupport` is not `no`. Environmental (skipped for cloud-only, human and eliminate tools): a runner exists with `unattendedAllowed`, a platform the tool supports, and, for `needs_host` tools, kind `unattended_vm` or `server_scheduler`. If a `needs_host` tool passes, `W-HOST-UNATTENDED` is added. |
| `T-CRED` | capability, then environmental | hard | `credentialsRequired = yes` and unattended; skipped for `human_checkpoint`, `eliminate`, `parser_ocr_ml` and `llm_node` tools, and for hosts. Capability: no system the tool reaches signs in with `mfa_interactive` or `shared_login`. Environmental: some unattended runner has `credentialModel` `service_account` or `vaulted_secret`. |
| `T-FLOW` | policy or environmental | hard | Section 3.4. Non-model tools: `dataFlow` is at or below the class ceiling (and `local` on an air-gapped network). Model tools: the connection-type intersection is non-empty, and the class `llmContentMode` is not `none`. |
| `T-SIZE` | capability | hard | `volumePerRun` <= `limits.maxItemsPerRun`; `inputSize` <= `limits.maxInputSize`. |
| `T-VAR` | capability | hard | For an extraction operation other than `ocr_text`: `inputVariability` is not above the tool's `maxInputVariability` (order: fixed_layout, few_templates, many_templates, unbounded). |
| `T-TRAIN` | capability | hard | For tools with `requiresTrainingData`: the same example-count test as the classify path of `RP-PARSE`. |
| `T-SYS` | capability | hard | Every system whose `kind` is known has that kind in the tool's `systemKinds`. An empty or absent `systemKinds` means the tool does not depend on a system kind, and the predicate passes. |
| `T-ACCESS` | capability | hard | For every system, effective access modes intersect the tool's `accessModes`. An empty or absent `accessModes` means the tool does not depend on an access mode, and the predicate passes (13 of the 29 seed entries, for example `human.manual_task`, `llm.cloud_model` and `parser.regex_template`, list neither). |
| `T-LOC` | capability, evidence | hard and soft | For a UI-capable tool reaching a UI-only system: locator `image_or_coordinates` fails (this product does not target by screen position); `unknown` passes with `W-LOC-UNVERIFIED`; otherwise the kind must be in the tool's `locatorKinds`. |
| `T-HOST` | environmental | hard | For tools with `hostToolIds`: at least one host passes the hard predicates evaluated as a host (hosts skip `T-SIZE`, `T-VAR`, `T-TRAIN`, `T-SYS`, `T-ACCESS`, `T-LOC`, `T-CRED`, `T-SKILL`). The host is chosen by the tie-breakers; its warnings are added; `hostToolId` is reported. |
| `T-COVER` | capability | hard | One tool covers every non-wrapper operation, or at most three tools at the same rung together cover the union (6.4). |
| `T-SKILL` | capability | soft | `skillLevel` is at or below `builderSkill`; otherwise `W-SKILL`. |

### 6.3 Warning catalog

Warnings are soft: they never remove a tool, and the user must acknowledge them before an override stands (section 12).

| Id | Fires when |
|---|---|
| `W-INSTALL-APPROVAL` | The tool needs an install request (`request_approval`). |
| `W-PS-POLICY` | PowerShell execution policy is restricted, undefined or unknown. |
| `W-SIGN` | Scripts must be signed. |
| `W-UNATTENDED-REVIEW` | The org requires review of unattended scripts. |
| `W-HOST-UNATTENDED` | The tool needs a dedicated signed-out machine for unattended runs. |
| `W-LOC-UNVERIFIED` | UI element ids or selectors have not been confirmed. |
| `W-API-UNVERIFIED` | API access is claimed or unstated, not verified. |
| `W-SKILL` | The tool needs more skill than the builder has. |
| `W-ENV-DOWNGRADE` | The ideal rung differs from the chosen rung. Fires only then. |
| `W-TIER-D-CODE` | Unattended deterministic code at tier D: add a dry run, a limit and an alert. |
| `W-AGENT-DISCOURAGED` | The recommendation is on the `llm_agent` rung (always shown, together with a justification card and a supervising review queue). |
| `W-ATTENDED-ONLY` | `attendance = either` and the chosen tool needs a person present. |
| `W-SCRAPE-TERMS` | The step scrapes a website; the engine cannot check terms of use or robots rules. |
| `W-NO-TRIGGER` | A trigger operation is not covered and no permitted trigger tool exists. |
| `W-RESIDUAL-UNAVAILABLE` | `residualHandling = llm` but no permitted model tool exists; route the leftovers to a person. |
| `W-ORG-<id>` | A non-blocking `require_attended` org rule applies. |
| `W-ROI-LOW`, `W-ROI-MARGINAL`, `W-STABILITY-PARTIAL` | Triage warnings (section 11). `W-ROI-LOW` and `W-ROI-MARGINAL` are advisory: they never change the verdict while the ROI gate is advisory. |

### 6.4 Coverage and bundles

A tool covers an operation when the tag is in its `capabilities[]`. A step's need is its non-wrapper operations (after the derived `approve_decision`). At a rung:

1. If one or more passing tools cover every operation, the winner is chosen among them by the tie-breakers.
2. Otherwise the engine builds a bundle of at most three passing tools at that rung, greedily: at each round it takes the tool that covers the most still-uncovered operations (ties broken by the tie-breakers), until nothing is left or three are chosen. If everything is covered the first-picked tool leads the result and the others appear in `bundle[]`.
3. Otherwise the rung is rejected with `T-COVER`, naming the closest tool, and the walk continues.

Bundles never mix rungs. A step that needs a script and a UI tool is a split (S-COVER or S-ACCESS), not a bundle, because the two halves fail differently and should be tested and owned separately.

## 7. Risk tiers and companions

### 7.1 Risk tier

| `costOfError` \ `reversibility` | reversible | partly | irreversible |
|---|---|---|---|
| low | A | A | B |
| medium | B | C | C |
| high | C | D | D |

### 7.2 Tier rules

| Id | Fires when | Effect |
|---|---|---|
| `RK-C` | Rung is `parser_ocr_ml` or `llm_node` and tier is C; or rung is `llm_agent` and tier is A or B. | Companion `human.review_queue`, role `review`. |
| `RK-D` | Rung is `parser_ocr_ml` or `llm_node` and tier is D. | Companion `human.approval_flow`, role `approve`. The model produces; a person approves before anything is committed. |
| `W-TIER-D-CODE` | Rung is a code rung, tier is D, attendance is unattended. | Warning only. Deterministic code is repeatable, so the engine does not force a human, but it asks for a dry run, a limit and an alert. |
| `RA-RISK` | `llm_agent` at tier C or D. | The rung is rejected. |

### 7.3 Trigger companions (`T-WRAP`)

A wrapper operation the chosen tool does not cover gets a companion with role `trigger`. Candidate sets (ASSUMPTION: rules-pack constants; a later version may derive them from `capabilities`): `schedule_trigger` from `builtin.windows_task_scheduler` and `api.power_automate_cloud_flow`; `event_trigger` from `api.power_automate_cloud_flow` and `builtin.outlook_rules`. The candidate that passes every hard predicate and wins the tie-breakers is used. If none passes, `W-NO-TRIGGER` is added and the user starts the run by hand.

## 8. Tie-breakers and the explanation trace

### 8.1 Tie-breakers

Applied in order among tools that passed every hard predicate at the same rung. The first difference decides. There are no weights. `TB-0` never moves the rung: an org-preferred tool that fails a hard predicate is not chosen, and a preferred tool at a later rung does not beat a tool that already fits at an earlier one (FX-50).

| Id | Prefer |
|---|---|
| `TB-0` | A tool the org prefers: lower position in `environment.preferredToolIds` wins; a tool not listed ranks last. For a hosted tool, the host is chosen the same way. |
| `TB-1` | A tool the builder already has (`alreadyHasToolIds`). |
| `TB-2` | Fewer soft warnings. |
| `TB-3` | A tool that needs no host. |
| `TB-4` | Lower `skillLevel`. |
| `TB-5` | Lower data flow (local, tenant, vendor_cloud, ai_cloud); for a hosted tool, the larger of tool and host. |
| `TB-6` | Fewer total `capabilities` (the more specific tool). |
| `TB-7` | Earlier position in the catalog. The catalog order is a deliberate, versioned tie-break, so results are stable. |

### 8.2 The trace

`ruleTrace[]` starts with one `SENS` entry (3.4: the sensitivity class used and the ceiling it implies). It then lists, in evaluation order (ladder order, then catalog order): each rung predicate with `pass` or `fail`; each failed tool predicate with its `class`; for the winner, `T-ALL` (no hard predicate failed), `T-COVER`, `TB` (selected) and `LADDER` (stop: the first rung that fits wins). It ends with an `RK` info line giving the risk tier.

`rejectedRungs[]` has one entry per rung before the chosen one: `stage = rung` when a rung predicate failed (the step does not qualify for that rung) and `stage = tool` when the rung qualified but no tool passed (naming the closest tool and its failed rules). This is the answer to "why not something simpler?"; the Coach explains it in its own words but shows these entries as the evidence.

`alternatives[]` lists up to two same-rung runners-up and the first passing tool of each later rung the step also qualifies for, each with why it lost ("tie-breakers ranked X first", "a lower rung is chosen first", or for the agent "discouraged: reached only where a person is forbidden or does not fit").

## 9. Decision table

### 9.1 What the answers open

For steps with `needsUnderstanding = false` (`languageUnderstanding = none`, no language operation, no unbounded extraction):

| `outputDeterminism` | `judgmentRequired` | State | Rungs open |
|---|---|---|---|
| yes | no | `ruleCore` | Code rungs (access permitting); `parser_ocr_ml` if the operations are extraction only. |
| yes | sometimes, yes | `V-CONFLICT` | None until corrected. |
| mostly | no | `ruleCore`; `V-RESID` asks `residualHandling` | Code rungs, plus a residual companion (section 14). |
| mostly | sometimes | `ruleCore`; same | Same. |
| mostly | yes | `pureJudgment` | `human_checkpoint` (derived `approve_decision`); S-COVER if other operations are listed. |
| no | no | `V-CONFLICT` | None until corrected. |
| no | sometimes, yes | `pureJudgment` | `human_checkpoint`; S-COVER if other operations are listed. |

For steps with `needsUnderstanding = true` the code rungs are closed (`RP-CODE`). `parser_ocr_ml` opens if the step is extraction-only (and not unbounded) or a classification with enough stable labeled examples. `llm_node` opens with the attractor evidence. `human_checkpoint` opens if `RH-AUTH` holds, which includes open-ended work of modest volume. `llm_agent` is last: it opens only for open-ended paths at tier A or B, attended, and only when the human rung is closed or has no permitted tool.

### 9.2 The ladder

| Order | Rung | Opens when | Tools in the seed catalog |
|---|---|---|---|
| 1 | `eliminate` | `E-1` | `eliminate.remove_step` |
| 2 | `builtin_feature` | `RP-CODE` and `RP-ACC-1` | Excel formulas, Power Query, mail rules, Task Scheduler, PowerToys PowerRename |
| 3 | `api_connector` | `RP-CODE` and `RP-ACC-2` | Power Automate cloud flow, REST request, Microsoft Graph, third-party iPaaS |
| 4 | `script` | `RP-CODE` and `RP-ACC-3` | PowerShell, Python, VBA, Office Scripts, SQL |
| 5 | `ui_automation` | `RP-CODE` and `RP-ACC-4` | AutoMate (`ui.automate`), Power Automate for desktop, Playwright |
| 6 | `parser_ocr_ml` | `RP-PARSE` | Regex template, Tesseract, prebuilt document extraction, trained text classifier |
| 7 | `llm_node` | `RL-NEED` and `RL-EVID` | Cloud model, org endpoint, local model |
| 8 | `human_checkpoint` | `RH-AUTH` | Approval flow, review queue, manual task |
| 9 | `llm_agent` | `RA-OPEN`, `RA-RISK`, `RA-ATT`, `RL-EVID`; only after rung 8 found nothing | Bounded agent (discouraged) |

### 9.3 Situation lookup (for QA and for the Coach's "is this plausible?" check)

| Situation | Expected result | Example |
|---|---|---|
| Total or pivot a spreadsheet column | `builtin.excel_formulas` | FX-01 |
| Rename files, a person is there | `builtin.powertoys_powerrename` | FX-02 |
| Same, nightly and unattended | `script.powershell` plus `builtin.windows_task_scheduler` | FX-03 |
| Same, builder already has Python | `script.python` | FX-04 |
| Build a report and email it on a schedule | `script.powershell` plus scheduler | FX-05 |
| Keep two SaaS tools in sync, both have connectors | `api.power_automate_cloud_flow` | FX-06 |
| Copy between two screen-only desktop apps | `ui.automate`, alternative `ui.power_automate_desktop` | FX-07 |
| Read a legacy screen and write to a SaaS API | Split: UI read, API write | FX-09 |
| Fields from invoices in many layouts | `ml.document_intelligence_prebuilt` in a script, review queue | FX-10 |
| Same, restricted data | `blocked_by_policy`, manual fallback | FX-11 |
| Invoices of unbounded layout | `llm.cloud_model` with a card | FX-12 |
| Classify email with enough labeled history | `ml.trained_text_classifier` | FX-13 |
| Classify email without history | `llm.cloud_model` with a card | FX-14 |
| Summarize contracts | `llm.cloud_model` with a card | FX-15 |
| Rule plus judgment in one step | Split: rules, then the judgment | FX-18 |
| Scrape a static site, unattended | `script.powershell` with `W-SCRAPE-TERMS` | FX-19 |
| Scrape a JavaScript site, unattended | `ui.playwright_browser` | FX-20 |
| Portal with an interactive second factor, unattended | `no_fit` (`T-CRED`) | FX-21 |
| Duplicate report nobody reads | `eliminate` | FX-22 |
| Mostly rules, leftovers to a person | Flow plus `human.review_queue` | FX-24 |
| Mostly rules, leftovers to a model | Flow plus `llm.cloud_model` with a card | FX-25 |
| A phone call | `human.manual_task` | FX-26 |
| Open-ended research, attended, modest volume | `human.manual_task`; the agent is listed as a discouraged alternative | FX-27 |
| Open-ended research, the org forbids the manual-task tool | `agent.bounded_llm_agent`, review queue, `W-AGENT-DISCOURAGED`, card | FX-47 |
| Open-ended triage of 120 items per run | `agent.bounded_llm_agent` (the person does not fit: `RH-AUTH` fails on volume) | FX-48 |
| The org prefers one of two tools that both fit | The preferred tool (`TB-0`) | FX-49 |
| The org prefers a script tool but a built-in feature fits | The built-in feature (`TB-0` never crosses rungs) | FX-50 |
| Draft a reply with legal risk | `llm.cloud_model` plus `human.approval_flow` | FX-28 |
| Quote accepted or rejected by a named person | `human.approval_flow` | FX-36 |

## 10. When nothing fits

### 10.1 `split_required`

Structural. Evaluated in the ideal environment, so an environment never causes a split. Checked in this order; the first that fires wins.

| Code | Fires when | Parts |
|---|---|---|
| `S-ACCESS` | The step touches two or more systems, and walking the ideal ladder with each system alone gives different rungs (or a fit for one and none for another). | One part per system, ordered source, lookup, both, target. Names "Read from X", "Write to Y", "Use Z". Operations follow the system's best access mode (`call_api`, `query_database`, `file_operations`, `scrape_web`, `read_from_ui`, `write_to_ui`, else `transfer_data`). Wrapper operations go to the first part. If a system is screen-only while another has an API, the hybrid pattern `ui_read_api_write` is reported. |
| `S-MIXED` | `decisionPoints[]` contains at least one `judgment` and at least one `explicit` or `partial`. | Part 1: the stated rules (all operations except `judge_quality` and `approve_decision`; `validate_rules` if nothing is left). Then one part per judgment decision point (`judge_quality` when `languageUnderstanding` is not none, else `approve_decision`). |
| `S-COVER` | No single catalog tool, and no same-rung bundle of at most three, covers all non-wrapper operations, and the operations fall into at least two groups. | Group operations by class in first-appearance order; merge groups of the same class; then merge neighbours greedily while one tool or same-rung bundle covers the union. Wrapper operations go to the first part. |

A split part is never split again by the rule that created it: S-COVER parts are groups the catalog covers or single-class groups; S-ACCESS parts each have one system; S-MIXED parts each have one decision point. A part that still cannot be covered ends in `no_fit` with `T-COVER`.

When the user confirms a split, the original step is replaced by the new steps, each with `derivedFromStepId` pointing to it and the diagnostic fields copied as a starting point for the user to confirm. The original stays in the audit log.

### 10.2 `no_fit` and `blocked_by_policy`

If the real walk finds nothing:

1. **Ideal walk.** If the ideal walk finds a tool, that is the tool the environment is blocking. `envDelta` lists, for the ideal rung and the closest tools, which predicates failed, their class, and what would have to change.
2. **Relaxed walk.** The engine walks again with policy relaxed: sensitivity ceilings and connection-type limits opened to the defaults of `public`, org rules dropped, tool and rung lists cleared, `llm_agent` mode set to `allowed_with_justification`. The hard cap of section 3.4 stays. Environmental facts (no runner, installs locked, scripting off, no model connection configured, air gap) are not relaxed. If the relaxed walk finds a fit, `status = blocked_by_policy` and `policyRelaxedFit` names it. The distinction matters: policy is what an admin can change in the Coach policy bundle, environment is what IT would have to change outside Coach.
3. **Manual fallback.** `manualFallback` offers `human.manual_task`.

Rules for the person-facing message (the Coach rewords, the facts stay): say which rule blocks the step and which class it belongs to; never suggest that the builder get around a policy rule; show `policyRelaxedFit` only to admins and CoE reviewers (it says what a policy change would unlock). The engine does not offer a model as a substitute for a blocked rule-based step (G5).

### 10.3 Accepting the manual fallback

Choosing `human.manual_task` is always allowed because it declines to automate and cannot violate a tool predicate. It is recorded as an override (section 12) with a reason; the step is then treated as human work in the ROI (no hours saved, no build cost).

### 10.4 `needs_info` and `not_confirmed`

`needs_info` carries `missing[]` with a stable `questionId` (`diag.<field>`), the field, `kind` (`missing` or `conflict`) and the question text to ask, in plain words. The engine produces no provisional rung. The Coach asks the questions, records answers through its narrow tool calls, and re-evaluates. `not_confirmed` means the user has not yet confirmed the step as the Coach described it; nothing is evaluated. After a reopen (2.5) every step is `proposed`, so every step returns `not_confirmed` until the user keeps it, and while `sensitivity` is still pending a confirmed step returns `needs_info` with `blueprint.sensitivity` (`V-REOPEN`).


## 11. Triage verdicts and ROI

Triage runs at the `triage` stage, before steps exist. Its inputs are seven answers (`Blueprint.triage.answers`) and the process facts (`Blueprint.process`: frequency, time per run, people).

### 11.1 Answers

| Answer | Values |
|---|---|
| `outputIsUsed` | yes, no |
| `couldStopDoingIt` | yes, no |
| `processIsDocumented` | yes, partly, no |
| `peopleDoItTheSameWay` | yes, mostly, no |
| `ownerIdentified` | yes, no |
| `hasKnownPainOrErrors` | yes, no |
| `touchesRegulatedOrHighStakes` | yes, no |

Every answer may also be `unknown` (`$defs/triageAnswers` allows it): the user was asked and does not know. The seven answers are given on host controls (`show_control`, fields `triage.*`), so each is stored as `user_stated` without `evidence` (ruling S11); the Coach has no tool that writes them. `unknown` counts as missing, exactly like an absent answer. All seven, plus `process.frequency`, `process.timePerRunMinutes` and `process.people`, are required; if any is absent or `unknown`, the result is `needs_info`, `missing[]` lists `triage.<answer>` for each such answer, no `TR-*` rule runs and no verdict is stored (`Blueprint.triage.verdict` stays null). An `unknown` never counts as `no` or as `yes` (`TX-09`, `TX-13`). While `Blueprint.reopen.pending` lists `triage` (section 2.5), the stored answers count as unconfirmed: all seven are listed in `missing[]` and no verdict is produced (`RO-5`). While it lists `process`, the four process facts `process.frequency`, `process.volume`, `process.timePerRunMinutes` and `process.people` are listed (`RO-6`).

### 11.2 Verdict rules

First match wins.

| Id | Fires when | Verdict |
|---|---|---|
| `TR-1` | `outputIsUsed = no` OR `couldStopDoingIt = yes` | `dont_automate`. Remove the work instead of automating it. |
| `TR-2` | `ownerIdentified = no` OR `processIsDocumented = no` OR `peopleDoItTheSameWay = no` OR (`touchesRegulatedOrHighStakes = yes` AND `processIsDocumented = partly`) | `fix_process_first`. Automating now would freeze today's variation. |
| `TR-3` | ROI gate (11.3). **Advisory** until the owner calibrates it from design-partner data (`roiGate = advisory`, the v1 default). | Advisory: never changes the verdict; adds `W-ROI-LOW` or `W-ROI-MARGINAL` and a trace entry that shows the constants. Enforced (`roiGate = enforced`): `dont_automate` when it fires. |
| `TR-4` | `touchesRegulatedOrHighStakes = yes` and the verdict is `automate` | Adds the conditions `coe_review_required` and `human_checkpoint_on_writes`. |
| (none) | Nothing above fired | `automate`. |

Every triage result carries a `TR-3` trace entry with result `info` that prints the constants used (share, build and maintain hours, test overhead, residual share, payback limit, marginal factor, gate mode), so a reader can see which placeholder numbers produced a warning. The numbers are also stored in `Blueprint.roi.constants` and the gate mode in `Blueprint.roi.gate`.

`W-STABILITY-PARTIAL` is added when `processIsDocumented = partly` or `peopleDoItTheSameWay = mostly` and `TR-2` did not fire: settle the differences during decompose. `Blueprint.triage` stores the verdict, rationale, answers, conditions, warnings and the rule trace.

### 11.3 ROI

```
runsPerYear         = frequency.count x periodsPerYear[frequency.period]
personsPerRun       = sum(people[].count)            (at least 1)
manualHoursPerYear  = runsPerYear x timePerRunMinutes / 60 x personsPerRun
hoursSavedPerYear   = manualHoursPerYear x automatableShare
buildHours          = (sum of build hours) x (1 + testOverheadFactor)
netHoursPerYear     = hoursSavedPerYear - maintainHoursPerYear
paybackYears        = buildHours / netHoursPerYear   (null when net <= 0)
netValuePerYear     = netHoursPerYear x hourlyRate   (only when an org hourly rate is configured)
```

ASSUMPTION: `timePerRunMinutes` is minutes per person per run. The result is in hours. Money appears only if the org supplies an hourly rate; the engine has no wage data.

**Two modes** (`roi.mode`):

| Mode | When | `automatableShare`, build, maintain |
|---|---|---|
| `triage` | Before steps are classified. | ASSUMPTION: share 0.5, build 16 hours, maintain 4 hours per year. |
| `classified` | Every step has a recommendation. | Each step weighs `1 / number of steps`. A step on `eliminate` saves its full share; on `human_checkpoint` it saves nothing; on any other rung it saves its share, reduced by `residualShare` (ASSUMPTION: 0.10) when `outputDeterminism = mostly`. Build and maintain hours are summed from the per-rung table. When ROI is computed for a subset of steps (`scope = steps`), the weight is still `1 / total steps`, so the subset's saving is its true share of the whole process. |

**Per-rung build and maintain hours** (all ASSUMPTION: placeholder priors, to be calibrated from pilot data; they are the least certain numbers in this file):

| Rung | Build hours | Maintain hours per year |
|---|---|---|
| eliminate | 0.5 | 0 |
| builtin_feature | 1 | 0.5 |
| api_connector | 6 | 2 |
| script | 10 | 3 |
| ui_automation | 16 | 8 |
| parser_ocr_ml | 24 | 6 |
| llm_node | 20 | 8 |
| llm_agent | 40 | 16 |
| human_checkpoint | 2 | 0 |

`testOverheadFactor` is 0.3 (ASSUMPTION). Rung hours are not summed per companion; a companion's build cost is ignored in v1 (ASSUMPTION; it understates cost for hybrid steps).

**TR-3 thresholds** (ASSUMPTION): `paybackMaxYears` = 1.0, `marginalFactor` = 2.0. All of these constants, and every number in the per-rung table above, are uncalibrated placeholders. The owner will replace them with figures from design-partner data and then decide whether to enforce the gate; until then the gate is advisory.

| Condition | Advisory (v1 default) | Enforced (after calibration) |
|---|---|---|
| `netHoursPerYear` <= 0, or payback is null, or payback > 2.0 years | Verdict unchanged; `W-ROI-LOW`; trace result `advisory`. | `TR-3` fires: `dont_automate`. |
| 1.0 < payback <= 2.0 (marginal band) and (`hasKnownPainOrErrors = yes` or `touchesRegulatedOrHighStakes = yes`) | Verdict unchanged; `W-ROI-MARGINAL` ("error reduction is the reason to proceed"). | Passes with `W-ROI-MARGINAL`. |
| 1.0 < payback <= 2.0 and neither | Verdict unchanged; `W-ROI-MARGINAL` ("no known pain was given; the estimate is advisory"); trace result `advisory`. | `TR-3` fires: `dont_automate`. |
| payback <= 1.0 | Passes. | Passes. |

Why advisory: the build and maintain hours are guesses, so a verdict that depends on them would be a guess with a veto. A warning still tells the user and the CoE reviewer when the numbers look weak, and `TX-04`, `TX-06` and `TX-10` to `TX-12` (section 16.1) show both modes on the same inputs.

**When the verdict is recomputed.** ASSUMPTION: the triage-mode verdict is recomputed with the classified ROI when the user reaches `design`. If the verdict changes, the Coach tells the user and the earlier verdict stays in the audit log. A user may continue after `dont_automate` or `fix_process_first` only through a `triage_override` decision, subject to `coach.triageOverride.mode`.

## 12. Overrides and the LLM justification card

### 12.1 Override validation

An override is a user's choice of a rung or tool other than the engine's. The engine validates it deterministically. A check that fails (`OV-1`, `OV-2`, a hard tool predicate, or `coach.override.mode = forbidden`) fails the request: nothing is stored, no record is written and no state exists. Only a request that passes these checks is stored, as `active`, `incomplete` or `pending_approval`.

| Id | Check | Failure |
|---|---|---|
| `OV-1` | `chosenToolId` is present unless the chosen rung is `eliminate`. The tool exists in the catalog (or among the org's `customTools`) and sits on the chosen rung, and it passes every hard tool predicate for this step in this environment (`T-COVER` is excluded: the user may plan to combine tools). Choosing `human.manual_task` is always allowed (10.3). | The request fails; nothing is stored. Hard tool predicates are never overridable (G8). Rung predicates are: choosing a model for a formula-shaped step is the case the card exists for. |
| `OV-2` | The reason has at least 15 characters (the schema floor, `override.reason` `minLength`). `coach.override.reasonMinChars` may raise the floor and never lowers it (policy maximum 400, the schema maximum of `override.reason`). | The request fails; nothing is stored. |
| `OV-3` | Every `W-*` warning is acknowledged: the warnings the engine currently shows for the step, plus the warnings the chosen tool itself would raise (for example `W-LOC-UNVERIFIED`, `W-SCRAPE-TERMS`). Choosing `human.manual_task` needs no acknowledgement. | The override is `incomplete`; the unacknowledged warnings are listed. |
| `OV-4` | The chosen rung is `llm_node` or `llm_agent` and is later in the ladder than the engine's rung (so a person-to-agent override counts: `human_checkpoint` precedes `llm_agent`), and `coach.llmOverride.requireJustificationCard` is true (default), and no confirmed card with a `whyNotCode` that counts as provided (`CARD-6`) is on file. | `incomplete`. |
| `OV-5` | Mode. For an LLM-over-earlier-rung override the mode is `coach.llmOverride.mode`, otherwise `coach.override.mode`: `advisory` leaves it `active`, `approval_required` makes it `pending_approval` (approver role from `coach.llmOverride.approverRole`), `forbidden` fails the request with `blocked_by_policy` and stores nothing. | As stated. |
| `OV-6` | Staleness: when the step's diagnostic, systems, the environment or the catalog change after the override was recorded, the engine's `inputsHash` changes. | The override becomes `stale` until the user reconfirms; the engine re-runs OV-1..OV-5 on reconfirmation. |

Stored states: `active`, `incomplete`, `pending_approval`, plus `stale` and `revoked` set by later events. There is no `rejected` override state. A reviewer's rejection of a `pending_approval` override sets it to `revoked` (the `approval.state` becomes `rejected`) and the decision record stays in `decisions[]`. The same holds for `triage_override` and `org_rule_waiver` records.

**Recording.** The full record is appended to `Blueprint.decisions[]` (`kind = override`, with the engine's recommendation at that moment, the chosen rung and tool, reason, acknowledged warnings, and the state). `Step.override` holds the current record (`by`, `reason`, `at` plus `decisionId`, `chosenRungId`, `chosenToolId`, `status`). The engine's own recommendation is never overwritten: both are kept, and exports show the override.

**Other decision kinds** in `decisions[]`: `llm_justification`, `triage_override`, `org_rule_waiver`, and the deferred `graduation_proposal` (section 13). They are append-only and merge by union on `id` when syncing.

### 12.2 When an LLM justification card is required

`cardRequired` is true when:

1. the engine recommends `llm_node` or `llm_agent`;
2. a hybrid pattern puts a model on the residual edge (`rules_first_llm_residual`); or
3. an override selects a model rung over an earlier engine rung (`OV-4`).

### 12.3 What the card contains

`Step.llmJustification`: `whyNotCode` (at least 30 characters: why code, formulas, an API or UI automation do not work; written or edited by the user, `CARD-6`), `citedDiagnosticFields` (1 to 6 diagnostic field names the argument rests on), `validator` (`schema_check`, `rule_check`, `lookup_check`, `human_review`, `sampling_audit` or `second_model_check`, with a description), `fallback` (`human_checkpoint`, `retry_then_human`, `flag_and_skip` or `halt_run`, with a description), `costPerRun` (engine-computed and derived, `CARD-4`; the schema does not require it, because the engine fills it in on every write and it is not part of the hash), `provenance` (a map from field name to `{origin, evidence?}`; only the key `whyNotCode` is defined) and `cardState` (`proposed`, `confirmed`, `stale`, `rejected`).

| Id | Rule |
|---|---|
| `CARD-1` | `whyNotCode`, `validator` and `fallback` are present and valid against the schema (`costPerRun` is filled in by the engine and is not required). `coach.llmNode.requireValidatorAndFallback` (default true) makes validator and fallback mandatory before export. |
| `CARD-2` | For an engine-chosen model step the engine pre-fills `citedDiagnosticFields` from the failed rung predicates (for example `languageUnderstanding`, `inputVariability`, `attractorCheck`), so the user confirms evidence instead of inventing it. |
| `CARD-3` | The Coach may draft the card (`proposed`). Only a person confirms it (`confirmed`), and only with a user-written `whyNotCode` (`CARD-6`; the schema requires `provenance.whyNotCode.origin = user_stated` on a confirmed card). A Blueprint cannot reach `approved`, `built` or `deployed` while a step that needs a card lacks a confirmed one. The schema encodes this in the second entry of the root `allOf`: when `status` is `approved`, `built` or `deployed`, every step with `recommendation.rungId` `llm_node` or `llm_agent`, with `recommendation.cardRequired` true (this also covers the hybrid residual of 12.2) or with `override.chosenRungId` `llm_node` or `llm_agent` must carry an `llmJustification` whose `cardState` is `confirmed`. `CARD-6` is the condition inside the card. |
| `CARD-4` | `costPerRun` comes from a price table supplied by the model catalog or the gateway, with `priceTableVersion` and the token counts used. The engine contains no prices. With no table loaded the value is null and `basis = unavailable`. ASSUMPTION: the model catalog or gateway can supply per-model prices; VERIFY with the architecture owner. The value is engine-computed and derived (ruling S2): the schema marks it `x-derived`, so the generated `contentHash` exclude list drops `steps[].llmJustification.costPerRun`, and recomputing it when a price table changes never changes an approved Blueprint's hash (`CH-2`). The snapshot in the append-only `llm_justification` decision stays in the hash (`CH-3`, ASSUMPTION). |
| `CARD-5` | A change to the step's diagnostic, tool or model connection after confirmation sets the card `stale`; export is blocked until it is reconfirmed. |
| `CARD-6` | `whyNotCode` counts as provided only when it has at least 30 characters (`CARD-1`) **and** `provenance.whyNotCode.origin = user_stated` (ruling R5). The model may draft the text (origin `coach_inferred`), and the engine may compute a suggestion (`engine_derived`), but the host stores the field as the user's only after the user has typed or edited text. A `whyNotCode` with another origin, or with none, behaves exactly like a missing one: the card is incomplete, `OV-4` leaves an LLM override `incomplete`, and the Blueprint cannot reach `approved` (`WC-2` to `WC-5`, `WC-7`). |

The attractor check (2.3) is what the card builds on: the user has already said which rule they tried and where it breaks, and the card turns that into a justification a CoE reviewer can read in one screen.

`CARD-1` to `CARD-6` are specified here and enforced by the schema where it can be (shape, minimum lengths, the status conditional, the `user_stated` condition and the approval conditional of `CARD-3`). The reference run exercises `OV-4`, `CARD-1` and `CARD-6` (`WC-1` to `WC-7`) and the hash rule of `CARD-4` (`CH-1` to `CH-4`), and the example Blueprint carries a confirmed card, but no fixture tests `CARD-2` or `CARD-5` yet.

### 12.4 The approval-required gate (rulings R2 and R7)

The gates that wait on an approval are the values of the policy key `governance.approval.requiredBefore` (`design/settings-catalog.md`): `build_handoff`, `handoff_brief`, `automate_flow_draft`, `export`, `automate_apply` and `automate_test_run`. `review_packet` has no gate, because it is how review is requested. A sensitivity class that sets `requireApprovalBeforeHandoff` (by default `restricted`) raises the same gate before `handoff_brief`, `automate_flow_draft` and `automate_apply`. Which gate applies to which action is a policy and host matter. This section defines the one predicate that decides whether a gate is **met**, so every gate value and every class trigger uses the same test (`AG-13`). It holds for every class, including `restricted`.

`ApprovalGate(blueprint, currentHash, context, verifiedRecordIds, gate?)` is a pure function; the optional `gate` names one of the six values, is echoed in the result and changes nothing else, and any other name is refused. `currentHash` is the host's computed `contentHash` (section 1.3, C13). `context` is `{plan, billableSeats}` (3.7). `verifiedRecordIds` lists the ApprovalRecords the host has verified. **Verified** means three things: the signature is valid, the `kid` is a known server key and the record's `tenantId` equals the Blueprint's tenant (the `tenantId` of its sync envelope; owner decision 2026-10-26). `tenantId` is inside the signed bytes, so it cannot be changed without breaking the signature. The engine does no cryptography and never sees tenants: a record issued for another tenant is simply never in `verifiedRecordIds`, so the gate treats it as no approval (`AG-15`). The gate is met by exactly one of:

- (a) an `approved` ApprovalRecord by a CoE Reviewer for `currentHash`; or
- (b) a SelfAttestation for `currentHash`, valid only while the host context allows it.

| Id | Check | Effect |
|---|---|---|
| `GATE-1` | Among the verified `approval_recorded` entries (signature valid, `kid` known and `tenantId` equal to the Blueprint's tenant; a record that fails any of the three is not in `verifiedRecordIds` and counts as no record) whose `contentHash` equals `currentHash`, the latest by `at` has `decision = approved`. Records for another hash do not count; a later `rejected` record for the same hash cancels an earlier approval. | Met, label `approved`. Nothing else is checked. |
| `GATE-2` | The host context allows a self-attestation: `plan` is `free` or `individual`, or `plan` is `team` and `billableSeats` is exactly 1. Everything else is refused: `enterprise`, a team with 0 or 2 or more seats, a missing or unknown plan. | Only when it passes can (b) hold. |
| `GATE-3` | A `self_attested` entry exists for `currentHash` whose `attestedBy` is `Blueprint.owner`. | With `GATE-2`: met, label `self-attested`. |

A self-attestation is never labelled `approved`: the interface, the exports and the audit trail say "self-attested". Both routes are bound to the content hash, so any edit after the record or the attestation makes it stop counting (`AG-7`), and so does a reopen (`RO-8`). The optional `plan` inside a SelfAttestation records what the host said when the user attested. It is informational only; the gate reads the context at evaluation time (`AG-12`). When a second billable member joins a team, earlier self-attestations stop satisfying approval-required gates and a CoE Reviewer is needed again (`AG-5`); nothing has to be migrated. The result lists the checks it ran as trace entries, so the interface can say which one failed.

ASSUMPTION: a reviewer's rejection does not veto an eligible self-attestation by the owner. The contract names two ways to meet the gate and no veto; policy may add one. ASSUMPTION: a team that reports `billableSeats = 0` is refused (`AG-10`) because the host always counts the owner.

## 13. Graduation: from LLM to code (DEFERRED to v1.x)

**Status.** Deferred. Contract v2 keeps the rule spec and collects no content: v1 produces no `RunStats`, the host never calls the graduation function, and the schema marks `runStats`, `graduationProposal` and the `graduation_proposal` decision kind `x-deferred`. The gates below, the reference function and the fixtures `GX-01` and `GX-02` stay so that v1.x can pick the feature up without a redesign. The constants are placeholders and will be recalibrated with real run data.

A model step that runs for a while on a stable set of inputs often turns out to be a lookup in disguise. The engine does not convert anything. It judges aggregated run statistics and, if all gates pass, returns a proposal that a person must approve.

### 13.1 Inputs (`RunStats`, from the `deploy_monitor` stage)

Counts and rates only, never content: `window.days`, `runs`, `validatorFailures`, `humanCorrections`, `distinctOutputs`, `newInputShapeRate`, and `miner{ruleCount, coverage, heldOutAgreement, heldOutN}`.

ASSUMPTION: the "miner" is a deterministic rule learner (for example decision-tree induction over extracted input features) run by the host on logged inputs and outputs. It is not an LLM and not part of the engine; the engine only reads its reported statistics. ASSUMPTION: an "input shape" is a deterministic fingerprint of structural features (fields present, length buckets, token classes); `newInputShapeRate` is the share of runs whose shape was not seen in the earlier window.

### 13.2 Gates

| Id | Passes when (ASSUMPTION: all thresholds) |
|---|---|
| `GR-1` | At least 200 runs over at least 30 days. |
| `GR-2` | At most 12 distinct outputs (the step is effectively a classification into a small set). |
| `GR-3` | Mined rules cover at least 0.90 of runs, with held-out agreement of at least 0.98 on at least 50 held-out samples. |
| `GR-4` | New input shapes are at most 0.01 of runs. |
| `GR-5` | (human corrections + validator failures) / runs is at most 0.02. |

### 13.3 Output

If every gate passes, the result is eligible and carries a `proposal` (the schema's `graduationProposal`: `fromRungId: llm_node`, `pattern`, `ruleCount`, `residualShare = 1 - coverage`, `requiresApproval: true`, `autoApply: false`, and the next steps) beside the `stepId` of the result. The host wraps the proposal into a `graduation_proposal` decision record (`id`, `kind`, `stepId`, `at`, `by`, `proposal`, `stats`, `ruleTrace`, `state = proposed`; `$defs/decisionGraduation`), so `kind` and `stepId` belong to the record and not to the proposal. The pattern is `rules_first_llm_residual` when the residual share is above zero (a code spine with the model kept only for the uncovered cases) and `pure_code` only when it is zero. Next steps: re-run the engine with `languageUnderstanding = none`, `outputDeterminism = mostly`, `residualHandling = llm`; generate regression tests from the mined rules and the held-out samples; the user approves a diff. If a gate fails, the trace names it (`GR-3`, `GR-4`) so the user knows what is missing.

Why these gates: `GR-1` guards against small samples, `GR-2` against open-ended outputs, `GR-3` against rules that fit the past but not new cases, `GR-4` against drift, `GR-5` against hiding a quality problem behind rules. The thresholds are starting points and sit in the rules pack (18.1).

## 14. Hybrid patterns: deterministic spine, model at the edges

Many good designs are a rule-based spine with a model or a person handling a narrow edge. `design/pattern-library.md` gives eleven worked patterns (ten hybrids and one boundary case) (steps, rung per step, validators, human checkpoint, and the engine fixture that proves each). The engine reports the pattern so the design stays honest about where the non-determinism lives. `Step.recommendation.hybrid = {pattern, spine{rungId, toolId}}`.

| Pattern | Detected when | Spine | Edge (companion) | Card |
|---|---|---|---|---|
| `rules_first_llm_residual` | A code rung is chosen, `outputDeterminism = mostly` or `judgmentRequired = sometimes`, and `residualHandling = llm`, and a permitted model tool exists. | The code tool. | A model tool for the cases the rules cannot decide (`H-RESID`, role `residual`). | Required. |
| `rules_first_human_residual` | Same, and `residualHandling` is `human_review` or `fallback_rule`. | The code tool. | `human.review_queue`. ASSUMPTION: with `fallback_rule` the rule is part of the spine and the queue catches what still fails. | Not required. |
| `llm_draft_human_review` | `llm_node` is chosen at tier C or D. | The model tool. | `human.review_queue` (tier C) or `human.approval_flow` (tier D), from `RK-C` and `RK-D`. | Required. |
| `ui_read_api_write` | `S-ACCESS` fires and one system is screen-only. | The split steps. | None; the seam is the split. | Not required. |
| `ml_human_exception` | `parser_ocr_ml` is chosen and (`outputDeterminism = mostly` or tier B, C or D). | The extractor or classifier. | `human.review_queue` for fields it is unsure of or that fail validation (unless `RK-C` or `RK-D` already added a reviewer). | Not required. |

If `residualHandling = llm` but no model tool is permitted, the engine adds `W-RESIDUAL-UNAVAILABLE` and no hybrid is reported; the user routes the leftovers to a person.

A hybrid has a seam, and the seam needs a validator: something that decides whether a case stays on the spine or goes to the edge (a rule, a threshold from the extractor, a sampling audit). For a model edge the validator lives in the card; for a human edge it is the queue's entry criterion, which the Coach asks the user to state when drafting the test plan.


## 15. Worked examples as test fixtures: step evaluation

Each fixture is an input and an expected result. A conforming implementation must produce the asserted fields exactly; the abridged traces show the rules that decide. Fixtures run against `tool-catalog.seed.json` as shipped, with `rulesPackVersion 0.3.0-draft`. The suite was re-run for the contract v2 ladder (`human_checkpoint` before `llm_agent`): FX-27 changed its expected result, FX-47 to FX-50 are new, and every other fixture kept its result. Round 3 re-ran all 51: none changed. The new `SENS` entry now starts every evaluated trace; the abridged traces below leave it out, and 16.5 shows it.

### 15.1 Fixture format

A fixture is `{id, env, blueprintSensitivity, stepName, diagnosticDelta, systems, stepEnvironment?, decisionPoints?, expect}`.

- `step.diagnostic` = `BASE` overlaid with `diagnosticDelta`. `BASE` (the defaults of the fixture suite, not of the engine):

```json
{
  "inputStructure": "structured", "outputDeterminism": "yes", "costOfError": "low", "reversibility": "reversible",
  "interfaceAvailability": "file_exchange", "attendance": "attended", "credentialsRequired": "no",
  "dataSensitivity": "internal", "languageUnderstanding": "none", "judgmentRequired": "no", "frequency": "weekly"
}
```

- `systems` is `Step.environment.systems`; `stepEnvironment` holds `builderSkill` and `alreadyHasToolIds`. Where a system has no `accessModes`, effective modes are derived (section 2.4).
- `env` names an environment from 15.2. `blueprintSensitivity` is `Blueprint.sensitivity`.
- Every step is `confirmationState = confirmed` unless the fixture says otherwise, and `builderSkill` is set to `intermediate` so that no result depends on a default; a fixture shows `stepEnvironment.builderSkill` only when it differs. `"builderSkill": null` (FX-51 only) leaves the property out of the step: the engine reads an unset `builderSkill` as `basic`, and a tool that needs more skill then carries `W-SKILL`.
- `expect` keys: `status`, `outcome`, `rungId`, `toolId`, `hostToolId`, `tier` (risk tier), `cardRequired`; `companions` and `alternativeTools` (each listed `toolId` must be present); `warningsInclude` (each `ruleId` must be present); `rejectedRules` (each id must appear as `rejectedRungs[].rule` or in `failedRules`); `envDeltaRules` (each id must appear in some `envDelta[].blockedBy[].ruleId`); `idealToolId` (an `envDelta` entry with `ideal: true` names it); `missingFields` and `missingKinds` (against `missing[]`); `splitCode`, `splitOps` (the `operations` of each proposed part, in order); `hybridPattern`. Keys not listed in `expect` are not asserted.

### 15.2 Environments

All fixtures start from `ENV-OPEN` and change only what is listed.

| Environment | Differs from ENV-OPEN by |
|---|---|
| `ENV-OPEN` | Baseline: Windows, installs free, all five scripting languages, PowerShell RemoteSigned, full internet, managed + both BYOK connection types reachable, one attended runner and one unattended VM runner with a service account, default sensitivity matrix (section 3.4). |
| `ENV-ATTENDED-ONLY` | `runners` has only `end_user_attended` (`unattendedAllowed: false`). No unattended runner exists. |
| `ENV-LOCKED` | `os.softwareInstallPolicy: locked_down`; `scripting.allowed: false`, `languages: []`. |
| `ENV-NO-API-RUNG` | `tools.forbiddenRungIds: ["api_connector"]`. |
| `ENV-REQUEST-INSTALL` | `os.softwareInstallPolicy: request_approval`. |
| `ENV-PS-RESTRICTED` | `scripting.powershellExecutionPolicy: restricted`; `scripting.unattendedRequiresReview: true`. |
| `ENV-NO-LLM` | `llm.availableConnectionTypes: []` (no model connection configured). |
| `ENV-NO-HOSTS` | `tools.forbiddenToolIds: [script.powershell, script.python, api.power_automate_cloud_flow]`. |
| `ENV-ORG-NO-UI` | `orgRules: [{id: no-ui, type: forbid_rungs, rungIds: [ui_automation]}]`. |
| `ENV-PREFER-PY` | `preferredToolIds: [script.python]` (the org's preferred tools, in order; TB-0). |
| `ENV-ORG-NO-MANUAL` | `orgRules: [{id: no-manual, type: forbid_tools, toolIds: [human.manual_task]}]` (a person is forbidden for open-ended work; T-PERM exempts human tools from `forbiddenToolIds`, so an org rule is the way to forbid them). |


### 15.3 Results at a glance

The 51 fixtures cover every rung and every outcome. Edge cases by theme:

| Theme | Fixtures |
|---|---|
| Split into two or more steps | FX-09 (`S-ACCESS`: screen read, API write), FX-17 (`S-COVER`: rule and approval), FX-18 (`S-MIXED`: rule and judgment), FX-37 (`S-COVER` on a derived operation) |
| Tie-breakers | FX-49 (`TB-0` org-preferred tool), FX-50 (`TB-0` never crosses a rung), FX-01 (`TB-6` fewest capabilities), FX-04 (`TB-1` owned tool), FX-20 (`TB-2` fewer warnings), FX-51 (`TB-4` lower skill: an unset `builderSkill` reads as `basic`, so Playwright carries `W-SKILL` and ties with Power Automate for desktop on warnings), FX-39 (`TB-2`: with a restricted execution policy PowerShell would also carry `W-PS-POLICY`, so Python wins) |
| Environment changes the answer | FX-03 (`T-EXEC`), FX-08 (`T-EXEC`, `no_fit`), FX-29 (`T-SCRIPT`, `no_fit`), FX-30 (`W-ENV-DOWNGRADE`), FX-46 (`T-HOST`, `no_fit`, no model substituted) |
| Soft environmental rules (warning, not a block) | FX-38 (`W-INSTALL-APPROVAL`), FX-39 (`W-UNATTENDED-REVIEW` on the chosen tool), FX-40 (`W-ATTENDED-ONLY`) |
| Policy changes the answer | FX-11, FX-16 (`T-FLOW`), FX-31 (`ORG-no-ui`): `blocked_by_policy`; FX-47 (`ORG-no-manual` removes the person, so the agent is reached) |
| System property no tool can meet | FX-21 (`T-CRED`) |
| Elimination | FX-22, FX-23 (`requiredByControl`) |
| Risk tiers | FX-41 (`W-TIER-D-CODE`: a warning, never a forced human), FX-26, FX-36 |
| Hybrid patterns | FX-09, FX-10, FX-24, FX-25, FX-28; FX-42 (`W-RESIDUAL-UNAVAILABLE`: the residual edge cannot be built, so no hybrid is reported) |
| Model rungs and their guards | FX-12, FX-14, FX-15, FX-28, FX-34 (missing attractor check), FX-45 (`V-ATTR` on unbounded extraction stated as deterministic) |
| The agent as the last rung (contract v2 order) | FX-27 (a person comes first; the agent is a discouraged alternative), FX-47 (person forbidden), FX-48 (person does not fit: 120 items per run) |
| Human rung | FX-26 (physical action), FX-27 (open-ended, modest volume), FX-36 (pure judgment) |
| Validation | FX-32 (missing), FX-33 (conflict), FX-34 (conditional), FX-35 (not confirmed), FX-43 (`V-AUTH`), FX-44 (`V-RESID`) |

Rules that no fixture result shows (found by collecting every rule id in the reference run of the engine fixtures): `T-PLAT`, `V-VAR`, `V-TRAIN`, `W-SIGN`, `W-API-UNVERIFIED`, `W-NO-TRIGGER`, the `W-ORG-<id>` form of an org rule, and the triage warning `W-STABILITY-PARTIAL` (it appears only in the example Blueprint). `W-ROI-LOW` and `W-ROI-MARGINAL` are shown by the triage cases of 16.1. `W-PS-POLICY` is never shown in a result (in FX-39 it only raises PowerShell's warning count, which is why Python wins), and `W-LOC-UNVERIFIED` is shown only in override cases OV-09 to OV-11 (16.2). `TB-3` to `TB-5` are not deliberately exercised (`TB-0` is, by FX-49 and FX-50), and `CARD-1` to `CARD-5` are spec only (`CARD-1` and `CARD-6` are exercised by 16.6). Round 3 rules are shown by their own cases: `SENS` by 16.5, `V-REOPEN` by `RO-3`, and `GATE-1` to `GATE-3` by 16.7. A conforming implementation must still follow their text in sections 6 to 8 and 12.3; adding fixtures for them is the first test task after a first build.

| Id | Case | Env | Result | Rung / tool | Deciding rule(s) |
|---|---|---|---|---|---|
| FX-01 | Total a column | OPEN | recommended | builtin_feature / builtin.excel_formulas | E-1 |
| FX-02 | Rename files by pattern (attended, ad hoc) | OPEN | recommended | builtin_feature / builtin.powertoys_powerrename | E-1 |
| FX-03 | Rename files by pattern every night (unattended) | OPEN | recommended | script / script.powershell | T-EXEC, RP-ACC-2 |
| FX-04 | Rename files, builder already owns Python | OPEN | recommended | script / script.python | T-EXEC, RP-ACC-2 |
| FX-05 | Weekly report email | OPEN | recommended | script / script.powershell | T-SYS, RP-ACC-2 |
| FX-06 | Sync two SaaS tools that have connectors | OPEN | recommended | api_connector / api.power_automate_cloud_flow | T-COVER |
| FX-07 | Copy data between two legacy apps with no API | OPEN | recommended | ui_automation / ui.automate | RP-ACC-1, RP-ACC-2, RP-ACC-3 |
| FX-08 | Same copy, but it must run unattended and no unattended runner exists | ATTENDED-ONLY | no_fit | - | T-EXEC |
| FX-09 | Read from a legacy screen, write to a SaaS tool with a connector | OPEN | split_required | - | S-ACCESS |
| FX-10 | Extract fields from invoice PDFs that come in many layouts | OPEN | recommended | parser_ocr_ml / ml.document_intelligence_prebuilt in script.powershell | T-COVER, RP-ACC-2, RP-ACC-4 ; ml_human_exception |
| FX-11 | Same invoices, data is restricted | OPEN | blocked_by_policy | - | T-FLOW |
| FX-12 | Extract fields from invoices with unbounded layouts | OPEN | recommended | llm_node / llm.cloud_model in script.powershell | RP-CODE, RP-PARSE |
| FX-13 | Classify support emails, with labeled history | OPEN | recommended | parser_ocr_ml / ml.trained_text_classifier in script.python | RP-CODE ; ml_human_exception |
| FX-14 | Classify support emails, no labeled history | OPEN | recommended | llm_node / llm.cloud_model in script.powershell | RP-CODE, RP-PARSE |
| FX-15 | Summarize a long contract (internal) | OPEN | recommended | llm_node / llm.cloud_model in script.powershell | RP-CODE, RP-PARSE |
| FX-16 | Summarize the same contract, data is restricted and no local model exists | OPEN | blocked_by_policy | - | T-FLOW |
| FX-17 | Approve an expense above a threshold | OPEN | split_required | - | S-COVER |
| FX-18 | Review a purchase request: check the budget code, judge the justification | OPEN | split_required | - | S-MIXED |
| FX-19 | Scrape a price list from a static website with no API (unattended) | OPEN | recommended | script / script.powershell | T-EXEC, RP-ACC-2 |
| FX-20 | Scrape a site that renders with JavaScript (unattended) | OPEN | recommended | ui_automation / ui.playwright_browser | RP-ACC-1, RP-ACC-2, RP-ACC-3 |
| FX-21 | Download a bank statement from a portal with interactive MFA, unattended | OPEN | no_fit | - | T-CRED |
| FX-22 | Print and file a second copy of a report nobody reads | OPEN | eliminate | eliminate / eliminate.remove_step | E-1 passes |
| FX-23 | Same step, but an audit control requires the copy | OPEN | recommended | script / script.powershell | T-COVER, RP-ACC-2 |
| FX-24 | Route invoices by amount; a few have unclear cost centers | OPEN | recommended | api_connector / api.power_automate_cloud_flow | T-COVER ; rules_first_human_residual |
| FX-25 | Triage support tickets by keyword; leftovers need reading | OPEN | recommended | api_connector / api.power_automate_cloud_flow | T-COVER ; rules_first_llm_residual |
| FX-26 | Call a supplier to confirm a delivery date | OPEN | recommended | human_checkpoint / human.manual_task | RP-ACC-4, RP-PARSE, RL-NEED |
| FX-27 | Research three competitors and draft a comparison | OPEN | recommended | human_checkpoint / human.manual_task | RP-CODE, RP-PARSE, T-COVER |
| FX-28 | Draft a reply to a customer complaint that mentions legal action | OPEN | recommended | llm_node / llm.cloud_model in script.powershell | RP-CODE, RP-PARSE ; llm_draft_human_review |
| FX-29 | Convert exports and email them nightly, scripting is switched off | LOCKED | no_fit | - | T-SCRIPT |
| FX-30 | Sync two SaaS tools, but the org forbids the api_connector rung | NO-API-RUNG | recommended | script / script.powershell | T-COVER, T-PERM |
| FX-31 | Legacy copy step, org rule forbids UI automation | ORG-NO-UI | blocked_by_policy | - | ORG-no-ui |
| FX-32 | Incomplete diagnostic | OPEN | needs_info | - | V-MISSING |
| FX-33 | Contradictory answers | OPEN | needs_info | - | V-CONFLICT |
| FX-34 | Free text with a rule that keeps breaking, no attractor evidence yet | OPEN | needs_info | - | V-ATTR |
| FX-35 | Step not yet confirmed by the user | OPEN | not_confirmed | - | gate |
| FX-36 | Accept or reject a quote after comparing three offers | OPEN | recommended | human_checkpoint / human.approval_flow | RP-CODE, RP-PARSE, RL-NEED |
| FX-37 | Calculate a bonus, but who gets it is not settled by rules | OPEN | split_required | - | S-COVER |
| FX-38 | Rename scanned files, the tool needs an install request | REQUEST-INSTALL | recommended | builtin_feature / builtin.powertoys_powerrename | E-1 |
| FX-39 | Nightly rename when PowerShell is restricted and unattended scripts need review | PS-RESTRICTED | recommended | script / script.python | T-EXEC, RP-ACC-2 |
| FX-40 | Rename files, attendance is 'either' | OPEN | recommended | builtin_feature / builtin.powertoys_powerrename | E-1 |
| FX-41 | Nightly rename that moves payment files (high cost, irreversible) | OPEN | recommended | script / script.powershell | T-COVER, RP-ACC-2 |
| FX-42 | Ticket routing with a model residual, but no model connection is configured | NO-LLM | recommended | api_connector / api.power_automate_cloud_flow | T-COVER |
| FX-43 | Unattended screen step with a login, sign-in method not stated | OPEN | needs_info | - | V-AUTH |
| FX-44 | Routing that is mostly rules, with no answer for the leftovers | OPEN | needs_info | - | V-RESID |
| FX-45 | Fields from invoices of unbounded layout, determinism stated as 'yes' | OPEN | needs_info | - | V-ATTR |
| FX-46 | Invoice extraction when every host for the extractor is forbidden | NO-HOSTS | blocked_by_policy | - | T-HOST |
| FX-47 | Research three competitors, but the org does not allow manual-task tooling | ORG-NO-MANUAL | recommended | llm_agent / agent.bounded_llm_agent in script.python | RP-PARSE, T-COVER, ORG-no-manual |
| FX-48 | Open-ended triage of 120 items per run | OPEN | recommended | llm_agent / agent.bounded_llm_agent in script.python | RP-PARSE, T-COVER, RH-AUTH |
| FX-49 | Nightly rename with an org-preferred script tool | PREFER-PY | recommended | script / script.python | T-EXEC, RP-ACC-2 |
| FX-50 | Total a column, but the org prefers a script tool | PREFER-PY | recommended | builtin_feature / builtin.excel_formulas | E-1 |
| FX-51 | Scrape a site that renders with JavaScript, builder skill never recorded | OPEN | recommended | ui_automation / ui.power_automate_desktop | RP-ACC-1, RP-ACC-2, RP-ACC-3 |

### 15.4 Fixture cards

#### FX-01  Total a column
*Edge case:* simplest builtin win; two builtin tools cover it, fewest capabilities wins.

```json
{
  "id": "FX-01",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Total the sales column",
  "diagnosticDelta": {"frequency": "monthly", "operations": ["aggregate_group"]},
  "systems": [{"name": "Monthly sales workbook", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "builtin_feature", "toolId": "builtin.excel_formulas", "tier": "A"}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- chosen `builtin.excel_formulas` at rung `builtin_feature` (first tool passing every hard predicate; tie-breakers applied)
- alternative `builtin.excel_power_query` (builtin_feature): same rung; tie-breakers ranked builtin.excel_formulas first
- alternative `script.vba_macro` (script): a lower rung is chosen first (first rung that fits wins)
- riskTier A; cardRequired false

#### FX-02  Rename files by pattern (attended, ad hoc)
*Edge case:* builtin tool that is interactive-only is fine when the run is attended.

```json
{
  "id": "FX-02",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Rename scanned files to the agreed pattern",
  "diagnosticDelta": {"frequency": "ad_hoc", "operations": ["rename_files"]},
  "systems": [{"name": "Scan folder", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "builtin_feature", "toolId": "builtin.powertoys_powerrename"}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- chosen `builtin.powertoys_powerrename` at rung `builtin_feature` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- riskTier A; cardRequired false

#### FX-03  Rename files by pattern every night (unattended)
*Edge case:* same step, attendance flips: the interactive builtin is rejected (T-EXEC) and script wins.

```json
{
  "id": "FX-03",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Rename incoming files to the agreed pattern each night",
  "diagnosticDelta": {"attendance": "unattended", "frequency": "daily", "operations": ["rename_files", "schedule_trigger"]},
  "systems": [{"name": "Drop folder", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "script",
    "toolId": "script.powershell",
    "companions": ["builtin.windows_task_scheduler"],
    "rejectedRules": ["T-EXEC"]
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-EXEC`: builtin.powertoys_powerrename cannot run unattended
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- chosen `script.powershell` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.python` (script): same rung; tie-breakers ranked script.powershell first
- companion `builtin.windows_task_scheduler` (trigger, T-WRAP): schedule_trigger is not covered by script.powershell
- riskTier A; cardRequired false

#### FX-04  Rename files, builder already owns Python
*Edge case:* TB-1: a tool the builder already has outranks equals.

```json
{
  "id": "FX-04",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Rename incoming files to the agreed pattern each night",
  "diagnosticDelta": {"attendance": "unattended", "frequency": "daily", "operations": ["rename_files", "schedule_trigger"]},
  "systems": [{"name": "Drop folder", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "stepEnvironment": {"alreadyHasToolIds": ["script.python"]},
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "script", "toolId": "script.python"}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-EXEC`: builtin.powertoys_powerrename cannot run unattended
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- chosen `script.python` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.powershell` (script): same rung; tie-breakers ranked script.python first
- companion `builtin.windows_task_scheduler` (trigger, T-WRAP): schedule_trigger is not covered by script.python
- riskTier A; cardRequired false

#### FX-05  Weekly report email
*Edge case:* no single builtin or connector tool covers shape + send; a script covers both; trigger comes from a companion.

```json
{
  "id": "FX-05",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Build the weekly sales summary and email it",
  "diagnosticDelta": {
    "reversibility": "irreversible",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "operations": ["aggregate_group", "generate_report", "send_message", "schedule_trigger"]
  },
  "systems": [
    {"name": "Sales workbook", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified", "authModel": "sso"},
    {"name": "Outlook mailbox", "kind": "email_or_calendar", "role": "target", "accessEvidence": "verified", "authModel": "sso"}
  ],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "script", "toolId": "script.powershell", "companions": ["builtin.windows_task_scheduler"], "tier": "B"}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-SYS`: builtin.outlook_rules does not cover system kind spreadsheet_or_file
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- chosen `script.powershell` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.python` (script): same rung; tie-breakers ranked script.powershell first
- alternative `script.vba_macro` (script): same rung; tie-breakers ranked script.powershell first
- companion `builtin.windows_task_scheduler` (trigger, T-WRAP): schedule_trigger is not covered by script.powershell
- riskTier B; cardRequired false

#### FX-06  Sync two SaaS tools that have connectors
*Edge case:* api_connector wins; iPaaS and REST cover it too but lose on tie-breakers.

```json
{
  "id": "FX-06",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Keep customer records in sync between the CRM and the billing tool",
  "diagnosticDelta": {
    "costOfError": "medium",
    "reversibility": "partly",
    "interfaceAvailability": "api_available",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "frequency": "continuous",
    "operations": ["sync_records", "schedule_trigger"]
  },
  "systems": [
    {"name": "CRM", "kind": "web_app", "role": "both", "accessModes": ["connector", "api"], "accessEvidence": "verified", "authModel": "service_account"},
    {"name": "Billing tool", "kind": "web_app", "role": "both", "accessModes": ["connector", "api"], "accessEvidence": "verified", "authModel": "service_account"}
  ],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "api_connector", "toolId": "api.power_automate_cloud_flow", "tier": "C"}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['sync_records']
- chosen `api.power_automate_cloud_flow` at rung `api_connector` (first tool passing every hard predicate; tie-breakers applied)
- alternative `api.third_party_ipaas` (api_connector): same rung; tie-breakers ranked api.power_automate_cloud_flow first
- alternative `api.rest_http_request` (api_connector): same rung; tie-breakers ranked api.power_automate_cloud_flow first
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- riskTier C; cardRequired false

#### FX-07  Copy data between two legacy apps with no API
*Edge case:* both systems UI-only: no split, AutoMate wins; Power Automate for desktop is the alternative.

```json
{
  "id": "FX-07",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Copy the order number from the order app into the shipping app",
  "diagnosticDelta": {"interfaceAvailability": "ui_only", "frequency": "daily", "operations": ["read_from_ui", "write_to_ui", "transfer_data"], "volumePerRun": 40},
  "systems": [
    {"name": "Legacy order app", "kind": "desktop_app", "role": "source", "accessModes": ["ui"], "accessEvidence": "verified", "uiLocator": {"kind": "automation_id"}},
    {"name": "Legacy shipping app", "kind": "desktop_app", "role": "target", "accessModes": ["ui"], "accessEvidence": "verified", "uiLocator": {"kind": "automation_id"}}
  ],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "ui_automation", "toolId": "ui.automate", "alternativeTools": ["ui.power_automate_desktop"]}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-ACC-1`: needs one of ['builtin', 'connector', 'file_or_db', 'http_html']; step access is ['ui']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['ui']
- rejected `script` by `RP-ACC-3`: needs one of ['api', 'file_or_db', 'http_html', 'scriptable']; step access is ['ui']
- chosen `ui.automate` at rung `ui_automation` (first tool passing every hard predicate; tie-breakers applied)
- alternative `ui.power_automate_desktop` (ui_automation): same rung; tie-breakers ranked ui.automate first
- riskTier A; cardRequired false

#### FX-08  Same copy, but it must run unattended and no unattended runner exists
*Edge case:* environment blocks the ideal tool: no_fit with an envDelta, never a fall to a model.

```json
{
  "id": "FX-08",
  "env": "ENV-ATTENDED-ONLY",
  "blueprintSensitivity": "internal",
  "stepName": "Copy the order number from the order app into the shipping app overnight",
  "diagnosticDelta": {"interfaceAvailability": "ui_only", "attendance": "unattended", "frequency": "daily", "operations": ["read_from_ui", "write_to_ui", "transfer_data"]},
  "systems": [
    {"name": "Legacy order app", "kind": "desktop_app", "role": "source", "accessModes": ["ui"], "accessEvidence": "verified", "uiLocator": {"kind": "automation_id"}},
    {"name": "Legacy shipping app", "kind": "desktop_app", "role": "target", "accessModes": ["ui"], "accessEvidence": "verified", "uiLocator": {"kind": "automation_id"}}
  ],
  "expect": {"status": "ok", "outcome": "no_fit", "envDeltaRules": ["T-EXEC"], "idealToolId": "ui.automate"}
}
```

Reference engine output (abridged trace):

- Without this environment the engine would choose ui.automate (ui_automation). It cannot be used here, and the engine does not substitute a less deterministic rung for a blocked one.
- envDelta `ui_automation` / `ui.automate` [ideal] blocked by `T-EXEC` (environmental): no unattended runner is available for ui.automate
- envDelta `ui_automation` / `ui.power_automate_desktop` blocked by `T-EXEC` (environmental): no unattended runner is available for ui.power_automate_desktop
- envDelta `ui_automation` / `ui.playwright_browser` blocked by `T-EXEC` (environmental): no unattended runner is available for ui.playwright_browser
- envDelta `ui_automation` / `ui.playwright_browser` blocked by `T-SYS` (capability): ui.playwright_browser does not cover system kind desktop_app
- envDelta `ui_automation` / `ui.playwright_browser` blocked by `T-LOC` (capability): ui.playwright_browser does not support automation_id locators
- manualFallback: `human.manual_task`

#### FX-09  Read from a legacy screen, write to a SaaS tool with a connector
*Edge case:* S-ACCESS: the systems need different rungs, so split into a UI read and an API write.

```json
{
  "id": "FX-09",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Move new orders from the legacy app into the CRM",
  "diagnosticDelta": {"interfaceAvailability": "ui_only", "frequency": "daily", "operations": ["transfer_data"]},
  "systems": [
    {"name": "Legacy order app", "kind": "desktop_app", "role": "source", "accessModes": ["ui"], "accessEvidence": "verified", "uiLocator": {"kind": "automation_id"}},
    {"name": "CRM", "kind": "web_app", "role": "target", "accessModes": ["api", "connector"], "accessEvidence": "verified"}
  ],
  "expect": {"status": "ok", "outcome": "split_required", "splitCode": "S-ACCESS", "splitOps": [["read_from_ui"], ["call_api"]], "hybridPattern": "ui_read_api_write"}
}
```

Reference engine output (abridged trace):

- `S-ACCESS` fired: the systems in this step need different rungs (Legacy order app -> ui_automation, CRM -> builtin_feature).
- proposed step 1: Read from Legacy order app, operations ["read_from_ui"]
- proposed step 2: Write to CRM, operations ["call_api"]
- hybrid pattern: `ui_read_api_write`

#### FX-10  Extract fields from invoice PDFs that come in many layouts
*Edge case:* parser rung with a human exception queue (hybrid); hosted by a script.

```json
{
  "id": "FX-10",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "confidential",
  "stepName": "Read supplier, date and total from each invoice PDF",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "costOfError": "medium",
    "attendance": "unattended",
    "dataSensitivity": "confidential",
    "operations": ["extract_fields_document"],
    "residualHandling": "human_review",
    "inputVariability": "many_templates",
    "attractorCheck": {"ruleAttempt": "look for the word Total followed by a number", "whereItBreaks": "some suppliers put the total in a table and others print it twice"}
  },
  "systems": [{"name": "Supplier invoice PDFs", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "parser_ocr_ml",
    "toolId": "ml.document_intelligence_prebuilt",
    "hostToolId": "script.powershell",
    "companions": ["human.review_queue"],
    "hybridPattern": "ml_human_exception",
    "tier": "B"
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['extract_fields_document']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- rejected `script` by `T-COVER`: no single tool or same-rung bundle covers ['extract_fields_document']
- rejected `ui_automation` by `RP-ACC-4`: needs one of ['ui']; step access is ['builtin', 'file_or_db', 'scriptable']
- chosen `ml.document_intelligence_prebuilt (runs in script.powershell)` at rung `parser_ocr_ml` (first tool passing every hard predicate; tie-breakers applied)
- companion `human.review_queue` (residual, H-RESID): fields the extractor is unsure of or fails validation go to a person
- hybrid pattern: `ml_human_exception`
- riskTier B; cardRequired false

#### FX-11  Same invoices, data is restricted
*Edge case:* policy: the only covering tool sends data to the tenant cloud; restricted allows local only, so blocked_by_policy (not an LLM).

```json
{
  "id": "FX-11",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "restricted",
  "stepName": "Read supplier, date and total from each invoice PDF",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "costOfError": "medium",
    "attendance": "unattended",
    "dataSensitivity": "restricted",
    "operations": ["extract_fields_document"],
    "residualHandling": "human_review",
    "inputVariability": "many_templates",
    "attractorCheck": {"ruleAttempt": "look for the word Total followed by a number", "whereItBreaks": "some suppliers put the total in a table and others print it twice"}
  },
  "systems": [{"name": "Supplier invoice PDFs", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "blocked_by_policy", "outcome": "no_fit", "envDeltaRules": ["T-FLOW"], "idealToolId": "ml.document_intelligence_prebuilt"}
}
```

Reference engine output (abridged trace):

- Without this environment the engine would choose ml.document_intelligence_prebuilt (parser_ocr_ml). It cannot be used here, and the engine does not substitute a less deterministic rung for a blocked one.
- Policy is what blocks it: with the policy rules relaxed, ml.document_intelligence_prebuilt would fit.
- envDelta `parser_ocr_ml` / `ml.document_intelligence_prebuilt` [ideal] blocked by `T-FLOW` (policy): ml.document_intelligence_prebuilt sends data to tenant; restricted data is limited to local
- policyRelaxedFit: `ml.document_intelligence_prebuilt`
- manualFallback: `human.manual_task`

#### FX-12  Extract fields from invoices with unbounded layouts
*Edge case:* variability beyond what templates or prebuilt models handle opens the LLM rung; card required.

```json
{
  "id": "FX-12",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Read supplier, date and total from invoices from hundreds of small suppliers",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "costOfError": "medium",
    "attendance": "unattended",
    "operations": ["extract_fields_document"],
    "residualHandling": "human_review",
    "inputVariability": "unbounded",
    "attractorCheck": {"ruleAttempt": "pattern-match the total line", "whereItBreaks": "every small supplier lays out the invoice differently, many are photos"}
  },
  "systems": [{"name": "Supplier invoice PDFs", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "llm_node", "toolId": "llm.cloud_model", "cardRequired": true, "rejectedRules": ["RP-CODE", "RP-PARSE"]}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=no
- rejected `api_connector` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=no
- rejected `script` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=no
- rejected `ui_automation` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=no
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- chosen `llm.cloud_model (runs in script.powershell)` at rung `llm_node` (first tool passing every hard predicate; tie-breakers applied)
- riskTier B; cardRequired true

#### FX-13  Classify support emails, with labeled history
*Edge case:* a trained classifier is cheaper and testable than a model; needs a stable label set and enough examples.

```json
{
  "id": "FX-13",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Label each incoming support email with its topic",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "mostly",
    "interfaceAvailability": "api_available",
    "attendance": "unattended",
    "languageUnderstanding": "core",
    "judgmentRequired": "sometimes",
    "frequency": "continuous",
    "operations": ["classify_text"],
    "training": {"examples": 1200, "classCount": 8, "labelSetStable": true},
    "attractorCheck": {"ruleAttempt": "if the text contains a known keyword, pick the matching label", "whereItBreaks": "customers describe the same problem in many different words"}
  },
  "systems": [{"name": "Support mailbox", "kind": "email_or_calendar", "role": "source", "accessEvidence": "verified", "authModel": "sso"}],
  "stepEnvironment": {"builderSkill": "advanced"},
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "parser_ocr_ml", "toolId": "ml.trained_text_classifier", "hostToolId": "script.python"}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=sometimes
- rejected `api_connector` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=sometimes
- rejected `script` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=sometimes
- rejected `ui_automation` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=sometimes
- chosen `ml.trained_text_classifier (runs in script.python)` at rung `parser_ocr_ml` (first tool passing every hard predicate; tie-breakers applied)
- alternative `llm.cloud_model` (llm_node): a lower rung is chosen first (first rung that fits wins)
- companion `human.review_queue` (residual, H-RESID): fields the extractor is unsure of or fails validation go to a person
- hybrid pattern: `ml_human_exception`
- riskTier A; cardRequired false

#### FX-14  Classify support emails, no labeled history
*Edge case:* same step without training data falls to an llm_node, which needs the attractor evidence and a justification card.

```json
{
  "id": "FX-14",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Label each incoming support email with its topic",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "mostly",
    "interfaceAvailability": "api_available",
    "attendance": "unattended",
    "languageUnderstanding": "core",
    "judgmentRequired": "sometimes",
    "frequency": "continuous",
    "operations": ["classify_text"],
    "training": {"examples": 0, "classCount": 8, "labelSetStable": false},
    "attractorCheck": {"ruleAttempt": "if the text contains a known keyword, pick the matching label", "whereItBreaks": "customers describe the same problem in many different words"}
  },
  "systems": [{"name": "Support mailbox", "kind": "email_or_calendar", "role": "source", "accessEvidence": "verified", "authModel": "sso"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "llm_node", "toolId": "llm.cloud_model", "cardRequired": true, "rejectedRules": ["RP-PARSE"]}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=sometimes
- rejected `api_connector` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=sometimes
- rejected `script` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=sometimes
- rejected `ui_automation` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=sometimes
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=240 examples)
- chosen `llm.cloud_model (runs in script.powershell)` at rung `llm_node` (first tool passing every hard predicate; tie-breakers applied)
- riskTier A; cardRequired true

#### FX-15  Summarize a long contract (internal)
*Edge case:* language is the core of the step: code rungs are rejected up front; the model is the right rung.

```json
{
  "id": "FX-15",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Summarize each supplier contract for the buyer",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "costOfError": "medium",
    "languageUnderstanding": "core",
    "judgmentRequired": "sometimes",
    "frequency": "monthly",
    "operations": ["summarize_text"],
    "inputSize": "large",
    "attractorCheck": {"ruleAttempt": "pull the headings and first sentence of each clause", "whereItBreaks": "the obligations are spread across several clauses and the schedules"}
  },
  "systems": [{"name": "Contract files", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "llm_node", "toolId": "llm.cloud_model", "cardRequired": true, "tier": "B"}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=sometimes
- rejected `api_connector` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=sometimes
- rejected `script` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=sometimes
- rejected `ui_automation` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=sometimes
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- chosen `llm.cloud_model (runs in script.powershell)` at rung `llm_node` (first tool passing every hard predicate; tie-breakers applied)
- riskTier B; cardRequired true

#### FX-16  Summarize the same contract, data is restricted and no local model exists
*Edge case:* policy forbids cloud models and no local model is configured: no_fit, blocked_by_policy.

```json
{
  "id": "FX-16",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "restricted",
  "stepName": "Summarize each supplier contract for the buyer",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "costOfError": "medium",
    "dataSensitivity": "restricted",
    "languageUnderstanding": "core",
    "judgmentRequired": "sometimes",
    "frequency": "monthly",
    "operations": ["summarize_text"],
    "inputSize": "large",
    "attractorCheck": {"ruleAttempt": "pull the headings and first sentence of each clause", "whereItBreaks": "the obligations are spread across several clauses and the schedules"}
  },
  "systems": [{"name": "Contract files", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "blocked_by_policy", "outcome": "no_fit", "envDeltaRules": ["T-FLOW"]}
}
```

Reference engine output (abridged trace):

- Without this environment the engine would choose llm.org_endpoint (llm_node). It cannot be used here, and the engine does not substitute a less deterministic rung for a blocked one.
- Policy is what blocks it: with the policy rules relaxed, llm.cloud_model would fit.
- envDelta `llm_node` / `llm.org_endpoint` [ideal] blocked by `T-FLOW` (policy): restricted data may use only ['local'] model connections; llm.org_endpoint uses ['custom_openai_compat']
- envDelta `llm_node` / `llm.cloud_model` blocked by `T-FLOW` (policy): restricted data may use only ['local'] model connections; llm.cloud_model uses ['managed', 'byok_openrouter', 'byok_provider']
- envDelta `llm_node` / `llm.local_model` blocked by `T-FLOW` (environmental): no local connection is configured or reachable here (class allows ['local'])
- envDelta `llm_node` / `llm.local_model` blocked by `T-SIZE` (capability): inputSize large exceeds the tool's medium
- policyRelaxedFit: `llm.cloud_model`
- manualFallback: `human.manual_task`

#### FX-17  Approve an expense above a threshold
*Edge case:* S-COVER: the rule part and the approval part sit on different rungs; split into two steps.

```json
{
  "id": "FX-17",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Approve expenses above 500",
  "diagnosticDelta": {"frequency": "daily", "operations": ["route_by_rule"], "humanAuthority": "approval_required"},
  "systems": [{"name": "Expense sheet", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "split_required", "splitCode": "S-COVER", "splitOps": [["route_by_rule"], ["approve_decision"]]}
}
```

Reference engine output (abridged trace):

- `S-COVER` fired: no single tool or same-rung bundle covers all operations (route_by_rule, approve_decision).
- proposed step 1: Part 1 (data), operations ["route_by_rule"]
- proposed step 2: Part 2 (human), operations ["approve_decision"]

#### FX-18  Review a purchase request: check the budget code, judge the justification
*Edge case:* S-MIXED: one decision is a rule, one is judgment; split the judgment out.

```json
{
  "id": "FX-18",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Review the purchase request",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "languageUnderstanding": "some",
    "judgmentRequired": "sometimes",
    "operations": ["validate_rules", "judge_quality"],
    "attractorCheck": {"ruleAttempt": "approve when the budget code exists and the text is longer than 50 words", "whereItBreaks": "long text can still be a weak reason"}
  },
  "systems": [{"name": "Request form", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "decisionPoints": [
    {"question": "Does the budget code exist?", "outcomes": ["yes", "no"], "ruleStatus": "explicit"},
    {"question": "Is the justification convincing?", "outcomes": ["yes", "no"], "ruleStatus": "judgment"}
  ],
  "expect": {"status": "ok", "outcome": "split_required", "splitCode": "S-MIXED", "splitOps": [["validate_rules"], ["judge_quality"]]}
}
```

Reference engine output (abridged trace):

- `S-MIXED` fired: decision points differ in rule status (explicit, judgment).
- proposed step 1: Apply the stated rules, operations ["validate_rules"]
- proposed step 2: Decide: Is the justification convincing?, operations ["judge_quality"]

#### FX-19  Scrape a price list from a static website with no API (unattended)
*Edge case:* http_html access lets a script win; the engine warns about terms of use.

```json
{
  "id": "FX-19",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Collect the weekly price list from the supplier website",
  "diagnosticDelta": {"inputStructure": "semi_structured", "interfaceAvailability": "ui_only", "attendance": "unattended", "operations": ["scrape_web", "schedule_trigger"]},
  "systems": [{"name": "Supplier price site", "kind": "web_app", "role": "source", "accessModes": ["http_html", "ui"], "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "script", "toolId": "script.powershell", "warningsInclude": ["W-SCRAPE-TERMS"], "rejectedRules": ["T-EXEC"]}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-EXEC`: builtin.excel_power_query cannot run unattended
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['http_html', 'ui']
- chosen `script.powershell` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.python` (script): same rung; tie-breakers ranked script.powershell first
- alternative `ui.playwright_browser` (ui_automation): a lower rung is chosen first (first rung that fits wins)
- companion `builtin.windows_task_scheduler` (trigger, T-WRAP): schedule_trigger is not covered by script.powershell
- warning `W-SCRAPE-TERMS`: Check the site's terms of use and robots rules before scraping; the engine cannot check them.
- riskTier A; cardRequired false

#### FX-20  Scrape a site that renders with JavaScript (unattended)
*Edge case:* no static HTML path: UI automation with DOM selectors; AutoMate is rejected (T-SYS), Playwright beats Power Automate for desktop on warnings.

```json
{
  "id": "FX-20",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Collect the weekly price list from the supplier portal",
  "diagnosticDelta": {"inputStructure": "semi_structured", "interfaceAvailability": "ui_only", "attendance": "unattended", "operations": ["scrape_web", "read_from_ui"]},
  "systems": [{"name": "Supplier portal", "kind": "web_app", "role": "source", "accessModes": ["ui"], "accessEvidence": "verified", "uiLocator": {"kind": "dom_selector"}}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "ui_automation", "toolId": "ui.playwright_browser", "warningsInclude": ["W-SCRAPE-TERMS"]}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-ACC-1`: needs one of ['builtin', 'connector', 'file_or_db', 'http_html']; step access is ['ui']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['ui']
- rejected `script` by `RP-ACC-3`: needs one of ['api', 'file_or_db', 'http_html', 'scriptable']; step access is ['ui']
- chosen `ui.playwright_browser` at rung `ui_automation` (first tool passing every hard predicate; tie-breakers applied)
- alternative `ui.power_automate_desktop` (ui_automation): same rung; tie-breakers ranked ui.playwright_browser first
- warning `W-SCRAPE-TERMS`: Check the site's terms of use and robots rules before scraping; the engine cannot check them.
- riskTier A; cardRequired false

#### FX-21  Download a bank statement from a portal with interactive MFA, unattended
*Edge case:* a system property no tool can meet: no_fit with the blocking rule named, regardless of environment.

```json
{
  "id": "FX-21",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Download the monthly statement from the bank portal",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "interfaceAvailability": "ui_only",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "frequency": "monthly",
    "operations": ["read_from_ui"]
  },
  "systems": [
    {
      "name": "Bank portal",
      "kind": "web_app",
      "role": "source",
      "accessModes": ["ui"],
      "accessEvidence": "verified",
      "authModel": "mfa_interactive",
      "uiLocator": {"kind": "dom_selector"}
    }
  ],
  "expect": {"status": "ok", "outcome": "no_fit", "envDeltaRules": ["T-CRED"]}
}
```

Reference engine output (abridged trace):

- No catalog tool or same-rung bundle fits this step as described (operations: read_from_ui).
- envDelta `ui_automation` / `ui.power_automate_desktop` blocked by `T-CRED` (capability): Bank portal signs in with mfa_interactive, which cannot run unattended
- envDelta `ui_automation` / `ui.playwright_browser` blocked by `T-CRED` (capability): Bank portal signs in with mfa_interactive, which cannot run unattended
- envDelta `ui_automation` / `ui.automate` blocked by `T-CRED` (capability): Bank portal signs in with mfa_interactive, which cannot run unattended
- envDelta `ui_automation` / `ui.automate` blocked by `T-SYS` (capability): ui.automate does not cover system kind web_app
- envDelta `ui_automation` / `ui.automate` blocked by `T-LOC` (capability): ui.automate does not support dom_selector locators
- manualFallback: `human.manual_task`

#### FX-22  Print and file a second copy of a report nobody reads
*Edge case:* eliminate wins first; the same step with requiredByControl would not be eliminated (FX-23).

```json
{
  "id": "FX-22",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Print and file the duplicate weekly report",
  "diagnosticDelta": {"operations": ["file_operations"], "necessity": "duplicate_of_step"},
  "systems": [{"name": "Report folder", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "eliminate", "rungId": "eliminate", "toolId": "eliminate.remove_step"}
}
```

Reference engine output (abridged trace):

- chosen `eliminate.remove_step` at rung `eliminate` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- riskTier A; cardRequired false

#### FX-23  Same step, but an audit control requires the copy
*Edge case:* E-1 fails on requiredByControl; the ladder continues and a script handles the filing.

```json
{
  "id": "FX-23",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "File the duplicate weekly report",
  "diagnosticDelta": {"operations": ["file_operations"], "necessity": "duplicate_of_step", "requiredByControl": true},
  "systems": [{"name": "Report folder", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "script", "toolId": "script.powershell", "rejectedRules": ["E-1"]}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=duplicate_of_step, requiredByControl=True
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['file_operations']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- chosen `script.powershell` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.python` (script): same rung; tie-breakers ranked script.powershell first
- riskTier A; cardRequired false

#### FX-24  Route invoices by amount; a few have unclear cost centers
*Edge case:* rules-first with a human residual: the spine is a connector flow, the leftovers go to a review queue.

```json
{
  "id": "FX-24",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Route each invoice email to the right approver",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "costOfError": "medium",
    "interfaceAvailability": "api_available",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "frequency": "daily",
    "operations": ["route_by_rule"],
    "residualHandling": "human_review",
    "attractorCheck": {
      "ruleAttempt": "send to the approver listed for the cost center on the invoice",
      "whereItBreaks": "about one invoice in twenty has a missing or misspelled cost center"
    }
  },
  "systems": [{"name": "Invoice mailbox", "kind": "email_or_calendar", "role": "source", "accessEvidence": "verified", "authModel": "service_account"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "api_connector",
    "toolId": "api.power_automate_cloud_flow",
    "companions": ["human.review_queue"],
    "hybridPattern": "rules_first_human_residual"
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['route_by_rule']
- chosen `api.power_automate_cloud_flow` at rung `api_connector` (first tool passing every hard predicate; tie-breakers applied)
- alternative `api.third_party_ipaas` (api_connector): same rung; tie-breakers ranked api.power_automate_cloud_flow first
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- companion `human.review_queue` (residual, H-RESID): cases the rule cannot decide go to a person
- hybrid pattern: `rules_first_human_residual`
- riskTier B; cardRequired false

#### FX-25  Triage support tickets by keyword; leftovers need reading
*Edge case:* rules-first with an LLM residual: spine is code, the residual edge is a model and needs a card.

```json
{
  "id": "FX-25",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Route each ticket to a queue",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "interfaceAvailability": "api_available",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "frequency": "continuous",
    "operations": ["route_by_rule"],
    "residualHandling": "llm",
    "attractorCheck": {"ruleAttempt": "if the subject contains refund, route to billing", "whereItBreaks": "customers describe refunds without the keyword"}
  },
  "systems": [{"name": "Ticket mailbox", "kind": "email_or_calendar", "role": "source", "accessEvidence": "verified", "authModel": "service_account"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "api_connector",
    "toolId": "api.power_automate_cloud_flow",
    "companions": ["llm.cloud_model"],
    "hybridPattern": "rules_first_llm_residual",
    "cardRequired": true
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['route_by_rule']
- chosen `api.power_automate_cloud_flow` at rung `api_connector` (first tool passing every hard predicate; tie-breakers applied)
- alternative `api.third_party_ipaas` (api_connector): same rung; tie-breakers ranked api.power_automate_cloud_flow first
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- companion `llm.cloud_model` (residual, H-RESID): cases the rule cannot decide go to a language model; justification card required
- hybrid pattern: `rules_first_llm_residual`
- riskTier A; cardRequired true

#### FX-26  Call a supplier to confirm a delivery date
*Edge case:* a physical action belongs to the human rung; no automation is invented.

```json
{
  "id": "FX-26",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Phone the supplier to confirm the delivery date",
  "diagnosticDelta": {"inputStructure": "free_text", "operations": ["physical_action"]},
  "systems": [{"name": "Telephone", "kind": "paper_or_phone", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "human_checkpoint", "toolId": "human.manual_task"}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-ACC-1`: needs one of ['builtin', 'connector', 'file_or_db', 'http_html']; step access is []
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is []
- rejected `script` by `RP-ACC-3`: needs one of ['api', 'file_or_db', 'http_html', 'scriptable']; step access is []
- rejected `ui_automation` by `RP-ACC-4`: needs one of ['ui']; step access is []
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- rejected `llm_node` by `RL-NEED`: languageUnderstanding=none, language ops=False, unbounded extraction=False
- chosen `human.manual_task` at rung `human_checkpoint` (first tool passing every hard predicate; tie-breakers applied)
- riskTier A; cardRequired false

#### FX-27  Research three competitors and draft a comparison
*Edge case:* ladder v2: human_checkpoint comes before llm_agent; an open-ended attended step with a small volume stays with a person and the agent is listed as a discouraged alternative.

```json
{
  "id": "FX-27",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Research competitors and draft a comparison",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "languageUnderstanding": "core",
    "judgmentRequired": "yes",
    "frequency": "ad_hoc",
    "operations": ["plan_open_ended"],
    "pathPredictability": "open_ended",
    "attractorCheck": {"ruleAttempt": "search a fixed list of sites and copy the pricing page", "whereItBreaks": "each competitor hides pricing somewhere different and the sites change"}
  },
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "human_checkpoint",
    "toolId": "human.manual_task",
    "alternativeTools": ["agent.bounded_llm_agent"],
    "cardRequired": false
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `api_connector` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `script` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `ui_automation` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- rejected `llm_node` by `T-COVER`: no single tool or same-rung bundle covers ['plan_open_ended']
- chosen `human.manual_task` at rung `human_checkpoint` (first tool passing every hard predicate; tie-breakers applied)
- alternative `agent.bounded_llm_agent` (llm_agent): discouraged: reached only where a person is forbidden or does not fit
- riskTier A; cardRequired false

#### FX-28  Draft a reply to a customer complaint that mentions legal action
*Edge case:* tier D: the model may draft, a person must approve before anything is sent.

```json
{
  "id": "FX-28",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "confidential",
  "stepName": "Draft the reply to the complaint",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "costOfError": "high",
    "reversibility": "partly",
    "dataSensitivity": "confidential",
    "languageUnderstanding": "core",
    "judgmentRequired": "yes",
    "frequency": "ad_hoc",
    "operations": ["generate_text"],
    "attractorCheck": {"ruleAttempt": "pick a template by complaint type", "whereItBreaks": "legal threats need wording specific to the claim"}
  },
  "systems": [{"name": "Complaint inbox", "kind": "email_or_calendar", "role": "source", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "llm_node",
    "toolId": "llm.cloud_model",
    "companions": ["human.approval_flow"],
    "hybridPattern": "llm_draft_human_review",
    "cardRequired": true,
    "tier": "D"
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `api_connector` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `script` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `ui_automation` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- chosen `llm.cloud_model (runs in script.powershell)` at rung `llm_node` (first tool passing every hard predicate; tie-breakers applied)
- companion `human.approval_flow` (approve, RK-D): risk tier D: the model produces, a person approves before anything is committed
- hybrid pattern: `llm_draft_human_review`
- riskTier D; cardRequired true

#### FX-29  Convert exports and email them nightly, scripting is switched off
*Edge case:* environment removes every scripting language: no_fit (environmental), and the engine does not suggest a model.

```json
{
  "id": "FX-29",
  "env": "ENV-LOCKED",
  "blueprintSensitivity": "internal",
  "stepName": "Convert the CSV export to Excel and email it",
  "diagnosticDelta": {
    "reversibility": "irreversible",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "frequency": "daily",
    "operations": ["format_convert", "send_message", "schedule_trigger"]
  },
  "systems": [
    {"name": "Export folder", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified", "authModel": "service_account"},
    {"name": "Outlook mailbox", "kind": "email_or_calendar", "role": "target", "accessEvidence": "verified", "authModel": "service_account"}
  ],
  "expect": {"status": "ok", "outcome": "no_fit", "envDeltaRules": ["T-SCRIPT"], "idealToolId": "script.powershell"}
}
```

Reference engine output (abridged trace):

- Without this environment the engine would choose script.powershell (script). It cannot be used here, and the engine does not substitute a less deterministic rung for a blocked one.
- envDelta `script` / `script.powershell` [ideal] blocked by `T-SCRIPT` (environmental): scripting language powershell is not allowed
- envDelta `script` / `script.vba_macro` blocked by `T-SCRIPT` (environmental): scripting language vba is not allowed
- envDelta `script` / `script.python` blocked by `T-INST` (environmental): script.python must be installed and software installs are locked down
- envDelta `script` / `script.python` blocked by `T-SCRIPT` (environmental): scripting language python is not allowed
- manualFallback: `human.manual_task`

#### FX-30  Sync two SaaS tools, but the org forbids the api_connector rung
*Edge case:* falling to the next rung of the same code family is legitimate; the engine records that the ideal differs.

```json
{
  "id": "FX-30",
  "env": "ENV-NO-API-RUNG",
  "blueprintSensitivity": "internal",
  "stepName": "Keep customer records in sync between the CRM and the billing tool",
  "diagnosticDelta": {
    "costOfError": "medium",
    "reversibility": "partly",
    "interfaceAvailability": "api_available",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "frequency": "continuous",
    "operations": ["sync_records", "schedule_trigger"]
  },
  "systems": [
    {"name": "CRM", "kind": "web_app", "role": "both", "accessModes": ["connector", "api"], "accessEvidence": "verified", "authModel": "service_account"},
    {"name": "Billing tool", "kind": "web_app", "role": "both", "accessModes": ["connector", "api"], "accessEvidence": "verified", "authModel": "service_account"}
  ],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "script", "toolId": "script.powershell", "warningsInclude": ["W-ENV-DOWNGRADE"]}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['sync_records']
- rejected `api_connector` by `T-PERM`: rung api_connector is forbidden
- chosen `script.powershell` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.python` (script): same rung; tie-breakers ranked script.powershell first
- companion `builtin.windows_task_scheduler` (trigger, T-WRAP): schedule_trigger is not covered by script.powershell
- warning `W-ENV-DOWNGRADE`: Without this environment the engine would choose api.power_automate_cloud_flow (api_connector); script.powershell is the best that fits here.
- riskTier C; cardRequired false

#### FX-31  Legacy copy step, org rule forbids UI automation
*Edge case:* an org rule is a hard predicate: no_fit with the rule named.

```json
{
  "id": "FX-31",
  "env": "ENV-ORG-NO-UI",
  "blueprintSensitivity": "internal",
  "stepName": "Copy the order number from the order app into the shipping app",
  "diagnosticDelta": {"interfaceAvailability": "ui_only", "frequency": "daily", "operations": ["read_from_ui", "write_to_ui", "transfer_data"]},
  "systems": [
    {"name": "Legacy order app", "kind": "desktop_app", "role": "source", "accessModes": ["ui"], "accessEvidence": "verified", "uiLocator": {"kind": "automation_id"}},
    {"name": "Legacy shipping app", "kind": "desktop_app", "role": "target", "accessModes": ["ui"], "accessEvidence": "verified", "uiLocator": {"kind": "automation_id"}}
  ],
  "expect": {"status": "blocked_by_policy", "outcome": "no_fit", "envDeltaRules": ["ORG-no-ui"]}
}
```

Reference engine output (abridged trace):

- Without this environment the engine would choose ui.automate (ui_automation). It cannot be used here, and the engine does not substitute a less deterministic rung for a blocked one.
- Policy is what blocks it: with the policy rules relaxed, ui.automate would fit.
- envDelta `ui_automation` / `ui.automate` [ideal] blocked by `ORG-no-ui` (policy): org rule no-ui forbids rung ui_automation
- envDelta `ui_automation` / `ui.power_automate_desktop` blocked by `ORG-no-ui` (policy): org rule no-ui forbids rung ui_automation
- envDelta `ui_automation` / `ui.playwright_browser` blocked by `ORG-no-ui` (policy): org rule no-ui forbids rung ui_automation
- envDelta `ui_automation` / `ui.playwright_browser` blocked by `T-SYS` (capability): ui.playwright_browser does not cover system kind desktop_app
- envDelta `ui_automation` / `ui.playwright_browser` blocked by `T-LOC` (capability): ui.playwright_browser does not support automation_id locators
- policyRelaxedFit: `ui.automate`
- manualFallback: `human.manual_task`

#### FX-32  Incomplete diagnostic
*Edge case:* needs_info: the engine names exactly what to ask and gives no provisional rung.

```json
{
  "id": "FX-32",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Process the supplier file",
  "diagnosticDelta": {"interfaceAvailability": "unknown"},
  "expect": {"status": "needs_info", "missingFields": ["interfaceAvailability", "attendance", "credentialsRequired", "operations"]}
}
```

Reference engine output (abridged trace):

- `V-MISSING` on `interfaceAvailability` (missing): How can the system be reached: through an API or connector, by exchanging files, or only through its screen?
- `V-MISSING` on `attendance` (missing): Would this run with a person watching, or on its own?
- `V-MISSING` on `credentialsRequired` (missing): Does the step need a login?
- `V-MISSING` on `operations` (missing): What does this step do to the data? Pick from the operation list.

#### FX-33  Contradictory answers
*Edge case:* needs_info with kind=conflict: language ops listed but languageUnderstanding=none.

```json
{
  "id": "FX-33",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Sort the emails by topic",
  "diagnosticDelta": {"inputStructure": "free_text", "operations": ["classify_text"], "training": {"examples": 0, "classCount": 5, "labelSetStable": false}},
  "expect": {"status": "needs_info", "missingFields": ["languageUnderstanding"], "missingKinds": ["conflict"]}
}
```

Reference engine output (abridged trace):

- `V-CONFLICT` on `languageUnderstanding` (conflict): The step lists a language operation (classify_text) but languageUnderstanding is none. Which is right?

#### FX-34  Free text with a rule that keeps breaking, no attractor evidence yet
*Edge case:* the LLM rung cannot be reached without the attractor check; the engine asks for it.

```json
{
  "id": "FX-34",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Label each complaint by topic",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "mostly",
    "languageUnderstanding": "core",
    "judgmentRequired": "sometimes",
    "operations": ["classify_text"],
    "training": {"examples": 0, "classCount": 5, "labelSetStable": false}
  },
  "expect": {"status": "needs_info", "missingFields": ["attractorCheck"]}
}
```

Reference engine output (abridged trace):

- `V-ATTR` on `attractorCheck` (missing): What rule did you try, and where does it give the wrong answer?

#### FX-35  Step not yet confirmed by the user
*Edge case:* the engine does not evaluate proposed steps.

```json
{
  "id": "FX-35",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Check the totals",
  "diagnosticDelta": {"operations": ["calculate"]},
  "expect": {"status": "not_confirmed"}
}
```

Reference engine output (abridged trace):

- `not_confirmed`: the user has not confirmed this step; nothing else is evaluated.

#### FX-36  Accept or reject a quote after comparing three offers
*Edge case:* pure judgment (no wording, not settled by rules): the human rung owns the decision; the approval flow is the tool.

```json
{
  "id": "FX-36",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Accept or reject the supplier quote",
  "diagnosticDelta": {
    "outputDeterminism": "no",
    "costOfError": "medium",
    "reversibility": "partly",
    "judgmentRequired": "yes",
    "frequency": "monthly",
    "operations": ["approve_decision"],
    "humanAuthority": "accountable_decision",
    "attractorCheck": {"ruleAttempt": "pick the lowest price that meets the delivery date", "whereItBreaks": "supplier reliability and the relationship matter and are not in any table"}
  },
  "systems": [{"name": "Quote spreadsheet", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "human_checkpoint",
    "toolId": "human.approval_flow",
    "tier": "C",
    "rejectedRules": ["RP-CODE", "RP-PARSE", "RL-NEED"]
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-CODE`: needsUnderstanding=False, outputDeterminism=no, judgmentRequired=yes
- rejected `api_connector` by `RP-CODE`: needsUnderstanding=False, outputDeterminism=no, judgmentRequired=yes
- rejected `script` by `RP-CODE`: needsUnderstanding=False, outputDeterminism=no, judgmentRequired=yes
- rejected `ui_automation` by `RP-CODE`: needsUnderstanding=False, outputDeterminism=no, judgmentRequired=yes
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- rejected `llm_node` by `RL-NEED`: languageUnderstanding=none, language ops=False, unbounded extraction=False
- chosen `human.approval_flow` at rung `human_checkpoint` (first tool passing every hard predicate; tie-breakers applied)
- riskTier C; cardRequired false

#### FX-37  Calculate a bonus, but who gets it is not settled by rules
*Edge case:* S-COVER on a derived operation: the engine adds approve_decision because the output is not determined and no wording is involved; calculation and decision go to different rungs.

```json
{
  "id": "FX-37",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Work out the bonus and decide who gets it",
  "diagnosticDelta": {
    "outputDeterminism": "no",
    "judgmentRequired": "sometimes",
    "frequency": "monthly",
    "operations": ["calculate"],
    "residualHandling": "human_review",
    "attractorCheck": {"ruleAttempt": "pay by the sales target table", "whereItBreaks": "managers adjust for circumstances that are not recorded anywhere"}
  },
  "systems": [{"name": "Bonus workbook", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "split_required", "splitCode": "S-COVER", "splitOps": [["calculate"], ["approve_decision"]]}
}
```

Reference engine output (abridged trace):

- `S-COVER` fired: no single tool or same-rung bundle covers all operations (calculate, approve_decision).
- proposed step 1: Part 1 (data), operations ["calculate"]
- proposed step 2: Part 2 (human), operations ["approve_decision"]

#### FX-38  Rename scanned files, the tool needs an install request
*Edge case:* soft environmental predicate: the install policy asks for approval, so the tool stays eligible and carries a warning.

```json
{
  "id": "FX-38",
  "env": "ENV-REQUEST-INSTALL",
  "blueprintSensitivity": "internal",
  "stepName": "Rename scanned files to the agreed pattern",
  "diagnosticDelta": {"frequency": "ad_hoc", "operations": ["rename_files"]},
  "systems": [{"name": "Scan folder", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "builtin_feature", "toolId": "builtin.powertoys_powerrename", "warningsInclude": ["W-INSTALL-APPROVAL"]}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- chosen `builtin.powertoys_powerrename` at rung `builtin_feature` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- warning `W-INSTALL-APPROVAL`: builtin.powertoys_powerrename needs an install request
- riskTier A; cardRequired false

#### FX-39  Nightly rename when PowerShell is restricted and unattended scripts need review
*Edge case:* TB-2: both scripting tools carry the review warning, only PowerShell also carries the execution-policy warning, so Python wins on fewer warnings.

```json
{
  "id": "FX-39",
  "env": "ENV-PS-RESTRICTED",
  "blueprintSensitivity": "internal",
  "stepName": "Rename incoming files to the agreed pattern each night",
  "diagnosticDelta": {"attendance": "unattended", "frequency": "daily", "operations": ["rename_files", "schedule_trigger"]},
  "systems": [{"name": "Drop folder", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "script",
    "toolId": "script.python",
    "alternativeTools": ["script.powershell"],
    "warningsInclude": ["W-UNATTENDED-REVIEW"]
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-EXEC`: builtin.powertoys_powerrename cannot run unattended
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- chosen `script.python` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.powershell` (script): same rung; tie-breakers ranked script.python first
- companion `builtin.windows_task_scheduler` (trigger, T-WRAP): schedule_trigger is not covered by script.python
- warning `W-UNATTENDED-REVIEW`: unattended scripts need a review
- riskTier A; cardRequired false

#### FX-40  Rename files, attendance is 'either'
*Edge case:* an interactive builtin tool is acceptable for 'either' but the engine says so.

```json
{
  "id": "FX-40",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Rename scanned files to the agreed pattern",
  "diagnosticDelta": {"attendance": "either", "operations": ["rename_files"]},
  "systems": [{"name": "Scan folder", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "builtin_feature", "toolId": "builtin.powertoys_powerrename", "warningsInclude": ["W-ATTENDED-ONLY"]}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- chosen `builtin.powertoys_powerrename` at rung `builtin_feature` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- warning `W-ATTENDED-ONLY`: attendance is 'either' but builtin.powertoys_powerrename needs a person present; decide whether unattended runs are wanted.
- riskTier A; cardRequired false

#### FX-41  Nightly rename that moves payment files (high cost, irreversible)
*Edge case:* tier D for deterministic code: no forced human, but a warning asks for a dry run, a limit and an alert.

```json
{
  "id": "FX-41",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Move the approved payment files to the bank drop folder each night",
  "diagnosticDelta": {"costOfError": "high", "reversibility": "irreversible", "attendance": "unattended", "frequency": "daily", "operations": ["file_operations", "schedule_trigger"]},
  "systems": [{"name": "Payment drop folder", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "script",
    "toolId": "script.powershell",
    "tier": "D",
    "warningsInclude": ["W-TIER-D-CODE"],
    "companions": ["builtin.windows_task_scheduler"]
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['file_operations']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- chosen `script.powershell` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.python` (script): same rung; tie-breakers ranked script.powershell first
- companion `builtin.windows_task_scheduler` (trigger, T-WRAP): schedule_trigger is not covered by script.powershell
- warning `W-TIER-D-CODE`: High-cost, hard-to-undo action run unattended by code: add a dry run, a limit and an alert. The engine does not force an approval here.
- riskTier D; cardRequired false

#### FX-42  Ticket routing with a model residual, but no model connection is configured
*Edge case:* the spine stands; the residual edge cannot be built, so the engine warns and reports no hybrid.

```json
{
  "id": "FX-42",
  "env": "ENV-NO-LLM",
  "blueprintSensitivity": "internal",
  "stepName": "Route each ticket to a queue",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "interfaceAvailability": "api_available",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "frequency": "continuous",
    "operations": ["route_by_rule"],
    "residualHandling": "llm",
    "attractorCheck": {"ruleAttempt": "if the subject contains refund, route to billing", "whereItBreaks": "customers describe refunds without the keyword"}
  },
  "systems": [{"name": "Ticket mailbox", "kind": "email_or_calendar", "role": "source", "accessEvidence": "verified", "authModel": "service_account"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "api_connector",
    "toolId": "api.power_automate_cloud_flow",
    "warningsInclude": ["W-RESIDUAL-UNAVAILABLE"],
    "hybridPattern": null,
    "cardRequired": false
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['route_by_rule']
- chosen `api.power_automate_cloud_flow` at rung `api_connector` (first tool passing every hard predicate; tie-breakers applied)
- alternative `api.third_party_ipaas` (api_connector): same rung; tie-breakers ranked api.power_automate_cloud_flow first
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- warning `W-RESIDUAL-UNAVAILABLE`: No permitted language model for the residual cases; route them to a person instead.
- riskTier A; cardRequired false

#### FX-43  Unattended screen step with a login, sign-in method not stated
*Edge case:* V-AUTH: the engine asks how the system signs in before it will judge an unattended run.

```json
{
  "id": "FX-43",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Read the open orders from the supplier portal",
  "diagnosticDelta": {"inputStructure": "semi_structured", "interfaceAvailability": "ui_only", "attendance": "unattended", "credentialsRequired": "yes", "operations": ["read_from_ui"]},
  "systems": [{"name": "Supplier portal", "kind": "web_app", "role": "source", "accessModes": ["ui"], "accessEvidence": "verified", "uiLocator": {"kind": "dom_selector"}}],
  "expect": {"status": "needs_info", "missingFields": ["authModel"]}
}
```

Reference engine output (abridged trace):

- `V-AUTH` on `authModel` (missing): How does Supplier portal sign in: single sign-on, a service account, a shared login, or an interactive login with a second factor?

#### FX-44  Routing that is mostly rules, with no answer for the leftovers
*Edge case:* V-RESID: a mostly-deterministic rule step must say what happens to the cases the rule cannot decide.

```json
{
  "id": "FX-44",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Route each invoice email to the right approver",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "interfaceAvailability": "api_available",
    "operations": ["route_by_rule"],
    "attractorCheck": {
      "ruleAttempt": "send to the approver listed for the cost center on the invoice",
      "whereItBreaks": "about one invoice in twenty has a missing or misspelled cost center"
    }
  },
  "systems": [{"name": "Invoice mailbox", "kind": "email_or_calendar", "role": "source", "accessEvidence": "verified"}],
  "expect": {"status": "needs_info", "missingFields": ["residualHandling"]}
}
```

Reference engine output (abridged trace):

- `V-RESID` on `residualHandling` (missing): What should happen to the cases the rule cannot decide: a person reviews them, a fallback rule, or a language model?

#### FX-45  Fields from invoices of unbounded layout, determinism stated as 'yes'
*Edge case:* V-ATTR also fires for unbounded extraction: the model rung needs evidence even when the determinism answer looks safe.

```json
{
  "id": "FX-45",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Read the invoice number from invoices from hundreds of small suppliers",
  "diagnosticDelta": {"inputStructure": "semi_structured", "operations": ["extract_fields_document"], "inputVariability": "unbounded"},
  "systems": [{"name": "Supplier invoice PDFs", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "needs_info", "missingFields": ["attractorCheck"]}
}
```

Reference engine output (abridged trace):

- `V-ATTR` on `attractorCheck` (missing): What rule did you try, and where does it give the wrong answer?

#### FX-46  Invoice extraction when every host for the extractor is forbidden
*Edge case:* T-HOST: the extractor runs inside a script or a flow; with all three hosts forbidden it cannot run, and the engine does not substitute a model.

```json
{
  "id": "FX-46",
  "env": "ENV-NO-HOSTS",
  "blueprintSensitivity": "confidential",
  "stepName": "Read supplier, date and total from each invoice PDF",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "costOfError": "medium",
    "attendance": "unattended",
    "dataSensitivity": "confidential",
    "operations": ["extract_fields_document"],
    "residualHandling": "human_review",
    "inputVariability": "many_templates",
    "attractorCheck": {"ruleAttempt": "look for the word Total followed by a number", "whereItBreaks": "some suppliers put the total in a table and others print it twice"}
  },
  "systems": [{"name": "Supplier invoice PDFs", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "blocked_by_policy", "outcome": "no_fit", "envDeltaRules": ["T-HOST"], "idealToolId": "ml.document_intelligence_prebuilt"}
}
```

Reference engine output (abridged trace):

- Without this environment the engine would choose ml.document_intelligence_prebuilt (parser_ocr_ml). It cannot be used here, and the engine does not substitute a less deterministic rung for a blocked one.
- Policy is what blocks it: with the policy rules relaxed, ml.document_intelligence_prebuilt would fit.
- envDelta `parser_ocr_ml` / `ml.document_intelligence_prebuilt` [ideal] blocked by `T-HOST` (environmental): no permitted host runs ml.document_intelligence_prebuilt (script.powershell: T-PERM | script.python: T-PERM | api.power_automate_...
- policyRelaxedFit: `ml.document_intelligence_prebuilt`
- manualFallback: `human.manual_task`

#### FX-47  Research three competitors, but the org does not allow manual-task tooling
*Edge case:* the agent is reached only when a person is forbidden: org rule forbid_tools on human.manual_task removes the human option, so the discouraged agent is recommended with a card and a reviewer.

```json
{
  "id": "FX-47",
  "env": "ENV-ORG-NO-MANUAL",
  "blueprintSensitivity": "internal",
  "stepName": "Research competitors and draft a comparison",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "languageUnderstanding": "core",
    "judgmentRequired": "yes",
    "frequency": "ad_hoc",
    "operations": ["plan_open_ended"],
    "pathPredictability": "open_ended",
    "attractorCheck": {"ruleAttempt": "search a fixed list of sites and copy the pricing page", "whereItBreaks": "each competitor hides pricing somewhere different and the sites change"}
  },
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "llm_agent",
    "toolId": "agent.bounded_llm_agent",
    "warningsInclude": ["W-AGENT-DISCOURAGED"],
    "cardRequired": true,
    "companions": ["human.review_queue"],
    "rejectedRules": ["ORG-no-manual"]
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `api_connector` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `script` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `ui_automation` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- rejected `llm_node` by `T-COVER`: no single tool or same-rung bundle covers ['plan_open_ended']
- rejected `human_checkpoint` by `ORG-no-manual`: org rule no-manual forbids human.manual_task
- chosen `agent.bounded_llm_agent (runs in script.python)` at rung `llm_agent` (first tool passing every hard predicate; tie-breakers applied)
- companion `human.review_queue` (review, RK-C): agent runs are supervised
- warning `W-SKILL`: agent.bounded_llm_agent needs advanced skill; builder has intermediate
- warning `W-ENV-DOWNGRADE`: Without this environment the engine would choose human.manual_task (human_checkpoint); agent.bounded_llm_agent is the best that fits here.
- warning `W-AGENT-DISCOURAGED`: llm_agent is discouraged: the path is chosen by the model at run time. A justification card and an allowlist of tools are required.
- riskTier A; cardRequired true

#### FX-48  Open-ended triage of 120 items per run
*Edge case:* the person does not fit: RH-AUTH fails because the volume is above humanMaxItemsPerRun, so the walk reaches the discouraged agent.

```json
{
  "id": "FX-48",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Look through each flagged case and decide what to try next",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "languageUnderstanding": "core",
    "judgmentRequired": "yes",
    "frequency": "daily",
    "operations": ["plan_open_ended"],
    "pathPredictability": "open_ended",
    "volumePerRun": 120,
    "attractorCheck": {"ruleAttempt": "match the case to a known fix by keyword", "whereItBreaks": "most cases combine two problems and need a different next step each time"}
  },
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "llm_agent",
    "toolId": "agent.bounded_llm_agent",
    "warningsInclude": ["W-AGENT-DISCOURAGED"],
    "cardRequired": true,
    "rejectedRules": ["RH-AUTH"]
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `api_connector` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `script` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `ui_automation` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=no, judgmentRequired=yes
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- rejected `llm_node` by `T-COVER`: no single tool or same-rung bundle covers ['plan_open_ended']
- rejected `human_checkpoint` by `RH-AUTH`: humanAuthority=None, human ops=False, pure judgment=False, open-ended path a person can take=False (open-ended=True, volumePerRun=120, limit 50)
- chosen `agent.bounded_llm_agent (runs in script.python)` at rung `llm_agent` (first tool passing every hard predicate; tie-breakers applied)
- companion `human.review_queue` (review, RK-C): agent runs are supervised
- warning `W-SKILL`: agent.bounded_llm_agent needs advanced skill; builder has intermediate
- warning `W-AGENT-DISCOURAGED`: llm_agent is discouraged: the path is chosen by the model at run time. A justification card and an allowlist of tools are required.
- riskTier A; cardRequired true

#### FX-49  Nightly rename with an org-preferred script tool
*Edge case:* TB-0: the org's preferred tool wins among tools that already fit at the same rung (script.python ahead of script.powershell), with no change to the rung.

```json
{
  "id": "FX-49",
  "env": "ENV-PREFER-PY",
  "blueprintSensitivity": "internal",
  "stepName": "Rename incoming files to the agreed pattern each night",
  "diagnosticDelta": {"attendance": "unattended", "frequency": "daily", "operations": ["rename_files", "schedule_trigger"]},
  "systems": [{"name": "Drop folder", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "script", "toolId": "script.python", "alternativeTools": ["script.powershell"]}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-EXEC`: builtin.powertoys_powerrename cannot run unattended
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- chosen `script.python` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.powershell` (script): same rung; tie-breakers ranked script.python first
- companion `builtin.windows_task_scheduler` (trigger, T-WRAP): schedule_trigger is not covered by script.python
- riskTier A; cardRequired false

#### FX-50  Total a column, but the org prefers a script tool
*Edge case:* TB-0 never crosses rungs: a preferred script tool does not beat a built-in feature that already fits.

```json
{
  "id": "FX-50",
  "env": "ENV-PREFER-PY",
  "blueprintSensitivity": "internal",
  "stepName": "Total the sales column",
  "diagnosticDelta": {"frequency": "monthly", "operations": ["aggregate_group"]},
  "systems": [{"name": "Monthly sales workbook", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "builtin_feature", "toolId": "builtin.excel_formulas"}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- chosen `builtin.excel_formulas` at rung `builtin_feature` (first tool passing every hard predicate; tie-breakers applied)
- alternative `builtin.excel_power_query` (builtin_feature): same rung; tie-breakers ranked builtin.excel_formulas first
- alternative `script.python` (script): a lower rung is chosen first (first rung that fits wins)
- riskTier A; cardRequired false

#### FX-51  Scrape a site that renders with JavaScript, builder skill never recorded
*Edge case:* builderSkill is unset, which the engine reads as basic (the same default as prefs.skillLevel): Playwright needs intermediate skill and now carries W-SKILL, which ties it with Power Automate for desktop on warnings (TB-2), so TB-4 (lower skill) picks Power Automate for desktop; the same step with intermediate recorded is FX-20.

```json
{
  "id": "FX-51",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Collect the weekly price list from the supplier portal",
  "diagnosticDelta": {"inputStructure": "semi_structured", "interfaceAvailability": "ui_only", "attendance": "unattended", "operations": ["scrape_web", "read_from_ui"]},
  "systems": [{"name": "Supplier portal", "kind": "web_app", "role": "source", "accessModes": ["ui"], "accessEvidence": "verified", "uiLocator": {"kind": "dom_selector"}}],
  "stepEnvironment": {"builderSkill": null},
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "ui_automation",
    "toolId": "ui.power_automate_desktop",
    "alternativeTools": ["ui.playwright_browser"],
    "warningsInclude": ["W-SCRAPE-TERMS", "W-HOST-UNATTENDED"]
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-ACC-1`: needs one of ['builtin', 'connector', 'file_or_db', 'http_html']; step access is ['ui']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['ui']
- rejected `script` by `RP-ACC-3`: needs one of ['api', 'file_or_db', 'http_html', 'scriptable']; step access is ['ui']
- chosen `ui.power_automate_desktop` at rung `ui_automation` (first tool passing every hard predicate; tie-breakers applied)
- alternative `ui.playwright_browser` (ui_automation): same rung; tie-breakers ranked ui.power_automate_desktop first
- warning `W-HOST-UNATTENDED`: ui.power_automate_desktop needs a dedicated signed-out machine for unattended runs
- warning `W-SCRAPE-TERMS`: Check the site's terms of use and robots rules before scraping; the engine cannot check them.
- riskTier A; cardRequired false


## 16. Worked examples: triage, overrides, graduation and the round 3 rulings

### 16.1 Triage and ROI

Each case gives the answers that differ from `GOOD` and the process facts. Payback uses the triage-mode ROI of section 11.3. The ROI gate is **advisory** (the v1 default), so TX-04 and TX-06 return `automate` with a warning where draft 0.1 returned `dont_automate`; TX-10 to TX-12 run the same inputs with `roiGate = enforced` to show the behavior that applies once the owner has calibrated the constants. TX-09 (absent answers) and TX-13 (answers recorded as `unknown`) both return `needs_info` with no verdict and no `TR-*` entry in the trace. Every result carries a `TR-3` trace entry that prints the constants.

| Id | Case | Answers that matter | Process | Expect |
|---|---|---|---|---|
| TX-01 | Nobody uses the output | GOOD with {"outputIsUsed": "no"} | 1 per week, 90 min per person, people [2] | {"verdict": "dont_automate", "rule": "TR-1"} |
| TX-02 | People do it differently | GOOD with {"processIsDocumented": "partly", "peopleDoItTheSameWay": "no"} | 1 per week, 90 min per person, people [2] | {"verdict": "fix_process_first", "rule": "TR-2"} |
| TX-03 | Weekly report, two analysts | GOOD with {} | 1 per week, 90 min per person, people [2] | {"verdict": "automate", "paybackMax": 0.5} |
| TX-04 | Twenty minutes a month (advisory gate) | GOOD with {} | 1 per month, 20 min per person, people [1] | {"verdict": "automate", "warning": "W-ROI-LOW", "advisory": true} |
| TX-05 | Marginal payback, known pain | GOOD with {"hasKnownPainOrErrors": "yes"} | 1 per month, 180 min per person, people [1] | {"verdict": "automate", "warning": "W-ROI-MARGINAL"} |
| TX-06 | Marginal payback, no known pain (advisory gate) | GOOD with {} | 1 per month, 180 min per person, people [1] | {"verdict": "automate", "warning": "W-ROI-MARGINAL", "advisory": true} |
| TX-07 | Regulated and only partly documented | GOOD with {"processIsDocumented": "partly", "touchesRegulatedOrHighStakes": "yes"} | 1 per week, 90 min per person, people [2] | {"verdict": "fix_process_first", "rule": "TR-2"} |
| TX-08 | Regulated and well documented | GOOD with {"touchesRegulatedOrHighStakes": "yes"} | 1 per week, 90 min per person, people [2] | {"verdict": "automate", "conditions": ["coe_review_required"]} |
| TX-09 | Missing answers | {"outputIsUsed": "yes"} | 1 per week, 90 min per person, people [2] | {"status": "needs_info"} |
| TX-10 | Twenty minutes a month, gate enforced | GOOD with {} | 1 per month, 20 min per person, people [1] | {"verdict": "dont_automate", "rule": "TR-3", "gate": "enforced"} |
| TX-11 | Marginal payback, no known pain, gate enforced | GOOD with {} | 1 per month, 180 min per person, people [1] | {"verdict": "dont_automate", "rule": "TR-3", "gate": "enforced"} |
| TX-12 | Marginal payback, known pain, gate enforced | GOOD with {"hasKnownPainOrErrors": "yes"} | 1 per month, 180 min per person, people [1] | {"verdict": "automate", "warning": "W-ROI-MARGINAL", "gate": "enforced"} |
| TX-13 | Two answers recorded as unknown | GOOD with {"couldStopDoingIt": "unknown", "ownerIdentified": "unknown"} | 1 per week, 90 min per person, people [2] | {"status": "needs_info", "missingIds": ["triage.couldStopDoingIt", "triage.ownerIdentified"]} |

`GOOD` = `{outputIsUsed: yes, couldStopDoingIt: no, processIsDocumented: yes, peopleDoItTheSameWay: yes, ownerIdentified: yes, hasKnownPainOrErrors: no, touchesRegulatedOrHighStakes: no}`.

Reference engine output:

- **TX-01** `dont_automate`; trace TR-1:fire
- **TX-02** `fix_process_first`; trace TR-1:pass, TR-2:fire
- **TX-03** `automate`; payback 0.28 years, net 74.0 h/year, build 20.8 h; trace TR-1:pass, TR-2:pass, TR-3:pass
- **TX-04** `automate`; no payback (net -2.0 h/year, build 20.8 h); trace TR-1:pass, TR-2:pass, TR-3:advisory; warnings W-ROI-LOW
- **TX-05** `automate`; payback 1.49 years, net 14.0 h/year, build 20.8 h; trace TR-1:pass, TR-2:pass, TR-3:advisory; warnings W-ROI-MARGINAL
- **TX-06** `automate`; payback 1.49 years, net 14.0 h/year, build 20.8 h; trace TR-1:pass, TR-2:pass, TR-3:advisory; warnings W-ROI-MARGINAL
- **TX-07** `fix_process_first`; trace TR-1:pass, TR-2:fire
- **TX-08** `automate`; payback 0.28 years, net 74.0 h/year, build 20.8 h; trace TR-1:pass, TR-2:pass, TR-3:pass, TR-4:condition; conditions coe_review_required, human_checkpoint_on_writes
- **TX-09** `needs_info`; missing triage.couldStopDoingIt, triage.processIsDocumented, triage.peopleDoItTheSameWay...
- **TX-10** `dont_automate`; no payback (net -2.0 h/year, build 20.8 h); trace TR-1:pass, TR-2:pass, TR-3:fire
- **TX-11** `dont_automate`; payback 1.49 years, net 14.0 h/year, build 20.8 h; trace TR-1:pass, TR-2:pass, TR-3:fire
- **TX-12** `automate`; payback 1.49 years, net 14.0 h/year, build 20.8 h; trace TR-1:pass, TR-2:pass, TR-3:marginal-pass; warnings W-ROI-MARGINAL
- **TX-13** `needs_info`; missing triage.couldStopDoingIt, triage.ownerIdentified


### 16.2 Override validation

Overrides are validated by `OV-1` to `OV-6` (section 12.1) against the same step, environment and catalog as the engine fixtures. `Card on file` says whether a confirmed justification card exists; `Policy` shows non-default settings.

| Id | Case | Chosen | Policy | Warnings acknowledged | Card on file | Resulting state | Rules that fire |
|---|---|---|---|---|---|---|---|
| OV-01 | Advisory mode, user prefers a script over the formula | `script.powershell` | defaults | none | no | `active` | none |
| OV-02 | LLM over a formula, no card yet | `llm.cloud_model` | defaults | none | no | `incomplete` | `OV-4` |
| OV-03 | Same, with a card on file | `llm.cloud_model` | defaults | none | yes | `active` | none |
| OV-04 | Same, org requires approval of LLM overrides | `llm.cloud_model` | `{"coach.llmOverride.mode": "approval_required"}` | none | yes | `pending_approval` | none |
| OV-05 | Hard predicate: cloud model for restricted data | `llm.cloud_model` | defaults | none | yes | fails, nothing stored | `T-FLOW` |
| OV-06 | Reason too short | `script.powershell` | defaults | none | no | fails, nothing stored | `OV-2` |
| OV-07 | Accept the manual fallback after no_fit | `human.manual_task` | defaults | none | no | `active` | none |
| OV-08 | Keep the step manual although the engine found a fit | `human.manual_task` | defaults | none | no | `active` | none |
| OV-09 | Override to a UI tool, warnings not acknowledged | `ui.playwright_browser` | defaults | none | no | `incomplete` | `OV-3` (W-SCRAPE-TERMS), `OV-3` (W-LOC-UNVERIFIED) |
| OV-10 | Same, warnings acknowledged | `ui.playwright_browser` | defaults | 2 acknowledged | no | `active` | none |
| OV-11 | Same, org blocks overrides | `ui.playwright_browser` | `{"coach.override.mode": "forbidden"}` | 2 acknowledged | no | fails, nothing stored | `OV-5` |
| OV-12 | No chosen tool on a non-eliminate rung | no tool (`script`) | defaults | none | no | fails, nothing stored | `OV-1` |
| OV-13 | Reason of 14 characters is below the floor | `script.powershell` | defaults | none | no | fails, nothing stored | `OV-2` |
| OV-14 | Reason of exactly 15 characters passes the floor | `script.powershell` | defaults | none | no | `active` | none |
| OV-15 | Override the person to the agent, no card yet (later rung) | `agent.bounded_llm_agent` | defaults | 2 acknowledged | no | `incomplete` | `OV-4` |
| OV-16 | Same, with the justification card on file | `agent.bounded_llm_agent` | defaults | 2 acknowledged | yes | `active` | none |
| OV-17 | Eliminate needs no tool id | no tool (`eliminate`) | defaults | none | no | `active` | none |

OV-01..04, OV-06, OV-08, OV-12..14 and OV-17 run on the FX-01 step (ENV-OPEN, internal); OV-05 on FX-11 (restricted); OV-07 on FX-08 (ENV-ATTENDED-ONLY); OV-09..11 on FX-19 (static scrape, unattended), where the engine shows W-SCRAPE-TERMS and the chosen tool adds W-LOC-UNVERIFIED; OV-15 and OV-16 on FX-27 (open-ended research, where the engine recommends a person and the agent is a later rung), where the chosen agent adds W-SKILL for an intermediate builder. OV-06 uses a 6-character reason and OV-13 a 14-character one (below the floor of 15); OV-14 uses exactly 15 characters. OV-12 has no chosen tool (fails: `chosenToolId` is required unless the chosen rung is `eliminate`); OV-17 chooses `eliminate` and needs none.


### 16.3 Graduation (deferred to v1.x)

Deferred: v1 collects no run content and never calls this function. The two cases are kept so that v1.x starts from a tested spec. Inputs are the aggregate `RunStats` of section 13.1.

**GX-01** Stable classifier with high rule coverage.

```json
{
  "stats": {
    "window": {"days": 45},
    "runs": 1500,
    "validatorFailures": 6,
    "humanCorrections": 9,
    "distinctOutputs": 6,
    "newInputShapeRate": 0.004,
    "miner": {"ruleCount": 11, "coverage": 0.94, "heldOutAgreement": 0.985, "heldOutN": 120}
  }
}
```

Reference engine output: eligible `true`; `GR-1` pass (1500 runs over 45 days (needs >= 200 runs and >= 30 days)); `GR-2` pass (6 distinct outputs (max 12)); `GR-3` pass (rules cover 0.94 of runs, held-out agreement 0.985 on 120 samples); `GR-4` pass (new input shapes 0.004 of runs (max 0.010)); `GR-5` pass (corrections plus validator failures 0.010 of runs (max 0.020)). The result's `proposal` is a `graduationProposal` and `stepId` is on the result; the host wraps both into the `graduation_proposal` decision record (13.3).

```json
{
  "fromRungId": "llm_node",
  "pattern": "rules_first_llm_residual",
  "ruleCount": 11,
  "residualShare": 0.06,
  "requiresApproval": true,
  "autoApply": false,
  "next": [
    "engine re-run with languageUnderstanding=none, outputDeterminism=mostly, residualHandling=llm",
    "regression tests from mined rules",
    "user approves diff"
  ]
}
```

**GX-02** Low coverage and drifting inputs.

```json
{
  "stats": {
    "window": {"days": 45},
    "runs": 1500,
    "validatorFailures": 6,
    "humanCorrections": 9,
    "distinctOutputs": 6,
    "newInputShapeRate": 0.05,
    "miner": {"ruleCount": 11, "coverage": 0.7, "heldOutAgreement": 0.985, "heldOutN": 120}
  }
}
```

Reference engine output: eligible `false`; `GR-1` pass (1500 runs over 45 days (needs >= 200 runs and >= 30 days)); `GR-2` pass (6 distinct outputs (max 12)); `GR-3` fail (rules cover 0.70 of runs, held-out agreement 0.985 on 120 samples); `GR-4` fail (new input shapes 0.050 of runs (max 0.010)); `GR-5` pass (corrections plus validator failures 0.010 of runs (max 0.020)).

### 16.4 Reopened Blueprints (ruling R3)

`Reopen` (section 2.5) is a pure function of the Blueprint, the arrival kind, the time and two audit ids, so these cases are exact. `RO-1` to `RO-11` use the Blueprint `MINI` below, which is approved and restricted; `RO-12` uses the Blueprint of section 19. Steps are evaluated against `ENV-OPEN` and the seed catalog. Unless a case says otherwise, `now` is `2026-10-26T09:00:00Z` and the actor is the owner `usr_owner`.

`MINI` is a complete Blueprint that validates against `blueprint.schema.json` (its ids use the ULID alphabet, so any validator accepts it): one step (the step of `FX-06` with its recommendation under the class of the Blueprint), one exception, one test, a deploy plan, seven triage answers (`GOOD` of 16.1) and the process facts shown:
```json
{
  "id": "bp_01M5S4KHM0MN1BP00000000000",
  "schemaVersion": "1.0",
  "version": 5,
  "etag": "wmxNedX5b34dVkBBrWLoPB8ODQ-zekAwt7NwTf2DBGk",
  "kind": "new",
  "title": "Keep customer records in sync",
  "owner": "usr_owner",
  "status": "approved",
  "sensitivity": "restricted",
  "stage": "design",
  "triage": {
    "answers": {
      "outputIsUsed": "yes",
      "couldStopDoingIt": "no",
      "processIsDocumented": "yes",
      "peopleDoItTheSameWay": "yes",
      "ownerIdentified": "yes",
      "hasKnownPainOrErrors": "no",
      "touchesRegulatedOrHighStakes": "no"
    },
    "verdict": "automate",
    "rationale": ["The process is used and stable enough to automate."]
  },
  "process": {
    "frequency": {"count": 1, "period": "week"},
    "volume": {"itemsPerRun": 40, "itemLabel": "records"},
    "timePerRunMinutes": 90,
    "people": [{"role": "analyst", "count": 2}]
  },
  "steps": [
    {
      "id": "stp_01M5S4KHM0MN1ST10000000000",
      "order": 1,
      "name": "Keep customer records in sync between the CRM and the billing tool",
      "actor": "Analyst",
      "createdBy": "coach",
      "confirmationState": "confirmed",
      "confirmedBy": "usr_owner",
      "confirmedAt": "2026-10-25T09:00:00Z",
      "diagnostic": {
        "inputStructure": "structured",
        "outputDeterminism": "yes",
        "costOfError": "medium",
        "reversibility": "partly",
        "interfaceAvailability": "api_available",
        "attendance": "unattended",
        "credentialsRequired": "yes",
        "dataSensitivity": "internal",
        "languageUnderstanding": "none",
        "judgmentRequired": "no",
        "frequency": "continuous",
        "operations": ["sync_records", "schedule_trigger"]
      },
      "environment": {
        "systems": [
          {
            "name": "CRM",
            "kind": "web_app",
            "role": "both",
            "accessModes": ["connector", "api"],
            "accessEvidence": "verified",
            "authModel": "service_account"
          },
          {
            "name": "Billing tool",
            "kind": "web_app",
            "role": "both",
            "accessModes": ["connector", "api"],
            "accessEvidence": "verified",
            "authModel": "service_account"
          }
        ],
        "builderSkill": "intermediate"
      },
      "recommendation": {
        "rungId": "api_connector",
        "toolId": "api.rest_http_request",
        "rationale": ["The output follows rules (determinism=yes, no language understanding needed), so the code family applies and models are not considered."],
        "alternatives": [],
        "status": "ok",
        "outcome": "recommended",
        "riskTier": "C"
      },
      "provenance": {"source": "user_turn", "turnId": "t1", "quote": "we keep the two tools in sync by hand"}
    }
  ],
  "exceptions": [
    {
      "id": "exc_01M5S4KHM0MN1EX10000000000",
      "description": "A customer exists in one tool only",
      "frequency": "occasional",
      "createdBy": "user",
      "confirmationState": "confirmed",
      "confirmedBy": "usr_owner",
      "confirmedAt": "2026-10-25T09:05:00Z",
      "provenance": {"source": "user_turn", "turnId": "t1", "quote": "we keep the two tools in sync by hand"}
    }
  ],
  "decisions": [],
  "tests": [
    {
      "id": "tst_01M5S4KHM0MN1TS10000000000",
      "title": "A new customer appears in both tools",
      "kind": "happy_path",
      "status": "confirmed",
      "confirmationState": "confirmed",
      "confirmedBy": "usr_owner",
      "confirmedAt": "2026-10-25T09:06:00Z",
      "createdBy": "coach"
    }
  ],
  "deployPlan": {"createdBy": "coach", "confirmationState": "confirmed", "confirmedBy": "usr_owner", "confirmedAt": "2026-10-25T09:07:00Z", "reviewAfterDays": 90},
  "auditLog": [],
  "createdAt": "2026-10-25T08:30:00Z",
  "updatedAt": "2026-10-25T10:00:00Z"
}
```

Cases `RO-4` and `RO-7` call the host step "confirm a scope" (section 2.5), which removes the scope from `reopen.pending` and removes `reopen` when it is empty.

| Id | Case | Setup | Expected | Rules |
|---|---|---|---|---|
| RO-1 | A file import opens as a draft with every confirmation reset | Approved Blueprint (one step, one exception, one test, a deploy plan) arrives by file import. | status draft; every confirmationState proposed; confirmedBy and confirmedAt gone; createdBy and provenance as received; audit blueprint_imported then confirmations_reset with counts steps 1, exceptions 1, tests 1, deployPlan 1, cards 0; reopen.pending lists sensitivity, process, triage. | R3 |
| RO-2 | A reset step gets no recommendation | RO-1 result, the step is evaluated. | status not_confirmed; no rung, no tool. | `G0` |
| RO-3 | The step is kept again, but the sensitivity is still pending | RO-1 result; the user confirms the step; reopen.pending still holds sensitivity. | needs_info; one missing item blueprint.sensitivity; trace V-REOPEN; no rung. | `V-REOPEN` |
| RO-4 | Sensitivity confirmed: the recommendation returns, equal to the original | RO-3, then the user confirms the sensitivity class; process and triage are still pending. | status ok; same rung and tool as before the reset (steps never read the process or triage scopes). | `V-REOPEN`, `G0` |
| RO-5 | Triage scope pending: no verdict, the seven answers are asked again | RO-1 result with only triage pending; the stored answers are all present. | needs_info; seven missing items, each `triage.<answer>`; no verdict, no TR trace. | `TR`, `V-REOPEN` |
| RO-6 | Process scope pending: the four process facts are asked again | RO-1 result with only process pending; the stored facts are present. | needs_info; process.frequency, process.volume, process.timePerRunMinutes, process.people missing; no verdict. | `TR`, `V-REOPEN` |
| RO-7 | Everything re-confirmed: the reopen marker is gone and the engine answers as before | RO-1 result; sensitivity, process and triage confirmed; the step kept again. | no reopen property; step recommendation equal to the original; triage verdict automate. | `V-REOPEN` |
| RO-8 | The reset changes contentHash, so an approval of the received copy does not carry over | Approved Blueprint with a reviewer's record for its hash, then imported (RO-1). | contentHash after the reset differs; the approval gate on the original is met, on the reopened copy it is not (the record is bound to the old hash). | R3, `GATE-1` |
| RO-9 | A review packet opens read-only and unmodified: same hash, the reviewer's approval applies | The owner's approved Blueprint is opened as a review packet (no reset, no arrival action). | contentHash equals the owner's; no new audit entry; the approval gate is met via approved, on any plan (also enterprise). | R2, `GATE-1` |
| RO-10 | A normal sync pull of a newer revision onto the owner's own device is not a restore | The same owner's device pulls a newer revision of the same Blueprint. | state kept: status approved, confirmations kept, no reopen property, no audit entry, hash unchanged. | R3 (ASSUMPTION) |
| RO-11 | The three arrival kinds write their own action | The same Blueprint arrives by import, by share and by restore. | blueprint_imported, blueprint_share_received or blueprint_restored, each followed by confirmations_reset; reopen.via names the kind. | R3 |
| RO-12 | On the full example: the reset changes contentHash, a review packet keeps it | The example Blueprint (in_review) is imported; and opened as a review packet. | hash after import differs; hash of the packet equals the original; counts {"cards": 1, "deployPlan": 0, "exceptions": 2, "steps": 5, "tests": 1}. | R3, R2 |

Reference engine output:

- **RO-1** status draft; counts {"steps": 1, "exceptions": 1, "tests": 1, "deployPlan": 1, "cards": 0}; audit ["blueprint_imported", "confirmations_reset"]
- **RO-2** status not_confirmed, rung null
- **RO-3** status needs_info; missing ["blueprint.sensitivity"]
- **RO-4** api_connector, api.rest_http_request, pending ["process", "triage"]
- **RO-5** status needs_info; 7 questions
- **RO-6** status needs_info; ["process.frequency", "process.volume", "process.timePerRunMinutes", "process.people"]
- **RO-7** reopen gone; api.rest_http_request; verdict automate
- **RO-8** hash changed true; gate original true, reopened false
- **RO-9** hash equal true; gate true via approved
- **RO-10** status approved; counts null
- **RO-11** [["blueprint_imported", "confirmations_reset", "import"], ["blueprint_share_received", "confirmations_reset", "share"], ["blueprint_restored", "confirmations_reset", "restore"]]
- **RO-12** counts {"steps": 5, "exceptions": 2, "tests": 1, "deployPlan": 0, "cards": 1}

### 16.5 Sensitivity order and routing (ruling R4)

`SE-1` to `SE-6` evaluate fixture steps of section 15 under different values of `Blueprint.sensitivity`; only that value changes between the runs of a case, and the trace lines quoted are the evidence the Coach shows. `SE-7` checks the order. `SE-8` (ruling S14) shows that a raise or an undo changes `inputsHash`: the stored result is then stale and the next evaluation recomputes from the new class. The ceilings are the defaults of 3.4.

| Id | Case | Setup | Expected | Rules |
|---|---|---|---|---|
| SE-1 | Baseline: internal data, a tenant flow tool is chosen | FX-06 with Blueprint sensitivity internal. | api.power_automate_cloud_flow; api.third_party_ipaas is a listed alternative; SENS names internal and ceiling ai_cloud; no T-FLOW failure. | `SENS`, `T-FLOW` |
| SE-2 | The model raises the class to confidential: the ceiling drops to tenant at once | SE-1 after a model call raised the Blueprint class (R4, no confirmation). | same tool; api.third_party_ipaas now fails T-FLOW (vendor_cloud above tenant) and disappears from the alternatives; SENS names confidential and ceiling tenant. | `SENS`, `T-FLOW` |
| SE-3 | A further raise to restricted: the ceiling is local and the tool changes | SE-2 after a second raise. | api.rest_http_request; api.power_automate_cloud_flow fails T-FLOW (tenant above local); SENS names restricted and ceiling local. | `SENS`, `T-FLOW` |
| SE-4 | The owner lowers the class again in the panel: the engine reads it at once | SE-3, then the owner lowers restricted to confidential (sensitivity_changed). | api.power_automate_cloud_flow again; SENS names confidential. Lowering is not a model action (R4). | `SENS` |
| SE-5 | A raise below the step's own class changes nothing, and the trace says which value decided | FX-10: the step's dataSensitivity is confidential. Blueprint internal, then raised to confidential. | identical rung and tool; SENS names confidential in both runs, set by the step in the first and by the Blueprint in the second. | `SENS` |
| SE-6 | A raise to restricted stops the cloud model | FX-12 (an unbounded-layout extraction on the model rung): Blueprint internal, then raised to restricted. | internal: llm.cloud_model; restricted: blocked_by_policy, T-FLOW names that restricted data may use only local model connections; SENS names restricted. | `SENS`, `T-FLOW` |
| SE-7 | The order is public < internal < confidential < restricted; only a strictly stricter class counts as tightening | Six (from, to) pairs, and the order published in the schema. | public to internal: yes; internal to internal: no; confidential to internal: no; internal to restricted: yes; restricted to restricted: no; restricted to public: no. engine order equals x-order of $defs/sensitivity. | R4 |
| SE-8 | A raise or an undo changes inputsHash: the stored result is stale and the next evaluation recomputes | FX-06 evaluated under internal (hash stored), raised to confidential (recomputed, hash stored), then undone to internal. FX-10 (own class confidential) raised from internal to confidential. | after the raise the stored hash differs from the current one (stale) and the recomputed result is for confidential; after the undo it differs again (stale) and the recomputed result and hash equal the original; the Blueprint-level hash follows the class; FX-10 keeps its hash because its effective class did not change. | S14, section 4 |

Reference engine output:

- **SE-1** api.power_automate_cloud_flow; effective class internal, set by the Blueprint (Blueprint internal, step dataSensitivity internal; the stricter wins); toolDataFlowCeiling ai_cloud, llmContentMode full
- **SE-2** api.power_automate_cloud_flow; T-FLOW: ["api.third_party_ipaas"]
- **SE-3** api.rest_http_request; T-FLOW: ["builtin.outlook_rules", "api.power_automate_cloud_flow", "api.microsoft_graph"]
- **SE-4** api.power_automate_cloud_flow
- **SE-5** same rung and tool ml.document_intelligence_prebuilt; first run: set by the step; second run: set by the Blueprint
- **SE-6** llm.cloud_model -> blocked_by_policy
- **SE-7** public to internal: yes; internal to internal: no; confidential to internal: no; internal to restricted: yes; restricted to restricted: no; restricted to public: no
- **SE-8** stale after raise true; stale after undo true; recomputed result equals the original true; step hash unchanged when the step decides the class true; Blueprint-level hash follows the class true

### 16.6 `whyNotCode` provenance (ruling R5)

Every case takes the step of `FX-01` (a plain total, `ENV-OPEN`, internal data). The user overrides to `llm_node` with `llm.cloud_model`, the reason is "I want to just describe the total in words to the model", no warning needs acknowledging, the policy is the default, and the card on file is the one below with only the stated property changed (`costPerRun` is left out on purpose: the engine fills it in, the schema does not require it and it is not part of the hash). "Override" is the state `OV-4` gives.
```json
{
  "whyNotCode": "A formula cannot read the supplier's free wording; the note has to explain the mismatch in plain words.",
  "citedDiagnosticFields": ["languageUnderstanding"],
  "validator": {"kind": "human_review", "description": "The clerk reads every draft."},
  "fallback": {"kind": "human_checkpoint", "description": "The clerk writes the note by hand."},
  "provenance": {"whyNotCode": {"origin": "user_stated"}}
}
```

| Id | Case | Setup | Expected | Rules |
|---|---|---|---|---|
| WC-1 | whyNotCode written by the user | Step FX-01 (a plain total); the user overrides to llm_node with this card on file. | card complete; whyNotCode counts as provided; the override is active. | `CARD-6`, `OV-4` |
| WC-2 | whyNotCode with no provenance | Step FX-01 (a plain total); the user overrides to llm_node with this card on file. | card incomplete: the text is long enough but its provenance is not user_stated, so whyNotCode counts as missing; the override stays incomplete (OV-4). | `CARD-6`, `OV-4` |
| WC-3 | whyNotCode drafted by the Coach (coach_inferred) | Step FX-01 (a plain total); the user overrides to llm_node with this card on file. | card incomplete: the text is long enough but its provenance is not user_stated, so whyNotCode counts as missing; the override stays incomplete (OV-4). | `CARD-6`, `OV-4` |
| WC-4 | whyNotCode computed by the engine (engine_derived) | Step FX-01 (a plain total); the user overrides to llm_node with this card on file. | card incomplete: the text is long enough but its provenance is not user_stated, so whyNotCode counts as missing; the override stays incomplete (OV-4). | `CARD-6`, `OV-4` |
| WC-5 | whyNotCode missing altogether (the baseline) | Step FX-01 (a plain total); the user overrides to llm_node with this card on file. | card incomplete: whyNotCode is missing; the override stays incomplete (OV-4). This is the baseline of WC-7. | `CARD-1`, `OV-4` |
| WC-6 | whyNotCode user_stated but only 20 characters | Step FX-01 (a plain total); the user overrides to llm_node with this card on file. | card incomplete: whyNotCode is shorter than 30 characters; the override stays incomplete (OV-4). | `CARD-1`, `OV-4` |
| WC-7 | A whyNotCode without user_stated provenance behaves exactly like a missing one | WC-2, WC-3 and WC-4 against WC-5. | same completeness, same missing list [whyNotCode], same override state. | `CARD-6` |

Reference engine output:

- **WC-1** complete true; missing []; override active; first failing rule none, CARD-6 passes
- **WC-2** complete false; missing ["whyNotCode"]; override incomplete; first failing rule CARD-6
- **WC-3** complete false; missing ["whyNotCode"]; override incomplete; first failing rule CARD-6
- **WC-4** complete false; missing ["whyNotCode"]; override incomplete; first failing rule CARD-6
- **WC-5** complete false; missing ["whyNotCode"]; override incomplete; first failing rule CARD-1
- **WC-6** complete false; missing ["whyNotCode"]; override incomplete; first failing rule CARD-1
- **WC-7** parity true

### 16.7 The approval-required gate (rulings R2 and R7)

`ApprovalGate` (section 12.4) is evaluated on `MINI` (16.4) with `status = in_review` and `sensitivity = restricted`, owner `usr_owner`. `h` is its current `contentHash`. An "approval" is an `approval_recorded` audit entry whose details are an ApprovalRecord by the reviewer `usr_coe` for `h`, decision `approved`, issued for the tenant `tnt_acme_0001` that the Blueprint belongs to, signature and `kid` verified by the host; an "attestation" is a `self_attested` entry by the owner for `h`. A context is `{plan, billableSeats}`.

| Id | Case | Setup | Expected | Rules |
|---|---|---|---|---|
| AG-1 | Restricted data, approved by a CoE Reviewer for the current hash | Restricted Blueprint; approval_recorded entry bound to the current contentHash; plan individual. | met via approved (label approved). A self-attestation is not needed. | R2, `GATE-1` |
| AG-2 | Restricted data, self-attested on the Individual plan | Restricted Blueprint; the owner's self_attested entry bound to the current hash; plan individual (no CoE Reviewer exists). | met via self_attested (label self-attested, never approved); restricted needs no other route. | R2, R7, `GATE-2`, `GATE-3` |
| AG-3 | The Free plan accepts a self-attestation too | As AG-2 on the free plan (no account, no seat count). | met via self_attested. | R7, `GATE-2` |
| AG-4 | A Team with exactly one billable seat may self-attest | Self-attestation by the owner; plan team, billableSeats 1. | met via self_attested. | R7, `GATE-2` |
| AG-5 | A second billable seat joins: the earlier self-attestation stops counting | AG-4's Blueprint evaluated again with billableSeats 2. | not met; GATE-2 fails; a CoE Reviewer approval is needed. | R7, `GATE-2` |
| AG-6 | Enterprise never accepts a self-attestation; an approval still works | A self-attested Blueprint on plan enterprise; and the same Blueprint with a reviewer's approval. | self-attestation: not met (GATE-2 fails). approval: met via approved. | R7, `GATE-1`, `GATE-2` |
| AG-7 | Hash mismatch: content edited after the attestation or the approval | A step is renamed after a self-attestation (individual) or after an approval (enterprise). | not met in both cases: the record names the old contentHash. | R2, `GATE-1`, `GATE-3` |
| AG-8 | The latest record for the current hash is a rejection | An approval at 11:00 and a rejection at 12:00, both for the current hash; enterprise. | not met; GATE-1 says the latest record is a rejection. | `GATE-1` |
| AG-9 | No host context: self-attestation fails closed, approval still works | context absent. | self-attestation not met (plan unknown); approval met via approved. | `GATE-2` |
| AG-10 | A team that reports zero billable seats is rejected | Self-attested; plan team, billableSeats 0 (ASSUMPTION: the host always counts the owner). | not met. | R7 (ASSUMPTION), `GATE-2` |
| AG-11 | A self-attestation by someone other than the owner | The entry names attestedBy usr_other; the Blueprint owner is usr_owner. | not met. | R2, `GATE-3` |
| AG-12 | The plan recorded inside the attestation is never trusted | An attestation that says plan individual, evaluated under a context of team with two seats. | not met: the gate reads the host context at evaluation time. | R7, `GATE-2` |
| AG-13 | One predicate for every gate value | AG-2's Blueprint checked for each of the six values of governance.approval.requiredBefore: build_handoff, handoff_brief, automate_flow_draft, export, automate_apply, automate_test_run. A class that sets requireApprovalBeforeHandoff uses the same predicate for handoff_brief, automate_flow_draft and automate_apply. An unknown name such as sensitivity_class is refused. | the same result for each of the six: met via self_attested. The unknown gate name raises an error. | R2 |
| AG-14 | The host context is hashed into the Blueprint-level inputsHash only | The same Blueprint under four contexts. | four different engine.inputsHash values; one step-level inputsHash; one contentHash (the context never enters the Blueprint content). | R2, R7, section 4 |
| AG-15 | A record issued for another tenant never reaches the gate (host-level) | MINI in_review, plan enterprise. The Blueprint's tenant is tnt_acme_0001 (host knowledge, as in the sync envelope). An approval_recorded entry for the current hash whose tenantId is tnt_other_0002, replayed from another organisation. The host builds verifiedRecordIds from three checks: signature valid, kid known, tenantId equal to the Blueprint's tenant. | the record is not in verifiedRecordIds, so the gate is not met and GATE-1 fails with the same reason as when there is no record at all (no approval record). The same record with tenantId tnt_acme_0001 meets the gate via approved. | R2, `GATE-1` (host check) |

Reference engine output:

- **AG-1** GATE-1 pass
- **AG-2** GATE-1 fail | GATE-2 pass | GATE-3 pass
- **AG-3** GATE-1 fail | GATE-2 pass | GATE-3 pass
- **AG-4** GATE-1 fail | GATE-2 pass | GATE-3 pass
- **AG-5** GATE-1 fail | GATE-2 fail | GATE-3 pass
- **AG-6** self-attestation: GATE-1 fail | GATE-2 fail | GATE-3 pass; approval: GATE-1 pass
- **AG-7** after the attestation: GATE-1 fail | GATE-2 pass | GATE-3 fail; after the approval: GATE-1 fail | GATE-2 fail | GATE-3 fail
- **AG-8** GATE-1 fail | GATE-2 fail | GATE-3 fail
- **AG-9** self-attestation: GATE-1 fail | GATE-2 fail | GATE-3 pass; approval: GATE-1 pass
- **AG-10** GATE-1 fail | GATE-2 fail | GATE-3 pass
- **AG-11** GATE-1 fail | GATE-2 pass | GATE-3 fail
- **AG-12** GATE-1 fail | GATE-2 fail | GATE-3 pass
- **AG-13** 6 gates, all met via self_attested; unknown name refused true
- **AG-14** 4 different root hashes, 1 step-level hash
- **AG-15** foreign record verified: false; GATE-1 fail | GATE-2 fail | GATE-3 fail; same trace as no record: true; own-tenant record: true (GATE-1 pass); ApprovalGate called with no verified list is tenant-blind and counts it: true

### 16.8 Hashes and derived fields (ruling S2)

These cases use the Blueprint of section 19 and the `x-hashes.contentHash.exclude` list generated into `blueprint.schema.json` (21 paths).

| Id | Case | Setup | Expected | Rules |
|---|---|---|---|---|
| CH-1 | The exclude list is generated and names the card's costPerRun | x-hashes.contentHash.exclude in the schema. | contains steps[].llmJustification.costPerRun; does not contain decisions[].costPerRun. | S2, C13 |
| CH-2 | A recomputed costPerRun on the step card leaves contentHash unchanged | The example's card gets a new costPerRun (a price table was loaded). | contentHash equal to the original. | S2 |
| CH-3 | The append-only decision record keeps its snapshot, and changing it changes the hash | decisions[kind=llm_justification].costPerRun is rewritten. | contentHash differs. | S2 |
| CH-4 | Card content still counts: the text and its provenance are hashed | whyNotCode edited; and its provenance changed. | contentHash differs in both cases. | S2, R5 |

Reference engine output:

- **CH-1** 21 paths
- **CH-2** equal true
- **CH-3** differs true
- **CH-4** text differs true; provenance differs true

## 17. What sibling files must provide for this engine

I did not edit these files. Contract v2 (section 8) assigns the changes to their owners; this section lists what the engine needs, and what I saw when I read the files on 2026-10-25 while their owners were still editing. Tool names are those in `design/coach-tools.json` (28 tools when I read it on 2026-10-25, with `show_control` and `raise_sensitivity` added and the old triage-recording tool removed: the triage answers are now given on host controls).

### 17.1 `coach-tools.json`

| Tool | What the engine needs | Seen on 2026-10-25 |
|---|---|---|
| `show_control` | The only write path for every closed-choice value the engine reads (ruling S12): the seven `triage.*` answers; the `diagnostic.*` enums, the `operations` checklist and the `attractorCheck` form; `decisionPoint.ruleStatus`; the `system.*` choices; `environment.builderSkill` and `environment.alreadyHasToolIds`. The host stores the click with `provenance.origin = user_stated` and no `evidence` (ruling S11), and the value counts as confirmed. The options must be the enumerations of 2.1, 2.2, 2.4 and 11.1; a stored `unknown` stays valid (11.1). | The `field` enum has 37 entries. I diffed it against `blueprint.schema.json`: the options of the 32 single-choice fields equal the schema enumerations (each triage control offers `unknown`, stored as such), the operation checklist has the 36 tags of `$defs/operationTag` and the access-mode checklist the 8 values of `stepSystem.accessModes`. Not diffed: the two host-built lists (`system.profileSystemId`, `environment.alreadyHasToolIds`), which depend on the organisation profile and the catalog. |
| `record_diagnostic_answers` | Only the numbers the user states in words: `volumePerRun` and `training {examples, classCount}`. Each becomes a chip the user accepts and is stored as `coach_inferred` with a verbatim quote in `evidence`. It writes no closed-choice value. `provenance` stays host-written. | Parameters are `volumePerRun`, `training`, `withdrawFields`, `valueEvidence` and `evidence`. Matches. |
| `record_environment_facts` | System names only (up to 8 per step); each becomes a chip and is stored with `kind unknown`. Role, access modes, `uiLocator.kind`, `authModel`, `profileSystemId`, builder skill and owned tools are closed choices answered with `show_control`. `authModel` is mandatory for unattended steps that need a login (`V-AUTH`). | Parameters are `systemNames`, `withdrawSystemNames`, `valueEvidence` and `evidence`. Matches. |
| `set_process_info` | Process facts the user states in words: summary, trigger, frequency, volume, time per run and people. Each becomes a chip with a verbatim quote and is stored as `coach_inferred` with `evidence`. Frequency, volume, time per run and people are what triage and ROI read (11.1, 11.3). | Present. Matches. |
| `request_recommendation` | Return the `EngineResult` fields unchanged (`outcome`, `proposedSplit`, `envDelta`, `manualFallback`, `missing`, `rejectedRungs`, `warnings`, `companions`, `hybrid`). The model must not rewrite `rungId` or `toolId`. | Not diffed. |
| `record_override` | `chosenToolId` required unless the chosen rung is `eliminate` (`OV-1`); `reason` of at least 15 characters (`OV-2`); `acknowledgedRuleIds` maps to `OV-3`; `human.manual_task` accepted as the manual fallback (10.3); a failed check and `coach.override.mode = forbidden` fail the call (`blocked_by_policy` for the policy case) and store nothing; a reviewer's rejection of a `pending_approval` override sets `revoked`. | `chosenToolId` is present with the right pattern and described as required unless `eliminate`. The `reason` parameter has `minLength: 1`; the schema floor is 15, so the host (or the tool schema) must enforce 15. |
| `generate_llm_justification_card` | Keep `costPerRun` out of the model's parameters; the host computes it from a price table (`CARD-4`) and it is excluded from `contentHash` (ruling S2). Pre-fill `citedDiagnosticFields` from the engine (`CARD-2`). The model may draft `whyNotCode`; the host stores it only after the user has typed or edited text, with `provenance.whyNotCode.origin = user_stated` (ruling R5, `CARD-6`). | Not diffed. |
| `raise_sensitivity` | The host rejects a target that is not strictly stricter than the current class (`sensitivity_not_tightening`), applies an accepted raise at once, writes `sensitivity_tightened` with `{from, to, turnId}` and shows an undo that writes `sensitivity_changed` (ruling R4, section 3.4). No tool lowers the class. | The tool exists, with `toClass` limited to `internal`, `confidential` and `restricted`. Matches. VERIFY after the coach owner finishes the round 3 patch. |
| `update_step` | `decisionPoints[].ruleStatus` (explicit, partial, judgment, unknown) is not written by the model: the host stores `unknown` and the user answers with `show_control`. `unknown` counts as neither rule nor judgment for `S-MIXED`. | The tool says so. Matches. |
| `request_triage_verdict`, `request_roi_estimate` | Read-only. The verdict comes from the answers the user gave on controls; there is no tool that writes them. The model never supplies ROI numbers; the verdict and ROI results carry `roi.gate` and `roi.constants`. | Both exist and change no value. The `triage.*` control options equal the answers 11.1 reads (diffed above). |
| Step, exception and test `confirmationState` | `proposed` to `confirmed` only by a user action in the UI, never by a model tool call; the host writes `createdBy`, `confirmedBy`, `confirmedAt`. The only other writer is the reopen reset (2.5), which sets `proposed` and removes `confirmedBy` and `confirmedAt`. | Gate `G0`. |
| Reopen flow (import, share, restore) | On opening, the host runs `Reopen` (2.5), writes its two audit entries, asks again for each engine-read value with option controls, offers one "keep" action per free-text entity, and removes a scope from `reopen.pending` when every value in it is confirmed. A review packet opens unmodified. A model tool call never confirms anything in this flow. | Not diffed. The coach owner patches the flow in the same round. |
| Test `status` and run results | `status` is the confirmation status (`proposed` or `confirmed`, always equal to `confirmationState`) and is part of the content hash. The run outcome is its own field, `lastRunOutcome` (`passed`, `failed`, `skipped`), beside `lastRunAt`, `lastRunId` and `lastRunDetail`. All four are host-written from the run report and excluded from `contentHash`. Older drafts stored the outcome in `status`. | The test-case rules and the attended-run tool in the file write `lastRunOutcome` and leave `status` alone. Matches. |

### 17.2 Other sibling files

| File | Needed | Why |
|---|---|---|
| `policy.schema.json`, `settings-catalog.md` | (a) `toolDataFlowCeiling` per class in `data.sensitivityRules` (values `local`, `tenant`, `vendor_cloud`, `ai_cloud`) with the defaults of 3.4, and `llmContentMode` allowing `none`. (b) `preferredToolIds` in the environment profile. (c) Software with status `prohibited` forbids its `providesToolIds` (3.2, ASSUMPTION). (d) `orgToolEntry.toolId` uses the org pattern `^org\.[a-z0-9][a-z0-9_]{0,59}$`, `providesToolIds` use catalog `toolId`s, an org tool's `capabilities` come from the 36-tag vocabulary, and the optional extension fields default as in C3. (e) The refusal word for the agent is `forbidden`. | The projection of section 3. At the time I read `policy.schema.json` it already used `forbidden` but did not yet contain `toolDataFlowCeiling` or `preferredToolIds`; VERIFY after the policy owner finishes. |
| `architecture.md` | The engine runs as the same library on the client and on the sync server. After a sync merge the merging client recomputes the derived fields (`recommendation`, `roi`, the `triage` verdict and trace; marked `x-derived` in the schema) under its own rules and catalog versions, recomputes `inputsHash` and `traceHash`, and flags a result `stale` when `inputsHash` differs. The server re-runs the engine at status transitions only (submit for review, approve), on the decrypted document of a synced Blueprint, to check org rules. It never re-runs it on a merge and not on every push; for a local-only Blueprint the check runs on the reviewer's client (architecture X3, 3.4). A price table for `CARD-4` is needed and is outside the engine. For round 3: restore from backup or history, share receipt and file import run `Reopen` (2.5) when the client opens the Blueprint (ASSUMPTION: the server returns the revision as it is stored and does not reset anything); a review packet and a same-owner sync pull do not; a raise to `restricted` stops uploads (ruling S4) and "Delete backed-up copies" removes every server revision and the history and writes `blueprint_backup_deleted` with `revisionCount` and `includesHistory` (ruling S6); the host supplies `context {plan, billableSeats}` (3.7) to the engine on the client and on the server, and the server applies the same `ApprovalGate` (12.4) at the status transitions that need an approval. | Sections 1.3 (G1), 2.5, 3.7, 4, 12.3, 12.4. |
| `tiers.md` | No engine change. Custom-predicate org rules stay an Enterprise feature; the engine only sees resolved actions (3.3). The permission-matrix row "Record self-attestation" (Blueprint owner; Individual, or Team with one billable seat; not Team with two or more; not Enterprise) is what `GATE-2` and `GATE-3` implement. | Section 12.4. |

## 18. Assumptions, things to verify, open questions

### 18.1 Constants in the rules pack (all ASSUMPTION unless noted)

| Constant | Value | Used by |
|---|---|---|
| Attractor text minimum | 10 characters each for `ruleAttempt` and `whereItBreaks` (matches `coach-tools.json`) | `V-ATTR`, `RL-EVID` |
| Minimum labeled examples | max(100, 30 x `classCount`) with a stable label set | `RP-PARSE`, `T-TRAIN` |
| Bundle size | At most 3 tools, same rung | `T-COVER` |
| Tool data-flow ceilings | Defaults of the policy key `toolDataFlowCeiling`: public and internal: ai_cloud; confidential: tenant; restricted: local; hard cap for restricted: tenant | `T-FLOW` |
| Human volume limit | `humanMaxItemsPerRun` = 50 items per run for an open-ended step a person can take | `RH-AUTH` clause (d) |
| Override reason floor | 15 characters (schema `minLength`); policy may only raise it | `OV-2` |
| Org tool defaults | `dataFlow = vendor_cloud`, `unattendedSupport = no` when omitted | `T-FLOW`, `T-EXEC` |
| Trigger candidate sets | See 7.3 | `T-WRAP` |
| Periods per year | hour 2080, day 260, week 52, month 12, quarter 4, year 1, ad_hoc 1 (working-time periods) | ROI |
| ROI placeholders | Section 11.3 tables: per-rung build and maintain hours, test overhead 0.3, residual share 0.10, triage-mode share 0.5 / 16 h / 4 h | ROI |
| Payback limits | 1.0 year; marginal factor 2.0; gate mode `advisory` | `TR-3` |
| Graduation thresholds | Section 13.2 (deferred to v1.x) | `GR-1` to `GR-5` |
| Sensitivity order | `public < internal < confidential < restricted` (contract, ruling R4; `x-order` in the schema) | `SENS`, 3.4 |
| Self-attestation context | Plan `free` or `individual`, or `team` with exactly 1 billable seat; never `enterprise`; unknown fails closed (contract, ruling R7) | `GATE-2` |
| Reopen scopes | `sensitivity`, `process`, `triage` (ASSUMPTION; the contract names the fields, not the grouping) | `V-REOPEN`, 2.5 |

Whether any of these become admin settings is open (question 8). They live in the rules pack and change only with a new `rulesPackVersion`, so old results stay reproducible.

### 18.2 VERIFY

- 27 of the 29 seed catalog entries carry `VERIFY:` or `ASSUMPTION:` notes (23 carry `VERIFY:`). Ten Microsoft documentation pages were read on 2026-10-25 and are cited in the entries' `sources`; the Power Automate HTTP connector page and the Outlook rules page returned HTTP 404, so connector licence tiers and the exact set of server-side mail-rule actions are `VERIFY`. No price, licence tier or limit in the catalog is stated as fact without a cited source.
- Whether each `tenant`-class tool actually keeps data inside the customer's tenant depends on configuration (3.4).
- Provider zero-retention options per model route (catalog entry `llm.cloud_model`).
- Whether `settings-catalog.md`'s default sensitivity matrix is confirmed by the owner (it is itself marked ASSUMPTION there).
- Whether the answer enumerations in `coach-tools.json` for triage match section 11.1.
- Whether the `ApprovalRecord` that the architecture file stores in `approval_recorded` audit details has the keys `ApprovalGate` reads (`recordId`, `blueprintId`, `contentHash`, `decision`, `at`, `reviewerId`) and the keys the host needs to decide which records are verified (`kid`, `signature`, `tenantId`; `tenantId` is required in the schema since 2026-10-26), and whether the host can supply the verified record ids (12.4).
- Whether the host can supply the billable-seat count and the plan to the engine on the client without a network call (3.7); the entitlement token carries `plan` and `seats` (ruling R1).

### 18.3 Open questions for the owner

Resolved by contract v2 and removed from this list: where `llm_agent` sits (it follows `human_checkpoint`), org-preferred tools (`preferredToolIds` and `TB-0`), and the missing `interfaceAvailability` value (there is no `none`; the paper-and-phone exemption stays).

1. **What "unfit" means for a person.** Contract v2 says the agent is reached only where a human checkpoint is forbidden or unfit. I made that testable: a person can take an open-ended step up to 50 items per run (`humanMaxItemsPerRun`, ASSUMPTION), and the manual-task tool now covers the language operations and `plan_open_ended`. An open-ended, attended, low-risk step therefore goes to a person first and the agent is a discouraged alternative. Confirm this reading and the number.
2. **Frequency.** `frequency` does not change the rung. Should a once-a-year step prefer the human rung when ROI is below the limit? Today ROI is advisory and decides nothing.
3. **Restricted data and models.** With the default matrix, restricted data plus no local model gives `blocked_by_policy` for any step that needs language understanding. Confirm this is intended, since local model support is a launch requirement.
4. **ROI numbers and the gate.** Build and maintain hours are placeholders and `TR-3` is advisory. Who calibrates them, from which design-partner data, and what is the rule for switching `roiGate` to `enforced`? Companion tools add no cost in v1.
5. **Graduation data (v1.x).** The rule miner needs logged inputs and outputs. For `confidential` and `restricted` classes, where may that data live, and may it be mined at all? v1 collects none.
6. **Manual fallback.** Choosing `human.manual_task` is always allowed and recorded as an override. Should an approver be required when a `no_fit` step is left manual in a Blueprint that claims a time saving?
7. **`llm_agent` at launch.** Keep the rung discouraged but reachable (default `coach.llmAgent.mode = allowed_with_justification`), or hide it until the first customers ask?
8. **Admin-tunable constants.** Which constants of 18.1 should be admin settings (training-example floor, payback limit, `humanMaxItemsPerRun`)?
9. **Org tool defaults.** An org tool that omits `dataFlow` is treated as `vendor_cloud` and one that omits `unattendedSupport` as `no`, so a half-filled entry is never recommended into a place it should not go. Confirm that fail-safe default.
10. **Per-field confirmation after a reopen (ruling R3).** The ruling asks for value-by-value confirmation, but the Blueprint has no per-field confirmation flag, so one step flag (`G0`) and three scope markers (`reopen.pending`) carry it (2.5). Is that enough, or should each diagnostic field carry its own confirmation state so the engine can ignore a single unconfirmed value?
11. **A reviewer's rejection and a self-attestation (ruling R7).** Today an eligible self-attestation still meets the gate after a reviewer rejected the same content (12.4). Should a rejection veto it?
12. **Process people in the reopen scope.** `process.people` is added to the process facts that are asked again after a reopen, because triage and ROI read it; the contract lists only frequency, volume and time per run. Confirm.
13. **The cost snapshot in a decision record.** `costPerRun` on the step card is excluded from `contentHash` (ruling S2); the snapshot copied into the `llm_justification` decision at confirmation stays in the hash (`CH-3`). Confirm that an append-only record should be hashed.

## 19. Example Blueprint

One complete, valid Blueprint for the process "Supplier invoice intake and approval": `kind = new`, five steps, two exceptions, two tests (one proposed, one confirmed, with `exampleData`), a proposed deploy plan, one export record, two decision records (a user override and a confirmed LLM justification card whose `whyNotCode` is `user_stated`), a triage block with per-answer provenance, a classified ROI estimate that carries its gate mode and constants, a root `engine` block with the Blueprint-level `inputsHash` and the host context (`plan = team`, `billableSeats = 3`), and sync fields (`baseRev`, `lastSyncedRev`). Every step, exception, test and the deploy plan carries `createdBy` and `confirmationState`, with `confirmedBy` and `confirmedAt` where confirmed, and the diagnostic of steps 2 and 4, the triage answers and the process facts carry per-field provenance: closed-choice answers are `user_stated` without `evidence` (a click on a host control, ruling S11), and the volume and frequency numbers are `coach_inferred` with a verbatim quote. Step results, triage and ROI come from the reference run of this spec. Identifiers are generated ULIDs; `org_example`, `usr_ap_lead`, the model key `example/model-a` and the environment profile id `finance-windows` are invented placeholders. The export's `contentHash` is the SHA-256 of a stand-in byte string, and `etag` is the base64url SHA-256 of the canonical JSON (sorted keys, no spaces) without `etag` and `sync`, which equals RFC 8785 for this document.

What it shows:

| Step | Result |
|---|---|
| 1. Save invoice PDFs from the shared mailbox | `api_connector`: `api.power_automate_cloud_flow`, tier A. |
| 2. Read the fields from each invoice PDF | `parser_ocr_ml`: `ml.document_intelligence_prebuilt` hosted by `script.powershell`, `human.review_queue` companion, hybrid `ml_human_exception`, tier B. |
| 3. Match each invoice to its purchase order | `script`: engine recommends `script.powershell`; the user overrides to `script.python` (decision `kind = override`, state active, warnings acknowledged), tier B. |
| 4. Approve invoices over 5,000 | `human_checkpoint`: `human.approval_flow`, tier D. |
| 5. Draft the rejection note to the supplier | `llm_node`: `llm.cloud_model` hosted by `script.powershell`, confirmed justification card (decision `kind = llm_justification`), tier B. |

Triage: `automate` with the conditions `coe_review_required` and `human_checkpoint_on_writes` (the process is marked regulated or high-stakes) and the warning `W-STABILITY-PARTIAL`. ROI (classified mode, advisory gate, placeholder constants): 260 runs a year, 2 people, 1040 manual hours, 811.2 hours saved, 80.6 build hours, 19.0 maintenance hours, payback about 0.1 years.

Validated against `design/blueprint.schema.json` with 0 errors. The same Blueprint with `status` set to `approved` also validates, because the conditions the schema ties to that status hold: a triage verdict, confirmed steps, a recommendation on every step, and a confirmed card on the model step. Ninety-five deliberately broken variants were rejected and thirty-two valid variants were accepted (the new audit actions, the new contexts, control answers without evidence, mid-interview diagnostics, unpriced cards and two reopened copies, section 1.4). The content hash stayed the same after an export was appended, the engine results were recomputed and a test run was recorded, and it changed when content or a test confirmation changed (`CH-1` to `CH-4`).

```json

{
  "id": "bp_01M5S4KHM03YGQEZC6J1MKH0EZ",
  "schemaVersion": "1.0",
  "version": 7,
  "etag": "KTGkp_kldPtCdJsz_vGalk4sKhRTz0Cx6KYrHj16c4o",
  "kind": "new",
  "title": "Supplier invoice intake and approval",
  "owner": "usr_ap_lead",
  "orgId": "org_example",
  "status": "in_review",
  "sensitivity": "confidential",
  "stage": "design",
  "triage": {
    "verdict": "automate",
    "rationale": ["The process is used and stable enough to automate. The placeholder ROI estimate is within the payback limit."],
    "answers": {
      "outputIsUsed": "yes",
      "couldStopDoingIt": "no",
      "processIsDocumented": "yes",
      "peopleDoItTheSameWay": "mostly",
      "ownerIdentified": "yes",
      "hasKnownPainOrErrors": "yes",
      "touchesRegulatedOrHighStakes": "yes"
    },
    "conditions": ["coe_review_required", "human_checkpoint_on_writes"],
    "warnings": [
      {
        "ruleId": "W-STABILITY-PARTIAL",
        "text": "The process is only partly documented or followed; settle the differences during decompose."
      }
    ],
    "ruleTrace": [
      {"ruleId": "TR-1", "result": "pass", "because": "output is used and the process cannot simply stop"},
      {"ruleId": "TR-2", "result": "pass", "because": "owner, documentation and consistency gates pass"},
      {
        "ruleId": "TR-3",
        "result": "info",
        "because": "constants (ASSUMPTION placeholders): triage mode: share 0.50, build 16h, maintain 4h/y; test overhead 0.30; residual share 0.10; payback limit 1.0 y, marginal x2.0; gate advisory"
      },
      {"ruleId": "TR-3", "result": "pass", "because": "payback 0.04 years within 1.0"},
      {
        "ruleId": "TR-4",
        "result": "condition",
        "because": "regulated or high-stakes: CoE review and a human checkpoint on writes"
      }
    ],
    "engine": {
      "rulesPackVersion": "0.3.0-draft",
      "catalogVersion": "2026.10.25-seed",
      "policyVersion": 12,
      "inputsHash": "eb3f542b8e42768c6061d6bd2e5dddd5f452b1d86e81ec52416ee48d3030f7cc",
      "computedAt": "2026-10-25T09:00:00Z"
    },
    "provenance": {
      "outputIsUsed": {"origin": "user_stated"},
      "hasKnownPainOrErrors": {"origin": "user_stated"},
      "touchesRegulatedOrHighStakes": {"origin": "user_stated"}
    }
  },
  "process": {
    "summary": "Supplier invoices arrive by email as PDFs. They are read, matched to purchase orders, approved when large, and rejected ones get a note back.",
    "trigger": "An email arrives in the shared invoices mailbox",
    "frequency": {"count": 1, "period": "day"},
    "volume": {"itemsPerRun": 40, "itemLabel": "invoices"},
    "timePerRunMinutes": 120,
    "people": [{"role": "AP clerk", "count": 2}],
    "provenance": {
      "frequency": {
        "origin": "coach_inferred",
        "evidence": {"source": "user_turn", "turnId": "t02", "quote": "the mailbox is worked every working day", "at": "2026-10-25T08:31:00Z"}
      },
      "volume": {
        "origin": "coach_inferred",
        "evidence": {
          "source": "user_turn",
          "turnId": "t06",
          "quote": "about forty invoices come in on a normal day",
          "at": "2026-10-25T08:36:00Z"
        }
      }
    }
  },
  "steps": [
    {
      "id": "stp_01M5S4KHM0CEHRD78WBHCGPXDT",
      "order": 1,
      "name": "Save invoice PDFs from the shared mailbox",
      "description": "Every PDF attached to a new email in the shared invoices mailbox is copied to the invoice folder.",
      "actor": "Mail system",
      "inputs": [{"name": "Invoice email", "format": "email"}],
      "outputs": [{"name": "Invoice PDF", "format": "PDF"}],
      "decisionPoints": [],
      "exceptionRefs": [],
      "diagnostic": {
        "inputStructure": "structured",
        "outputDeterminism": "yes",
        "costOfError": "low",
        "reversibility": "reversible",
        "interfaceAvailability": "api_available",
        "attendance": "unattended",
        "credentialsRequired": "yes",
        "dataSensitivity": "confidential",
        "languageUnderstanding": "none",
        "judgmentRequired": "no",
        "frequency": "daily",
        "operations": ["transfer_data", "event_trigger"],
        "volumePerRun": 40
      },
      "recommendation": {
        "rungId": "api_connector",
        "toolId": "api.power_automate_cloud_flow",
        "rationale": [
          "The output follows rules (determinism=yes, no language understanding needed), so the code family applies and models are not considered.",
          "Earlier rungs were rejected: eliminate (E-1); builtin_feature (T-EXEC).",
          "api.power_automate_cloud_flow is the first tool at rung api_connector that passes every hard rule for this step in this environment."
        ],
        "alternatives": [
          {
            "rungId": "script",
            "toolId": "script.powershell",
            "whyNot": "a lower rung is chosen first (first rung that fits wins)"
          }
        ],
        "status": "ok",
        "outcome": "recommended",
        "riskTier": "A",
        "cardRequired": false,
        "rejectedRungs": [
          {"rungId": "eliminate", "rule": "E-1", "whyNot": "necessity=required, requiredByControl=False", "stage": "rung"},
          {
            "rungId": "builtin_feature",
            "rule": "T-EXEC",
            "whyNot": "builtin.excel_power_query cannot run unattended",
            "stage": "tool",
            "toolId": "builtin.excel_power_query",
            "failedRules": ["T-EXEC", "T-SYS"]
          }
        ],
        "warnings": [],
        "policyNotes": [],
        "companions": [],
        "ruleTrace": [
          {
            "ruleId": "SENS",
            "result": "info",
            "because": "effective class confidential, set by the Blueprint (Blueprint confidential, step dataSensitivity confidential; the stricter wins); toolDataFlowCeiling tenant, llmContentMode redacted"
          },
          {
            "ruleId": "RP-CODE",
            "rungId": "api_connector",
            "result": "pass",
            "because": "needsUnderstanding=False, outputDeterminism=yes, judgmentRequired=no"
          },
          {
            "ruleId": "RP-ACC-2",
            "rungId": "api_connector",
            "result": "pass",
            "because": "needs one of ['api', 'connector']; step access is ['api', 'connector', 'file_or_db']"
          },
          {
            "ruleId": "T-SYS",
            "rungId": "api_connector",
            "toolId": "api.rest_http_request",
            "result": "fail",
            "class": "capability",
            "because": "api.rest_http_request does not cover system kind email_or_calendar"
          },
          {
            "ruleId": "T-SYS",
            "rungId": "api_connector",
            "toolId": "api.rest_http_request",
            "result": "fail",
            "class": "capability",
            "because": "api.rest_http_request does not cover system kind spreadsheet_or_file"
          },
          {
            "ruleId": "T-ACCESS",
            "rungId": "api_connector",
            "toolId": "api.rest_http_request",
            "result": "fail",
            "class": "capability",
            "because": "api.rest_http_request reaches systems through ['api']; Invoice folder offers ['connector', 'file_or_db']"
          },
          {
            "ruleId": "T-ACCESS",
            "rungId": "api_connector",
            "toolId": "api.microsoft_graph",
            "result": "fail",
            "class": "capability",
            "because": "api.microsoft_graph reaches systems through ['api']; Invoice folder offers ['connector', 'file_or_db']"
          },
          {
            "ruleId": "T-FLOW",
            "rungId": "api_connector",
            "toolId": "api.third_party_ipaas",
            "result": "fail",
            "class": "policy",
            "because": "api.third_party_ipaas sends data to vendor_cloud; confidential data is limited to tenant"
          },
          {
            "ruleId": "T-ALL",
            "rungId": "api_connector",
            "toolId": "api.power_automate_cloud_flow",
            "result": "pass",
            "because": "no hard tool predicate failed (T-PERM, T-INST, T-PLAT, T-SCRIPT, T-EXEC, T-CRED, T-FLOW, T-SIZE, T-VAR, T-TRAIN, T-SYS, T-ACCESS, T-LOC, T-HOST)"
          },
          {
            "ruleId": "T-COVER",
            "rungId": "api_connector",
            "toolId": "api.power_automate_cloud_flow",
            "result": "pass",
            "because": "covers ['transfer_data']"
          },
          {
            "ruleId": "TB",
            "rungId": "api_connector",
            "toolId": "api.power_automate_cloud_flow",
            "result": "selected",
            "because": "tie-breakers in order: TB-0 org preferred, TB-1 owned, TB-2 fewest warnings, TB-3 no host needed, TB-4 lowest skill, TB-5 lowest data flow, TB-6 fewest capabilities, TB-7 catalog order"
          },
          {
            "ruleId": "LADDER",
            "rungId": "api_connector",
            "result": "stop",
            "because": "first rung that fits wins; later rungs are not evaluated for the decision"
          },
          {"ruleId": "RK", "result": "info", "because": "risk tier A (costOfError=low, reversibility=reversible)"}
        ],
        "engine": {
          "rulesPackVersion": "0.3.0-draft",
          "catalogVersion": "2026.10.25-seed",
          "policyVersion": 12,
          "inputsHash": "8a5147f9822c8f4bf220cead6ba84a264a43ab394aaa8e1ed5be832ca4ac59d4",
          "computedAt": "2026-10-25T09:00:00Z"
        }
      },
      "createdBy": "coach",
      "confirmationState": "confirmed",
      "confirmedBy": "usr_ap_lead",
      "confirmedAt": "2026-10-25T08:50:00Z",
      "provenance": {
        "source": "user_turn",
        "turnId": "t11",
        "quote": "every invoice that comes into the shared mailbox",
        "at": "2026-10-25T08:35:00Z"
      },
      "environment": {
        "systems": [
          {
            "name": "Shared invoices mailbox",
            "kind": "email_or_calendar",
            "role": "source",
            "accessModes": ["connector", "api"],
            "accessEvidence": "verified",
            "authModel": "service_account"
          },
          {
            "name": "Invoice folder",
            "kind": "spreadsheet_or_file",
            "role": "target",
            "accessModes": ["connector", "file_or_db"],
            "accessEvidence": "verified",
            "authModel": "none"
          }
        ],
        "builderSkill": "intermediate"
      },
      "createdAt": "2026-10-25T09:00:00Z",
      "updatedAt": "2026-10-25T09:00:00Z"
    },
    {
      "id": "stp_01M5S4KHM04X91912JZMP35F6K",
      "order": 2,
      "name": "Read the fields from each invoice PDF",
      "description": "Supplier, invoice number, date, purchase order number and total are read from the PDF into a row.",
      "actor": "AP clerk",
      "inputs": [{"name": "Invoice PDF", "format": "PDF"}],
      "outputs": [{"name": "Invoice row", "format": "Excel sheet"}],
      "decisionPoints": [],
      "exceptionRefs": ["exc_01M5S4KHM0AX7QGD9RSGBGPAWE", "exc_01M5S4KHM0BZRYZ5F7HSK9KC3H"],
      "diagnostic": {
        "inputStructure": "semi_structured",
        "outputDeterminism": "mostly",
        "costOfError": "medium",
        "reversibility": "reversible",
        "interfaceAvailability": "file_exchange",
        "attendance": "unattended",
        "credentialsRequired": "no",
        "dataSensitivity": "confidential",
        "languageUnderstanding": "none",
        "judgmentRequired": "no",
        "frequency": "weekly",
        "operations": ["extract_fields_document"],
        "residualHandling": "human_review",
        "inputVariability": "many_templates",
        "attractorCheck": {
          "ruleAttempt": "look for the word Total followed by a number",
          "whereItBreaks": "some suppliers put the total in a table and others print it twice"
        },
        "volumePerRun": 40,
        "provenance": {
          "outputDeterminism": {"origin": "user_stated"},
          "inputVariability": {"origin": "user_stated"},
          "operations": {"origin": "user_stated"},
          "attractorCheck": {"origin": "user_stated"},
          "residualHandling": {"origin": "user_stated"},
          "volumePerRun": {
            "origin": "coach_inferred",
            "evidence": {
              "source": "user_turn",
              "turnId": "t06",
              "quote": "about forty invoices come in on a normal day",
              "at": "2026-10-25T08:36:00Z"
            }
          }
        }
      },
      "recommendation": {
        "rungId": "parser_ocr_ml",
        "toolId": "ml.document_intelligence_prebuilt",
        "rationale": [
          "The step reads fields or labels from documents or text without needing to understand the wording; a template, a prebuilt extractor or a trained classifier is enough, so the language-model rung is not considered.",
          "Earlier rungs were rejected: eliminate (E-1); builtin_feature (T-COVER); api_connector (RP-ACC-2); script (T-COVER); ui_automation (RP-ACC-4).",
          "ml.document_intelligence_prebuilt is the first tool at rung parser_ocr_ml that passes every hard rule for this step in this environment.",
          "ml.document_intelligence_prebuilt runs inside script.powershell."
        ],
        "alternatives": [],
        "status": "ok",
        "outcome": "recommended",
        "riskTier": "B",
        "cardRequired": false,
        "rejectedRungs": [
          {"rungId": "eliminate", "rule": "E-1", "whyNot": "necessity=required, requiredByControl=False", "stage": "rung"},
          {
            "rungId": "builtin_feature",
            "rule": "T-COVER",
            "whyNot": "no single tool or same-rung bundle covers ['extract_fields_document']",
            "stage": "tool",
            "toolId": "builtin.windows_task_scheduler",
            "failedRules": ["T-COVER"]
          },
          {
            "rungId": "api_connector",
            "rule": "RP-ACC-2",
            "whyNot": "needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']",
            "stage": "rung"
          },
          {
            "rungId": "script",
            "rule": "T-COVER",
            "whyNot": "no single tool or same-rung bundle covers ['extract_fields_document']",
            "stage": "tool",
            "toolId": "script.powershell",
            "failedRules": ["T-COVER"]
          },
          {
            "rungId": "ui_automation",
            "rule": "RP-ACC-4",
            "whyNot": "needs one of ['ui']; step access is ['builtin', 'file_or_db', 'scriptable']",
            "stage": "rung"
          }
        ],
        "warnings": [],
        "policyNotes": [],
        "companions": [
          {
            "role": "residual",
            "rungId": "human_checkpoint",
            "toolId": "human.review_queue",
            "ruleId": "H-RESID",
            "why": "fields the extractor is unsure of or fails validation go to a person"
          }
        ],
        "ruleTrace": [
          {
            "ruleId": "SENS",
            "result": "info",
            "because": "effective class confidential, set by the Blueprint (Blueprint confidential, step dataSensitivity confidential; the stricter wins); toolDataFlowCeiling tenant, llmContentMode redacted"
          },
          {
            "ruleId": "RP-PARSE",
            "rungId": "parser_ocr_ml",
            "result": "pass",
            "because": "extract path=True, classify path=False (needs labelSetStable and >=100 examples)"
          },
          {
            "ruleId": "T-VAR",
            "rungId": "parser_ocr_ml",
            "toolId": "parser.regex_template",
            "result": "fail",
            "class": "capability",
            "because": "input variability many_templates exceeds the tool's few_templates"
          },
          {
            "ruleId": "T-TRAIN",
            "rungId": "parser_ocr_ml",
            "toolId": "ml.trained_text_classifier",
            "result": "fail",
            "class": "capability",
            "because": "needs a stable label set and at least 100 labeled examples"
          },
          {
            "ruleId": "T-ALL",
            "rungId": "parser_ocr_ml",
            "toolId": "ml.document_intelligence_prebuilt",
            "result": "pass",
            "because": "no hard tool predicate failed (T-PERM, T-INST, T-PLAT, T-SCRIPT, T-EXEC, T-CRED, T-FLOW, T-SIZE, T-VAR, T-TRAIN, T-SYS, T-ACCESS, T-LOC, T-HOST)"
          },
          {
            "ruleId": "T-COVER",
            "rungId": "parser_ocr_ml",
            "toolId": "ml.document_intelligence_prebuilt",
            "result": "pass",
            "because": "covers ['extract_fields_document']"
          },
          {
            "ruleId": "TB",
            "rungId": "parser_ocr_ml",
            "toolId": "ml.document_intelligence_prebuilt",
            "result": "selected",
            "because": "tie-breakers in order: TB-0 org preferred, TB-1 owned, TB-2 fewest warnings, TB-3 no host needed, TB-4 lowest skill, TB-5 lowest data flow, TB-6 fewest capabilities, TB-7 catalog order"
          },
          {
            "ruleId": "LADDER",
            "rungId": "parser_ocr_ml",
            "result": "stop",
            "because": "first rung that fits wins; later rungs are not evaluated for the decision"
          },
          {"ruleId": "RK", "result": "info", "because": "risk tier B (costOfError=medium, reversibility=reversible)"}
        ],
        "engine": {
          "rulesPackVersion": "0.3.0-draft",
          "catalogVersion": "2026.10.25-seed",
          "policyVersion": 12,
          "inputsHash": "3f78939b8764d16cbc9ae5751f53815d9bff1175b422779d763ae5874bb46da8",
          "computedAt": "2026-10-25T09:00:00Z"
        },
        "hostToolId": "script.powershell",
        "hybrid": {"pattern": "ml_human_exception", "spine": {"rungId": "parser_ocr_ml", "toolId": "ml.document_intelligence_prebuilt"}}
      },
      "createdBy": "coach",
      "confirmationState": "confirmed",
      "confirmedBy": "usr_ap_lead",
      "confirmedAt": "2026-10-25T08:50:00Z",
      "provenance": {"source": "user_turn", "turnId": "t12", "quote": "someone types the numbers off the PDF", "at": "2026-10-25T08:35:00Z"},
      "environment": {
        "systems": [{"name": "Invoice folder", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified"}],
        "builderSkill": "intermediate"
      },
      "createdAt": "2026-10-25T09:00:00Z",
      "updatedAt": "2026-10-25T09:00:00Z"
    },
    {
      "id": "stp_01M5S4KHM0VX28M6RQSPWKFF9Y",
      "order": 3,
      "name": "Match each invoice to its purchase order",
      "description": "Each invoice row is looked up against the purchase order list; amount and supplier must match within the stated tolerance.",
      "actor": "AP clerk",
      "inputs": [{"name": "Invoice row", "format": "Excel sheet"}, {"name": "Purchase order list", "format": "Excel sheet"}],
      "outputs": [{"name": "Matched or rejected row", "format": "Excel sheet"}],
      "decisionPoints": [
        {
          "question": "Do amount and supplier match the purchase order?",
          "outcomes": ["matched", "rejected"],
          "ruleStatus": "explicit"
        }
      ],
      "exceptionRefs": ["exc_01M5S4KHM0AX7QGD9RSGBGPAWE"],
      "diagnostic": {
        "inputStructure": "structured",
        "outputDeterminism": "yes",
        "costOfError": "medium",
        "reversibility": "reversible",
        "interfaceAvailability": "file_exchange",
        "attendance": "unattended",
        "credentialsRequired": "no",
        "dataSensitivity": "confidential",
        "languageUnderstanding": "none",
        "judgmentRequired": "no",
        "frequency": "weekly",
        "operations": ["lookup_join", "validate_rules"],
        "volumePerRun": 40
      },
      "recommendation": {
        "rungId": "script",
        "toolId": "script.powershell",
        "rationale": [
          "The output follows rules (determinism=yes, no language understanding needed), so the code family applies and models are not considered.",
          "Earlier rungs were rejected: eliminate (E-1); builtin_feature (T-EXEC); api_connector (RP-ACC-2).",
          "script.powershell is the first tool at rung script that passes every hard rule for this step in this environment."
        ],
        "alternatives": [
          {"rungId": "script", "toolId": "script.python", "whyNot": "same rung; tie-breakers ranked script.powershell first"},
          {
            "rungId": "script",
            "toolId": "script.office_scripts",
            "whyNot": "same rung; tie-breakers ranked script.powershell first"
          }
        ],
        "status": "ok",
        "outcome": "recommended",
        "riskTier": "B",
        "cardRequired": false,
        "rejectedRungs": [
          {"rungId": "eliminate", "rule": "E-1", "whyNot": "necessity=required, requiredByControl=False", "stage": "rung"},
          {
            "rungId": "builtin_feature",
            "rule": "T-EXEC",
            "whyNot": "builtin.excel_formulas cannot run unattended",
            "stage": "tool",
            "toolId": "builtin.excel_formulas",
            "failedRules": ["T-EXEC"]
          },
          {
            "rungId": "api_connector",
            "rule": "RP-ACC-2",
            "whyNot": "needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']",
            "stage": "rung"
          }
        ],
        "warnings": [],
        "policyNotes": [],
        "companions": [],
        "ruleTrace": [
          {
            "ruleId": "SENS",
            "result": "info",
            "because": "effective class confidential, set by the Blueprint (Blueprint confidential, step dataSensitivity confidential; the stricter wins); toolDataFlowCeiling tenant, llmContentMode redacted"
          },
          {
            "ruleId": "RP-CODE",
            "rungId": "script",
            "result": "pass",
            "because": "needsUnderstanding=False, outputDeterminism=yes, judgmentRequired=no"
          },
          {
            "ruleId": "RP-ACC-3",
            "rungId": "script",
            "result": "pass",
            "because": "needs one of ['api', 'file_or_db', 'http_html', 'scriptable']; step access is ['builtin', 'file_or_db', 'scriptable']"
          },
          {
            "ruleId": "T-SYS",
            "rungId": "script",
            "toolId": "script.sql",
            "result": "fail",
            "class": "capability",
            "because": "script.sql does not cover system kind spreadsheet_or_file"
          },
          {
            "ruleId": "T-ALL",
            "rungId": "script",
            "toolId": "script.powershell",
            "result": "pass",
            "because": "no hard tool predicate failed (T-PERM, T-INST, T-PLAT, T-SCRIPT, T-EXEC, T-CRED, T-FLOW, T-SIZE, T-VAR, T-TRAIN, T-SYS, T-ACCESS, T-LOC, T-HOST)"
          },
          {
            "ruleId": "T-COVER",
            "rungId": "script",
            "toolId": "script.powershell",
            "result": "pass",
            "because": "covers ['lookup_join', 'validate_rules']"
          },
          {
            "ruleId": "TB",
            "rungId": "script",
            "toolId": "script.powershell",
            "result": "selected",
            "because": "tie-breakers in order: TB-0 org preferred, TB-1 owned, TB-2 fewest warnings, TB-3 no host needed, TB-4 lowest skill, TB-5 lowest data flow, TB-6 fewest capabilities, TB-7 catalog order"
          },
          {
            "ruleId": "LADDER",
            "rungId": "script",
            "result": "stop",
            "because": "first rung that fits wins; later rungs are not evaluated for the decision"
          },
          {"ruleId": "RK", "result": "info", "because": "risk tier B (costOfError=medium, reversibility=reversible)"}
        ],
        "engine": {
          "rulesPackVersion": "0.3.0-draft",
          "catalogVersion": "2026.10.25-seed",
          "policyVersion": 12,
          "inputsHash": "e888490fce529caaa9a6f8e81e7df364e76dc140842d9f0115a93697726b7be6",
          "computedAt": "2026-10-25T09:00:00Z"
        }
      },
      "createdBy": "coach",
      "confirmationState": "confirmed",
      "confirmedBy": "usr_ap_lead",
      "confirmedAt": "2026-10-25T08:50:00Z",
      "provenance": {
        "source": "user_turn",
        "turnId": "t13",
        "quote": "we check it against the purchase order list",
        "at": "2026-10-25T08:35:00Z"
      },
      "environment": {
        "systems": [
          {
            "name": "Invoice rows and purchase order list",
            "kind": "spreadsheet_or_file",
            "role": "both",
            "accessEvidence": "verified"
          }
        ],
        "builderSkill": "intermediate"
      },
      "createdAt": "2026-10-25T09:00:00Z",
      "updatedAt": "2026-10-25T09:00:00Z",
      "override": {
        "by": "usr_ap_lead",
        "reason": "Our finance analyst maintains Python scripts and nobody on the team knows PowerShell",
        "at": "2026-10-25T09:20:00Z",
        "decisionId": "dec_01M5S4KHM0Z5ZX2J92D4A1Y5BY",
        "chosenRungId": "script",
        "chosenToolId": "script.python",
        "status": "active"
      }
    },
    {
      "id": "stp_01M5S4KHM025ZFY9KQHPQEMMGT",
      "order": 4,
      "name": "Approve invoices over 5,000",
      "description": "A manager approves or rejects each matched invoice with a total over 5,000.",
      "actor": "Finance manager",
      "inputs": [{"name": "Matched row", "format": "Excel sheet"}],
      "outputs": [{"name": "Approval decision", "format": "email"}],
      "decisionPoints": [{"question": "Is the invoice total over 5,000?", "outcomes": ["approve", "reject"], "ruleStatus": "explicit"}],
      "exceptionRefs": [],
      "diagnostic": {
        "inputStructure": "structured",
        "outputDeterminism": "yes",
        "costOfError": "high",
        "reversibility": "partly",
        "interfaceAvailability": "file_exchange",
        "attendance": "either",
        "credentialsRequired": "no",
        "dataSensitivity": "confidential",
        "languageUnderstanding": "none",
        "judgmentRequired": "no",
        "frequency": "daily",
        "operations": ["approve_decision"],
        "humanAuthority": "approval_required",
        "provenance": {"humanAuthority": {"origin": "user_stated"}, "costOfError": {"origin": "user_stated"}}
      },
      "recommendation": {
        "rungId": "human_checkpoint",
        "toolId": "human.approval_flow",
        "rationale": [
          "The output follows rules (determinism=yes, no language understanding needed), so the code family applies and models are not considered.",
          "A person must decide or act here; automation can prepare the case but not own the decision.",
          "Earlier rungs were rejected: eliminate (E-1); builtin_feature (T-COVER); api_connector (RP-ACC-2); script (T-COVER); ui_automation (RP-ACC-4); parser_ocr_ml (RP-PARSE); llm_node (RL-NEED).",
          "human.approval_flow is the first tool at rung human_checkpoint that passes every hard rule for this step in this environment."
        ],
        "alternatives": [],
        "status": "ok",
        "outcome": "recommended",
        "riskTier": "D",
        "cardRequired": false,
        "rejectedRungs": [
          {"rungId": "eliminate", "rule": "E-1", "whyNot": "necessity=required, requiredByControl=False", "stage": "rung"},
          {
            "rungId": "builtin_feature",
            "rule": "T-COVER",
            "whyNot": "no single tool or same-rung bundle covers ['approve_decision']",
            "stage": "tool",
            "toolId": "builtin.outlook_rules",
            "failedRules": ["T-COVER"]
          },
          {
            "rungId": "api_connector",
            "rule": "RP-ACC-2",
            "whyNot": "needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']",
            "stage": "rung"
          },
          {
            "rungId": "script",
            "rule": "T-COVER",
            "whyNot": "no single tool or same-rung bundle covers ['approve_decision']",
            "stage": "tool",
            "toolId": "script.powershell",
            "failedRules": ["T-COVER"]
          },
          {
            "rungId": "ui_automation",
            "rule": "RP-ACC-4",
            "whyNot": "needs one of ['ui']; step access is ['builtin', 'file_or_db', 'scriptable']",
            "stage": "rung"
          },
          {
            "rungId": "parser_ocr_ml",
            "rule": "RP-PARSE",
            "whyNot": "extract path=False, classify path=False (needs labelSetStable and >=100 examples)",
            "stage": "rung"
          },
          {
            "rungId": "llm_node",
            "rule": "RL-NEED",
            "whyNot": "languageUnderstanding=none, language ops=False, unbounded extraction=False",
            "stage": "rung"
          }
        ],
        "warnings": [],
        "policyNotes": [],
        "companions": [],
        "ruleTrace": [
          {
            "ruleId": "SENS",
            "result": "info",
            "because": "effective class confidential, set by the Blueprint (Blueprint confidential, step dataSensitivity confidential; the stricter wins); toolDataFlowCeiling tenant, llmContentMode redacted"
          },
          {
            "ruleId": "RH-AUTH",
            "rungId": "human_checkpoint",
            "result": "pass",
            "because": "humanAuthority=approval_required, human ops=True, pure judgment=False, open-ended path a person can take=False (open-ended=False, volumePerRun=None, limit 50)"
          },
          {
            "ruleId": "T-ALL",
            "rungId": "human_checkpoint",
            "toolId": "human.approval_flow",
            "result": "pass",
            "because": "no hard tool predicate failed (T-PERM, T-INST, T-PLAT, T-SCRIPT, T-EXEC, T-CRED, T-FLOW, T-SIZE, T-VAR, T-TRAIN, T-SYS, T-ACCESS, T-LOC, T-HOST)"
          },
          {
            "ruleId": "T-COVER",
            "rungId": "human_checkpoint",
            "toolId": "human.approval_flow",
            "result": "pass",
            "because": "covers ['approve_decision']"
          },
          {
            "ruleId": "TB",
            "rungId": "human_checkpoint",
            "toolId": "human.approval_flow",
            "result": "selected",
            "because": "tie-breakers in order: TB-0 org preferred, TB-1 owned, TB-2 fewest warnings, TB-3 no host needed, TB-4 lowest skill, TB-5 lowest data flow, TB-6 fewest capabilities, TB-7 catalog order"
          },
          {
            "ruleId": "LADDER",
            "rungId": "human_checkpoint",
            "result": "stop",
            "because": "first rung that fits wins; later rungs are not evaluated for the decision"
          },
          {"ruleId": "RK", "result": "info", "because": "risk tier D (costOfError=high, reversibility=partly)"}
        ],
        "engine": {
          "rulesPackVersion": "0.3.0-draft",
          "catalogVersion": "2026.10.25-seed",
          "policyVersion": 12,
          "inputsHash": "ea05959e947293423cf083e0fa57d25ab610ccb02e623477ddf0fb9611045755",
          "computedAt": "2026-10-25T09:00:00Z"
        }
      },
      "createdBy": "coach",
      "confirmationState": "confirmed",
      "confirmedBy": "usr_ap_lead",
      "confirmedAt": "2026-10-25T08:50:00Z",
      "provenance": {
        "source": "user_turn",
        "turnId": "t14",
        "quote": "anything over five thousand goes to the finance manager",
        "at": "2026-10-25T08:35:00Z"
      },
      "environment": {
        "systems": [
          {
            "name": "Approval inbox",
            "kind": "email_or_calendar",
            "role": "both",
            "accessEvidence": "verified",
            "authModel": "sso"
          }
        ],
        "builderSkill": "intermediate"
      },
      "createdAt": "2026-10-25T09:00:00Z",
      "updatedAt": "2026-10-25T09:00:00Z"
    },
    {
      "id": "stp_01M5S4KHM0GHDDPN4WQYEZ4QJV",
      "order": 5,
      "name": "Draft the rejection note to the supplier",
      "description": "When an invoice is rejected, a short note explains why in plain words; the clerk reads and sends it.",
      "actor": "AP clerk",
      "inputs": [{"name": "Rejected row", "format": "Excel sheet"}],
      "outputs": [{"name": "Draft note", "format": "email body"}],
      "decisionPoints": [],
      "exceptionRefs": [],
      "diagnostic": {
        "inputStructure": "free_text",
        "outputDeterminism": "no",
        "costOfError": "low",
        "reversibility": "irreversible",
        "interfaceAvailability": "file_exchange",
        "attendance": "attended",
        "credentialsRequired": "no",
        "dataSensitivity": "confidential",
        "languageUnderstanding": "core",
        "judgmentRequired": "sometimes",
        "frequency": "daily",
        "operations": ["generate_text"],
        "attractorCheck": {
          "ruleAttempt": "pick a canned rejection text by reason code",
          "whereItBreaks": "the supplier needs the specific mismatch explained in plain words"
        }
      },
      "recommendation": {
        "rungId": "llm_node",
        "toolId": "llm.cloud_model",
        "rationale": [
          "The step needs wording or layout to be understood (language=core), which rules cannot supply, so rungs before the model rungs were rejected on that basis.",
          "Earlier rungs were rejected: eliminate (E-1); builtin_feature (RP-CODE); api_connector (RP-CODE); script (RP-CODE); ui_automation (RP-CODE); parser_ocr_ml (RP-PARSE).",
          "llm.cloud_model is the first tool at rung llm_node that passes every hard rule for this step in this environment.",
          "llm.cloud_model runs inside script.powershell."
        ],
        "alternatives": [],
        "status": "ok",
        "outcome": "recommended",
        "riskTier": "B",
        "cardRequired": true,
        "rejectedRungs": [
          {"rungId": "eliminate", "rule": "E-1", "whyNot": "necessity=required, requiredByControl=False", "stage": "rung"},
          {
            "rungId": "builtin_feature",
            "rule": "RP-CODE",
            "whyNot": "needsUnderstanding=True, outputDeterminism=no, judgmentRequired=sometimes",
            "stage": "rung"
          },
          {
            "rungId": "api_connector",
            "rule": "RP-CODE",
            "whyNot": "needsUnderstanding=True, outputDeterminism=no, judgmentRequired=sometimes",
            "stage": "rung"
          },
          {
            "rungId": "script",
            "rule": "RP-CODE",
            "whyNot": "needsUnderstanding=True, outputDeterminism=no, judgmentRequired=sometimes",
            "stage": "rung"
          },
          {
            "rungId": "ui_automation",
            "rule": "RP-CODE",
            "whyNot": "needsUnderstanding=True, outputDeterminism=no, judgmentRequired=sometimes",
            "stage": "rung"
          },
          {
            "rungId": "parser_ocr_ml",
            "rule": "RP-PARSE",
            "whyNot": "extract path=False, classify path=False (needs labelSetStable and >=100 examples)",
            "stage": "rung"
          }
        ],
        "warnings": [],
        "policyNotes": [
          "coach.llmNode.requireValidatorAndFallback: a validator and a fallback are required before export.",
          "Allowed connection types for confidential data: managed; content mode: redacted."
        ],
        "companions": [],
        "ruleTrace": [
          {
            "ruleId": "SENS",
            "result": "info",
            "because": "effective class confidential, set by the Blueprint (Blueprint confidential, step dataSensitivity confidential; the stricter wins); toolDataFlowCeiling tenant, llmContentMode redacted"
          },
          {
            "ruleId": "RL-NEED",
            "rungId": "llm_node",
            "result": "pass",
            "because": "languageUnderstanding=core, language ops=True, unbounded extraction=False"
          },
          {
            "ruleId": "RL-EVID",
            "rungId": "llm_node",
            "result": "pass",
            "because": "attractorCheck (rule attempt and where it breaks) is on record"
          },
          {
            "ruleId": "T-FLOW",
            "rungId": "llm_node",
            "toolId": "llm.org_endpoint",
            "result": "fail",
            "class": "environmental",
            "because": "no custom_openai_compat connection is configured or reachable here (class allows ['managed', 'custom_openai_compat', 'local'])"
          },
          {
            "ruleId": "T-FLOW",
            "rungId": "llm_node",
            "toolId": "llm.local_model",
            "result": "fail",
            "class": "environmental",
            "because": "no local connection is configured or reachable here (class allows ['managed', 'custom_openai_compat', 'local'])"
          },
          {
            "ruleId": "T-ALL",
            "rungId": "llm_node",
            "toolId": "llm.cloud_model",
            "result": "pass",
            "because": "no hard tool predicate failed (T-PERM, T-INST, T-PLAT, T-SCRIPT, T-EXEC, T-CRED, T-FLOW, T-SIZE, T-VAR, T-TRAIN, T-SYS, T-ACCESS, T-LOC, T-HOST)"
          },
          {
            "ruleId": "T-COVER",
            "rungId": "llm_node",
            "toolId": "llm.cloud_model",
            "result": "pass",
            "because": "covers ['generate_text']"
          },
          {
            "ruleId": "TB",
            "rungId": "llm_node",
            "toolId": "llm.cloud_model",
            "result": "selected",
            "because": "tie-breakers in order: TB-0 org preferred, TB-1 owned, TB-2 fewest warnings, TB-3 no host needed, TB-4 lowest skill, TB-5 lowest data flow, TB-6 fewest capabilities, TB-7 catalog order"
          },
          {
            "ruleId": "LADDER",
            "rungId": "llm_node",
            "result": "stop",
            "because": "first rung that fits wins; later rungs are not evaluated for the decision"
          },
          {"ruleId": "RK", "result": "info", "because": "risk tier B (costOfError=low, reversibility=irreversible)"}
        ],
        "engine": {
          "rulesPackVersion": "0.3.0-draft",
          "catalogVersion": "2026.10.25-seed",
          "policyVersion": 12,
          "inputsHash": "fafe2d743e0e1a817e41fa27dbdb314879dfc47142422b598fc1d411a49d8c90",
          "computedAt": "2026-10-25T09:00:00Z"
        },
        "hostToolId": "script.powershell"
      },
      "createdBy": "coach",
      "confirmationState": "confirmed",
      "confirmedBy": "usr_ap_lead",
      "confirmedAt": "2026-10-25T08:50:00Z",
      "provenance": {
        "source": "user_turn",
        "turnId": "t15",
        "quote": "we write back to the supplier when we reject one",
        "at": "2026-10-25T08:35:00Z"
      },
      "environment": {
        "systems": [
          {
            "name": "Shared invoices mailbox",
            "kind": "email_or_calendar",
            "role": "target",
            "accessEvidence": "verified",
            "authModel": "sso"
          }
        ],
        "builderSkill": "intermediate"
      },
      "createdAt": "2026-10-25T09:00:00Z",
      "updatedAt": "2026-10-25T09:00:00Z",
      "llmJustification": {
        "whyNotCode": "The note must explain a specific mismatch in plain words; a canned text by reason code was tried and suppliers could not act on it.",
        "citedDiagnosticFields": ["languageUnderstanding", "outputDeterminism"],
        "validator": {"kind": "human_review", "description": "The AP clerk reads every draft before it is sent."},
        "fallback": {
          "kind": "human_checkpoint",
          "description": "If the draft is wrong or the model is unavailable, the clerk writes the note by hand."
        },
        "costPerRun": {
          "value": null,
          "basis": "unavailable",
          "assumptions": ["No price table is loaded in this example; the engine states no price without one."]
        },
        "provenance": {
          "whyNotCode": {
            "origin": "user_stated",
            "evidence": {
              "source": "user_turn",
              "turnId": "t47",
              "quote": "suppliers could not act on the canned text",
              "at": "2026-10-25T09:29:40Z"
            }
          }
        },
        "cardState": "confirmed",
        "decisionId": "dec_01M5S4KHM00QD19QACQW84MQCJ"
      }
    }
  ],
  "exceptions": [
    {
      "id": "exc_01M5S4KHM0AX7QGD9RSGBGPAWE",
      "description": "Invoice has no purchase order number",
      "frequency": "common",
      "frequencyNote": "about one in five",
      "handling": "Send it back to the supplier and ask for the number.",
      "stepIds": ["stp_01M5S4KHM04X91912JZMP35F6K", "stp_01M5S4KHM0VX28M6RQSPWKFF9Y"],
      "createdBy": "coach",
      "confirmationState": "confirmed",
      "confirmedBy": "usr_ap_lead",
      "confirmedAt": "2026-10-25T08:55:00Z",
      "provenance": {
        "source": "user_turn",
        "turnId": "t21",
        "quote": "about one in five has no purchase order number",
        "at": "2026-10-25T08:52:00Z"
      },
      "createdAt": "2026-10-25T09:00:00Z",
      "updatedAt": "2026-10-25T09:00:00Z"
    },
    {
      "id": "exc_01M5S4KHM0BZRYZ5F7HSK9KC3H",
      "description": "The PDF is a phone photo of a paper invoice",
      "frequency": "occasional",
      "frequencyNote": "a few a month",
      "handling": "A clerk keys it by hand from the review queue.",
      "stepIds": ["stp_01M5S4KHM04X91912JZMP35F6K"],
      "createdBy": "user",
      "confirmationState": "confirmed",
      "confirmedBy": "usr_ap_lead",
      "confirmedAt": "2026-10-25T08:56:00Z",
      "provenance": {
        "source": "user_turn",
        "turnId": "t22",
        "quote": "sometimes it is a phone photo of a paper invoice",
        "at": "2026-10-25T08:53:00Z"
      },
      "createdAt": "2026-10-25T09:00:00Z",
      "updatedAt": "2026-10-25T09:00:00Z"
    }
  ],
  "environmentProfileRef": {"id": "finance-windows", "policyVersion": 12},
  "roi": {
    "mode": "classified",
    "scope": "blueprint",
    "runsPerYear": 260,
    "personsPerRun": 2,
    "manualHoursPerYear": 1040.0,
    "automatableShare": 0.78,
    "hoursSavedPerYear": 811.2,
    "buildHours": 80.6,
    "maintainHoursPerYear": 19.0,
    "netHoursPerYear": 792.2,
    "paybackYears": 0.1,
    "assumptions": [
      "periodsPerYear: {\"hour\": 2080, \"day\": 260, \"week\": 52, \"month\": 12, \"quarter\": 4, \"year\": 1, \"ad_hoc\": 1}",
      "ASSUMPTION: timePerRunMinutes is minutes per person per run",
      "ASSUMPTION: build and maintain hours are placeholder priors, to be calibrated from pilot data",
      "ASSUMPTION: steps weigh equally; Step.timePerRunMinutes is not used for weighting yet",
      "residualShare 0.10 applied to outputDeterminism=mostly steps (ASSUMPTION)"
    ],
    "caveats": [
      "Hours only: no hourly rate is configured for this organization.",
      "Constants are uncalibrated placeholders; the ROI gate is advisory."
    ],
    "gate": "advisory",
    "constants": {
      "periodsPerYear": {"hour": 2080, "day": 260, "week": 52, "month": 12, "quarter": 4, "year": 1, "ad_hoc": 1},
      "buildHoursByRung": {
        "eliminate": 0.5,
        "builtin_feature": 1,
        "api_connector": 6,
        "script": 10,
        "ui_automation": 16,
        "parser_ocr_ml": 24,
        "llm_node": 20,
        "llm_agent": 40,
        "human_checkpoint": 2
      },
      "maintainHoursPerYearByRung": {
        "eliminate": 0,
        "builtin_feature": 0.5,
        "api_connector": 2,
        "script": 3,
        "ui_automation": 8,
        "parser_ocr_ml": 6,
        "llm_node": 8,
        "llm_agent": 16,
        "human_checkpoint": 0
      },
      "testOverheadFactor": 0.3,
      "residualShare": 0.1,
      "triageMode": {"automatableShare": 0.5, "buildHours": 16, "maintainHoursPerYear": 4},
      "paybackMaxYears": 1.0,
      "marginalFactor": 2.0
    },
    "engine": {
      "rulesPackVersion": "0.3.0-draft",
      "catalogVersion": "2026.10.25-seed",
      "policyVersion": 12,
      "inputsHash": "542187e96b6cb9a642f72e3bd0457c9ede519c98db9b103cdada6f8908265e60",
      "computedAt": "2026-10-25T09:00:00Z"
    }
  },
  "decisions": [
    {
      "id": "dec_01M5S4KHM0Z5ZX2J92D4A1Y5BY",
      "kind": "override",
      "stepId": "stp_01M5S4KHM0VX28M6RQSPWKFF9Y",
      "at": "2026-10-25T09:20:00Z",
      "by": "usr_ap_lead",
      "chosenRungId": "script",
      "chosenToolId": "script.python",
      "reason": "Our finance analyst maintains Python scripts and nobody on the team knows PowerShell",
      "acknowledgedRuleIds": [],
      "engineRecommendation": {
        "rungId": "script",
        "toolId": "script.powershell",
        "rulesPackVersion": "0.3.0-draft",
        "traceHash": "63abc3a50777bc299711c1e78f27a7420ccba5c12beab2c73bf234f65f4d0d9b"
      },
      "overriddenRuleIds": ["TB"],
      "approval": {"required": false, "state": "not_required"},
      "status": "active",
      "evidence": {"source": "user_turn", "turnId": "t41", "quote": "nobody on the team knows PowerShell", "at": "2026-10-25T09:19:40Z"}
    },
    {
      "id": "dec_01M5S4KHM00QD19QACQW84MQCJ",
      "kind": "llm_justification",
      "stepId": "stp_01M5S4KHM0GHDDPN4WQYEZ4QJV",
      "at": "2026-10-25T09:30:00Z",
      "by": "usr_ap_lead",
      "source": "recommended",
      "whyNotCode": "The note must explain a specific mismatch in plain words; a canned text by reason code was tried and suppliers could not act on it.",
      "citedDiagnosticFields": ["languageUnderstanding", "outputDeterminism"],
      "validator": {"kind": "human_review", "description": "The AP clerk reads every draft before it is sent."},
      "fallback": {
        "kind": "human_checkpoint",
        "description": "If the draft is wrong or the model is unavailable, the clerk writes the note by hand."
      },
      "costPerRun": {
        "value": null,
        "basis": "unavailable",
        "assumptions": ["No price table is loaded in this example; the engine states no price without one."]
      },
      "provenance": {
        "whyNotCode": {
          "origin": "user_stated",
          "evidence": {
            "source": "user_turn",
            "turnId": "t47",
            "quote": "suppliers could not act on the canned text",
            "at": "2026-10-25T09:29:40Z"
          }
        }
      },
      "cardState": "confirmed",
      "confirmedBy": "usr_ap_lead",
      "confirmedAt": "2026-10-25T09:31:00Z",
      "approval": {"required": false, "state": "not_required"},
      "evidence": {
        "source": "user_turn",
        "turnId": "t47",
        "quote": "suppliers could not act on the canned text",
        "at": "2026-10-25T09:29:40Z"
      }
    }
  ],
  "tests": [
    {
      "id": "tst_01M5S4KHM020Q14XCWA61EBJ7J",
      "title": "Invoice with a missing purchase order number is sent back",
      "kind": "exception",
      "stepIds": ["stp_01M5S4KHM0VX28M6RQSPWKFF9Y"],
      "exceptionIds": ["exc_01M5S4KHM0AX7QGD9RSGBGPAWE"],
      "given": "An invoice PDF with no purchase order number",
      "when": "The matching step runs",
      "then": "The row is marked rejected with reason missing_po",
      "exampleData": "Supplier Brightwell, invoice 4471, total 1,280.00, purchase order blank",
      "status": "proposed",
      "createdBy": "coach",
      "confirmationState": "proposed",
      "provenance": {
        "source": "user_turn",
        "turnId": "t21",
        "quote": "about one in five has no purchase order number",
        "at": "2026-10-25T08:52:00Z"
      }
    },
    {
      "id": "tst_01M5S4KHM0E9MP2VJXM1NV1P3X",
      "title": "A 6,200 invoice waits for approval",
      "kind": "happy_path",
      "stepIds": ["stp_01M5S4KHM025ZFY9KQHPQEMMGT"],
      "exceptionIds": [],
      "given": "A matched invoice for 6,200",
      "when": "The approval step runs",
      "then": "No payment is released until the manager approves",
      "exampleData": "Supplier Harlow Tools, invoice 5530, total 6,200.00, purchase order 88213",
      "status": "confirmed",
      "createdBy": "coach",
      "confirmationState": "confirmed",
      "confirmedBy": "usr_ap_lead",
      "confirmedAt": "2026-10-25T09:32:00Z"
    }
  ],
  "deployPlan": {
    "backupOwner": "AP team lead",
    "failureSignals": [
      {
        "stepId": "stp_01M5S4KHM04X91912JZMP35F6K",
        "signal": "More than 5 invoices in one day land in the review queue",
        "notify": "AP team lead"
      }
    ],
    "manualFallback": "The AP clerks read and key the invoices by hand from the shared mailbox until the automation is back.",
    "changeTriggers": ["A new purchase order system", "A supplier changes its invoice layout"],
    "reviewAfterDays": 90,
    "createdBy": "coach",
    "confirmationState": "proposed"
  },
  "exports": [
    {
      "id": "exp_01M5S6KMD05T6G3RRR62V2SR1D",
      "kind": "review_packet",
      "fileFormat": "pdf",
      "scope": "blueprint",
      "blueprintVersion": 7,
      "contentHash": "e7d68afe19d0af0439b8491fb678936eea42009edbd89a7d8df6d38444f4d18a",
      "sensitivityAtExport": "confidential",
      "createdAt": "2026-10-25T09:35:00Z",
      "createdBy": "usr_ap_lead"
    }
  ],
  "auditLog": [
    {
      "id": "aud_01M5S3EXR0M8MZCV3K50EP45SN",
      "at": "2026-10-25T08:40:00Z",
      "actor": {"type": "coach"},
      "action": "step_added",
      "entity": {"type": "step", "id": "stp_01M5S4KHM0CEHRD78WBHCGPXDT"},
      "blueprintVersion": 2,
      "summary": "Five steps proposed from the user's account",
      "details": {
        "callId": "call_0007",
        "connectionId": "managed",
        "modelKey": "example/model-a",
        "tool": "add_steps",
        "entityIds": [
          "stp_01M5S4KHM0CEHRD78WBHCGPXDT",
          "stp_01M5S4KHM04X91912JZMP35F6K",
          "stp_01M5S4KHM0VX28M6RQSPWKFF9Y",
          "stp_01M5S4KHM025ZFY9KQHPQEMMGT",
          "stp_01M5S4KHM0GHDDPN4WQYEZ4QJV"
        ]
      }
    },
    {
      "id": "aud_01M5S4WPK07R2NDFGEMW2HAPCZ",
      "at": "2026-10-25T09:05:00Z",
      "actor": {"type": "engine"},
      "action": "recommendation_computed",
      "entity": {"type": "blueprint"},
      "blueprintVersion": 5,
      "summary": "Recommendations computed for five confirmed steps"
    },
    {
      "id": "aud_01M5S5R5G0Z1VKN7DXDMEDQA78",
      "at": "2026-10-25T09:20:00Z",
      "actor": {"type": "user", "id": "usr_ap_lead"},
      "action": "override_recorded",
      "entity": {"type": "decision", "id": "dec_01M5S4KHM0Z5ZX2J92D4A1Y5BY"},
      "blueprintVersion": 6,
      "summary": "Chose script.python over script.powershell for step 3"
    },
    {
      "id": "aud_01M5S6CA10BBVEMP6CKK8Q8E0Q",
      "at": "2026-10-25T09:31:00Z",
      "actor": {"type": "user", "id": "usr_ap_lead"},
      "action": "llm_justification_confirmed",
      "entity": {"type": "decision", "id": "dec_01M5S4KHM00QD19QACQW84MQCJ"},
      "blueprintVersion": 7,
      "summary": "Confirmed the justification card for step 5"
    }
  ],
  "engine": {
    "rulesPackVersion": "0.3.0-draft",
    "catalogVersion": "2026.10.25-seed",
    "policyVersion": 12,
    "computedAt": "2026-10-25T09:00:00Z",
    "inputsHash": "b18be138ea31f6f76789575e0f6ee65446ac9fde54dba7b248986ed0530bcd71",
    "context": {"plan": "team", "billableSeats": 3}
  },
  "sync": {"deviceId": "dev_laptop_01", "baseRev": 6, "lastSyncedRev": 6, "lastSyncedAt": "2026-10-25T09:10:00Z", "state": "dirty"},
  "createdAt": "2026-10-25T08:30:00Z",
  "updatedAt": "2026-10-25T09:31:00Z"
}
```
