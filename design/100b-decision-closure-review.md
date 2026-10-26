# 100b. Decision-closure review (second pass on 99b)

Reviewer: independent subagent, fresh context. I did not write or patch any of these files. Date: 2026-10-25. No existing file was edited; this is the only file written.

Citation style: `file N` means section or heading N of that file; `file line N` means the line in the file as it stands today (lines shift if the file is edited). `DC-nn` are the 99b findings. `N-nn` are the new or residual issues found in this pass (section 7). "99b s9 n" is item n of the 41-item owner-decision list in 99b section 9 (the register in 99b section 2 uses a different `OD-nn` numbering; this report uses the section 9 numbers only).

## 0. Scope, method, limits

Read in full: `00-shared-contract.md` (contract v2), `99b-decision-consistency-review.md`, `tiers.md`, `model-certification.md`. Read by section or by targeted search: `architecture.md` (0.1, 0.2, 1.2 to 1.10, 2 to 7), `settings-catalog.md` (1 to 8, parts of 9 to 11), `coach-spec.md` (1, 3 to 4, 6 to 7, 9 to 12, App B), `rules-engine.md` (0 to 2, 11, 13, 17 to 19, TR-3, TR-4, G0), `pattern-library.md` (header, index, 4, 6). Machine-checked with short scripts: `coach-tools.json`, `blueprint.schema.json`, `policy.schema.json`, `connection.schema.json`, `tool-catalog.seed.json`. Not re-read: `research/*.md` and `99a-data-contract-review.md` (a separate agent holds the schema cross-check).

Status rule. Closed = the 99b direction is implemented in every document that carries the claim, and I found no residue worth a ticket. Partially closed = the decision is recorded but at least one document still disagrees, or the fix needs a field, rule or screen nobody specified. Open = nothing done. Regressed = the patch made it worse than the 99b state; none found (the patch round did create new seams, listed in section 7, but none worsens a DC item it claims to close).

No external source was fetched. Statements about OpenRouter, Stripe, Microsoft, and similar facts are only checked against what the documents cite.

## 1. Summary

Counts over the 58 findings: **Closed 40, Partially closed 15, Open 3, Regressed 0.**

Closed items are mostly the ones that were pure decisions (signing algorithm, enrollment, roles, retention, ladder order, certification fingerprint, adversarial traffic, scope cuts, accessibility). The partial items cluster in four places: the free offer and licensing (DC-43, DC-44, with DC-20 and DC-01 behind them), the `restricted` class (DC-04, DC-22, DC-55), the "model proposes, user confirms" mechanism (DC-11, DC-40, DC-55), and stale cross-references left in files that were not the target of the fix (DC-25, DC-29, DC-50).

Five worst remaining contradictions:
1. **Licensing and monetization (N-01, N-09; DC-43, DC-44).** The free offer is worded as a no-model wizard, but the sign-in rules make local and BYOK chat coaching free forever. A paying Individual gets only sync and backup (managed is dark). Subscription billing is scheduled inside the phase built dark behind the managed flag. Section 5.
2. **`restricted` deadlock (N-02; DC-04, DC-22).** The default `restricted` class has export "no" and approval before handoff "yes". That blocks the review packet the architecture relies on, blocks the file-based AutoMate fallback, contradicts "export always works", and makes handoff impossible on Individual (self-attestation is not approval).
3. **Thesis holes (N-03; DC-03, DC-11, DC-55).** The engine gates on step-level confirmation and ignores provenance. Imported or shared Blueprint JSON keeps `confirmed` state and values. Entity-level clicks confirm model-written text. The model's `sensitivity` raise applies at once. Chip volume invites click-through. Section 4.
4. **Server-engine timing and approval metadata (N-05, N-06; DC-25).** `rules-engine.md` 17.2 and `tiers.md` line 163 still say the server recomputes after every merge or re-evaluates every synced Blueprint. Architecture X3 says transitions only. X10 (approval metadata when sync is locked off) is not in the catalog.
5. **Stale claims about managed and the gateway (N-04, N-07, N-11; DC-01, DC-05, DC-29).** `tiers.md` line 195 still tells customers to use `managed` for a hard guarantee with no flag caveat. `model-certification.md` line 304 says the gateway "cannot see prompts". The certification registry has three delivery descriptions.

Licensing recommendation: open-core (Model A, section 5.5) with four amendments. The free coach (wizard, local, BYOK, export) stays free and unmetered. Paid Individual means sync, backup, devices and (after G1) managed. The first-buyer trial becomes a Team org pilot, and subscription billing is decoupled from the managed flag.

Owner decisions that genuinely remain: 10 (section 9). The headline three are the licensing set, `restricted` handoff and export semantics, and the import and entity-confirm policy.

## 2. DC-01 to DC-58 closure table

Original severity in brackets. Evidence cites the document that now carries the fix.

