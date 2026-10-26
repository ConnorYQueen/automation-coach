# 99b. Decision-and-claims consistency review

Reviewer: independent subagent, no prior context on these files. Date: 2026-10-25. No existing file was edited; this is the only file written.

Citation style: `file.md N` means the numbered section or heading N of that file (for example `tiers.md 4.1`). `C1`..`C11` are architecture.md 0.1 rows, `D1`..`D12` are architecture.md 0.2 rows, `T1`..`T12` are architecture.md 5.2 threats, `R1`..`R15` are research/openrouter-gateway-billing.md recommendations, `S4` is an architecture.md 3.4 workflow rule. Finding ids are `DC-nn`.

## 0. Scope, method, limits

Read in full or in the sections that matter: 00-shared-contract, tiers, architecture, settings-catalog, coach-spec, model-certification, research/openrouter-gateway-billing, research/competitive-landscape, research/local-and-enterprise-endpoints. rules-engine.md (3606 lines) was read selectively: ladder and C1 conflicts, operations tags (2.2), ROI (11.3), graduation (13), hybrid patterns (14), integration (17), assumptions and open questions (18), the example Blueprint (19). JSON was used only for: coach-tools.json (labelExposure, global rules, absence of `operations`), tool-catalog.seed.json (entry count, sources), and a few greps of the two schemas. A separate agent is cross-checking the data contracts (schemas against each other), so this review does not duplicate that work.

No external source was fetched. "VERIFY" status below is judged only from what the documents themselves cite.

Severity scale: **Critical** = negates an owner decision, a stated non-negotiable, or a launch gate. **High** = two documents would produce divergent builds or a misleading security or privacy claim. **Medium** = needs an owner call but has a workable default. **Low** = wording, naming, staleness.

## 1. Summary

Counts: 3 Critical, 11 High, 37 Medium, 7 Low (58 findings, register in section 2; DC-58 sits with the Medium rows).

Verified consistent (so you can stop worrying about these): tier counts 36 / 45 / 1 of 82 settings match between tiers.md and the catalog; the approval-token protocol (single use, bound to diff hash, 10-minute expiry, minted by a trusted click) is identical in coach-spec 1 and 6, coach-tools.json and architecture 5.3 L4; telemetry defaults are consistently off in the catalog, architecture 2.1 and 6.3; the honest "soft versus hard" enforcement matrix in tiers 3.2 and architecture 5.1 agree on every control that both cover (differences are listed in 5.2); decision 1 (AutoMate has no AI at runtime) is honoured everywhere I looked; decision 2 is enforced mechanically by architecture D2 (Engine assembly may not reference HTTP or LLM namespaces).

Five worst contradictions:
1. DC-01: `managed` is a launch requirement but rests on OpenRouter permission that research rates "not clearly permitted"; no fallback exists.
2. DC-02 with DC-04: decision 8 requires full backup, yet `restricted` defaults to no sync, sync is admin-lockable, and `restricted` also needs a server approval record it can never have.
3. DC-03 with DC-11: model-written diagnostics and operations tags drive the verdict without per-value confirmation; coach-spec 7.4 says injection "cannot change a verdict", which the field authority matrix does not support. coach-tools.json also has no `operations` field at all.
4. DC-06 with DC-07 and DC-08: "thin" admin scope versus an L-sized portal with a server-side engine; signing algorithm and machine enrollment disagree between tiers.md and architecture.md.
5. DC-05 with DC-09: "metadata only" gateway wording versus a gateway that holds plaintext prompts, a planned scan, and an org key vault that stores provider keys on our servers.

## 2. Findings register