| ID | Status | Evidence of the fix | What is left |
|---|---|---|---|
| DC-01 [Critical] | Partially | Contract d4; architecture D13, 4.0, gate G1 (6.2), line 1068; catalog `tenant.managed.flag`, invariant 11; tiers 1 row "Connection types", 1.2 | `tiers.md` line 195 (3.3 last paragraph) still says "for a hard guarantee use `managed`" with no flag caveat. The money path including subscription webhooks is row 3.2 inside "Phase 3: built dark" (N-01). The fallback 3.5 is built only if permission is refused. |
| DC-02 [Critical] | Closed | Contract d8; catalog 4 (`sync` on, opt_in, forbidden), `sync.blueprints.enabled`; architecture S8 (line 581), 3.4b (lines 687 to 695) | Owner ruled it a capability. The export side effect of the `restricted` default is N-02. |
| DC-03 [Critical] | Closed | Coach-spec 1 rule 6, 1.1, 6.2 (proposal queue, chips, no bulk accept), 7.4 residual-risk wording; coach-tools `noBulkAccept` | New holes beyond the DC are in section 4 (H-1 to H-9). |
| DC-04 [High] | Partially | Catalog 4 `approvalMetadataSync` (default yes for every class); architecture 3.4b item 4 (body-less envelope, record issued against the metadata `rev`) | Individual cannot satisfy `requireApprovalBeforeHandoff` (tiers line 115: self-attestation is not approval). The review-packet route (architecture 3.4b item 5) is blocked by `restricted` `exportAllowed` = no. X10 is not in the catalog (N-02, N-06). |
| DC-05 [High] | Closed | Contract d5; catalog 7 invariant 2; architecture 2.3 rule 5, A2; tiers 3.3 line 195 | Residue: `model-certification.md` line 304 "the gateway logs metadata only, so it cannot see prompts" (N-11). |
| DC-06 [High] | Partially | Six screens agreed in contract 7, tiers 7 and 8, architecture D12, 2.4 (sized M) | Tiers 7 Policy screen lists a bespoke environment-profile form, rollout list, key info and offline-bundle download, while architecture calls the screen "schema-generated". The account page and offline activation page (architecture 1.6 lines 416 to 417, row 2.1) are not counted in the six. Spend is hidden while the flag is off, so five are visible at launch (N-10). |
| DC-07 [High] | Closed | ES256 unless Ed25519 verified: contract d7, tiers 4.1 line 206, catalog lines 49 and 280, architecture D6, T5, V18. No `EdDSA` string in any of the four JSON files | None. |
| DC-08 [High] | Closed | Contract d7; tiers 1 and 4.3; catalog 6 (`OrgId`, `RequireOrgPolicy`, `PolicyFile`); architecture 2.2, 5.1 | The registry key path is unspecified (catalog line 240: "fixed once the product name is final") and ADMX or Intune packaging is after launch, so IT has values but no path (N-13). |
| DC-09 [High] | Closed | Contract d8 (mode A only, P2, security review); architecture D4, line 531; catalog `tenant.vault.enabled` | None. |
| DC-10 [High] | Closed | Architecture L3 (line 1036) and T1 (line 1001) now match coach-spec 3 and `x-labelExposure`; contract 6 | None. |
| DC-11 [High] | Partially | `operations` now in coach-tools (12 occurrences); coach-tools line 3337 "plain-language yes/no chip written by the host"; coach-spec 1.1 | The host glossary (plain words for the 36 tags and every enum) is referenced in coach-spec 6.2 and coach-tools but nobody owns or specifies its text. Omission of a tag is not covered (H-4). Chip volume is App B open question 2. |
| DC-12 [High] | Closed | Rules-engine TR-3 lines 635 to 639 and 681 to 687 (advisory, constants echoed in the trace), C12; contract 5 | Constants stay placeholders by design (V-21). |
| DC-13 [High] | Closed | Contract d9; catalog `governance.adminContentAccess`, invariant 10; tiers 2 lines 100 and 116; architecture 3.4 | Break-glass details open (tiers Q2: 4-hour time box, owner veto, second admin at Enterprise). |
| DC-14 [High] | Closed | Model-certification 3.5 rules 1 to 5 and 2.1 P6; architecture L10 | None. Consequence to note: on `managed` and `byok_openrouter` an unregistered model is lite-only (model-cert Q8), so full coaching on OpenRouter depends on the registry having content. |
| DC-15 [Medium] | Closed | Tiers lines 34, 314, 334; catalog line 110; architecture line 387 | None. |
| DC-16 | Closed | Tiers line 35 (approval records at Team); catalog lines 145 to 146 | None. |
| DC-17 | Closed | Tiers line 24; catalog 4 intro | None. |
| DC-18 | Closed | Tiers line 20; architecture line 380; contract d7 | None. |
| DC-19 | Closed | Catalog lines 147 to 148 ("P2 (hidden, inert)"), invariant 12; architecture X9 | Tiers lines 23 and 29 still advertise up to 20 or 200 rules and multi-reviewer while their editors and features are P2; disclosed inline. |
| DC-20 | Partially | Contract d3; tiers line 19; architecture 4.5 (lines 918 to 925, prepaid wallet) | Fee rate, minimum top-up, wallet expiry, refund and tax are not recorded (99b s9 n3 has no contract line); architecture Q1 line 1208 still asks. |
| DC-21 | Closed | Contract d9; tiers line 113; catalog invariant 9; architecture S4 and line 632; coach-tools `x-roleMatrix` includes `coe_reviewer` on write and AutoMate tools | Team of one (tiers Q6) open. |
| DC-22 | Partially | Tiers line 115 (advisory, self-attestation recorded); contract 7 | `rules-engine.md` TR-4 and the example Blueprint are silent on Individual. The self-attestation needs an `AuditEntry` kind (tiers line 115 and catalog line 272 both ASSUMPTION). `approved` is unreachable on Individual yet `restricted` requires it (N-02). |
| DC-23 | Closed | Catalog line 155 and invariant 6; architecture line 543; model-cert line 304 (upload only if the user opts in) | `telemetry.*` still allows value `anonymous` under an admin lock (N-08). |
| DC-24 | Closed | Catalog line 109 ("copies persist in backups for up to the 35-day backup window") | None. |
| DC-25 | Partially | Architecture X3 (server engine at status transitions only, never merges), 3.4 | `rules-engine.md` line 2674 (17.2) still says "After a sync merge the server recomputes the derived fields". `tiers.md` line 163 still says the server "re-evaluates any synced Blueprint" (N-05). |
| DC-26 | Closed | Architecture X5, row 1.5b (minimal signed registry stub; all models Experimental until the harness ships) | The stub must be built; Experimental means no approval-class tools in Phase 1 (panel buttons only), which is consistent. |
| DC-27 | Closed | (a) Architecture row 1.4 and X6 (trusted approval UI in Phase 1). (b) `blueprint.schema.json` `override.status` enum includes `pending_approval`; coach-spec line 145 and line 877 | None. |
| DC-28 | Closed | Model-cert lines 7, 22 (fingerprint with server kind, version, quantization), cap at `works`; contract 6 and 5 CapabilityReport | None. |
| DC-29 | Partially | Architecture X2 proposes one signed registry in the content feed with the content key and says "Coach owner to confirm the name" | `model-certification.md` line 282 still says the registry is "delivered and cached like the Policy bundle". `tiers.md` line 144 still says "gateway holds the certification table" (N-07). |
| DC-30 | Closed | Contract 3; rules-engine C1, RA-OPEN lines 395 and 400; schema `rungId` enum | None. |
| DC-31 | Closed | Contract 5 (all extensions listed); `connection.schema.json`; blueprint schema `asBuilt`, `kind`, provenance | None. |
| DC-32 | Closed | Coach-spec line 730 ("Rescue produces findings, not a verdict"); schema `asBuilt`, `kind = rescue` | The F1 "engine finding" compares against a user-described `asBuilt.rungId` (H-9). |
| DC-33 | Closed | Contract 5 last line; rules-engine C12 and 13 ("DEFERRED to v1.x"); architecture line 1152 | None. |
| DC-34 | Partially | Contract 5 DeployPlan: "ROI tracking is manual entry at `reviewAfterDays`" | No schema field records the actual figure (searched `blueprint.schema.json`: no actual, realized or review-outcome property in `deployPlan` or `roi`), no tool, no question in coach-spec. |
| DC-35 | Closed | Catalog line 77 and invariant 2; architecture line 162; contract d5 | None. |
| DC-36 | Open | Architecture 7.2 V1 to V9 (lines 1227 to 1235) unchanged | Refresh the register against the research. Low impact: they remain correctly labelled as unverified. |
| DC-37 | Closed | Contract d3 (four servers, Foundry preview, native Anthropic v1.1); architecture line 448; catalog | LM Studio licence is a counsel item (V-14). |
| DC-38 | Closed | Catalog lines 74, 75, 207; contract 6 | None. |
| DC-39 | Closed | Coach-spec 6.2 (lite extraction enters the queue "and carries no `toolId`"); catalog invariant 3 | The local research L1 sketch with `suggest_tool` was not edited (research is out of scope). |
| DC-40 | Partially | Tiers line 30 ("Justification card, self-attested") | No requirement in coach-spec, rules-engine, catalog or the exporter to label self-attested overrides in exports or the audit view. |
| DC-41 | Closed | Model-cert lines 152 and 244 ("No LLM judge output enters the run score"); contract 6 | Who funds the run is an ASSUMPTION (3.5 rule 2). |
| DC-42 | Open | `tool-catalog.seed.json`: 20 of 29 entries carry `lastVerified` and no `sources` (`eliminate.remove_step`, `builtin.excel_power_query`, `builtin.outlook_rules`, `api.power_automate_cloud_flow`, `api.rest_http_request`, `api.third_party_ipaas`, `script.python`, `script.sql`, `ui.automate`, `ui.playwright_browser`, `parser.regex_template`, `ocr.tesseract_local`, `ml.trained_text_classifier`, `llm.cloud_model`, `llm.org_endpoint`, `llm.local_model`, `agent.bounded_llm_agent`, `human.approval_flow`, `human.review_queue`, `human.manual_task`) | Drop `lastVerified` or add sources. Rules-engine 18.2 says ten Microsoft pages are "cited in the entries' sources", but only 9 entries have `sources`. 27 of 29 entries carry VERIFY or ASSUMPTION (matches 18.2). |
| DC-43 | Partially | Architecture 1.6 (token design, device binding, offline activation, device limit), tiers 1.2, catalog lines 233 to 236 | The monetization and gating gaps in section 5. |
| DC-44 | Partially | Contract d6; tiers line 12; catalog line 235 | The free tier is described two ways; Team trial (tiers Q3) and "free forever" (tiers Q5) are still open; post-trial data state undefined (section 5). |
| DC-45 | Closed | Architecture 1.9 (lines 487 to 491), 4.7; catalog `prefs.accessibility.*`, `prefs.locale.*`; tiers line 38; contract d11 | None. |
| DC-46 | Closed | Catalog line 120 `coach.aiMode` and `coach.aiFlows.allowedByMode`; coach-spec 3 | None. |
| DC-47 | Closed | Contract d8; architecture 6.3 line 1174, lines 723 to 730; tiers line 37 | None. |
| DC-48 | Closed | Model-cert line 26 (zero S0 for approval-class tools); contract 6 | None. |
| DC-49 | Closed | Contract 7 (Intake, Templates P2); blueprint `kind` is `new` or `rescue` | None. |
| DC-50 | Partially | Rescue and second opinion: tiers line 33, catalog `coach.aiFlows.allowedByMode`, contract 7 | The hybrid pattern library (`pattern-library.md`, eleven patterns) is referenced only by `rules-engine.md` line 769 and the contract. Zero mentions in coach-spec, coach-tools, tiers, catalog, architecture. No flow shows a pattern to a user and no setting can hide it. |
| DC-51 | Closed | Architecture line 462 (`compatibleAutomate{min,max}`), row 4.3 | None. |
| DC-52 | Closed | Architecture X7; catalog lines 16 and 248 | None. |
| DC-53 | Open | `tiers.md` line 262: after expiry `no_llm` blocks "any connection type", including `local` | The trade (local blocked although bypass 12 says local risk is quality) is not acknowledged in admin copy. |
| DC-54 | Closed | Contract 5 CapabilityReport; model-cert 2.1 and 2.3 | None. |
| DC-55 | Partially | Architecture 3.4b item 3: a Blueprint that becomes `restricted` after sync stops pushing and shows "Keep backup" or "Remove backup" | Coach-spec line 29 still says the model's raise is "applied at once"; there is no notice or undo in the Coach, and the contract thesis sentence has no carve-out for it (H-1). |
| DC-56 | Closed | Coach-spec lines 664 to 665 (host rejects output naming a rung or tool) | None. |
| DC-57 | Partially | Catalog line 1177 admits a hand-written validator and flags VERIFY | Not re-run with `jsonschema` or Ajv. |
| DC-58 | Closed | Contract d2 (AutoMate team owns the adapter API, file fallback); architecture 0.1(b), row 4.1, 1.10 | The AutoMate answer is still a precondition for the last build row; risk is concentrated at the end by design. |