| ID | Sev | Finding | Where | Direction |
|---|---|---|---|---|
| DC-01 | Critical | Decision 4 `managed` depends on a resale permission nobody holds. OpenRouter ToS section 7 prohibits "reselling API access to Models"; research verdict is "not clearly permitted", "do not launch managed on reading alone", written approval needed (R1). Architecture still lists managed credits as a launch requirement (coverage table) and tiers.md 3.3 tells customers to use `managed` for "a hard guarantee". No fallback is named. | openrouter research C1, R1, R5, R10; architecture 0.1 C1, 6.2 row 0.1, 3.1 to 3.4, coverage table, 6.4 R2, T12; tiers 3.3 last paragraph | Make written OpenRouter approval a ship gate in the contract. Name the fallback (direct provider contracts, or launch BYOK and local only with managed behind a flag). Until then do not describe `managed` as the guaranteed hard path. |
| DC-02 | Critical | Decision 8 says full backup is required and "not metadata-only". Three places weaken it: `restricted` defaults to no cloud sync; `sync.blueprints.enabled` is admin-lockable off; tiers and architecture each ask whether backup is a guarantee or a switchable capability (open, unanswered). Customer copy cannot say "full backup" until ruled. | catalog 4 (restricted row), 3 (sync.* keys); tiers 9 Q1; architecture 0.1 C2, 7.1 Q1 | Owner ruling, see OD-2. |
| DC-03 | Critical | coach-spec 7.4 says an injection "cannot change a verdict or recommendation". The field authority matrix (coach-spec 1.1) lets the model write `step.diagnostic` through `record_diagnostic_answers` with no per-value confirmation; the host checks that the quote is a verbatim substring of a typed turn, not that the enum value matches the quote; the engine verdict and rung depend on those values. A model that misreads a real user quote, or is steered by one, changes the verdict. The claim is overstated and the contract thesis (b) says the user confirms the structure. | coach-spec 1.1 row step.diagnostic, 6 tool table, 7.4, 9; rules-engine 2.2 | Add a confirmation chip for diagnostic values before the engine consumes them, or restate the claim as "cannot change a verdict without a user-visible diagnostic value". See OD-24. |
| DC-04 | High | `restricted` requires approval before handoff (catalog 4) and the AutoMate adapter checks "the server-signed approval record" against `contentHash` (architecture 5.1, 5.3 L4). `restricted` never syncs, so no server record can exist. Either handoff is impossible or the check is skipped. | catalog 4; architecture 5.1 AutoMate row, 5.3 L4; tiers 3.3 bypass 8 | Allow approval metadata (contentHash, status, signer, no content) to sync for `restricted`, or block handoff. See OD-22. |
| DC-05 | High | Contract wording "gateway logs metadata only" is true of persistence. The gateway holds plaintext prompts in memory, OpenRouter and the model provider see them, and the planned P2 in-transit scan reads content. Architecture C1 already says to write "not stored by us", never "we never see it"; contract, catalog invariant 2 and tiers 8 ("Deliberately not building: per-prompt logging") have not adopted it. | contract decision 4; architecture 0.1 C1, 2.2; tiers 3.2 row Redaction, 3.3 bypass 6, 8 P2 item 5; catalog 6 invariant 2 | Amend decision 4 wording (amendment A2). Treat the scan as an explicit owner-approved exception. |
| DC-06 | High | "Keep the launch admin surface thin but real: 16 screens, no bespoke setting widgets" (tiers 8) versus architecture C10, D12, 6.2 row 2.4: portal sized L, server-side engine, server-rendered review view; architecture says a thin portal "would not meet" the scope. Also the tiers launch list includes an Environment profile form, an org-rule template library with parameters, Intake and Templates screens; none is described as schema-generated, and architecture 2.4 lists none of them. True portal size is undefined. | tiers 7, 8; architecture 0.1 C10, 0.2 D12, 6.2 row 2.4, 6.3 | Re-baseline: either size all 16 screens in architecture 2.4, or move Intake, Templates and the org-rule editor to P2. See OD-17. |
| DC-07 | High | Policy signing algorithm: tiers.md 4.1 fixes EdDSA (Ed25519) with an HSM root; architecture C5 says EdDSA only "if the chosen HSM and .NET libraries support it", otherwise ES256, and hands the final call to "the policy owner" (V18 unresolved). A crypto choice compiled into the client has two documents and no owner. | tiers 4.1, 4.2; architecture 0.1 C5, 7.2 V18 | Default ES256 unless Ed25519 support is verified; keep `alg` in the protected header. See OD-14. |
| DC-08 | High | Machine enrollment: tiers.md 4.3 puts registry and ADMX "later"; architecture C6, D6, 5.1, 6.2 row 2.2 require a minimal registry enrollment (`RequireOrgPolicy`) at launch. Without it, decision 7 "Admins can disable personal keys" and "org policy required" are bypassed by not signing in, which architecture 5.1 admits. | tiers 4.3, 8 P2 item 7; architecture C6, 5.1, 6.3 Policy row | Minimal enrollment at launch, ADMX and Intune later. See OD-15. |
| DC-09 | High | Enterprise org key vault stores org provider credentials, mints sub-keys or leases keys, on our servers. Decision 4 and catalog invariant 1 keep keys on the client; architecture C7 calls it a "named exception"; architecture 2.3 rule 2 ("personal secrets never reach us") does not mention it. Raises breach impact (T10) and sub-processor exposure. | tiers 5; architecture 0.1 C7, 2.1 row Org-provisioned credentials; catalog 5 `tenant.vault.enabled` | Owner accepts or rejects the exception. If accepted, add it to the contract and send it to security-analyst before build (P2). See OD-8. |
| DC-10 | High | Experimental-model tool gating. Architecture L3 (marked ASSUMPTION, "coach-tools doc decides") gives weak or experimental labels read-only coaching with no write tools. coach-spec 3 item 4 and coach-tools.json `x-labelExposure` decide differently: Experimental keeps add and update tools, diagnostics, `advance_stage`, the justification card and test-case generation, and loses only the six approval-class tools and `propose_automate_flow_draft`. coach-spec says it "refines" L3; architecture was not updated, and T1 still reads "write tools gated by model label". | architecture 5.3 L3, 5.2 T1; coach-spec 3, App B; coach-tools.json x-labelExposure | Update architecture. Owner confirms an Experimental model may write diagnostics (ties to DC-03). See OD-31. |
| DC-11 | High | The 36 `operations` tags are the main rung driver (rules-engine 2.2). The model proposes them and the user "confirms the step", but a user cannot judge tag semantics. coach-tools.json defines no `operations` field (grep count 0), nor humanAuthority, residualHandling or inputVariability; per rules-engine 17.1 every step without `operations` returns `needs_info`. Coach as specified cannot produce a recommendation. | rules-engine 2.2, 17.1; coach-spec 1.1, App B; coach-tools.json | Add the fields to the tools. Present tags as plain-language yes/no questions the user answers, not as a model guess. See OD-24. |
| DC-12 | High | TR-3 (payback) can fire `dont_automate` from invented constants: triage share 0.5, build 16 h, maintain 4 h, per-rung hours, test overhead 0.3, residual share 0.10, payback limits 1.0 and 2.0 years. The doc itself calls them "the least certain numbers in this file". The engine has no LLM, but the "auditable" verdict is only as honest as its constants. | rules-engine 11.3, 18.1, 18.3 Q4, TR-3 | Ship TR-3 as an advisory warning until calibrated and owner-signed; show constants in the rule trace. See OD-25. |
| DC-13 | High | Who can read Blueprint content has four answers and no setting. tiers 2: "ASSUMPTION: Admin and CoE Reviewer can read synced Blueprint content" and Q3 asks whether that should be the default. architecture 3.4: "Admin reads any synced blueprint". architecture T11: "blueprints private until `in_review`". architecture 2.1: Admin "per policy", and the portfolio projection (title, summary, ROI, people in encrypted columns) is visible to Admin and CoE Reviewer. No catalog key exists. | tiers 2, 9 Q3; architecture 2.1, 3.4, 5.2 T11, 7.1 Q9; catalog (no key) | Default to metadata only until shared or in review; add a locked-only setting if content access is allowed. See OD-7. |
| DC-14 | High | Certification probe P6 (injection canary) auto-runs on connect, including on `managed` and `byok_openrouter`, and golden scenarios G23 to G27 are adversarial. OpenRouter terms (research R5) require prior written approval for "Red Teaming" (prompt injection). If the single upstream account is suspended, `managed` stops for every tenant. | model-certification 2.1 P6, 3.3 G23-G27; openrouter research R5 | Run adversarial suites against local or test models and a separate account, or get written approval first. See OD-33. |
| DC-15 | Medium | Audit-log retention for Team: 90 days (tiers 6, ASSUMPTION) versus default 365 with Team cap 365 (catalog `retention.auditLog.days`; architecture 2.1). | tiers 6; catalog 3 Data; architecture 2.1 | Pick 365 or amend the catalog. OD-11. |
| DC-16 | Medium | Approval records required before apply: tiers 1 matrix places them in Enterprise; catalog `governance.approval.*` (default `requiredBefore ["automate_apply"]`) has min tier Team. | tiers 1; catalog 3 Governance | OD-18. |
| DC-17 | Medium | tiers 1: Individual gets "built-in defaults the user can edit" for data domains and sensitivity rules. Catalog `data.sensitivityRules` and `data.minimumSensitivity` have min tier Team, so Individual cannot edit them. | tiers 1; catalog 3 Data | OD-19. |
| DC-18 | Medium | Individual policy bundle: tiers 1 matrix says "None, built-in baseline"; tiers 4.3 ("signed baseline bundle in the installer. ASSUMPTION") and architecture D5 say signed. Open as tiers Q2. | tiers 1, 4.3, 9 Q2; architecture D5 | Default signed (one code path). OD-16. |
| DC-19 | Medium | Catalog contains controls tiers.md defers to P2: `governance.approval.minReviewers` up to 3 (Enterprise), `reviewSlaDays`, and the tenant.* rows (vault, CMK, SCIM, SIEM stream, legal hold, region). tiers 8 says "every setting in the catalog honoured" at launch and "all 82 settings ship". Dead controls would appear in the schema-generated UI. | catalog 3 Governance, 5; tiers 7, 8 | Hide P2 settings until their feature ships, or move the features to launch. OD-18. |
| DC-20 | Medium | Spend wording: tiers 1 "Pay as used on `managed`" versus a prepaid wallet (architecture 4.5; research: stored value, legal review R10). Contract says "monthly for the platform plus usage at cost + transaction fee". Expiry, refund, tax and what "cost" includes (OpenRouter's 5.5% purchase fee, $0.80 minimum, per research) are unresolved. | tiers 1; architecture 4.5, 7.1 Q3, Q4; openrouter research | OD-3. |
| DC-21 | Medium | CoE Reviewer authority: tiers 2 lets a CoE Reviewer create Blueprints and run Coach and use a model connection; coach-spec App B assumes critique-only and read-only in Coach (open Q2). Separately architecture S4 says "only a CoE Reviewer can set `approved`" while 3.4 says Admin or CoE Reviewer. | tiers 2; coach-spec App B ASSUMPTIONs, Q2; architecture 3.4 S4 | OD-20. |
| DC-22 | Medium | TR-4 adds the condition `coe_review_required` (also in the rules-engine example Blueprint). Individual has no reviewer and `allowSelfApproval` defaults false. Handling for an unsatisfiable condition on Individual is not specified (not found). | rules-engine TR-4, 19; catalog `governance.approval.allowSelfApproval` | OD-21. |
| DC-23 | Medium | Telemetry is consistently off by default, but extra upload channels do not follow the same default or invariant: `governance.auditLog.clientReportedUsage` is admin-lockable and identifies user, model, tokens, time; model-certification 5.3 adds runtime rejection-count upload if a Team or Enterprise admin enables it (its own open Q2 asks if this breaks "metadata only"); architecture 2.1 allows BYOK and local usage upload "if policy asks". tiers 8 and catalog invariant 6 say org-forced identified telemetry is not built. | catalog 3, 6; tiers 8; model-certification 5.3, 8 Q2; architecture 2.1 | Classify these as audit data, not telemetry, and say so; default off; OD-9. |
| DC-24 | Medium | Catalog `retention.blueprints.deletedGraceDays` says hard purge "from storage and backups"; architecture 3.7 says deleted data persists in backups for the 35-day backup window (ASSUMPTION) and the DPA must say so. | catalog 3 Data; architecture 3.7 | Fix catalog wording; OD-12. |
| DC-25 | Medium | Server-side engine claims differ: tiers 3.2 "re-evaluates any synced Blueprint against current policy"; architecture C11 and D2 re-run the engine at status transitions; rules-engine 17.2 asks the server to recompute derived fields after every merge, but architecture D3 merges client-side and says the server never needs to merge. | tiers 3.2 last rows; architecture 0.1 C11, D3; rules-engine 17.2 | State exactly when the server evaluates (on transition only, or on every push). |
| DC-26 | Medium | Dependency inversion in build order: the connection layer and orchestrator (architecture 1.5, 1.6), `models.minCertification` and mode eligibility (model-certification 2.2) need certification labels, but the harness and manifest arrive in 4.2. In Phase 1 every model is Uncertified. Tiers 8 lists "certification labels and the capability probe" in Launch. | architecture 6.2 rows 1.5, 1.6, 4.2; model-certification 2.2; tiers 8 | Ship a minimal signed registry in Phase 1, or state that Phase 1 treats all models as Experimental. |
| DC-27 | Medium | Approval-flow gaps. (a) architecture 6.2 row 1.4 says approval UI "can follow in Phase 4", but `record_override`, removal of confirmed content and `export` need an approval click in Phase 1 (coach-spec 1, 6). (b) coach-spec App B admits how an override awaiting reviewer approval is stored on `Step.override` is still assumed, while catalog `coach.override.mode` and `coach.llmOverride.mode` have an `approval_required` setting. | architecture 6.2; coach-spec 1, 6, App B; catalog 3 Coach behavior | Specify override-pending state and schedule the approval UI in Phase 1. |
| DC-28 | Medium | Certification fingerprint is {provider, modelId, version or digest} plus prompt and schema versions (model-certification 5.1). Research C4 and 7.7 require (model, server kind, server version, quantization) because the same weights break on different servers (Ollama #14493). model-certification does not apply research C5: Claude through an OpenAI-compatible layer should be capped at Works or Experimental (it ignores `strict`, `response_format`, caching). | model-certification 5.1, 8 Q3; local research C4, C5, 7.7 | Extend the fingerprint; add the cap. OD-32. |
| DC-29 | Medium | The certification artifact has three names and three delivery routes: `ModelCertificationRegistry` delivered like the Policy bundle (model-certification 5.1); "certification manifest" in the content feed signed with a separate key (architecture); "gateway holds the certification table" (tiers 3.2). | model-certification 5.1; architecture 2.1, 6.2 row 4.2; tiers 3.2 | Pick one artifact, one signer, one channel. |
| DC-30 | Medium | Ladder order: the contract and coach-spec put `human_checkpoint` before `llm_agent`; rules-engine C1 and Q10 put `llm_node`, `llm_agent`, `human_checkpoint` and ask for confirmation. | contract ladder; rules-engine 0 C1, 18.3 Q10; coach-spec 2.4 | OD-26. |
| DC-31 | Medium | Contract entities are extended in at least five places without a ruling although the contract says "use exactly": Connection (local research 7.6: serverKind, authScheme, extraHeaders, modelIdKind, contextWindowOverride, capabilityProfile, tokenProviderRef); Step and Blueprint (coach-spec App B: provenance, confirmation, asBuilt, deployPlan, tests[], auditLog vocabulary); sync requirements (architecture C4); `kind` for template and intake (architecture 3.4 ASSUMPTION); `interfaceAvailability` "none" (rules-engine 18.3 Q9). | local research 7.6; coach-spec App B; architecture C4, 3.4; rules-engine 18.3 | One contract v2 revision. OD-27. |
| DC-32 | Medium | Rescue question Q-RSC-08 "Rescue, rebuild, or retire?" maps to the triage verdict path, but engine verdicts are only `automate`, `fix_process_first`, `dont_automate`; rebuild and retire have no engine meaning. Rescue also needs `Step.asBuilt`, a contract extension. `apply_existing` mode (changes live flows) has the same dependency. | coach-spec 11, App B item 2; catalog `automate.actions.mode` | Decide whether rescue produces a verdict or only findings. |
| DC-33 | Medium | Graduation (LLM to code, rules-engine 13, GR-1 to GR-5) is engine-only. The rule miner needs logged inputs and outputs (content) while RunStats are "counts and rates only"; the data source is open (18.3 Q5) because `ui.automate` cannot host an `llm_node`, so there is no AutoMate run log to mine. No tool, stage, setting or architecture component references graduation. | rules-engine 13, 18.3 Q5, seed `ui.automate`; coach-spec (none); architecture (none) | OD-28. |
| DC-34 | Medium | ROI is an estimate only. No field or flow records actual versus predicted savings (grep for realized, actual-versus-predicted, ROI tracking returns nothing); only `reviewAfterDays` and RunStats exist. | rules-engine 11; coach-spec App B item 3 | OD-29. |
| DC-35 | Medium | Privacy routing default: catalog `models.zeroRetentionProvidersOnly` defaults false and public and internal classes require no zero-retention provider; the openrouter research recommends `provider.data_collection="deny"` on every managed request; tiers 3.2 marks forced routing as hard with "VERIFY provider flags". | catalog 3 Connections, 4; openrouter research; tiers 3.2 | OD-10. |
| DC-36 | Medium | Architecture 7.2 V1 to V8 (cost reporting, privacy flags, fees, resale, key provisioning, activity export) are now answered by the research (cost from `usage.cost`, `/generation`, 5.5% fee with $0.80 minimum, key limits, guardrails, ToS section 7). Architecture 4.5 still treats the fee meaning as open; research recommends 20% on reported cost, $10 minimum top-up, Enterprise 10 to 12%. | architecture 7.2, 4.5; openrouter research | Refresh the register. |
| DC-37 | Medium | Local scope. Contract names Ollama, LM Studio, Foundry Local; research adds llama.cpp as a fourth `serverKind`, flags LM Studio licence and "recommending" terms as needing legal review (do not bundle), says Foundry Local REST is still preview with a dynamic port, and makes the native Anthropic adapter "v1.1, first priority" while architecture 1.5 says "one native adapter if research says it is required". Architecture sizes local at M and omits the lite coach, readiness check, server quirk profiles and Ollama context onboarding that research says make local usable (research 7.3 to 7.5). | contract decision 4; local research 0 C5, C6, 7.3-7.5, 7.8, 8 Q10; architecture 6.2 row 1.5 | OD-37. |
| DC-38 | Medium | Defaults send the most sensitive class to the weakest AI: `restricted` is local only with min cert `works`; self-tested models cap at Experimental (model-certification 5.2); custom endpoints get low fingerprint confidence; a 16 GB laptop is a lite-coach machine. With no registry-certified local model, `restricted` is wizard-only; rules-engine 18.3 Q3 asks the owner to confirm this is intended. | catalog 4; model-certification 5.2; rules-engine 18.3 Q3; local research C7 | OD-36. |
| DC-39 | Medium | Smaller thesis leaks: lite mode (coach-spec 9) has the model extract the enum value from the user's answer (same issue as DC-03); the L1 JSON-action sketch (local research 7.5) includes a `suggest_tool` action letting the model name any catalog `toolId`, which conflicts with catalog invariant 3 and the contract ("recommend tools only by catalog ID from the engine"). | coach-spec 9; local research 7.5; catalog 6 invariant 3 | Lite and L1 extraction must go through the same confirmation and must not carry a tool id. |
| DC-40 | Medium | `generate_llm_justification_card`: model drafts, user clicks, the engine checks completeness only (CARD-1 to CARD-5). On Individual there is no second person, so LLM-first overrides are self-attested. | coach-spec 1.1 row llmJustification; rules-engine CARD; catalog `coach.llmOverride.*` | Label self-attested overrides in exports and audit. |
| DC-41 | Medium | LLM judge (rubric E) carries up to 10% of the run score (Style is 20% by default, half from the judge) and can move mean-run thresholds (Certified 88, Works 78); labels feed the `models.minCertification` gate and tool exposure. Two judge models from different providers are required; a full run costs an assumed 10 to 30 million input tokens per model and nobody is named to pay. | model-certification 3.1, 4.1, 4.3, 5.4, 8 Q1 | OD-34. |
| DC-42 | Medium | Seed catalog provenance: 20 of 29 entries carry `lastVerified` 2026-10-25 but no `sources`; rules-engine 18.2 says 24 of 29 carry VERIFY or ASSUMPTION notes and two cited Microsoft pages returned 404. A date stamp without a source reads as verification that did not happen, and these constraints feed engine verdicts. | tool-catalog.seed.json; rules-engine 18.2 | Drop `lastVerified` on unsourced entries or add sources. |
| DC-43 | Medium | Licensing and offline activation are thin: architecture 2.1 has "entitlements in token claims, license lapse behavior" only; whether sign-in is required for local or BYOK use is open (architecture 7.1 Q2) although the contract says local is free and architecture "Free paths" says BYOK and local do not depend on billing apart from org sign-in; D5 makes Individual a tenant of one. | architecture 2.1, 4.5, 7.1 Q2, D5 | OD-5. |
| DC-44 | Medium | No free tier or trial is decided. Research F3: nearly every comparator has a free tier or a free BYOK or local path. Tiers lists candidate pricing axes and asks whether Viewer is free (Q8). | competitive F3, 6 Q2; tiers 1, 9 Q8 | OD-4. |
| DC-45 | Medium | Accessibility is one phrase ("Plain, accessible UI", architecture 6.2 row 1.4): no standard, keyboard or screen-reader requirement, no portal accessibility, no VPAT intent. Localization: coach-spec lists multilingual replies as an ASSUMPTION for v1 and a locale addendum in the golden set; no catalog key, no locale policy, engine rationale strings are templates, currency is USD only. | architecture 6.2; coach-spec App B; model-certification 8; architecture 4.5 | OD-38. |
| DC-46 | Medium | AI-off and lite/wizard forcing have no policy key (coach-spec App B and model-certification 8 both assume that disabling all connection types leaves the wizard). The catalog has no key to force lite, though coach-spec 3 says "or user or admin chooses it". Per-class AI-off exists only indirectly (empty `llmConnectionTypes`, catalog 4). | coach-spec 3, App B; model-certification 8; catalog 4 | OD-23. |
| DC-47 | Medium | CMK timing: decision 8 requires "an Enterprise option for customer-managed keys"; tiers P2 item 2 and architecture 6.2 fast follows put CMK after launch, while architecture 6.3 says "CMK design in, enablement per customer" at v1, and Enterprise is sold sales-assisted at launch. | contract decision 8; tiers 8; architecture 6.2, 6.3 | OD-13. |
| DC-48 | Medium | model-certification 4.2: a "Works" model may have up to one S0 (critical) run and still receives approval-class tools that can write to AutoMate. That is a safety tolerance with an assumed threshold. | model-certification 4.2, 4.3 | OD-35. |
| DC-49 | Medium | Intake and Templates have no data model. tiers 7 lists Intake and Templates screens at launch; catalog has `governance.intake.*`; architecture 3.4 offers only `kind` (blueprint, template, intake) as an ASSUMPTION; the contract and `blueprint.schema.json` have no Blueprint-level `kind`; architecture 6.2 has no workstream for them; `governance.intake.gateStage` needs an intake-to-Blueprint link that does not exist. | tiers 7; catalog 3 Governance; architecture 3.4; blueprint.schema.json | OD-17, OD-27. |
| DC-50 | Medium | `rescue`, `second_opinion` and hybrid patterns exist only in one document each (coach-spec for the first two, rules-engine for patterns): not in the tier matrix, the catalog, or architecture. An org cannot disable them, tiers do not place them, and the second-opinion cross-model check sends a digest to a second connection with no stated link to `data.sensitivityRules`. | grep: rescue and second_opinion only in coach-spec and one model-certification line; hybrid only in rules-engine | OD-30. |
| DC-58 | Medium | AutoMate dependency is not scheduled as a risk to the launch promise. Decision 3 and the launch list make AutoMate write actions a launch requirement, but they sit last (architecture 6.2 row 4.1), depend on an AutoMate draft-import, diff and authenticated IPC surface nobody has confirmed (architecture R3, 7.1 Q6), and architecture 5.1 adds an AutoMate-side import setting as a second policy gate, which asks AutoMate for new capability that tiers 3.2 does not assume. | architecture 5.1, 6.2 row 4.1, 6.4 R3, 7.1 Q6; tiers 3.2; contract decision 3 | Get the AutoMate team's written answer before Phase 2; keep the file-based draft import as the stated fallback (architecture 6.4). OD-40. |
| DC-51 | Low | Installer and update channel is covered (architecture 5.4, 6.2 row 4.3, MSIX, staged rings, `tenant.minClientVersion`) but compatibility between the Coach adapter and AutoMate versions is not specified. | architecture 5.4, 6.2; catalog 5 | Add a compatibility matrix. |
| DC-52 | Low | Naming collisions: "restricted mode" (architecture 5.1 enrollment fallback) versus the `restricted` sensitivity class; catalog "Enforced: gateway" means any server component (sync, portal), not the model gateway. | architecture 5.1; catalog 1 | Rename. |
| DC-53 | Low | `policy.onExpiry = no_llm` (tiers 4.5 default) blocks `local` as well, though tiers 3.3 bypass 12 says local risk is quality, not leakage; `last_known_good` lets an org run on an expired policy indefinitely. Defensible, not acknowledged. | tiers 3.3, 4.5 | Note the trade in the admin copy. |
| DC-54 | Low | Contract decision 5 lists three probe items; model-certification has P1 to P6 and local research adds streaming, speed, thinking leak and identity. Scope growth with a consent and cost step (model-certification 2.3). | contract decision 5; model-certification 2.1, 2.3; local research 7.2 | Note as extension. |
| DC-55 | Low | The model may "raise" `sensitivity` (coach-spec 1.1). Conservative, but an injected or confused model can move a Blueprint to `restricted`, which silently stops sync (catalog 4). | coach-spec 1.1; catalog 4 | Show a visible notice and let the user undo. |
| DC-56 | Low | The model "may add one introductory sentence" around engine-rendered results (coach-spec 2.3, 9). Acceptable; keep the deterministic phrasing check (naming a rung or tool is rejected by the host). | coach-spec 2.3, 9 | None beyond keeping the check. |
| DC-57 | Low | Example policy (catalog 8) lets `restricted` use `custom_openai_compat` while the default matrix says `local` (an org example), and it was validated with a purpose-built minimal validator, not `jsonschema`. | catalog 4, 8 | Re-run with a real validator before release. |

## 3. Owner decisions 1 to 9: honoured or not

| # | Decision | Verdict | Deviations (file, section) | Ids |
|---|---|---|---|---|
| 1 | AutoMate: local-only, deterministic, no AI at runtime; Coach is design-time only | Honoured | None found. Evidence: catalog 6 invariant 4; model-certification 3.2 S1 (calling AutoMate AI-powered is a critical failure); seed `ui.automate` "no AI at runtime, cannot host an llm_node"; architecture 5.3 L7. Watch: architecture 5.1 asks AutoMate for an import-side policy gate (new work for AutoMate) and R3 depends on an AutoMate API nobody has confirmed. | DC-58 (watch only) |
| 2 | Standalone core library, AutoMate adapter first | Honoured | architecture D2 and the CI architecture test enforce it. Five-plus contract extension requests are unresolved. | DC-31 |
| 3 | Draft-only, diff, approve, attended test, step mapping, nothing runs without a click | Honoured, with caveats | Caveats: `restricted` handoff needs a record that cannot exist (architecture 5.3 L4); `apply_existing` on live flows needs steps that do not exist yet (`Step.asBuilt`); approval UI scheduled after its first use; the AutoMate-side API is unconfirmed. Catalog `automate.actions.allowedKinds` allows delete with its own click, which is consistent. | DC-04, DC-27, DC-32, DC-58 |
| 4 | Five connection types; gateway metadata only; BYOK key never leaves the client | Partly honoured | (a) `managed` economics and legality; (b) "metadata only" wording versus plaintext in transit and the P2 scan; (c) org key vault stores keys on our servers; (d) local list, licence and adapter gaps; (e) Azure and Anthropic compat layers are not plug-and-play. Honoured: BYOK direct from client, key in DPAPI and never in logs (architecture 2.1, 2.3; catalog 6 invariant 1), no usage fee on BYOK, no embedded inference (local research 7.8), `local` loopback only (catalog 6 invariant 5). | DC-01, DC-05, DC-09, DC-20, DC-28, DC-36, DC-37 |
| 5 | Certification labels from a golden set plus capability probe | Honoured with additions | 33 scenarios ("about 30"); probes P1 to P6; extras: separate Lite OK badge, LLM judge in scoring, fingerprint missing server version, adversarial suite versus OpenRouter terms, S0 tolerance, experimental gating conflict, unfunded run cost. | DC-10, DC-14, DC-28, DC-29, DC-41, DC-48, DC-54 |
| 6 | Tiers: Individual, Team, Enterprise | Honoured | Placement conflicts only (audit, approvals, sensitivity rules, baseline, P2 settings, CMK, spend, free tier). | DC-15 to DC-19, DC-20, DC-44, DC-47 |
| 7 | Three setting states, signed bundle, offline grace, server-side for managed, client-side for the rest (documented honestly), admins can disable personal keys, environment profile | Partly honoured | Honest enforcement matrices exist (tiers 3, architecture 5.1). Open: signing algorithm, machine enrollment, Individual baseline, thin scope, server-engine timing, personal-key disabling is soft without enrollment, `no_llm` and `last_known_good` trade-offs. | DC-06, DC-07, DC-08, DC-18, DC-25, DC-53 |
| 8 | Full backup required, not metadata-only; encryption, tenant isolation, retention, export, DPA, Enterprise CMK; transcripts local by default | Weakened | `restricted` no sync; sync lockable; CMK after launch; backup window versus deletion wording. Honoured: envelope encryption (architecture 3.5), tenant isolation (3.8), retention, deletion and export (3.7), restore drills (3.9), DPA and sub-processors (5.5), transcripts local (`retention.transcripts.storage` local; admins cannot force transcript sync, catalog 6 invariant 6). | DC-02, DC-04, DC-24, DC-47 |
| 9 | Roles: Admin, CoE Reviewer, Builder, Viewer | Honoured | Role powers conflict (CoE Reviewer authoring, who sets `approved`, Admin content read, Viewer free). | DC-13, DC-21, DC-22 |

## 4. The seven known tensions: confirmed or refuted

| Tension | Verdict | Evidence | Ids |
|---|---|---|---|
| `restricted` defaults to local-only versus the owner's required full backup | Confirmed, and worse than stated | Catalog 4 sets cloud sync NO and export NO for `restricted`; `sync.blueprints.enabled` is lockable; `restricted` also requires approval before handoff with no server record; the matrix is itself marked ASSUMPTION. | DC-02, DC-04 |
| "Metadata only" versus the gateway seeing prompts | Confirmed as a wording problem; persistence is metadata-only by design | Architecture 2.3 rule 1 (typed `RequestMeta` allowlist, CI canary greps every sink) keeps storage clean, but 2.2 shows plaintext in gateway memory, and tiers 8 P2 plans a scan. | DC-05 |
| Managed credits versus OpenRouter ToS section 7 as a gate | Confirmed, and it gates launch | Research C1 and R1; architecture 6.2 row 0.1 and R2 make it a gate but the coverage table and tiers 3.3 still treat `managed` as delivered. Architecture V1 to V8 are stale. | DC-01, DC-36 |
| "Thin" launch admin scope versus a large portal | Confirmed | tiers 8 (16 screens, no bespoke widgets) versus architecture C10, D12, 6.2 row 2.4 (L, server-side engine, review view). | DC-06, DC-49 |
| Signing algorithm and key-registry enrollment | Confirmed | tiers 4.1 EdDSA; architecture C5 EdDSA or ES256, undecided (V18); tiers 4.3 enrollment later; architecture C6 at launch; Individual baseline "None" versus signed. | DC-07, DC-08, DC-18 |
| Enterprise org-key vault puts provider keys on our servers | Confirmed | tiers 5 (envelope-encrypted, modes A, B, C), architecture C7 and 2.1 ("named exception"), catalog `tenant.vault.enabled`. Personal BYOK keys stay device-only. | DC-09 |
| Experimental-model tool gating (coach-spec versus architecture L3) | Confirmed; coach-spec deliberately refines L3 and architecture was not updated | architecture 5.3 L3 and T1 versus coach-spec 3 item 4, App B, coach-tools.json `x-labelExposure`. | DC-10 |

## 5. Contradictions between documents, by topic

### 5.1 Feature-to-tier placement

| Feature | tiers.md | Catalog (min tier) | architecture.md | Ids |
|---|---|---|---|---|
| Audit-log retention, Team | 90 days (ASSUMPTION) | default 365, Team cap 365 | default 365, Enterprise up to 3650 | DC-15 |
| Approval records before apply | Enterprise (1 matrix) | Team (`governance.approval.*`) | "approval records" server-side, tier not stated | DC-16 |
| Sensitivity rules editing | Individual can edit defaults | Team (`data.sensitivityRules`, `data.minimumSensitivity`) | not stated | DC-17 |
| Individual policy baseline | "None, built-in" (1) and signed (4.3) | not stated | signed (D5) | DC-18 |
| Multi-reviewer approval, review SLA | P2 (8) | `minReviewers` up to 3, `reviewSlaDays` at Team or Enterprise | not stated | DC-19 |
| SSO | Team: Microsoft or Google sign-in; Enterprise custom OIDC and SAML in P2; Q5 asks if OIDC moves up | `tenant.sso.provider` Team (OIDC social) and Enterprise | custom OIDC and SAML at launch "where cheap" | DC-06, DC-19 |
| Customer-managed keys | Enterprise add-on, P2 | `tenant.cmk` Enterprise add-on | "design in, enablement per customer" (6.3) and fast follow (6.2) | DC-47 |
| Spend | "Pay as used" | `spend.*` caps | prepaid wallet | DC-20 |
| Intake and Templates | Launch (7) | `governance.intake.*` Team | no workstream, `kind` ASSUMPTION | DC-49 |
| Rescue, second opinion, hybrid patterns | not placed | no keys | not mentioned | DC-50 |

### 5.2 Enforcement claims by connection type

tiers.md 3.2 and architecture 5.1 agree on the main levels: managed is hard for type switching, model lists, caps, class routing (on the declared class, which the gateway cannot verify) and policy freshness; direct and local connections are soft; usage visibility for direct and local is client-reported and unverified. Disagreements and gaps:

| Control | Claim A | Claim B | Verdict | Ids |
|---|---|---|---|---|
| Machine-level enforcement | tiers 4.3: later | architecture 5.1: minimal registry enrollment at launch | conflict | DC-08 |
| AutoMate action modes | tiers 3.2: soft, local adapter | architecture 5.1: soft plus an AutoMate-side import setting as a second gate (ASSUMPTION) | architecture asks AutoMate for new capability | DC-58 |
| Org rules at approval time | tiers 3.2: server re-evaluates any synced Blueprint | architecture C11: at status transitions | timing differs | DC-25 |
| Zero-retention routing, managed | tiers 3.2: hard (VERIFY flags) | catalog default off; research recommends always deny | default mismatch | DC-35 |
| Certification floor, managed | tiers 3.2: gateway holds the table | architecture: signed manifest in content feed | artifact differs | DC-29 |
| Redaction before send | tiers 3.2: soft now, hard via later scan | architecture C1: no content inspection at v1 | agree, but both conflict with contract wording | DC-05 |
| Personal keys disabled | decision 7: "Admins can disable personal keys" | tiers 3.2 and architecture 5.1: soft; hard only with enrollment | honest, but depends on DC-08 | DC-08 |
| Approvals for local-only or `restricted` Blueprints | tiers 3.2: "outside this" | catalog 4: `restricted` needs approval before handoff | unsatisfiable | DC-04 |
| Usage visibility | tiers 8: no org-forced identified telemetry | catalog: `clientReportedUsage` admin-lockable and identified | wording | DC-23 |
| Expiry behaviour on `local` | tiers 3.3 bypass 12: local risk is quality | tiers 4.5: `no_llm` blocks local too | internal tension | DC-53 |

### 5.3 Approval and confirmation flow

Three mechanisms share the word "approval": (1) click approval of an action by a single-use token (coach-spec 1 rule 3, coach-tools `x-approvalProtocol`, architecture L4); (2) governance approval of a Blueprint by a reviewer with a server-signed record (catalog `governance.approval.*`, tiers 3.2, architecture S4); (3) override approval (`coach.llmOverride.mode`, `coach.override.mode`, `coach.triageOverride.mode`, `approval_required`). Consistent parts: token binding, expiry, taint step-up, typed-turn requirement. Contradictions: who may set `approved` (DC-21); how an override awaiting reviewer approval is stored (DC-27); approval UI scheduled after its first use (DC-27); a `restricted` record that cannot exist (DC-04); `coe_review_required` on Individual (DC-22); coach-spec lists `export` as an approved action while the catalog gates export by class and `data.exports.allowedKinds` rather than by token, so the two controls overlap without a stated order.

### 5.4 Build order and launch scope

| Item | tiers.md 8 | architecture.md 6.2 | Verdict | Ids |
|---|---|---|---|---|
| Admin surface | thin, 16 screens, schema-generated | portal L, server engine, review view | conflict | DC-06 |
| Intake, Templates, Environment profile form, org-rule templates | Launch | not a workstream | gap | DC-06, DC-49 |
| Certification labels and probe | Launch | Phase 4.2, after connections and orchestrator | inversion | DC-26 |
| `managed` | Launch | Phase 3, behind the OpenRouter gate 0.1 | gate vs promise | DC-01 |
| AutoMate write actions | Launch | Phase 4.1, last, behind R3 and an AutoMate API | risk concentrated at the end | DC-58 |
| Machine enrollment | P2 | Phase 2.2 | conflict | DC-08 |
| Local models | covered by `connections.local.enabled`, labels, probe | 1.5 sized M | under-scoped | DC-37 |
| CMK | P2 | design in at v1, fast follow | ambiguous | DC-47 |
| Multi-reviewer, SLA | P2 | not stated | catalog ahead of plan | DC-19 |
| Licensing and offline activation | not stated | one table row | gap | DC-43 |

### 5.5 Who can read Blueprint content

| Source | Statement |
|---|---|
| contract decision 9 | Roles named; no read rules |
| tiers 2 | ASSUMPTION: Admin and CoE Reviewer can read synced content; Q3 asks whether by default |
| tiers 7 | Blueprint inventory: "Read access follows the role rules" |
| architecture 2.1 | Owner, shares, CoE Reviewer once `in_review`, "Admin per policy"; projection visible to Admin and CoE Reviewer (title, summary, ROI, people encrypted columns) |
| architecture 3.4 | "Admin reads any synced blueprint (a tiers.md ASSUMPTION that is also its open question 3)"; every non-owner read audited |
| architecture T11 | "blueprints private until `in_review`" |
| catalog | no key |
| coach-spec App B | CoE Reviewer read-only inside Coach (assumed) |

Verdict: DC-13. The projection alone gives Admin the title, summary, ROI and people of every synced Blueprint.

### 5.6 Telemetry defaults

Consistent: crash reports and analytics off (catalog `telemetry.*`, architecture 2.1 and 6.3 "opt-in, content-free", tiers Q4 open, listed as ASSUMPTION "until the owner decides"). Inconsistent: the extra channels in DC-23. Also model-certification 5.3 and its own open Q2 ask whether rejection-code telemetry is permitted at all.

### 5.7 Retention

| Item | tiers | Catalog | Architecture | Verdict |
|---|---|---|---|---|
| Audit log | Team 90, Enterprise up to 10 years | 365 default, up to 3650 | 365, Enterprise up to 3650 | DC-15 |
| Transcripts | local only | 90 days local | 90 | agree |
| Versions kept | not stated | 50 | 50 | agree |
| Deleted grace | not stated | 30 days "from storage and backups" | 30 days; backups age out in 35 days (ASSUMPTION) | DC-24 |
| Gateway metadata | not stated | 400 days, minimum 90 | 400; ledger 7 years (ASSUMPTION) | agree, different clocks |
| Telemetry | not stated | not stated | 90 days (ASSUMPTION) | single source |
| Exports | not stated | not stated | 24 hours | single source |
| Legal hold | P2 | `tenant.legalHold` listed | P2 | agree |

### 5.8 Server-side versus client-side enforcement claims

Beyond 5.2: the catalog "Enforced" column says `gateway` for retention and approval settings, which really means the sync and portal services; `both` settings (`coach.llmOverride.mode`, approvals) are server-checked only for synced Blueprints, so a local-only Blueprint escapes them (tiers 3.3 bypass 8, stated honestly); the contract says "Enforcement is server-side for `managed`; client-side for direct and local" but approval and retention are server-side for every connection type that syncs, so the contract sentence is about model access only and should say so (amendment A7).

## 6. Thesis check: "no LLM in the recommendation path"

Clean paths (checked): verdict, rung, ROI math and policy gates are engine outputs (coach-spec 1.1: `triage.verdict`, `step.recommendation`, `roi{}` model-never); approval tokens are minted by a trusted click and the schema has no token field (architecture L4, coach-tools G1, G8); org rules and redaction are deterministic; the injection scanner and digest renderer are deterministic (coach-spec 7.5, 8.3); the second-opinion critic's claims are adjudicated by the engine and marked "disputed", never applied (coach-spec 12); rescue hypotheses are labelled separately from engine findings (coach-spec 11).

Places where a model, prompt or judge can influence an outcome:

| # | Point | Mechanism | Guard | Residual | Id |
|---|---|---|---|---|---|
| T-1 | `step.diagnostic` | model writes enum values via `record_diagnostic_answers` | quote must be a typed-turn substring; attractor check; engine validates | no check that value matches quote; no user confirmation; 7.4 overclaims | DC-03 |
| T-2 | `operations` tags | model proposes, user confirms the step | engine rejects unknown tags | tags drive rung selection and users cannot read them | DC-11 |
| T-3 | lite mode extraction | model extracts the answer into a tiny enum | host rejects phrasing that names a rung or tool | same as T-1 | DC-39 |
| T-4 | L1 JSON-action `suggest_tool` | model names a catalog toolId | enum of catalog ids | model-originated tool suggestion; conflicts with invariant 3 | DC-39 |
| T-5 | LLM justification card | model drafts, user clicks | engine checks completeness (CARD-1 to 5) | content is model prose; self-attested on Individual | DC-40 |
| T-6 | `sensitivity` raise | model may raise | raise-only; rules may raise | forces `restricted`, which stops sync | DC-55 |
| T-7 | step structure (names, actors, inputs) | model proposes, user confirms | proposed steps ignored until confirmed | user confirms wording, engine consumes fields | DC-03 |
| T-8 | certification labels | LLM judge up to 10% of score | never affects S0 or S1; two judges | can move label thresholds that gate tool exposure and `models.minCertification` | DC-41 |
| T-9 | ROI and TR-3 | no LLM, invented constants | rules pack versioned | verdict depends on placeholder numbers | DC-12 |
| T-10 | result presentation | model adds one introductory sentence | host phrase check | cosmetic | DC-56 |
| T-11 | approval-class tool calls after a paste | typed turn after a paste counts as typed | host-rendered card, taint step-up | open Q5 in coach-spec App B | DC-27 note |

## 7. Unsourced claims register (all tagged VERIFY)

"Status" says what the source document does today. Items already tagged ASSUMPTION or VERIFY in their source are listed because the contract rule says a price, fee, limit or policy must never be a fact without a cited source, and each should be upgraded to VERIFY before it reaches any customer or counsel.

| # | Claim | Where | Status in source | Tag |
|---|---|---|---|---|
| V-01 | OpenRouter 5.5% credit-purchase fee ($0.80 minimum), credits expire in 365 days, refundable only within 24 hours | openrouter research | sourced (S-list, 2026-10-25); Enterprise terms may differ | VERIFY |
| V-02 | Recommended transaction fee 20%, $10 minimum top-up, Enterprise 10 to 12% | openrouter research | recommendation, no market evidence | VERIFY |
| V-03 | OpenRouter ToS section 7 (resale), section 5.1 carve-out, Red Teaming clause | openrouter research C1, R5 | legal reading by a non-lawyer | VERIFY (counsel) |
| V-04 | Stripe acquiring OpenRouter (2026-08-19, not closed); Stripe-Metronome status | openrouter research | news, secondary caveats R14, R15 | VERIFY |
| V-05 | Per-key limits, guardrails, `/generation` endpoint, in-flight budget behaviour | openrouter research | partly flagged VERIFY | VERIFY |
| V-06 | Prepaid wallet legal treatment (stored value), tax handling, merchant of record, PCI scope with hosted checkout | openrouter research R10; architecture V9, V17 | open | VERIFY (counsel) |
| V-07 | Competitor prices and limits (Cursor, GitHub Copilot, Zapier, n8n, Appian, Make, Copilot Studio rates, Claude Code limits) | competitive 3, 4, S-list | mostly secondary or search-level | VERIFY |
| V-08 | Failure statistics (Gartner agentic cancellations, MIT, S&P, Stanford, McKinsey, Forrester) | competitive 1 item 3 | flagged "easy to misquote"; originals blocked to fetch (6 Q5) | VERIFY |
| V-09 | Absence claims ("no product does tool-agnostic per-step advice") | competitive 1 item 2 | search-based | VERIFY |
| V-10 | BFCL V4 leaderboard numbers; vendor-reported model numbers; xLAM non-commercial licence | local research 3 | leaderboard only, paper page blocked; vendor numbers self-reported | VERIFY |
| V-11 | Speed, memory and hardware tier thresholds, readiness-check pass marks | local research 4, 7.4 | ASSUMPTION; community-reported | VERIFY |
| V-12 | Ollama default 4k context, `num_ctx` ignored by OpenAI endpoint, issue #14493 status, LM Studio and Ollama silent-install flags | local research 2, 8 | partly third-party | VERIFY |
| V-13 | Bedrock short-term keys up to 12 h, Vertex token about 1 h, Azure key-auth and Entra scope, Foundry Local tool and schema support | local research 7.3, 8 | partly flagged | VERIFY |
| V-14 | LM Studio terms on recommending and enterprise use; model licence for each recommended weight set | local research 8 Q10 | open | VERIFY (counsel) |
| V-15 | Provider zero-retention and data-collection flags exist and behave as assumed; provider-side spend-limited keys exist | tiers 3.2; catalog; architecture V2 | ASSUMPTION or VERIFY | VERIFY |
| V-16 | GDPR roles (processor and controller), 72-hour breach notice, EU AI Act dates, EU-US transfer mechanism, SOC 2 timelines and cost, cyber-insurance | architecture 5.5, V15 to V17 | ASSUMPTION or VERIFY, "counsel to confirm" | VERIFY (counsel) |
| V-17 | Ed25519 support in the chosen KMS or HSM and .NET; WinUI and .NET LTS; SmartScreen reputation; cloud KMS cross-tenant CMK mechanics | architecture V10, V13, V18; tiers 4.2 | open | VERIFY |
| V-18 | Architecture numbers: RPO and RTO, SLOs, 35-day backup window, 7-year ledger retention, 15-minute access token, drift under 0.1%, 20 injection payloads | architecture 2.1, 3.7, 6.4, 7.3 | ASSUMPTION | VERIFY |
| V-19 | Catalog numbers: retention 90 / 50 / 30 / 365 / 400, 25 changes per diff, 256 KiB bundle limit, 14-day grace, default sensitivity matrix | catalog | ASSUMPTION | VERIFY |
| V-20 | tiers numbers: 4-hour refresh, 12-month key rotation, about 20 active rules and up to 200, Team 90-day audit | tiers | ASSUMPTION | VERIFY |
| V-21 | Rules-engine constants (ROI hours, 0.5 share, 0.3 overhead, 0.10 residual, payback 1.0 and 2.0, graduation 200 runs and 30 days, 0.90 coverage, 0.98 agreement) | rules-engine 11.3, 13, 18.1 | ASSUMPTION | VERIFY |
| V-22 | Certification thresholds (Certified 88, Works 78), judge weighting, 10 to 30 million tokens per run, 90 and 180-day staleness | model-certification 4, 5.4, 8 | ASSUMPTION | VERIFY |
| V-23 | Seed catalog tool constraints for 20 unsourced entries carrying `lastVerified`: likely candidates `builtin.excel_power_query`, `builtin.outlook_rules`, `api.power_automate_cloud_flow`, `api.rest_http_request`, `api.third_party_ipaas`, `script.python`, `script.sql`, `ui.playwright_browser`, `parser.regex_template`, `ocr.tesseract_local`, `ml.trained_text_classifier`, `llm.*`, `agent.bounded_llm_agent`, `human.*` (exact list to be confirmed by the data-contract agent) | tool-catalog.seed.json | dated but unsourced | VERIFY |
| V-24 | Microsoft documentation pages for Power Automate HTTP connector and Outlook rules returned HTTP 404; licence tiers and rule actions unknown | rules-engine 18.2 | flagged | VERIFY |
| V-25 | Copilot+ baseline (40+ TOPS NPU, 16 GB RAM, 256 GB) | local research C8 | sourced [S20] | VERIFY |

## 8. Coverage gaps

| Topic | Status | Where it lives | Gap |
|---|---|---|---|
| "Rescue my failed automation" | Partial | coach-spec 11 (question bank Q-RSC-01 onward, engine finding versus hypothesis) | Q-RSC-08 verdict mapping; `Step.asBuilt` extension; no tier placement or policy key; not in architecture or catalog (DC-32, DC-50) |
| Hybrid pattern library | Partial | rules-engine 14 (five patterns) | Nothing in coach-spec, tiers, catalog or architecture; users cannot learn or disable patterns (DC-50) |
| LLM-to-code graduation | Specified in engine only | rules-engine 13 (GR-1 to GR-5) | No data source, no run-stats ingestion, no content-handling rule for confidential or restricted, no tool or stage (DC-33) |
| Second-opinion critique | Partial | coach-spec 12, model-certification (one line) | No tier, key or architecture; cross-model digest path not tied to sensitivity rules (DC-50) |
| ROI tracking | Estimate only | rules-engine 11, `reviewAfterDays` | No actual-versus-predicted capture (DC-34) |
| Intake and approval queue | Partial | catalog `governance.intake.*`, `governance.approval.*`; tiers 7 screens | Intake and Templates have no data model or workstream; override-pending state undefined (DC-27, DC-49) |
| Backup restore | Covered | architecture 3.9 (quarterly restore drills, blank-device restore in R1 exit criteria) | Customer-facing restore flow and `restricted` local-only restore not described |
| AI-off mode | Partial | architecture D11 (no-model mode), coach-spec 10 (wizard), tiers 4.5 (`no_llm`) | No policy key to force AI-off, lite or wizard (DC-46) |
| Free tier | Missing | competitive F3, Q2 | Contract silent; no decision (DC-44) |
| Licensing and offline activation | Thin | architecture 2.1 one row, Q2 | Activation, device limits (architecture Q10), offline entitlement not designed (DC-43) |
| Installer and update channel (standalone app) | Covered | architecture 5.4, 6.2 row 4.3 (MSIX, staged rings, signed release manifest) | Adapter-to-AutoMate version compatibility (DC-51) |
| Accessibility | Missing | one phrase in architecture 6.2 | No standard or testing target (DC-45) |
| Localization | Missing | coach-spec App B (multilingual replies ASSUMPTION), model-certification locale addendum | No policy key, UI locale, currency, date or units rule (DC-45) |

## 9. OWNER DECISIONS (deduplicated, numbered)

Merged from: contract-level findings above; tiers.md Q1 to Q8; architecture.md 7.1 Q1 to Q10 and C2, C5, C6, C7; coach-spec.md App B Q1 to Q5; model-certification.md Q1 to Q7; rules-engine.md 18.3 Q1 to Q10; competitive-landscape.md Q1 to Q7; local research 8. Each line gives options, then a recommended default.

Commercial and legal
1. **Managed go/no-go.** Options: written OpenRouter approval first; direct provider contracts; launch BYOK and local only. Default: written approval is a ship gate, BYOK and local launch first, managed behind a flag until the letter arrives. (DC-01; competitive Q1)
2. **Is full backup a guarantee or a capability?** Options: guarantee for every class; capability with `restricted` local by default and admin opt-in; capability an admin may switch off per class. Default: capability, `restricted` local by default with a visible "Local only, not backed up" state and a one-click opt-in. (DC-02; tiers Q1; architecture Q1)
3. **Managed pricing mechanics.** Options: percentage on reported cost; flat per request; pass-through of upstream purchase fees; subscription credit allowance or none. Default: research numbers (20% on reported cost, $10 minimum top-up) after counsel reviews stored value; wallet expiry no longer than 365 days; unused balance refundable on request. (DC-20, DC-36; architecture Q3, Q4)
4. **Free tier or trial.** Options: none; permanent free no-model wizard; time-limited trial; free BYOK and local with capped backup. Default: 14-day trial of the full Individual plan plus a permanent free no-model wizard and export, no free managed credits. (DC-44; competitive Q2; tiers Q8)
5. **Sign-in and offline activation.** Options: no account for local, BYOK and no-model use; account always; account for sync and managed only. Default: no account for local, BYOK and no-model; account for sync, managed and orgs; signed offline entitlement token with a 30-day grace. (DC-43; architecture Q2)

Data and trust
6. **Gateway privacy wording and the P2 scan.** Options: amend to "does not store"; keep "metadata only" and drop the scan. Default: amend wording, keep the scan as a P2 owner-approved exception with counts-only persistence. (DC-05)
7. **Admin read access to Blueprint content.** Options: metadata only until shared or in review; Admin reads all; policy toggle. Default: metadata only, with a locked-only toggle and audited break-glass. (DC-13; tiers Q3; architecture Q9)
8. **Org key vault exception.** Options: reject; scoped sub-key mode A only; modes A, B, C. Default: mode A only, P2, after a security-analyst review. (DC-09)
9. **Telemetry.** Options: off everywhere; admin-lockable opt-in; default on for Team. Default: off everywhere; classify client-reported usage as audit data and say so; drop certification rejection-count upload unless the user opts in. (DC-23; tiers Q4; model-certification Q2)
10. **Managed privacy routing default.** Options: deny data collection on every request; only for confidential and restricted. Default: every managed request. (DC-35)
11. **Team audit retention.** Options: 90; 365. Default: 365. (DC-15)
12. **Backup window and erasure wording.** Default: state the 35-day backup window in the DPA and fix the catalog sentence. (DC-24)
13. **Customer-managed keys at launch.** Options: P2; launch blocker. Default: P2, and do not sign Enterprise contracts requiring CMK before it ships; fix architecture 6.3 wording. (DC-47; architecture Q8)
14. **Regions and residency.** Options: one US region; US plus EU. Default: one region at launch, field present. (tiers Q6; architecture Q5)

Policy and admin
15. **Policy signing algorithm.** Options: EdDSA; ES256. Default: ES256 unless Ed25519 support is verified in the chosen KMS and .NET. (DC-07)
16. **Machine enrollment at launch.** Options: registry key at launch; later with ADMX. Default: minimal registry enrollment at launch. (DC-08)
17. **Individual baseline bundle.** Options: signed; none. Default: signed, one code path. (DC-18; tiers Q2)
18. **Launch admin scope.** Options: all 16 screens (portal L); cut Intake, Templates and the org-rule editor to P2. Default: cut those three to P2, keep the review queue. (DC-06, DC-49)
19. **Approval features by tier.** Options: as the catalog; as tiers.md. Default: approval records and one reviewer at Team; multi-reviewer and review SLA at Enterprise and hidden until built. (DC-16, DC-19)
20. **Sensitivity rules editing on Individual.** Default: no; fix the tiers matrix wording. (DC-17)
21. **CoE Reviewer powers and who sets `approved`.** Options: critique only; Builder plus review. Default: Builder plus review, may not approve own Blueprints, only CoE Reviewer sets `approved`. (DC-21; coach-spec Q2)
22. **Individual review path and `coe_review_required`.** Options: advisory; self-attestation recorded; block. Default: advisory with a recorded self-attestation. (DC-22)
23. **`restricted` approval before handoff.** Options: sync approval metadata only; local attestation; block handoff. Default: sync approval metadata only (hash, status, signer). (DC-04)
24. **AI-off and mode forcing keys.** Default: add a locked-able `coach.aiMode` (off, lite_only, full) and a per-mode allow list for rescue and second opinion. (DC-46, DC-50; model-certification Q7)

Engine and thesis
25. **Confirmation of diagnostics and operations tags.** Options: confirm each value; confirm on summary; none. Default: confirm each value with a chip before the engine consumes it, including lite mode. (DC-03, DC-11, DC-39)
26. **ROI constants.** Options: ship as placeholders; calibrate from pilots; admin-tunable. Default: TR-3 advisory until calibrated by the owner from design-partner data; show constants in the trace. (DC-12; rules-engine Q4, Q8)
27. **Ladder order of `human_checkpoint` and `llm_agent`.** Default: contract order, `human_checkpoint` before `llm_agent`. (DC-30; rules-engine Q10)
28. **Contract v2 extensions.** Options: approve in one batch; case by case. Default: one batch (Connection fields, Step provenance, confirmation and asBuilt, deployPlan, tests[], Blueprint `kind`, `operations`, `interfaceAvailability` none). (DC-31, DC-49; rules-engine Q9)
29. **Graduation in v1.** Options: engine advice only; AutoMate run-stats ingestion; defer. Default: defer to v1.x, keep the rule spec, collect no content. (DC-33; rules-engine Q5)
30. **ROI tracking.** Options: none; manual entry at `reviewAfterDays`; automatic from run stats. Default: manual entry at the review date. (DC-34)
31. **Rescue and second opinion availability.** Default: all tiers; catalog keys per mode; the cross-model check obeys `data.sensitivityRules`. (DC-32, DC-50)
32. **Preferred tools and other engine questions.** Options: add `preferredToolIds` to the environment profile; frequency-aware human rung; `llm_agent` visible at launch. Default: add `preferredToolIds`, leave frequency out, keep `llm_agent` discouraged but reachable. (rules-engine Q1, Q2, Q6, Q7)

Models and certification
33. **Experimental-model tool exposure.** Options: coach-spec version; read-only (architecture L3). Default: coach-spec version; update architecture. (DC-10)
34. **Fingerprint and compat-layer cap.** Default: include server kind, server version, quantization; cap Claude through OpenAI-compatible layer at Works. (DC-28; model-certification Q3, Q5)
35. **Who runs and pays certification, and where adversarial tests run.** Default: a funded budget with a separate OpenRouter account and local models for adversarial suites; written approval before any red-team traffic. (DC-14, DC-41; model-certification Q1; coach-spec Q3)
36. **Judge weight and S0 tolerance.** Default: judge advisory only; zero S0 runs for any model exposed to approval-class tools. (DC-41, DC-48; model-certification Q4)
37. **`restricted` default model floor.** Options: min cert Works; allow an admin-approved local model to count as Works. Default: allow admin-approved local models; wizard fallback otherwise. (DC-38; rules-engine Q3)
38. **Local servers and adapters at launch.** Default: Ollama, LM Studio (do not bundle, counsel review), Foundry Local (labelled preview), llama.cpp; native Anthropic adapter in v1.1; `byok_provider` list limited to those with acceptable OpenAI-compatible endpoints. (DC-37; architecture Q7; local research 8)

Quality and scope
39. **Accessibility and localization targets.** Default: WCAG 2.2 AA with keyboard and screen-reader support for the shell and portal; English UI in v1 with locale-safe strings; model replies in the user's language as best effort. (DC-45; coach-spec V10)
40. **Cloud, device limit and AutoMate ownership.** Options: Azure with AWS KMS CMK later; device cap per user; AutoMate team owns draft-import, diff and IPC. Default: Azure, three devices per user, AutoMate team owns the adapter API with a file-based draft import as fallback. (architecture Q6, Q8, Q10)
41. **First paying buyer and competitor naming.** Default: CoE lead first; do not name competitors on the site. (competitive Q3, Q7)

## 10. Proposed contract v2 decision amendments

Decision-level text only, in the contract's style.

- **A1 (decision 4, managed).** `managed` is generally available only after written permission from the upstream aggregator, or an equivalent direct provider agreement, is on file. Until then it ships behind a flag; BYOK and local are unaffected.
- **A2 (decision 4, gateway).** The gateway **does not store** prompts or completions; it persists metadata only (user, model, tokens, cost, time). Prompts transit gateway memory, the upstream aggregator and the model provider. Customer and legal copy say "not stored by us", never "we never see it". Any future in-transit scan may read content in memory and must persist counts only.
- **A3 (decision 4, keys).** Personal BYOK keys never leave the device. An Enterprise org key vault may hold organization-provisioned credentials server-side, envelope-encrypted, preferring scoped sub-keys; this is the only exception.
- **A4 (decision 4, local).** `local` covers loopback OpenAI-compatible servers (Ollama, LM Studio, Foundry Local, llama.cpp). Servers are never bundled. Azure OpenAI, LiteLLM, vLLM and corporate gateways are `custom_openai_compat` with a server profile.
- **A5 (decision 5, certification).** A label belongs to a (model, server kind, server version, quantization) fingerprint. Models reached through a degraded compatibility layer cap at Works. Deterministic metrics decide labels; any LLM judge is advisory. Adversarial suites never run on the production gateway account.
- **A6 (decision 7, honesty).** Machine-level enrollment (registry key) ships at launch so "disable personal keys" and "org policy required" have a hard path on managed devices. Policy bundles are signed with ES256 unless Ed25519 support is verified. Individual runs on a signed baseline bundle.
- **A7 (decision 7, enforcement).** Enforcement of model access is server-side for `managed` and client-side otherwise; enforcement of approvals, retention and sharing is server-side for every Blueprint that syncs. Local-only Blueprints sit outside server enforcement and the product says so.
- **A8 (decision 8, backup).** Full backup of Blueprints is a capability for every sensitivity class. `restricted` Blueprints stay on the device by default and show "Local only, not backed up"; an admin or the owner may opt in. Approval metadata (hash, status, signer) may sync for any class. A customer-managed key is an Enterprise add-on delivered after launch.
- **A9 (decision 9, roles).** Admin sees Blueprint metadata and audited break-glass content access; content is readable by the owner, explicit shares and CoE Reviewers once a Blueprint is in review. Only a CoE Reviewer may set `approved`, and never on their own Blueprint.
- **A10 (thesis).** The model may write structured step data only as a proposal the user confirms value by value; the engine consumes nothing the user has not confirmed. No LLM output, including an LLM judge, can change a verdict, rung, ROI figure, policy gate or approval.
- **A11 (entities).** The contract entities gain the extensions in contract v2: Connection server profile fields, Step provenance, confirmation and asBuilt, Blueprint kind and deployPlan, tests[] fields and the `operations` tags.

## 11. Open items I could not settle

- Exact list of the 20 unsourced seed-catalog entries (V-23); the data-contract agent holds that.
- Whether rules-engine sections I read only by heading (the 36-tag table, hybrid patterns 14, graduation 13.2) contain further conflicts with coach-tools.json; the absence of `operations` there is confirmed.
- Whether coach-tools.json defines a tool equivalent to the L1 `suggest_tool` action; I found none, so DC-39 concerns the research sketch only.
- I did not verify policy.schema.json against the catalog key by key; that belongs to the data-contract review.