Totals: Closed 40 (02, 03, 05, 07, 08, 09, 10, 12, 13, 14, 15, 16, 17, 18, 19, 21, 23, 24, 26, 27, 28, 30, 31, 32, 33, 35, 37, 38, 39, 41, 45, 46, 47, 48, 49, 51, 52, 54, 56, 58). Partially 15 (01, 04, 06, 11, 20, 22, 25, 29, 34, 40, 43, 44, 50, 55, 57). Open 3 (36, 42, 53). Regressed 0. Sum 58.

## 3. The 12 locked decisions and the 41 owner-decision resolutions

### 3.1 Contract section 2, decision by decision, per document

Cell = honoured (ok) or the drift with its id. `Cat` = settings-catalog and policy schema, `Arch` = architecture, `Coach` = coach-spec and coach-tools, `Cert` = model-certification, `Eng` = rules-engine and pattern-library.

| # | Decision | Tiers | Cat | Arch | Coach | Cert | Eng |
|---|---|---|---|---|---|---|---|
| 1 | Standalone core library | ok | ok | ok (D2 CI test) | ok | ok | ok (same library client and server) |
| 2 | AutoMate draft-only, token, attended, file fallback | ok (row 35) | ok (invariant 4); file fallback blocked for `restricted` (N-02) | ok (L4, 1.10) | ok | ok (S1) | ok |
| 3 | Five connections, local free, no bundling | ok | ok | ok (line 448) | ok | ok (P6 opt-in on `byok_provider`) | ok |
| 4 | Managed only after written permission | drift: line 195 (N-04) | ok | ok; billing placement (N-01) | n/a | ok (managed after G1) | n/a |
| 5 | "Does not store"; deny routing | ok | ok | ok | ok | drift: line 304 (N-11) | n/a |
| 6 | Tiers; free offer | ambiguous vs d10 (N-09) | ok (line 235) | ambiguous (line 379 vs 1.6) | n/a | n/a | n/a |
| 7 | Three states, signed ES256, grace, enrollment, baseline, honest enforcement | ok; registry path (N-13) | ok; X10 missing (N-06) | ok | ok | drift: registry channel (N-07) | drift: 17.2 (N-05) |
| 8 | Backup is a capability; restricted opt-in; metadata sync | ok | ok; export "no" (N-02) | ok | ok | ok | n/a |
| 9 | Roles | ok | ok | ok | ok (`x-roleMatrix`) | n/a | n/a |
| 10 | Telemetry off, 365 days, sign-in rules, token, 3 devices | ok | drift: `anonymous` value (N-08) | ok | n/a | ok | n/a |
| 11 | WCAG 2.2 AA, English UI | ok | ok | ok | ok (screen-reader mode) | ok (locale addendum) | ok (strings in UI language) |
| 12 | First buyer CoE lead; no competitor names | ok | n/a | ok | ok | n/a | n/a |

Decision 12 versus decision 6 is a tension, not a drift: the first buyer is a CoE lead (a Team or Enterprise purchase), while the free offer and trial are designed around an Individual (section 5).

### 3.2 The 41 owner decisions (99b section 9)

| n | Topic | Where recorded | Honoured | Gap |
|---|---|---|---|---|
| 1 | Managed go/no-go | Contract d4 | Yes | N-04 |
| 2 | Backup as capability | Contract d8 | Yes | N-02 |
| 3 | Managed pricing mechanics | Not in contract | Not decided | Fee rate, minimum top-up, expiry, refund, tax. Not needed to ship while the flag is off |
| 4 | Free tier or trial | Contract d6 | Yes, ambiguous | N-09 |
| 5 | Sign-in and offline activation | Contract d10 | Yes | Section 5 |
| 6 | Gateway wording, P2 scan | Contract d5 | Yes | N-11 |
| 7 | Admin read access | Contract d9 | Yes | Break-glass details |
| 8 | Org key vault | Contract d8 | Yes | None |
| 9 | Telemetry | Contract d10 | Yes | N-08 |
| 10 | Managed privacy routing | Contract d5 | Yes | None |
| 11 | Team audit retention 365 | Contract d10 | Yes | None |
| 12 | Backup window wording | Contract d8 | Yes | None |
| 13 | CMK timing | Contract d8 | Yes | None |
| 14 | Regions | Contract d8 | Yes | None |
| 15 | Signing algorithm | Contract d7 | Yes | None |
| 16 | Machine enrollment | Contract d7 | Yes | N-13 |
| 17 | Individual baseline | Contract d7 | Yes | None |
| 18 | Launch admin scope | Contract 7 | Yes | N-10 |
| 19 | Approvals by tier | Contract 7 | Yes | None |
| 20 | Sensitivity editing on Individual | Contract 7 | Yes | None |
| 21 | CoE Reviewer powers | Contract d9 | Yes | Team of one |
| 22 | Individual review path | Contract 7 | Yes, tiers only | Engine and schema silent (DC-22) |
| 23 | `restricted` approval before handoff | Contract d8 | Metadata only | Individual deadlock, export (N-02) |
| 24 | AI-off and mode keys | Contract 5 Policy | Yes | None |
| 25 | Confirm diagnostics and tags value by value | Contract 1 | Yes by design | Section 4 |
| 26 | ROI constants advisory | Contract 5 | Yes | None |
| 27 | Ladder order | Contract 3 | Yes | None |
| 28 | Contract v2 extensions | Contract 5 | Yes | None |
| 29 | Graduation deferred | Contract 5 | Yes | None |
| 30 | ROI tracking manual | Contract 5 | In contract only | DC-34 |
| 31 | Rescue and second opinion on all tiers | Contract 7 | Yes | Hybrid patterns unplaced (DC-50) |
| 32 | Preferred tools and engine questions | Contract 5 Policy | Yes (`preferredToolIds` in blueprint schema, policy schema, rules-engine, catalog) | None |
| 33 | Experimental tool exposure | Contract 6 | Yes | None |
| 34 | Fingerprint and cap | Contract 6 | Yes | None |
| 35 | Certification funding, adversarial location | Contract 6 | Yes | Funding owner is an ASSUMPTION |
| 36 | Judge advisory, zero S0 | Contract 6 | Yes | None |
| 37 | `restricted` model floor | Contract 6 | Yes | None |
| 38 | Local servers and adapters | Contract d3 | Yes | LM Studio licence |
| 39 | Accessibility and localization | Contract d11 | Yes | None |
| 40 | Cloud, devices, AutoMate ownership | Contract d2, d10 | Yes | AutoMate commitment still a gate |
| 41 | First buyer, competitor naming | Contract d12 | Yes | Tension with Individual-centric trial |

## 4. Thesis check

Claim under test (contract 1): "no LLM output, including an LLM judge, can change a verdict, rung, ROI figure, policy gate or approval; the engine consumes nothing the user has not confirmed value by value."

### 4.1 Path walk

| Stage | Mechanism now in the documents | Verdict |
|---|---|---|
| Chat turn | The host builds the prompt; document text is untrusted data (coach-spec 7, R4, R5: diagnostics, facts and overrides accept typed user turns only); the injection scanner is deterministic | Sound. The model's prose can still bias the user (coach-spec line 569 says so). |
| Model tool call | JSON-schema validation, verbatim-quote check against a typed turn, attractor check, role and policy check; values go to the proposal queue, outside the Blueprint | Sound for chip-class fields. Two fields are written at once: `title` (a label) and a raise of `sensitivity` (H-1). |
| Proposal queue and chips | One chip per value, host-glossary words, the user's quote beside the value, Accept, Change, Reject; no bulk accept and no accepting tool; same in lite mode and for wizard free text (coach-spec 6.2, line 18) | Sound in design. Practical risk: H-2, H-3, H-4, H-5. |
| Entity-level confirmation | Steps, exceptions, tests, deploy plan and the justification card are "proposed" until one click on an entity; "Confirm steps" and "Confirm design" buttons | Single click confirms model-written text (names, descriptions, actor, inputs, outputs, handling, test givens, card prose) (H-6, H-7). |
| Engine intake | Gate G0: a step with `confirmationState != confirmed` is ignored (rules-engine line 334). The engine reads values and never provenance (rules-engine C11, schema description of `provenance`) | The per-value guarantee is a property of the host write path, not something the engine can check (H-8). |
| Tool call to engine and trace | Verdict, rung, ROI and gates are engine output; accepted values used are listed in the trace; `engine.inputsHash` recorded | Sound. |
| Certification labels | Deterministic metrics only; the judge is advisory (model-cert line 244); labels gate tool exposure | Sound. |
| Export | Exporter builds content from the Blueprint and engine, runs the sensitivity check at write time (coach-tools line 4979); the model can only request an export | Sound for generation. Exported `blueprint_json` becomes an import vector (H-8). |
| Approval | Single-use token minted by a trusted click, bound to the diff hash; ApprovalRecord signed by the server on a reviewer's click; schema has no token field | Sound. Weak spot is the local-only reviewer attestation (architecture T18, accepted). |
| Lite and wizard | Form controls write `user_stated` at once; lite and free-text mapping enter the queue as chips | Sound. |

### 4.2 Holes found

| ID | Hole | Why it matters | Suggested fix |
|---|---|---|---|
| H-1 | The model may raise `sensitivity` and it is "applied at once" (coach-spec line 29, coach-tools line 1374). `sensitivity` drives class rules, connection eligibility, the tool data-flow ceiling and `llm_node` availability. It is the one engine-visible value a model writes with no chip. It is protective, but an injected raise to `restricted` stops sync and export (catalog 4). | Violates the thesis sentence as written; DC-55 notice exists only in architecture 3.4b. | Either carve it out in the contract ("model may tighten sensitivity; the app shows an undo notice") or make it a chip. Add the notice and undo to coach-spec 1.1. |
| H-2 | Chip volume. A step can raise 20 or more chips (nine diagnostic fields, up to twelve tags, systems); a 6-step process is 120 or more clicks (coach-spec App B Q2). | Rubber-stamping turns "confirmed value by value" into a ritual. | Let a host-rendered option control under the engine's own question (user_stated at once, no chip) be the main path; chips only for free-text extraction. Group by question, default unanswered tags to "does not apply" in a visible checklist. |
| H-3 | "Shortest-first ordering and keyboard accept" are left to UX (App B Q2). Held Enter or key repeat is a bulk accept in effect. | Defeats "no bulk accept". | Specify: no key repeat on Accept, no auto-advance on accept, one chip focused at a time, a minimum interval between accepts, and a read-back summary before `advance_stage`. Test in design partners as planned. |
| H-4 | Omission. Nothing shows the user a tag or fact the model did not propose; an absent `operations` tag changes the rung. The engine's planner picks the questions, but tag extraction from free text is the model's. | A steered or lazy model can drop a risk tag without any chip. | Show the 36-tag list (or the relevant subset) as a checklist the user can scan, produced by the host, not the model. |
| H-5 | The host glossary (plain words per enum value and per tag) is the whole defence of the chip, but it is not specified, owned, localized or tested for comprehension (coach-spec 6.2, coach-tools lines 65 and 3337). | A misleading gloss defeats the confirmation as surely as a misleading model. | Write it as a table in coach-spec or rules-engine, owned by the engine side, with a comprehension test before launch. |
| H-6 | Entity-level confirmation of model-written text: `step.name`, `description`, `actor`, `inputs`, `outputs`, `exception.handling`, test `given` and `exampleData`, deploy plan (coach-spec 1.1 rows). The contract sentence says value by value. The engine does not appear to read the free-text step fields (no rule in rules-engine reads `actor`, `inputs[]` or `outputs[]`; VERIFY), but `exception.handling` is copied into test `then` and into the AutoMate draft. | The statement "engine consumes nothing the user has not confirmed value by value" is accurate only for fields the engine reads; the contract should say so. | State in the contract which fields are value-confirmed (engine-read) and which are entity-confirmed (text that flows into drafts). |
| H-7 | The LLM justification card is model prose accepted by one click; the engine checks completeness only (CARD-1 to CARD-5). It unlocks an LLM-first override, which is a policy gate. On Individual there is no second person (DC-40). | A model-authored artifact satisfies a gate after a single entity click. | Make the user type or edit the card's "why not code" field (user_stated), or label every such override self-attested in exports and the audit view. |
| H-8 | Import, share, restore and hand-edited JSON. Gate G0 reads `confirmationState` on the step; the engine ignores provenance (C11). Architecture T8 resets owner, `override`, approvals and `auditLog` on import, and marks text tainted, but does not say it resets step and exception `confirmationState`, `confirmedBy`, diagnostic values or `provenance`. Coach-spec has no import flow at all (searched; only the architecture mentions imports). | A forged or third-party Blueprint arrives with every step "confirmed by" someone else and diagnostic values nobody at this keyboard accepted; the engine produces a recommendation from them. The same applies to a Blueprint a colleague shares for editing. | On import, restore-from-file and share-accept: set all steps, exceptions, tests and the deploy plan to `proposed`, mark recommendations stale, treat diagnostic values as chips awaiting acceptance, and keep `confirmedBy` only as history. Specify the import flow in coach-spec. Certification scenario G25 already tests stored injection. |
| H-9 | Rescue: `asBuilt.rungId` is a user-described value (entity-confirmed) that feeds finding F1, which coach-spec labels "engine finding". | A model-proposed, entity-confirmed value gains engine authority in the label. | Rename F1 to "comparison with your description" or require a chip on `asBuilt.rungId`. |
| H-10 | Wording of the thesis. The contract's first sentence is absolute ("cannot change a verdict, rung..."). The accurate guarantee is: no LLM output changes a result except through a value the user accepted, and the trace shows which accepted values the engine used (coach-spec line 569). A user who accepts a wrong tag does change the rung. | Overclaim in customer or auditor copy. | Replace with the accurate sentence, keep the strong one for LLM output that is not accepted (judge, prose, labels, ROI). |

Not holes (checked): the LLM judge (advisory, never enters the score, model-cert lines 152 and 244); labels and tool exposure (deterministic); ROI and TR-3 (no LLM, advisory); the second-opinion critic (adjudicated by the engine and marked disputed, coach-spec 12); the justification of the model's phrasing of engine results (host phrase check, coach-spec 664); approval tokens (host-minted, schema has no token field); the gateway (cannot verify the class but only receives a class the client declared, and the model cannot lower it).

Wizard and lite: both route through the same queue (coach-spec 6.2 last paragraph and section 9). The wizard's own form controls are the user's clicks. The only wizard risk is the lexical matcher or lite model mapping free text to an enum; that mapping is a chip. No separate hole beyond H-2 to H-5.

## 5. Licensing and monetization gap

### 5.1 What the documents say

- Contract d6: tiers Individual, Team, Enterprise; "Free offer: 14-day trial of the full Individual plan plus a permanent free no-model wizard with export; no free managed credits."
- Contract d10 (and tiers 1.2, architecture 1.6): "Sign-in not required for local, BYOK and no-model use; account required for sync, managed and orgs; signed offline entitlement token with 30-day grace. Up to 3 devices per user."
- Contract d3: managed is "platform subscription plus usage at cost + transaction fee"; `local` is free; BYOK has no usage fee.
- Architecture 1.6: the entitlement token (ES256 JWT, device-bound via `cnf`, claims `tier, features[], managed, trial{endsAt}, seats`, `exp` = `iat` + 30 days), offline activation file, 3 devices. The token carries `features[]` "so any capability can be gated" but the floor is "signed-out use always includes the wizard, local models and BYOK".
- Tiers line 67 and Q5, architecture Q2: what a paid Individual plan unlocks beyond sync and managed is a pricing decision, and whether chat coaching on BYOK or local is free forever is an open question.
- Architecture row 3.2 (top-ups, subscription webhooks, statements, invoicing) sits in "Phase 3: money (built dark behind the managed flag)", and depends on the gateway (row 3.1). Tiers line 353 says Individual and Team are "self-serve" at launch.

### 5.2 What a free, no-account user has today

Everything except cloud services and governance: the wizard, the engine and every rule, local Blueprints and export, the `local` connection, `byok_openrouter`, `byok_provider` and `custom_openai_compat` chat coaching (lite or full, per certification), rescue and second opinion on Individual (tiers line 33), AutoMate draft, diff, apply and attended test actions (no document gates them by account), the signed Individual baseline policy, accessibility and locale. The only thing missing is backup and restore of Blueprints off the device.

### 5.3 What each tier's paying customer gets beyond that

| Tier | Gets that a free no-account user does not | Gated by | Enforced where |
|---|---|---|---|
| Individual (paid) | Blueprint sync, backup, restore on up to 3 devices; fixed retention defaults; `managed` wallet and usage once G1 passes; nothing else is defined | Account plus entitlement token (`tier`, `managed`) | Sync service and gateway re-check on every request (hard, tiers line 161). The client enforces token `exp` offline (soft) |
| Team | The above plus org policy with locks, roles, signed approvals and the review queue, org audit log (365 days), break-glass, org connections and integrated OAuth, spend caps (matter only for managed), sensitivity matrix editing, `coach.aiMode` lock, machine enrollment, retention controls, up to 20 template rules (editor is P2) | Account, org membership, entitlement | Server for synced objects; client for the rest (soft, tiers 3.2) |
| Enterprise | Team plus audit up to 3650 days and API, multiple profiles, offline policy file and offline activation, negotiated DPA. Almost everything that normally defines Enterprise (SSO enforcement, SCIM, CMK, vault, SIEM, legal hold, region choice, rule editor, multi-reviewer) is P2 | As Team | As Team |

So at launch: Individual paid = sync only. Team = governance. Enterprise = Team with longer retention and offline distribution. No client-side feature is gated by `features[]`.

### 5.4 How a trial expires without an account, and what the documents agree on

A trial cannot expire without an account because it cannot start without one: it "starts at first sign-in" (tiers 1.2, architecture 1.6). A user who never signs in has no trial, no expiry and no loss. For a signed-in user, the token carries `trial.endsAt` while `exp` is 30 days out, so the client must honour `endsAt` separately; the sync service and gateway enforce it server-side. What happens to data synced during the trial is not stated: the "past-due" row (architecture line 764: pushes allowed 14 days, then read-only, export always allowed, no deletion for 60 days) covers a lapsed subscription, not a lapsed trial. A Team trial after expiry (policy `onExpiry`? org data?) is not defined. Trial abuse (T7 lists "trial farming") has no stated mitigation for a trial that needs no payment method.

Agreements: no account for wizard, local and BYOK; account for sync, managed and orgs; 30-day token; 3 devices; 14-day trial; no free managed credits; export never locked.

Disagreements and gaps:

| ID | Gap |
|---|---|
| L-1 | The free offer says the permanent free tier is a "no-model wizard", but d10 and tiers 1.2 give signed-out users local and BYOK chat coaching with no limit. One of the two sentences is wrong. This is also tiers Q5, still open. |
| L-2 | "Full Individual plan" for the trial is overstated: it is sync (managed is dark, no credits). Marketing cannot promise more. |
| L-3 | Paid Individual has no defined differentiator besides sync and managed; `features[]` is empty. Pricing axes (tiers 1.1) list nothing a solo user lacks. |
| L-4 | The first buyer is a CoE lead (d12), who evaluates with teammates and reviewers. The trial is an Individual trial; a Team trial is an ASSUMPTION in tiers line 12 and tiers Q3. |
| L-5 | Billing is scheduled in the dark phase (row 3.2 depends on the gateway). Whether a Team can be invoiced and an Individual charged at launch, with managed off, is unspecified. |
| L-6 | Post-trial and lapsed-trial data state is undefined (above). |
| L-7 | Free users can use Coach inside a Team company without signing in; only machine enrollment (`RequireOrgPolicy`) stops that, and the registry path and packaging are unspecified (N-13). The documents say so honestly (tiers line 240). |
| L-8 | Account lifecycle pages (account, device deactivation, offline activation, billing link) are real work (row 2.1) but absent from the six admin screens (N-10). Individual account deletion and personal data requests are not described; the only erasure path found is tenant offboarding by an Admin (architecture line 762), and an Individual has no Admin. |
| L-9 | Three grace clocks: policy 14 days, entitlement 30 days, billing past-due 14 days plus a 60-day deletion hold. Each is documented separately; Enterprise Q7 (raise the 30 days for air-gapped sites) is open. |
| L-10 | Device limit and trial limit can only be enforced for signed-in use. That is fine, but it means "3 devices" is a sync limit, not a licence limit. |

### 5.5 Three licensing models

**Model A: Open core. The coach is free; the cloud and the governance are paid (the documents' direction, made explicit).**
- Free, no account, unmetered: wizard, engine, local and BYOK coaching, rescue and second opinion, AutoMate drafts, export.
- Paid Individual (account plus token): sync, backup and restore, version history, 3 devices, managed after G1, support. Trial: 14 days of exactly that.
- Team: the governance set (policy, roles, approvals, audit, break-glass, enrollment). First-buyer trial is a Team org pilot (14 or 30 days; owner picks) with an explicit post-trial state: org data read-only, policy per `onExpiry`, export always.
- Enforcement is server-side only (sync, gateway, portal, approvals); the token proves plan and device; no client-side paywall.
- Pros: matches d3, d10, tiers 1.2 and architecture 1.6; no DRM, no key-sharing problem, nothing to crack; conversion happens at felt value (losing a laptop, adding a teammate, needing an approver); consistent with the competitive finding that comparators offer a free BYOK or local path; strongest privacy and air-gap story; smallest change set.
- Cons: solo-user revenue is thin until managed is GA and the managed margin is proven; a 14-day sync trial rarely demonstrates backup value; revenue concentrates on Team and Enterprise, which have the thinnest launch feature set (many Enterprise items are P2).
- Documents that change: contract d6 and d10 (free-offer sentence); tiers 1 (free offer, sign-in, Team trial rows), 1.1, 1.2, Q3 and Q5 closed; catalog `tenant.trial.days` (add a Team variant), tenant rows for post-trial state; architecture 1.5, 1.6 (post-trial state, token claims), 4.5 (free paths), 6.2 (move subscription and entitlement billing out of the dark phase); tiers 7 (account and activation pages).

**Model B: Licence-key activation without identity.**
- A paid Individual (or small Team) buys a licence key from a merchant of record; an activation endpoint exchanges key plus device request code for a device-bound signed entitlement file (the existing offline-activation format, minus portal sign-in). The file unlocks a named client-side capability set (for example full guided coach on BYOK and local, rescue, second opinion, docx and pdf export, AutoMate apply, more Blueprints). Sync still needs an account. An anonymous 14-day trial token is issued on first launch.
- Pros: honours "no sign-in for local and BYOK" while still monetizing the largest group (the free majority); works for air-gapped and `restricted`-class users; reuses the token, key-set manifest and activation design; gives Enterprise offline sites a licence without identity.
- Cons: needs client-side gating (soft, defeatable by a local admin); contradicts the floor "signed-out use always includes the wizard, local models and BYOK"; key sharing, reinstall-based trial resets (no identity to key a trial on), lost-key support; a public activation endpoint is new attack surface (security-analyst review before build); two licensing paths (key and account) to run and explain; makes "free coach" positioning weaker than the free BYOK competitors.
- Documents that change: contract d6, d10, 5 Policy; tiers 1, 1.2, 3.2 and 3.3 (new bypass: key sharing), 9; catalog (new licence rows, feature-to-claim map); architecture 1.6, 5.2 (new threat), 6.2 (new workstream), 4.5; coach-spec 3 (tool and flow exposure by entitlement); model-cert none.

**Model C: Account required after the trial (and for chat coaching).**
- Free is literally the contract's "no-model wizard with export". After the 14-day trial, any chat coaching, including local and BYOK, needs a paid account or org membership. Variant C1: a free account is required for anything beyond the wizard.
- Pros: one gate, enforced by identity; strongest conversion and trial-abuse control; simple to explain; funnel visibility.
- Cons: contradicts d3 ("local is free"), d10 and the competitive evidence; blocks the exact users the `restricted` class sends to local models; turns the 30-day offline grace into a hard dependency; damages the privacy story that justifies "does not store" and BYOK direct; likely backlash from the first buyer's own staff.
- Documents that change: nearly all: contract d3, d6, d10; tiers 1, 1.2, 3.2, 3.3, 4.5; architecture 1.6, 4.5, 5.1, Free paths, D11; catalog connection rows; coach-spec modes; model-cert (lite and local certification still needed).

### 5.6 Recommendation

Adopt Model A with four amendments, and keep a narrow form of Model B only for what already exists (the Enterprise offline activation file for air-gapped sites). Amend: (1) rewrite the free-offer sentence in the contract, tiers, architecture and catalog to describe the real free tier, and close tiers Q5 as "free forever"; (2) define paid Individual at launch as sync, backup, restore, version history, 3 devices and, after G1, managed, and call the Individual trial a trial of those; (3) make the first-buyer trial a Team org pilot and define the post-trial state of data and policy; (4) move Stripe subscription billing and entitlement webhooks out of the dark phase so Team and Individual can be billed at launch with managed off. Reason: it is the only model consistent with every locked decision, and the first buyer is a CoE lead whose reason to pay is governance, which Model A prices.

## 6. Contradictions between documents after patching

Feature to tier placement. Tiers matrix, catalog `x-minTier` and architecture 1.5 agree on every row I compared (audit 365, approvals at Team, sensitivity editing not on Individual, baseline signed, P2 settings hidden). Residual: tiers lines 23 and 29 advertise rule counts and multi-reviewer whose editors and features are P2 (disclosed).

Enforcement claims by connection type. Tiers 3.2 and architecture 5.1 agree. Residual: tiers line 195 sells `managed` as the hard path without the flag caveat (N-04); `no_llm` blocks local (DC-53).

Approvals and who may approve. Contract d9, tiers line 113, catalog invariant 9, architecture S4 and line 632 agree: only a CoE Reviewer, never the author, Admin cannot. Residual: Team of one (tiers Q6); Individual cannot satisfy `restricted` approval before handoff (N-02).

Backup and sync of `restricted`. Catalog 4, architecture 3.4b and S8 agree on opt-in plus metadata sync. Residual: export "no" versus review packet, file fallback and "export always works" (N-02); X10 (N-06).

Signing algorithm and enrollment. ES256 everywhere, key-set manifest, enrollment at launch, signed baseline: consistent. Residual: registry key path (N-13); certification registry channel (N-07).

Launch scope and the six-screen portal versus build order. Six screens consistent in contract 7, tiers 7 and 8, architecture D12 and row 2.4. Residual: account and activation pages, Spend hidden, bespoke environment-profile form in tiers 7 (N-10). Certification harness "about 30" scenarios (architecture row 4.2) versus 36 scenarios G01 to G36 (N-12).

Telemetry and retention defaults. Off everywhere, 365-day Team audit, 35-day backup window: consistent. Residual: the `anonymous` enum value (N-08).

Wording of the gateway privacy claim. Contract d5, catalog invariant 2, architecture A2 and 2.3, tiers 3.3 use "does not store" and "not stored by us". Residual: model-cert line 304 (N-11); tiers line 369 says "metadata only persisted", which is acceptable.

## 7. New and residual issues register

| ID | Sev | Issue | Where | Fix direction |
|---|---|---|---|---|
| N-01 | High | Licensing and billing: paid Individual is sync only; subscription webhooks are in the dark phase; trial and post-trial states undefined; account and activation pages unscheduled | Section 5; architecture row 3.2, 1.6, 4.5; tiers 1.2, Q3, Q5 | Section 5.6 |
| N-02 | High | `restricted` default: export "no" and approval before handoff "yes". Blocks the review packet (architecture 3.4b item 5), the file-based AutoMate fallback (schema description of `exportAllowed`), the owner's own copy ("Export is the user's own copy", architecture 3.4b item 1), and "export always works" (tiers line 60, architecture lines 414 and 764). Individual cannot get an approval at all | Catalog 4 line 198; tiers lines 115, 60; architecture 3.4b, T18 | Allow the owner's local export and the review packet for `restricted` (local file, no upload), and let a recorded self-attestation satisfy handoff approval on Individual, or document that Individual cannot hand `restricted` Blueprints to AutoMate |
| N-03 | High | Thesis holes H-1 to H-10 | Section 4 | Section 4.2 |
| N-04 | Medium | `managed` presented as the hard guarantee without the flag caveat | Tiers line 195; tiers 3.2 table | Say "once `managed` is available; until then `custom_openai_compat` behind the org's own gateway" |
| N-05 | Medium | Server engine timing: rules-engine 17.2 (line 2674) and tiers line 163 versus architecture X3 | Rules-engine, tiers | Align both to "at status transitions; never merges" |
| N-06 | Medium | X10 (approval metadata when `sync.blueprints.enabled` is locked off) is an architecture ASSUMPTION marked "NEW rule for the catalog" and is not in the catalog or tiers | Architecture X10, 3.4b item 6; catalog | Add the rule to the catalog |
| N-07 | Medium | Certification registry: model-cert line 282 (like the Policy bundle), architecture X2 (content feed, content key), tiers line 144 (gateway table), and the name is unconfirmed | Three files | One artifact, one signer, one channel; update model-cert and tiers |
| N-08 | Medium | `telemetry.crashReports` and `telemetry.usageAnalytics` have `value` enum `off` or `anonymous` and admin lock "Yes", so an admin can lock `anonymous` on for every user. Contract d10 says off everywhere; tiers line 28 says the admin can lock it off; no telemetry sink exists at launch (architecture line 539 lists none) | `policy.schema.json`, catalog lines 113 to 114 | Remove `anonymous` or make it default-only and user-choice, or define the sink and the consent text |
| N-09 | High | Free-offer wording versus sign-in rules (L-1) | Contract d6 versus d10; tiers lines 12 and 67; architecture lines 379 and 404 | Section 5.6 amendment 1 |
| N-10 | Low | Portal screen count: six named screens, plus account page, activation page, hosted billing portal; Spend hidden at launch; bespoke environment-profile form in tiers 7 | Tiers 7; architecture 1.6, 2.1, 2.4 | Count them, or fold the account and activation pages into Users and roles |
| N-11 | Low | "the gateway logs metadata only, so it cannot see prompts" | Model-cert line 304 | Reword to "does not store prompts" |
| N-12 | Low | Scenario count: architecture row 4.2 "about 30" versus 36 in model-cert | Architecture 6.2; model-cert 3.3 | Fix the number |
| N-13 | Medium | Machine enrollment value names exist but the registry key path is undefined, and ADMX and Intune packaging is after launch, so IT cannot deploy it from the documents | Catalog 6 line 240; tiers 4.3 | Fix the path (a placeholder with the working name) and document a manual or script deployment |
| N-14 | Low | Three grace clocks documented separately | Tiers 4.5, architecture 1.6 and line 764 | One table in tiers 4.5 |
| N-15 | Medium | Rescue findings and hybrid patterns: F1 label (H-9); `pattern-library.md` has no consumer in the Coach (DC-50) | Coach-spec 11; pattern-library | Add a pattern-suggestion step or move the library out of launch scope |
| N-16 | Low | Blueprint import and restore-from-file flow is mentioned in architecture T8 and the export kind `blueprint_json`, but coach-spec specifies no import flow | Coach-spec | Specify it (with H-8) |

## 8. Unsourced or stale facts remaining (all VERIFY)

Carried from 99b section 7 without change in status: V-01 to V-25 (OpenRouter fees, resale terms and red-team clause, Stripe and OpenRouter news, competitor prices, failure statistics, absence claims, local model benchmarks and licences, server defaults, Bedrock and Vertex token lifetimes, Copilot+ baseline, GDPR and AI Act dates, SOC 2 timelines, architecture RPO and RTO and SLOs, catalog retention and limit defaults, tiers refresh and rotation numbers, engine ROI constants, certification thresholds). None of them was re-sourced in the patch round, and I did not re-read the research files to confirm; treat them as unchanged.

New or changed in this pass:

| # | Claim | Where | Tag |
|---|---|---|---|
| V-26 | Seed catalog: 20 entries carry `lastVerified` 2026-10-25 and no `sources` (list in DC-42); rules-engine 18.2 says ten Microsoft pages are cited, but 9 entries have `sources` | `tool-catalog.seed.json`, rules-engine 18.2 | VERIFY |
| V-27 | Entitlement token: claim set, refresh about daily, TPM-backed device keys, offline activation endpoint and file format | Architecture 1.6 lines 411 to 417 | VERIFY (ASSUMPTION in source) |
| V-28 | Stripe Billing as the subscription engine, hosted checkout PCI scope, tax and merchant of record | Architecture lines 920, 1102, V9, V17 | VERIFY (counsel) |
| V-29 | Trial "once per user" and the abuse limits (T7) with no payment method | Architecture line 402, T7 | VERIFY |
| V-30 | Registry key path, MSIX per-user install versus machine-wide key, Intune behaviour | Catalog line 240; architecture lines 454, V10, V20 | VERIFY |
| V-31 | Break-glass 4-hour time box | Tiers Q2 | ASSUMPTION |
| V-32 | Policy negative cases and examples validated with a hand-written validator | Catalog line 1177 | VERIFY (re-run with `jsonschema` or Ajv) |
| V-33 | Adversarial testing terms of OpenRouter and every other provider; who funds the separate certification account | Model-cert 3.5 | VERIFY |
| V-34 | Gate G1 itself: OpenRouter permission or a direct provider agreement; AutoMate team's commitment and date for draft import, diff and IPC | Architecture 0.1(a), 0.1(b), 4.0 | Non-code gates, in writing |

Coverage gaps still unspecified:
- Host glossary text for chips (H-5); its owner and localization.
- Blueprint import, share-accept and restore flow, including the reset rules (H-8, N-16).
- Post-trial and lapsed-trial data state; Team trial semantics (section 5).
- Account lifecycle: account page, activation page, Individual account deletion and personal data requests (L-8).
- ROI tracking field, tool and question (DC-34).
- Labelling of self-attested overrides in exports and audit (DC-40).
- Certification registry: one name, signer, channel (N-07).
- Registry key path and deployment without ADMX (N-13).
- A user-facing view for the hybrid pattern library, or a decision to cut it (DC-50).
- Customer-facing restore flow for a `restricted` local-only Blueprint after disk loss (architecture 3.9 covers service backups only; a never-backed-up Blueprint has no restore).

## 9. Owner decisions that genuinely remain (merged, owner-decided items dropped)

Dropped as already decided in contract v2: managed gating, gateway wording, ES256 and enrollment, Individual baseline, backup as capability and `restricted` opt-in, roles and who approves, retention and telemetry defaults, scope cuts, CMK and vault timing, ladder order, ROI advisory, graduation deferred, certification fingerprint, cap, judge and S0, local servers, accessibility, Azure and 3 devices, first buyer.

Remaining:
1. **Free versus paid, and the trial (N-01, N-09, L-1 to L-6).** Is chat coaching on BYOK and local free forever (recommended yes)? What does paid Individual contain at launch? Is the first trial a Team org pilot, and what is the post-trial state of data and policy? Is subscription billing live at launch while managed is dark (recommended yes)? (tiers Q3, Q5; architecture Q2.)
2. **`restricted` handoff and export (N-02).** May the owner export a `restricted` Blueprint locally? Does the review packet count as an export? May a recorded self-attestation satisfy handoff approval on Individual, or is `restricted` AutoMate handoff Team and above only?
3. **Import and confirmation policy (H-6, H-8, H-10).** Approve the rule that imported, shared and restored Blueprints reopen as proposed; decide which fields are value-confirmed and which entity-confirmed; approve the accurate thesis sentence.
4. **Sensitivity raise (H-1).** Keep "applied at once" with a visible undo, or require a chip.
5. **Chip budget (H-2, H-3).** Accept the host-rendered question controls as the main answer path (no chip), with chips only for free-text extraction; decide the acceptable chips per step for design-partner testing.
6. **Break-glass details (tiers Q2).** Time box, owner veto, second admin at Enterprise.
7. **Team of one (tiers Q6) and Viewer pricing (tiers Q4).** Whether a one-person Team may self-attest; whether Viewers are free.
8. **SSO at launch (tiers Q1).** Does custom OIDC enter the launch Enterprise offer, given Enterprise is otherwise mostly P2?
9. **Managed economics (99b s9 n3).** Fee rate, minimum top-up, wallet expiry and refund; needed before G1, not before launch.
10. **Telemetry `anonymous` (N-08).** Remove the value or define the sink and consent text.

Non-decision gates still outstanding, in writing: OpenRouter permission or a direct provider agreement (G1); the AutoMate team's commitment and date for the adapter API; counsel on stored-value wallets, DPA and sub-processors; the funded separate certification account.
