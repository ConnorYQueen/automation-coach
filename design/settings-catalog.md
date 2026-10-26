# Settings catalog

Status: design v2, 2026-10-25 (patch round against `design/00-shared-contract.md` v2 and the findings in `design/99a-data-contract-review.md` and `design/99b-decision-consistency-review.md`). Source of truth for every admin and user setting. The key set, types, defaults, admin-lock rules, minimum tier, phase, tier limits and enforcement point in the tables below are generated from the same table as `design/policy.schema.json` (`x-group`, `x-minTier`, `x-enforcedAt`, `x-adminLock`, `x-default`, `x-phase`, `x-tierBounds` annotations), so the two cannot drift. The Connection entity has its own file, `design/connection.schema.json`; the `connections.orgConnections` setting and that file are generated from one builder. Contract entities (`Policy`, `Connection`, `Blueprint`, `Step`, `ToolCatalogEntry`) are used exactly as named in the contract. Round 3 (owner rulings R1 to R9, `design/00-shared-contract.md` section 10) is applied: Individual Free versus Paid, the break-glass time box, approval gates for handoff and AutoMate drafts, SSO deferred, managed pricing deferred. Anything not confirmed from a source is marked `ASSUMPTION:` or `VERIFY:`; deferred pricing mechanics are marked `DEFERRED (R9)`.

Totals: 94 bundle settings in 8 groups. 83 are built at launch and 11 are P2 (in the schema, hidden in the portal, inert in the client until their feature ships). By minimum tier: 43 from Individual (39 apply to Free and Paid, 4 only to Individual Paid), 50 from Team, 1 from Enterprise. Plus 24 tenant-only rows (section 5) that never reach a client.

## 1. How to read this catalog

| Column | Meaning |
|---|---|
| Key | Dotted camelCase key. In the bundle it is `settings["<key>"] = {state, value?}`. |
| Type / Default | JSON type of `value` and the catalog default that applies when the key is absent or `user_choice`. Lists: `null` = unrestricted, `[]` = nothing permitted (allow lists) or nothing denied (deny lists). |
| Admin lock | **Yes** = admin may set any of the three states. **Default only** = admin may seed a default but never lock (personal preferences, accessibility). **Locked only** = org-wide fact enforced on a server or a rule with no user control, so the only valid state is `locked`. |
| Min tier | Lowest tier at which the setting exists. Individual means Free and Paid. **Individual (Paid)** means the setting needs Individual Paid or above, because it belongs to sync, backup, restore, version history, devices or `managed` (ruling R1); the schema carries `x-minPlan` = `individual` for it. Plan is an entitlement fact (token claim `plan`), checked by the client and the servers, not by the publish check, since a Team or Enterprise org always includes Paid. Individual has no admin, so an admin lock on any setting needs Team or above. A setting **below its minimum tier is inert**: clients and servers ignore it, and the portal refuses to publish it. Tier limits (numeric or length caps per tier) are listed after the tier. |
| Phase | **Launch** = built and honoured at launch. **P2** = present in the schema so bundles stay forward compatible, hidden in the portal and inert in the client until the feature ships (contract section 7). The publish check accepts a P2 setting with a warning. |
| Enforced | **gateway** = our managed gateway, sync service or portal (hard). **client** = Coach on the user's machine (soft: see `design/tiers.md` section 3 for how it can be bypassed). **both** = server check plus client check. |

## 2. State model and resolution

| State | Admin supplies | User can change | Typical use |
|---|---|---|---|
| `locked` | `value` (required) | No. User value is ignored (kept, not deleted, and restored if the lock is lifted). | Compliance controls, org-wide facts. |
| `default` | `value` (required) | Yes. Starting value only. | Sensible org starting points, seeded preferences. |
| `user_choice` | nothing (`value` must be absent) | Yes. Catalog default applies until the user chooses. | Admin has reviewed the setting and deliberately leaves it open. Shown as reviewed in the portal. |

The bundle shape is `settings{<key>:{state, value?}}`. `value` is present for `locked` and `default` and absent for `user_choice` (the schema enforces both directions; contract section 5, finding F-43).

```
effective(key):
  p = bundle.settings[key]                       # absent = {state: user_choice} (or locked at the catalog default if 'Locked only')
  if tier(org) < minTier(key):  return catalogDefault(key)   # inert below its tier
  if plan(user) < minPlan(key): return catalogDefault(key)   # needs Individual Paid or above (entitlement token)
  if p.state == locked:         return p.value
  if user.has(key):             return clamp(user.value)     # clamp = dependent rules below
  if p.state == default:        return p.value
  return catalogDefault(key)
```

Dependent rules (applied after resolution, never relaxed by a user value):
- A user value must still satisfy dependent locked settings. Examples: `spend.personalMonthlyCapUsd` cannot exceed an org cap; `prefs.preferredModel` must pass `models.allowlist`, `models.denylist`, `models.minCertification`, the connection switches and the Blueprint's sensitivity rule.
- `data.minimumSensitivity` is a floor: nothing lowers a Blueprint's class below it. Raising is open to any role that may edit the Blueprint and to the model's tighten-only tool; lowering is an owner-only panel action, never below this floor and subject to `data.sensitivityRules` (R4). ASSUMPTION: the engine also keeps `Blueprint.sensitivity` at or above the highest step-level data sensitivity (exposed as a step diagnostic).
- If a policy update makes a stored user value invalid, the client drops it, falls back to the resolved default and shows a notice. Nothing fails silently.
- Every change to a locked setting produces an in-app notice to affected users and an audit entry. A locked control in the UI always says "Set by your organization" and who to ask.
- Spend caps convert to integer micro-USD as round(USD x 1,000,000), half up, when the gateway reserves (finding F-38).

Bundle rules:
- **Version styles.** `schemaVersion` is a required integer (the Blueprint uses a "1.x" string, the tool schema a semver string; each is a separate artifact). A client that sees a higher number keeps its last good bundle and shows "update required".
- **Two validation profiles from one file.** The **client profile** is the schema as is: known keys are validated; an unknown key whose name does not start with `x-` is ignored with a warning (it must still be shaped like a setting, and it stays in the bytes the signature covers); `x-` keys are carried and ignored. An unknown enum value in a known key drops that one setting to its catalog default with a warning. The **authoring profile** (portal and gateway, at publish) adds `#/$defs/strictRootKeys` and `#/$defs/strictSettingKeys` (only catalog keys or `x-` keys) and the checks JSON Schema cannot express: tier gating (`x-minTier`), tier limits (`x-tierBounds`), phase (`x-phase`), cross-references (every `toolId` exists in the catalog or in `environment.customTools`, ids resolve, rule field paths exist in the Blueprint field registry) and a monotone `toolDataFlowCeiling` across classes.
- **Groups.** One bundle per org at v1 (contract decision 7). `environment.profiles[].groupIds` is the only group-aware field; at launch it holds ids of portal-managed groups (ASSUMPTION, R8), and directory groups arrive with SSO (P2). A user whose groups match several profiles gets the first matching profile in array order; with no match, `environment.defaultProfileId`. An optional `scope` field on a profile is reserved and ignored. Per-group sensitivity rules, budgets and reviewers are deferred.
- **Signature.** Detached JWS over RFC 8785 canonical JSON, ES256 unless Ed25519 support is verified in the chosen KMS and .NET (contract decision 7). The `kid` resolves through the root-signed key-set manifest (`design/tiers.md` section 4). The Individual baseline bundle uses `orgId` `baseline`.
- **Size.** ASSUMPTION: 256 KiB per bundle.

## 3. Settings

Groups follow the requested order. Org environment and policy mechanics are a separate group because they are neither user nor governance toggles. Tenant-only settings (never sent to clients) are in section 5.

### Connections and models (19)

| Key | Type | Default | Admin lock | Min tier | Phase | Enforced | Rationale |
|---|---|---|---|---|---|---|---|
| `connections.managed.enabled` | bool | `true` | Yes | Individual (Paid) | Launch | both | Needs Individual Paid or above. Master switch for the paid gateway path. The gateway refuses calls for an org that has switched it off, so this one is hard. Managed is generally available only after written upstream permission is on file; until then it sits behind a per-tenant flag (tenant.managed.flag) and this switch has no effect while the flag is off. |
| `connections.byokOpenrouter.enabled` | bool | `true` | Yes | Individual | Launch | client | Steers people off personal OpenRouter keys (byok_openrouter means the customer's own OpenRouter key). Soft unless the org also blocks the host at its firewall. |
| `connections.byokProvider.enabled` | bool | `true` | Yes | Individual | Launch | client | Same switch for direct provider keys. Soft unless the org blocks the provider hosts. |
| `connections.customOpenaiCompat.enabled` | bool | `true` | Yes | Individual | Launch | client | Turns user-created custom endpoints on or off. Org-provisioned connections (below) are not affected. |
| `connections.local.enabled` | bool | `true` | Yes | Individual | Launch | client | Local models keep data on the device. A regulated org may still want to limit which local models run (see models.allowlist). |
| `connections.allowPersonalKeys` | bool | `true` | Yes | Team | Launch | client | Master switch for any credential the user types in. When false only managed and org-provisioned connections remain. Soft on its own; on a managed device the machine enrollment value RequireOrgPolicy makes it a hard path (tiers.md section 4.3). |
| `connections.byokProvider.allowedProviders` | null / array of provider slug | `null` | Yes | Team | Launch | client | Limits direct-provider BYOK to approved providerIds. null = any, [] = none. |
| `connections.endpointHostAllowlist` | null / array of host glob | `null` | Yes | Team | Launch | client | Limits user-entered custom endpoints to approved hosts. Loopback for the local type is always allowed. |
| `connections.requireTls` | bool | `true` | Yes | Individual | Launch | client | Blocks plain-http custom endpoints. Loopback local endpoints are exempt. The Connection schema already refuses non-https endpoints outside loopback, so locking this to false only matters for older clients. |
| `connections.proxy` | object {mode, url} | `{"mode":"system"}` | Yes | Team | Launch | client | How direct connections reach the internet behind a corporate proxy. |
| `connections.orgConnections` | array of orgConnection | `[]` | Locked only | Team | Launch | client | Org-provisioned connections (the company gateway, Azure OpenAI, a shared provider account). Same shape as the Connection entity without credentialRef (design/connection.schema.json). No secrets in the bundle: the credential comes from the user, OAuth, or the Enterprise vault (P2). |
| `models.allowlist` | null / array of model key glob | `null` | Yes | Team | Launch | both | If set, only matching model keys can be picked (keys are namespaced: OpenRouter ids as is, `<providerId>/<id>`, `custom/<id>`, `local/<id>`). Hard on managed, soft elsewhere. null = no restriction. |
| `models.denylist` | array of model key glob | `[]` | Yes | Team | Launch | both | Deny always wins over allow. Same enforcement split as the allow list. |
| `models.minCertification` | enum | `"uncertified"` | Yes | Individual | Launch | both | Floor on the certification label. Default shows labels without blocking so local launch models work; admins usually lock 'works'. A model listed in models.adminApprovedLocal counts as works. Label meanings (S1): until the evaluation harness ships every model shows experimental ("not yet evaluated"); uncertified means evaluated and failed. So a floor of works or certified blocks every model except admin-approved local ones until the harness ships. |
| `models.adminApprovedLocal` | array of local model key glob | `[]` | Locked only | Team | Launch | client | Local models an admin has vetted. When models.adminApprovedLocalCountsAsWorks is on, a listed model counts as works for models.minCertification and for every class floor, which is how a restricted process can use a local model that has no certification label. The capability probe still applies. |
| `models.adminApprovedLocalCountsAsWorks` | bool | `true` | Yes | Team | Launch | client | Switch for the rule above. Off = approved local models keep their real label. |
| `models.requireCapabilityProbePass` | bool | `true` | Yes | Individual | Launch | client | A model that fails the tool-call or JSON-schema probe cannot drive coaching. Lock it so users cannot force one through. |
| `models.zeroRetentionProvidersOnly` | bool | `false` | Yes | Team | Launch | both | Route only to providers that do not retain prompts. managed always forces provider data-collection deny whatever this says; for byok_openrouter it is a request flag; elsewhere unverifiable. VERIFY provider flags. |
| `models.fallback` | enum | `"fail_loud"` | Yes | Individual | Launch | both | Default fails loudly so a silent swap to a different model never changes how a recommendation is explained. |

### Spend (8)

| Key | Type | Default | Admin lock | Min tier | Phase | Enforced | Rationale |
|---|---|---|---|---|---|---|---|
| `spend.orgMonthlyCapUsd` | number / null (USD) | `null` | Locked only | Team | Launch | gateway | Hard monthly ceiling on managed usage across the org. null = none. Managed only. Caps convert to micro-USD as round half up (USD x 1,000,000). |
| `spend.perUserMonthlyCapUsd` | number / null (USD) | `null` | Locked only | Team | Launch | gateway | Hard monthly ceiling per user on managed usage. |
| `spend.perSessionCapUsd` | number / null (USD) | `null` | Yes | Team | Launch | both | Stops a runaway coaching session. Gateway meters managed; the client estimates for other connections. |
| `spend.maxPricePerMillionOutputTokensUsd` | number / null (USD) | `null` | Yes | Team | Launch | both | Hides models above a list price. VERIFY the source of price data (OpenRouter model list or our own table). |
| `spend.warnAtPercent` | integer 1-100 | `80` | Yes | Team | Launch | both | Percent of any cap at which the user and admin are warned. |
| `spend.onCapReached` | enum | `"block"` | Locked only | Team | Launch | gateway | Hard stop by default. warn_only is for pilots. Managed only. |
| `spend.byokEstimatedMonthlyCapUsd` | number / null (USD) | `null` | Yes | Individual | Launch | client | Client-side estimate for BYOK calls. Advisory: the real hard cap must be set on the provider key. |
| `spend.personalMonthlyCapUsd` | number / null (USD) | `null` | Default only | Individual (Paid) | Launch | client | The user's own tighter cap on `managed` usage. It cannot exceed an org cap. Needs Individual Paid or above, because `managed` does. |

### Data and privacy (18)

| Key | Type | Default | Admin lock | Min tier | Phase | Enforced | Rationale |
|---|---|---|---|---|---|---|---|
| `data.sensitivityRules` | object: one rule per class | see matrix | Yes | Team | Launch | both | What each sensitivity class permits: connection types, content mode, model floor, backup and sync, approval metadata sync, export, and the tool data-flow ceiling. Editing is not available on Individual, which runs the default matrix of the signed baseline bundle. Defaults in the matrix below. |
| `data.minimumSensitivity` | enum | `"internal"` | Yes | Team | Launch | both | Floor for new Blueprints. Users and rules can raise a class, never lower it. Sync server rejects Blueprints below the floor. |
| `data.redaction.builtinPatterns` | array of enum | `["secret_keys","private_key_blocks","payment_card","us_ssn"]` | Yes | Individual | Launch | client | Built-in detectors that run before text leaves the device. Email and phone are off by default because process descriptions are full of them. VERIFY detector quality. |
| `data.redaction.customPatterns` | array of RedactionPattern | `[]` | Yes | Team | Launch | client | Org-specific patterns (employee ids, project codenames). Linear-time regex or keyword lists only. |
| `data.redaction.defaultAction` | enum | `"redact"` | Yes | Individual | Launch | client | What a built-in detector does on a hit. Custom patterns carry their own action. |
| `data.redaction.surfaces` | array of enum | `["prompt","transcript","diagnostics"]` | Yes | Individual | Launch | client | Where built-in detectors apply. Blueprint sync is deliberately absent: backup must be faithful. |
| `data.redaction.reversible` | bool | `true` | Yes | Individual | Launch | client | Swap matches for stable tokens before sending and restore them locally in the reply. The mapping never leaves the device. |
| `data.exports.allowedKinds` | null / array of export kind | `null` | Yes | Team | Launch | both | Which ExportRecord kinds are allowed (handoff_brief, process_document, review_packet, blueprint_json, automate_flow_draft). null = all, [] = none. Narrows data.sensitivityRules[class].exportAllowed. |
| `retention.transcripts.storage` | enum | `"local"` | Yes | Individual | Launch | client | Transcripts stay on the device by default. 'none' keeps them in memory only. |
| `retention.transcripts.days` | integer 1-3650 | `90` | Yes | Individual | Launch | client | Local auto-delete age. ASSUMPTION: 90 days. |
| `retention.localLogs.days` | integer 1-90 | `14` | Yes | Individual | Launch | client | Local diagnostic log age. Logs never contain prompts or secrets. |
| `retention.blueprints.versionsKept` | integer 1-1000 | `50` | Locked only | Team | Launch | gateway | Blueprint versions kept on the server per Blueprint. ASSUMPTION: 50. |
| `retention.blueprints.trashWindowDays` | integer 0-365 | `30` | Locked only | Team | Launch | gateway | Days a deleted Blueprint stays recoverable. After that it leaves live storage; copies persist in backups for up to the 35-day backup window, which the DPA states. ASSUMPTION: 30 days. |
| `retention.auditLog.days` | integer 30-3650 | `365` | Locked only | Team; limits: Team max 365; Enterprise max 3650 | Launch | gateway | Server audit log age. Team default and cap 365, Enterprise up to 3650, checked at publish. |
| `sync.blueprints.enabled` | bool | `true` | Yes | Individual (Paid) | Launch | both | Master switch for full Blueprint backup and sync, all classes. Per-class behavior (on, opt_in, forbidden) is data.sensitivityRules[class].sync. Locked off: the client stops uploading Blueprint bodies and the server rejects body writes. ASSUMPTION (architecture X10): body-less approval-metadata envelopes (ids, contentHash, status, sensitivity, schemaVersion, size; no title or content) still flow whenever approvals are in force and the class's approvalMetadataSync is yes, so approval and AutoMate handoff keep working. Sync, backup, restore and version history need Individual Paid or above, an account and a valid entitlement token; Individual Free has none of them (R1). |
| `sync.transcripts.enabled` | bool | `false` | Yes | Individual (Paid) | Launch | both | Opt-in transcript sync (a sync feature: Individual Paid or above). An admin can lock it to false but can never force it on: transcripts are local unless the user opts in. |
| `telemetry.crashReports` | enum: off, anonymous (admin: off only) | `"off"` | Yes | Individual | P2 (hidden, inert) | client | Crash reports with no content. Off everywhere (contract decision 10). No telemetry sink exists at launch, so the setting is reserved: hidden and inert (P2). An admin can only lock or default it to off; `anonymous` can be chosen only by the user (user_choice), and only once a sink ships with its consent text. |
| `telemetry.usageAnalytics` | enum: off, anonymous (admin: off only) | `"off"` | Yes | Individual | P2 (hidden, inert) | client | Product analytics. Off everywhere; no product analytics are planned. No telemetry sink exists at launch, so the setting is reserved: hidden and inert (P2). An admin can only lock or default it to off; `anonymous` can be chosen only by the user (user_choice), and only once a sink ships with its consent text. No 'identified' option exists. Client-reported usage for the org is an audit setting (governance.auditLog.clientReportedUsage), not telemetry. |

### Coach behavior (10)

| Key | Type | Default | Admin lock | Min tier | Phase | Enforced | Rationale |
|---|---|---|---|---|---|---|---|
| `coach.aiMode` | enum | `"full"` | Yes | Team | Launch | both | off = wizard only, no model traffic on any connection. lite_only = the engine picks every question and the model only phrases it and extracts the answer. full = the guided coach. managed calls are refused by the gateway when the org is off (hard); other connections are enforced by the client (soft). |
| `coach.aiFlows.allowedByMode` | object: aiMode -> list of flows | `{"off":[],"lite_only":["rescue"],"full":["rescue","second_opinion"]}` | Yes | Team | Launch | both | Which optional flows each aiMode allows: rescue (rescue my failed automation) and second_opinion (critique with a cross-model check that obeys data.sensitivityRules). ASSUMPTION: second_opinion needs full. |
| `coach.llmOverride.mode` | enum | `"advisory"` | Yes | Team | Launch | both | When a user picks llm_node or llm_agent over an earlier-rung recommendation: warn only, need approval, or block. The sync server checks approval records before 'approved'. |
| `coach.llmOverride.requireJustificationCard` | bool | `true` | Yes | Individual | Launch | both | User must fill Step.llmJustification (whyNotCode, validator, fallback, costPerRun) before the override stands. |
| `coach.llmOverride.approverRole` | enum | `"coe_reviewer"` | Locked only | Team | Launch | both | Who approves an LLM-first override when mode is approval_required. Only a CoE Reviewer approves, never their own Blueprint (contract decision 9), so the enum has one value today; the key stays so a later role needs no schema break. |
| `coach.llmAgent.mode` | enum | `"allowed_with_justification"` | Yes | Team | Launch | both | llm_agent is discouraged by the contract. Admins can require approval or remove the rung entirely. The engine projection maps forbidden to its policy.llmAgentMode. |
| `coach.llmNode.requireValidatorAndFallback` | bool | `true` | Yes | Individual | Launch | both | Every llm_node step needs a validator and a fallback before the Blueprint can be exported. Engine rule, re-checked on the server at approval. |
| `coach.override.mode` | enum | `"advisory"` | Yes | Team | Launch | both | Same control for any other override of the engine's recommended rung (advisory, approval_required, or forbidden). A reason is always required (Step.override.reason). |
| `coach.override.reasonMinChars` | integer 15-400 | `20` | Yes | Individual | Launch | client | Minimum length of an override reason. The floor is 15, equal to the Blueprint floor, and the ceiling is 400, the longest reason the Blueprint accepts (contract lengths), so no admin value makes every override impossible; the host rejects anything shorter. |
| `coach.triageOverride.mode` | enum | `"allowed_with_reason"` | Yes | Team | Launch | both | Continuing to build after a 'dont_automate' or 'fix_process_first' verdict: allow with a reason, need approval, or block. |

### AutoMate actions (5)

| Key | Type | Default | Admin lock | Min tier | Phase | Enforced | Rationale |
|---|---|---|---|---|---|---|---|
| `automate.actions.mode` | enum | `"draft_only"` | Yes | Individual | Launch | client | off = no AutoMate actions. draft_only = Coach writes new drafts after a diff approval. apply_existing = may also change existing workflows after a diff approval. Nothing is ever applied without a human click. |
| `automate.actions.allowedKinds` | array of enum | `["create","update"]` | Yes | Team | Launch | client | Delete is off by default; when enabled it still needs its own click. |
| `automate.actions.maxChangesPerDiff` | integer 1-200 | `25` | Yes | Individual | Launch | client | Caps how large a diff the user must approve in one click, so review stays real. ASSUMPTION: 25. |
| `automate.testRuns.mode` | enum | `"attended_only"` | Yes | Individual | Launch | client | Test runs need an explicit click and an attending user. Unattended test runs do not exist at launch; the enum grows later. |
| `automate.testRuns.blockProductionSystems` | bool | `true` | Yes | Team | Launch | client | Refuse test runs against systems marked isProduction in the environment profile. |

### Governance (14)

| Key | Type | Default | Admin lock | Min tier | Phase | Enforced | Rationale |
|---|---|---|---|---|---|---|---|
| `governance.approval.mode` | enum | `"by_rule"` | Locked only | Team | Launch | both | never = no review. by_rule = review only when an override or the Blueprint's sensitivity class asks for it; org rules are P2 and not a source of approval gates at launch (S14). always = every Blueprint is reviewed before the gates below. Approvals are server-issued records from Team up. Individual (Free or Paid) and a Team with exactly one billable seat meet an approval-required gate with a recorded self-attestation instead (R7); Enterprise never accepts one. |
| `governance.approval.requiredBefore` | array of gate | `["automate_apply"]` | Locked only | Team | Launch | both | Gates that need approval when approval applies. A gate is met by exactly one of: (a) approved by a CoE Reviewer for the current contentHash, with a signed approval record that the AutoMate adapter checks by recomputing contentHash, not just Blueprint.status; (b) a SelfAttestation for the current contentHash, valid only where R7 allows it. This holds for every sensitivity class including restricted, and approval metadata may sync even for a local-only restricted Blueprint. Gate values (R2): build_handoff (entering the handoff stage), handoff_brief (creating that export), automate_flow_draft (creating that export or writing a draft into AutoMate), export (any other export kind except review_packet), automate_apply, automate_test_run. review_packet has no gate: it is how review is requested. |
| `governance.approval.minReviewers` | integer 1-3 | `1` | Locked only | Team; limits: Team max 1; Enterprise max 3 | P2 (hidden, inert) | gateway | Number of distinct approvers. One at Team. Multi-reviewer approval is Enterprise and P2: hidden, and inert at 1, until built. |
| `governance.approval.reviewSlaDays` | integer 1-60 / null | `null` | Locked only | Team | P2 (hidden, inert) | gateway | Reminder and escalation age for the review queue. null = no reminders. P2: hidden until built. |
| `governance.adminContentAccess` | enum | `"break_glass"` | Locked only | Team | Launch | gateway | What an Admin can read of synced Blueprints. Always metadata (title, owner, status, class, dates, size, review state). break_glass adds audited content access: a stated reason of at least 15 characters (ASSUMPTION), a notice to the owner, a time box (governance.breakGlass.timeBoxHours) and a log entry for every read. Team: one Admin may approve their own request. Enterprise: a second Admin must approve, meaning any other user holding Admin in the tenant and never the requester, and with only one Admin the request fails closed (R6, S7). A grant cannot be renewed (S7). metadata_only removes break-glass. Content is otherwise readable only by the owner, explicit shares, and CoE Reviewers once in review. |
| `governance.breakGlass.timeBoxHours` | integer 1-4 | `4` | Locked only | Team | Launch | gateway | How long one approved break-glass read stays open before it ends on its own. Default 4 hours (ASSUMPTION, R6). Policy can only shorten it: the maximum is 4, so no bundle can lengthen it. Only meaningful while governance.adminContentAccess is break_glass. Fixed rules, not settings: a reason is required; the Blueprint owner is notified when access starts, naming the Admin and the reason; access ends automatically at expiry; every read is logged. A grant cannot be renewed: after expiry a new request with a new reason (and, at Enterprise, a new second-Admin approval) is needed. No owner veto (ASSUMPTION; S7). Portal events: break_glass_requested, break_glass_approved, break_glass_read, break_glass_expired. |
| `governance.intake.enabled` | bool | `false` | Locked only | Team | P2 (hidden, inert) | gateway | Turns on the intake queue: employees submit process ideas, reviewers triage them. P2: hidden until built. |
| `governance.intake.requiredFields` | array of enum | `[]` | Locked only | Team | P2 (hidden, inert) | gateway | Fields an intake submission must have. ASSUMPTION: this field list. P2. |
| `governance.intake.gateStage` | stage / null | `null` | Locked only | Team | P2 (hidden, inert) | both | If set, a Blueprint cannot pass this stage until its intake is accepted. null = intake does not gate. P2. |
| `governance.templates.required` | bool | `false` | Locked only | Team | P2 (hidden, inert) | both | New Blueprints must start from an org template. P2: hidden until built. |
| `governance.templates.allowPersonal` | bool | `true` | Locked only | Team | P2 (hidden, inert) | client | Users may save their own templates. P2. |
| `governance.auditLog.clientReportedUsage` | enum | `"off"` | Yes | Team | Launch | both | Audit data, not telemetry. Direct and local connections never touch our gateway. When 'metadata', the client reports connection type, model key, tokens and time (never content) to the org audit log, tied to the user. Honest clients only; the product says so. |
| `governance.orgRules` | array of OrgRule | `[]` | Locked only | Team (template rules) / Enterprise (custom predicates); limits: Team max 20 items, template rules only | P2 (hidden, inert) | both | Declarative org rules over Blueprint and Step, for example 'payroll needs a human_checkpoint'. The engine evaluates them; no code runs. The org-rule editor is P2, so the setting is hidden and inert until then (the engine's orgRules input stays empty). |
| `governance.dataDomains` | array of DataDomain | `[]` | Locked only | Team | P2 (hidden, inert) | both | Org vocabulary (payroll, customer PII) that rules key on. Matched by keyword and system, not by an LLM. Hidden and inert with the org-rule editor (P2). |

### Org environment and policy mechanics (6)

| Key | Type | Default | Admin lock | Min tier | Phase | Enforced | Rationale |
|---|---|---|---|---|---|---|---|
| `org.tier` | enum | `"individual"` | Locked only | Individual | Launch | gateway | Signed fact so the client knows which controls exist. The gateway and portal are authoritative; the client only displays. Settings below their minimum tier are inert (ignored by clients and servers). Individual covers both Free and Paid; the plan (free, individual, team, enterprise) is a separate fact in the entitlement token, not in this bundle (R1). |
| `environment.profiles` | array of EnvironmentProfile | `[]` | Locked only | Team (1 profile) / Enterprise (many); limits: Team max 1 item | Launch | both | Permitted and forbidden tools by toolId and rungId, preferred tools, installed software, OS, network and API availability, who runs automations. One bundle per org at v1: a user whose groups match several profiles gets the first in array order. |
| `environment.defaultProfileId` | slug / null | `null` | Locked only | Team | Launch | both | Profile used when a Blueprint has no environmentProfileRef and no profile matches the user's groups. |
| `environment.userMayDeclareSoftware` | bool | `true` | Yes | Team | Launch | client | Users may add software they have to their local view of the profile. Forbidden tools stay forbidden. |
| `environment.customTools` | array of org tool entry | `[]` | Locked only | Enterprise | Launch | both | Org-owned tools (in-house connectors, script libraries) merged into the catalog for this org. Same shape as ToolCatalogEntry, including the extension fields; absent dataFlow means vendor_cloud and absent unattendedSupport means no. |
| `policy.onExpiry` | enum | `"no_llm"` | Locked only | Team | Launch | client | After expiresAt with no refresh: no_llm = deterministic engine and local editing only (the default, S8); last_known_good = keep enforcing the cached bundle; read_only = view only. |

### User preferences (14)

| Key | Type | Default | Admin lock | Min tier | Phase | Enforced | Rationale |
|---|---|---|---|---|---|---|---|
| `prefs.coachingStyle` | enum | `"guided"` | Default only | Individual | Launch | client | guided asks one question at a time; direct states the recommendation first then the reasoning. |
| `prefs.verbosity` | enum | `"standard"` | Default only | Individual | Launch | client | Length of explanations. Never changes what the engine decides. |
| `prefs.skillLevel` | enum | `"basic"` | Default only | Individual | Launch | client | Adjusts explanation depth and which catalog entries are shown as within reach. The scale is none, basic, intermediate, advanced everywhere; the UI shows basic as Beginner. |
| `prefs.preferredModel` | null / {connectionId, modelId} | `null` | Yes | Individual | Launch | both | The model picker's choice (modelId is a namespaced model key). Admin can lock it to one model. Must pass allow list, certification floor and sensitivity rules. |
| `prefs.showEngineTrace` | bool | `false` | Default only | Individual | Launch | client | Expand the rule trace behind each recommendation by default. |
| `prefs.alerts.events` | array of enum | all six events | Default only | Individual | Launch | client | Which events raise a toast or email. In-app banners for a changed lock and for an expired policy always show. |
| `prefs.alerts.channels` | array of enum | `["in_app","windows_toast"]` | Default only | Individual | Launch | both | Where alerts appear. Email is sent by the server and needs an org or personal account. |
| `prefs.accessibility.reduceMotion` | enum | `"system"` | Default only | Individual | Launch | client | Animations and transitions. system follows Windows. Accessibility needs are personal, so an admin can seed a default but never lock it. Target: WCAG 2.2 AA with keyboard and screen-reader support for the shell and the portal. |
| `prefs.accessibility.highContrast` | enum | `"system"` | Default only | Individual | Launch | client | High-contrast theme. system follows Windows contrast themes. Default only. |
| `prefs.accessibility.textScalePercent` | integer 100-200 | `100` | Default only | Individual | Launch | client | Text size as a percentage of the Windows setting. Layouts must hold at 200 percent without loss of content. Default only. |
| `prefs.accessibility.screenReaderMode` | enum | `"system"` | Default only | Individual | Launch | client | on = every confirmation chip, engine result and warning is also announced as text, tables get row summaries, and no cue relies on motion or color alone. system detects a running screen reader. Default only. |
| `prefs.locale.uiLanguage` | enum | `"en"` | Default only | Individual | Launch | client | Interface language. English only in v1; strings are locale-safe (no sentence concatenation, plural-aware) so more languages need no schema change. Default only. |
| `prefs.locale.replyLanguage` | auto / BCP 47 tag | `"auto"` | Yes | Individual | Launch | client | Language of model replies. auto = the language the user writes in, best effort and not certified per language. An org may lock one language (for example en for reviewers). Engine rationale text stays in the interface language. |
| `prefs.locale.formats` | enum | `"system"` | Default only | Individual | Launch | client | Date, time and number display. system follows Windows regional settings; iso uses unambiguous formats. Currency is USD only in v1. Default only. |

## 4. Default sensitivity class matrix

Default value of `data.sensitivityRules`, one rule per class. Blueprint classes are the contract's `public | internal | confidential | restricted`. Each row is a setting the admin can change from Team up; **Individual cannot edit it** and runs these defaults through the signed baseline bundle (contract section 7, finding DC-17).

| Class | LLM may use | Content to LLM | Min cert | Zero-retention provider | Preview before send | Backup and sync | Approval metadata sync | Export | Approval before handoff | Tool data-flow ceiling |
|---|---|---|---|---|---|---|---|---|---|---|
| `public` | all five types | full | uncertified | no | no | `on` | yes | yes | no | `ai_cloud` |
| `internal` | all five types | full | uncertified | no | no | `on` | yes | yes | no | `ai_cloud` |
| `confidential` | managed, custom_openai_compat, local | redacted | works | yes | yes | `on` | yes | yes | no | `tenant` |
| `restricted` | local | redacted | works | yes | yes | `opt_in` | yes | yes | yes | `local` |

Notes:
- "LLM may use" is checked on every call: the client refuses the call if the active connection type is not listed. For `managed` it also sends the declared class as metadata (not content) so the gateway can enforce routing. The gateway cannot verify the class; it trusts the client's declaration (`design/tiers.md` section 3).
- `llmContentMode`: `full` sends content as is, `redacted` forces every redaction pattern to `redact` and shows the preview, `none` means no content may go to any model for that class, and the engine treats `llm_node` and `llm_agent` as unavailable for it (blueprint.schema.json). A class whose `llmConnectionTypes` is empty runs without a model: forms, rules and exports work, nothing goes to a model.
- `sync` is `on`, `opt_in` or `forbidden`. Full Blueprint backup is a capability for every class (contract decision 8). `restricted` defaults to `opt_in`: the Blueprint stays on the device, the UI says "Local only, not backed up", and an admin or the owner may opt in with one click. `forbidden` is the stricter admin choice for a class. `sync.blueprints.enabled` is the master switch above all classes.
- `approvalMetadataSync` (default yes for every class, including `restricted`) lets the approval record (contentHash, status, signer, no content) sync even when the content stays local, so the AutoMate adapter can verify an approval for a local-only Blueprint (finding DC-04). Turning it off for a class makes approval before handoff impossible for that class. Locking `sync.blueprints.enabled` off does not stop this metadata (invariant 13).
- `toolDataFlowCeiling` is the highest data-flow level a tool may have when used on a Blueprint of that class (`local < tenant < vendor_cloud < ai_cloud`). Defaults match the engine. The ceiling must not get looser as the class gets stricter, and the `restricted` ceiling is capped at `tenant` (the engine hard-caps it); both are checked at publish.
- ASSUMPTION (S4): when a synced Blueprint is raised to `restricted`, new revisions stop uploading at once and the client offers one-click "Delete backed-up copies"; until they are deleted, earlier server revisions follow normal retention. S6: "Delete backed-up copies" removes every server revision of that Blueprint including version history and leaves a tombstone (id, time, actor). Content leaves live storage at once and infrastructure backups within the 35-day backup window (DPA wording). Approval metadata (hash, status, signer) stays (decision 8). Audit action `blueprint_backup_deleted`.
- ASSUMPTION (S1): until the evaluation harness ships every model shows `experimental` ("not yet evaluated"), so a class whose `minModelCertification` is `works` (the `confidential` and `restricted` defaults) can use only admin-approved local models (`models.adminApprovedLocal`) until then.
- `exportAllowed` is narrowed further by `data.exports.allowedKinds` (ExportRecord kinds). A local export never uploads anything (R2), so the `restricted` default is now yes (v2 had no): the owner may always export locally unless the org excludes the kind. An admin who sets `exportAllowed` to no for a class makes that stricter choice for every kind (invariant 14).
- `requireApprovalBeforeHandoff` makes a Blueprint of that class need a met approval gate before `handoff_brief`, `automate_flow_draft` and `automate_apply`, on top of `governance.approval.requiredBefore` (invariant 15). It requires `approvalMetadataSync` yes.
- `minModelCertification` for `restricted` is `works`. An admin-approved local model (`models.adminApprovedLocal`) counts as `works` when `models.adminApprovedLocalCountsAsWorks` is on (contract section 6).
- `coach.aiMode` and the rescue and second-opinion flows sit above this matrix: the cross-model check of a second opinion obeys these rules like any other model call.

## 5. Tenant-only settings (not in the signed bundle)

These live in the gateway, portal or identity layer. Clients never receive them (the client learns the few facts it needs through the entitlement token and `org.tier`). Same columns as section 3. The grace clocks (policy bundle, entitlement token, payment failure) are stated once, in `tiers.md` section 4.5; the two rows below that carry a number repeat only that table.

| Key | Type | Default | Admin lock | Min tier | Phase | Enforced | Rationale |
|---|---|---|---|---|---|---|---|
| `tenant.managed.flag` | bool (per-tenant feature flag) | false | Locked only | Individual (Paid) | launch (dark) | gateway | Gate G1: managed is generally available only after written permission from OpenRouter, or an equivalent direct provider agreement, is on file. Until then the money path is built and tested dark; BYOK, local and no-model use never depend on it. Managed price mechanics are DEFERRED (R9). |
| `tenant.signIn.methods` | set of sign-in methods | per tier | Fixed by us | Individual (Paid): email or social; Team and above: adds Microsoft and Google | launch | gateway | Launch sign-in. Individual Free needs no account. ASSUMPTION: the social providers are chosen by us. SAML and OIDC single sign-on are P2 (R8). |
| `tenant.sso.provider` | SAML / OIDC config | none | Locked only | Enterprise | P2 | gateway | Custom SAML and OIDC single sign-on. DEFERRED to P2 (R8): not sold at launch. ASSUMPTION: OIDC with PKCE through the system browser; tokens in Credential Manager. |
| `tenant.sso.enforce` | bool | false | Locked only | Enterprise | P2 | gateway | Reject non-SSO sign-ins for the org's domains. DEFERRED to P2 (R8). |
| `tenant.scim.enabled` | bool | false | Locked only | Enterprise | P2 | gateway | Automatic user and group provisioning and deprovisioning. DEFERRED to P2 (R8). |
| `tenant.roleMapping` | map: IdP group -> role | {} | Locked only | Enterprise | P2 | gateway | Assign admin, coe_reviewer, builder, viewer from IdP groups. DEFERRED to P2 (R8); at launch roles are assigned in the portal. |
| `tenant.domainClaim` | array of domain | [] | Locked only | Team | launch | gateway | Verified domains for auto-join. |
| `tenant.invites.allowedDomains` | array of domain | [] | Locked only | Team | launch | gateway | Only these email domains can be invited. |
| `tenant.dataRegion` | enum us / eu | us | Locked only (set at org creation) | Team | launch: one region, field present; choice P2 | gateway | Where Blueprints are stored. ASSUMPTION: one region (us) at launch; the field exists so a second region needs no schema change. |
| `tenant.cmk` | customer KMS key ref | none | Locked only | Enterprise (add-on) | P2 | gateway | Customer-managed key wrapping the tenant data key. Revoking it crypto-shreds Blueprint storage. Ships after a security review; do not sign contracts that require it before it ships. |
| `tenant.vault.enabled` | bool | false | Locked only | Enterprise | P2 | gateway | Org-managed key vault for provider keys: scoped sub-key mode A only, after a security-analyst review (tiers.md section 5). |
| `tenant.ipAllowlist` | array of CIDR | [] | Locked only | Enterprise | P2 | gateway | Restrict portal, sync and gateway access to org networks. |
| `tenant.policy.offlineGraceDays` | integer 1-90 | 14 | Locked only | Team (fixed 14) / Enterprise (adjustable) | launch | gateway | Sets expiresAt = issuedAt + this at issue time. Clock 1 of the three independent grace clocks in tiers.md section 4.5 (S8); when it ends, policy.onExpiry applies (default no_llm). ASSUMPTION: 14. |
| `tenant.minPolicyVersion` | integer | auto | Locked only | Team | launch | gateway | Gateway and sync server reject clients reporting an older policy version, forcing a refresh. |
| `tenant.minClientVersion` | semver | none | Locked only | Team | launch | gateway | Reject clients older than this. |
| `tenant.audit.stream` | webhook / SIEM target | none | Locked only | Enterprise | P2 | gateway | Stream audit events to the org's SIEM. |
| `tenant.legalHold` | bool per Blueprint set | false | Locked only | Enterprise | P2 | gateway | Suspends deletion and purge for held Blueprints and their audit records. |
| `tenant.retention.gatewayMetadataDays` | integer 90-3650 | 400 | Locked only | Team | launch | gateway | Age of managed usage metadata (user, model, tokens, cost, time). Bounded below because it backs billing. ASSUMPTION: 400. |
| `tenant.devices.maxPerUser` | integer | 3 | Fixed by us | Individual (Paid), Team, Enterprise | launch | gateway | Up to 3 devices per user, each bound to the entitlement token (claim `devices`). Individual Free has no device management. Not an admin setting. |
| `tenant.entitlement.offlineGraceDays` | integer | 30 | Fixed by us | Individual (Paid), Team, Enterprise | launch | gateway | The signed entitlement token stays valid offline for 30 days. Clock 2 of the three independent grace clocks in tiers.md section 4.5 (S8); any older single 30-day grace wording means this clock only. |
| `tenant.trial.days` | integer | 14 | Fixed by us | Team | launch | gateway | 14-day trial of Team for a new organization, once per organization (R1; the v2 Individual trial is removed). No card at start (owner-confirmed 2026-10-26). Claim `trialEndsAt`; events trial_started and trial_ended. When it ends with no subscription, members fall to Individual Free: local data untouched, synced data downloadable for 90 days. No free managed credits. |
| `tenant.billing.paymentFailureGraceDays` | integer | 14 | Fixed by us | Individual (Paid), Team, Enterprise | launch | gateway | After a payment fails, paid features keep working for this long, then the account falls to Individual Free, the same fall as the end of the trial. Clock 3 of the three independent grace clocks in tiers.md section 4.5 (S8). 14 (R1, owner-confirmed 2026-10-26). Event payment_failed, then plan_changed. |
| `tenant.billing.*` | plan, seats, payment, invoices | n/a | Locked only | Individual (Paid), Team, Enterprise | launch | gateway | Platform subscription billing is live at launch and does not depend on tenant.managed.flag (R1). The portal shows and edits plan and seats; the entitlement token carries plan, trialEndsAt, seats and devices. No price points, seat prices or fee rates appear in the design. Managed usage billing mechanics (fee rate, markup, minimum charge, wallet or invoice model, top-up, refund, tax) are DEFERRED (R9); the metering ledger and spend caps stay. |
| `tenant.viewers.fairUseCap` | integer or none | none | Locked only | Team | launch | gateway | Viewer seats are free and not billed (R7). No cap at launch (owner-confirmed 2026-10-26): the terms limit free Viewers to reading and review, and a number, if any, is set from real Viewer-to-seat ratios after one quarter. |

## 6. Machine enrollment values

Contract decision 7: machine-level enrollment ships at launch, so "disable personal keys" and "org policy required" have a hard path on managed devices. IT writes these values under a machine-wide policy registry key (admin-writable only) through Intune or Group Policy. The key is `HKLM\SOFTWARE\Policies\Coach\Enrollment`. PLACEHOLDER: it uses the working name "Coach" and changes when the product name is final; ASSUMPTION: it sits under the machine policy hive so the later ADMX templates can write the same three values. ADMX templates and Intune packaging come after launch; until then IT deploys the values by script or `.reg` file (`tiers.md` section 4.3 has the script).

| Value | Type | Meaning |
|---|---|---|
| `OrgId` | string | The organization id the app must sign in to and whose policy it must hold. Equals the bundle `orgId`. |
| `RequireOrgPolicy` | DWORD 0 or 1 | 1 = enrollment-required mode until a valid org policy is held: no direct model connections and Blueprint sync paused, so the org's locks (for example `connections.allowPersonalKeys`) cannot be avoided by never signing in; the client still applies them, so they stay soft against a local admin; the no-model wizard and local Blueprints still work. 0 or absent = enrollment is informational only. |
| `PolicyFile` | string path, optional | Offline distribution (Enterprise): a folder or file the client reads as a signed bundle, verified exactly like a fetched one. Air-gapped sites pair it with the offline activation file. |

"Enrollment-required mode" is deliberately not called "restricted mode", which would collide with the `restricted` sensitivity class. The same key may also pin the update ring (architecture owns those values). Without enrollment a user can skip sign-in; the portal and the docs say plainly that client-side controls are for honest-but-careless users.

## 7. Invariants (not settings)

No policy can change these. They are listed so nobody builds a toggle for them.

1. Credentials never appear in logs, transcripts, Blueprints, exports or the policy bundle. Direct-connection keys live in Windows Credential Manager/DPAPI. The bundle's `credentialRef` is a reference, never a secret.
2. The gateway does not store prompts or completions and persists metadata only (user, model, tokens, cost, time). Prompts transit gateway memory, OpenRouter and the model provider, so copy says "not stored by us", never "we never see it". `managed` requests always force provider data-collection deny, whatever `models.zeroRetentionProvidersOnly` says. Any future in-transit scan (P2, owner-approved exception) may read content in memory and must persist counts only.
3. No LLM sits in the recommendation path. No setting adds one, and the model can recommend tools only by catalog `toolId` that the engine returned.
4. AutoMate stays free of AI at runtime. Coach actions are draft-first, show a diff, are approved by a single-use host-minted token from a trusted UI click, map to a Blueprint step, and a test run is attended only. Nothing sends, deletes or runs without a human click.
5. The `local` connection type accepts loopback endpoints only. Anything else is a `custom_openai_compat` connection.
6. Telemetry is off everywhere, and no telemetry sink exists at launch, so both telemetry keys are reserved (P2: hidden and inert). An admin can lock or default them only to `off`; `anonymous` can be chosen only by the user (`user_choice`), and only once a sink and its consent text ship. Admins cannot force transcript sync on (`sync.transcripts.enabled` can only be locked to false) and cannot force identified telemetry (the option does not exist). Client-reported usage is audit data (`governance.auditLog.clientReportedUsage`), not telemetry, and the product says so. Admins have no access to local transcripts.
7. Policy bundles are verified before use: signature against the root-signed key set, `orgId` match, monotonic `version`, `expiresAt`. A bundle that fails any check is discarded and the last good one stays.
8. A locked setting is never hidden from the user and never silently overridden.
9. Only a CoE Reviewer sets `approved`, never on their own Blueprint. This is a fixed rule, not a setting (the v1 key `governance.approval.allowSelfApproval` no longer exists).
10. An Admin sees Blueprint metadata always; content only through audited break-glass (`governance.adminContentAccess`, which can only remove break-glass, never widen it; the fixed rules are invariant 16).
11. `managed` is generally available only after written upstream permission is on file; until then it sits behind `tenant.managed.flag` and BYOK, local and no-model use never depend on it. Managed price mechanics are DEFERRED (R9).
12. A setting below the org's tier is inert, and a setting in a phase that has not shipped is hidden and inert.
13. Locking `sync.blueprints.enabled` off never blocks the approval-metadata path by itself. No Blueprint body is pushed for any class, and the server rejects body writes, but body-less envelopes (`enc.mode` = `none`: ids, `contentHash`, status, sensitivity, `schemaVersion`, size; no title and no content) still sync while approvals are in force, so approval and the AutoMate handoff check keep working. Only a class's own `approvalMetadataSync` = no turns that off for the class. ASSUMPTION (architecture X10 and 3.4b item 6): the sync service accepts such envelopes whenever approvals are required; architecture marked this a new catalog rule, and this is it.
14. **Restricted data, export and review packets (R2).** `restricted` content never uploads unless the owner or an admin opts in (contract decision 8). The owner may always export locally, and build a `review_packet` locally, unless the org's `data.exports.allowedKinds` excludes that kind. Neither action uploads anything, and `sensitivityAtExport` records `restricted`. The existing settings suffice for this: `data.exports.allowedKinds` already names all five kinds (`handoff_brief`, `process_document`, `review_packet`, `blueprint_json`, `automate_flow_draft`), so no setting was added. A local-only restricted Blueprint is reviewed in one of two ways: the owner gives the packet to a CoE Reviewer outside Coach, or opts in to sync. The packet opens read-only and unmodified in the reviewer's Coach, so the recomputed `contentHash` equals the owner's. The reviewer's ApprovalRecord is bound to that hash and syncs as approval metadata (invariant 13). The owner's client applies the record only when its local `contentHash` matches and the record's `tenantId` is the Blueprint's tenant.
15. **Approval-required gates (R2, R7).** A gate is met by exactly one of: (a) `approved` by a CoE Reviewer for the current `contentHash`; (b) a SelfAttestation for the current `contentHash`, which counts only where R7 allows it: Individual (Free or Paid), and a Team with exactly one billable seat (Admin, CoE Reviewer or Builder; Viewers are not billable). When a second billable member joins, gates need a CoE Reviewer again and earlier self-attestations stop satisfying them. Enterprise never accepts self-attestation. This holds for every class including `restricted`. A self-attestation is labelled "self-attested" and never sets `approved`. Gates come only from `governance.approval.requiredBefore` and `data.sensitivityRules[class].requireApprovalBeforeHandoff`; an org rule is not a source of approval gates at launch because org rules are P2 (S14). Gate values are listed after this list.
16. **Break-glass (R6).** Fixed rules, not settings: a reason is required; the Blueprint owner is notified when access starts, naming the Admin and the reason; access ends automatically at expiry; every read is logged. Only the length is a setting: `governance.breakGlass.timeBoxHours` (default 4 hours, ASSUMPTION; the maximum is 4, so policy can only shorten it). The request is made from the portal Review-queue inventory. Team: a single Admin may approve their own request (audited, owner notified). Enterprise: a second Admin must approve, meaning any other user holding Admin in the tenant and never the requester; with only one Admin the request fails closed. A grant cannot be renewed: after expiry a new request with a new reason (and, at Enterprise, a new second-Admin approval) is needed. The owner is notified and has no veto (ASSUMPTION; S7). Portal events: `break_glass_requested`, `break_glass_approved`, `break_glass_read`, `break_glass_expired`.
17. **Individual Free versus Paid (R1).** Free is permanent, with no account, no card and no trial clock. It has the engine, the no-AI wizard, the chat coach on `local`, `byok_openrouter`, `byok_provider` and `custom_openai_compat`, local Blueprints, local export of every kind (subject to policy), AutoMate draft actions, the signed baseline policy and every user setting. It has no sync, backup, restore, version history, device management or `managed`. Paid adds those (backup window 35 days, up to 3 devices; `managed` once decision 4 is met). Team and Enterprise include Paid. The trial is 14 days of Team for a new organization, once per organization (no card at start, owner-confirmed 2026-10-26). When a trial ends with no subscription, or a payment failure outlasts its grace (14 days, owner-confirmed 2026-10-26), members fall to Individual Free: local data untouched, synced data downloadable for 90 days, then purged with in-app and email notice before the purge (S10, owner decision 2026-10-26). Entitlement token claims: `plan` (`free|individual|team|enterprise`; Free needs no token), `trialEndsAt` (nullable), `seats`, `devices`. Portal events: `trial_started`, `trial_ended`, `payment_failed`, `plan_changed`.
18. **Managed pricing is deferred (R9).** Until the written permission in contract decision 4 exists, no managed price mechanic is specified: no fee rate, markup, minimum charge, wallet or invoice model, top-up, refund or tax treatment (`DEFERRED (R9)`). The metering ledger, gateway metadata and the spend-cap settings stay. No price points, seat prices or fee rates appear anywhere in the design.

Approval gate values (`governance.approval.requiredBefore`). ASSUMPTION: the mapping below; the engine and coach agents confirm it.

| Gate | What it guards |
|---|---|
| `build_handoff` | Entering the `build_handoff` stage (drafting flows in AutoMate, exporting briefs). |
| `handoff_brief` | Creating a `handoff_brief` export. Added in round 3 (R2). |
| `automate_flow_draft` | Creating an `automate_flow_draft` export or writing a draft into AutoMate. Added in round 3 (R2). |
| `export` | Any other export kind: `process_document`, `blueprint_json`. `review_packet` has no gate, because it is how review is requested. |
| `automate_apply` | Applying a draft to AutoMate. |
| `automate_test_run` | Starting an attended test run. |

## 8. Cross-agent assumptions

- ASSUMPTION: the engine agent publishes a Blueprint field registry. Rule `field` paths are checked against it at publish. The engine computes `step.derived.domains[]` from `governance.dataDomains` and the user's confirmation; example paths such as `step.diagnostic.attendance` stand in for the real diagnostic field names. The org-rule editor is P2, so until then the engine's `orgRules` input stays empty.
- ASSUMPTION: Blueprint `environmentProfileRef` holds an `environment.profiles[].id` (a `slug`).
- ASSUMPTION: the rules engine is a library that can also run on the sync server, so org rules and overrides are re-evaluated on a synced Blueprint at status-transition requests only (submit for review, approve), never on every push or merge (architecture X3); a local-only Blueprint is checked on the reviewer's client. This turns soft client rules into hard approval gates for synced Blueprints.
- ASSUMPTION: server-issued approval records are appended to `Blueprint.auditLog[]` and carry a server signature that the AutoMate adapter verifies. The Individual self-attestation (advisory review) is recorded by the client, in the Blueprint owner's name, as audit action `self_attested` with the contract's SelfAttestation details (`blueprintId`, `contentHash`, `attestedBy`, `at`, `statement` at most 400); it never sets `approved`. VERIFY: the Blueprint schema registers the action in `x-actions` and defines the shape (the engine agent's file).
- ASSUMPTION (R8): `environment.profiles[].groupIds` holds ids of portal-managed groups at launch; directory groups arrive with SSO (P2).
- ASSUMPTION (R1, R7): the entitlement token's `seats` is the number of billable seats (Admin, CoE Reviewer, Builder; not Viewers), and the client and the sync service read "exactly one billable seat" from it; `devices` is the allowed device count (3). Architecture 1.6 owns the token design.
- Model keys are namespaced: OpenRouter ids as is (`vendor/model`), direct providers `<providerId>/<id>`, custom endpoints `custom/<id>`, local models `local/<id>`. The built-in managed connection has the id `managed`. Connection ids match `^[a-z0-9][a-z0-9_-]{0,63}$`; `policyRef` is the `orgConnections[].id` a connection was provisioned from.
- ASSUMPTION: `providerId` is an additive field on Connection and orgConnection (required for `byok_provider`, forbidden elsewhere) so that `connections.byokProvider.allowedProviders` and `<providerId>/<id>` model keys have a referent. The contract names `serverKind` but no provider id.
- ASSUMPTION: the `credentialRef` format is `wincred:`, `dpapi:` or `orgvault:` plus a name; it is never a secret and never contains one.
- `environment.customTools` entries take the 8 contract fields, `description` and the 12 optional extension fields of `ToolCatalogEntry` (identical definitions, checked by script). The catalog-maintenance fields `licence`, `entryVersion`, `lastVerified`, `notes` and `sources` are not accepted in a bundle (ASSUMPTION: they describe our seed catalog, not an org's own tools).
- ASSUMPTION: org-defined tool ids use `org.` plus a lowercase slug (`^org\.[a-z0-9][a-z0-9_]{0,59}$`); `skillLevel` is `none | basic | intermediate | advanced`; the UI shows `basic` as Beginner.
- Export kind names for `data.exports.allowedKinds` are the ExportRecord kinds: `handoff_brief`, `process_document`, `review_packet`, `blueprint_json`, `automate_flow_draft`.
- VERIFY: every provider-side control mentioned (zero-retention routing flags, key spend limits, account-level model restrictions) before it appears in customer-facing copy.
- VERIFY: Ed25519 support in the chosen KMS and .NET; until then ES256 (86-character base64url signature tail).

## 9. Examples (validated against the schemas)

The signature is a placeholder with a valid shape, not a real signature; example org, host and model names are placeholders.

### 9.1 Enterprise bundle (`policy.schema.json`)

Uses all three states, two org connections, org rules, an environment profile, two org tools, data domains and the sensitivity matrix. Omitted keys take catalog defaults. It also carries an `x-portal.note` extension key, which clients carry and ignore. It passes both the client and the authoring profile. Org rules and data domains are P2 settings, so the portal accepts them with a warning and they stay inert until the editor ships.

Illustrative values, not defaults: this bundle locks `governance.approval.requiredBefore` to three gates (`handoff_brief`, `automate_flow_draft`, `automate_apply`) and `governance.breakGlass.timeBoxHours` to 2. The catalog and schema defaults are `["automate_apply"]` and 4. A key left out of a bundle takes its default, so a bundle that omits `requiredBefore` gates `automate_apply` only.

```json
{
  "schemaVersion": 1,
  "orgId": "org_example0001",
  "version": 7,
  "issuedAt": "2026-10-25T09:00:00Z",
  "expiresAt": "2026-11-08T09:00:00Z",
  "signature": "eyJhbGciOiJFUzI1NiIsImtpZCI6InBvbC0yMDI2LTEwLWEiLCJ0eXAiOiJjb2FjaC1wb2xpY3krandzIn0..AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
  "settings": {
    "org.tier": {
      "state": "locked",
      "value": "enterprise"
    },
    "connections.managed.enabled": {
      "state": "locked",
      "value": true
    },
    "connections.byokOpenrouter.enabled": {
      "state": "locked",
      "value": false
    },
    "connections.byokProvider.enabled": {
      "state": "locked",
      "value": false
    },
    "connections.customOpenaiCompat.enabled": {
      "state": "locked",
      "value": false
    },
    "connections.local.enabled": {
      "state": "default",
      "value": true
    },
    "connections.allowPersonalKeys": {
      "state": "locked",
      "value": false
    },
    "connections.requireTls": {
      "state": "locked",
      "value": true
    },
    "connections.orgConnections": {
      "state": "locked",
      "value": [
        {
          "id": "corp-gateway",
          "type": "custom_openai_compat",
          "label": "Corporate LLM gateway",
          "endpoint": "https://llm-gateway.corp.example/v1",
          "serverKind": "litellm",
          "authScheme": "token_provider",
          "credentialMode": "integrated_oauth",
          "extraHeaders": {
            "X-Tenant-Id": "corp"
          },
          "modelIdKind": "model",
          "contextWindowOverride": 32768,
          "allowedModels": [
            "custom/*"
          ]
        },
        {
          "id": "corp-azure",
          "type": "custom_openai_compat",
          "label": "Azure OpenAI (corporate tenant)",
          "endpoint": "https://corp-aoai.example.net/openai",
          "serverKind": "azure_openai",
          "authScheme": "token_provider",
          "credentialMode": "integrated_oauth",
          "modelIdKind": "deployment",
          "allowedModels": [
            "custom/gpt-prod"
          ]
        }
      ]
    },
    "models.allowlist": {
      "state": "locked",
      "value": [
        "vendor-a/*",
        "vendor-b/*",
        "custom/*",
        "local/*"
      ]
    },
    "models.denylist": {
      "state": "locked",
      "value": [
        "vendor-a/model-legacy*"
      ]
    },
    "models.minCertification": {
      "state": "locked",
      "value": "works"
    },
    "models.adminApprovedLocal": {
      "state": "locked",
      "value": [
        "local/qwen3.5:9b"
      ]
    },
    "models.adminApprovedLocalCountsAsWorks": {
      "state": "default",
      "value": true
    },
    "models.requireCapabilityProbePass": {
      "state": "locked",
      "value": true
    },
    "models.zeroRetentionProvidersOnly": {
      "state": "locked",
      "value": true
    },
    "models.fallback": {
      "state": "default",
      "value": "fail_loud"
    },
    "spend.orgMonthlyCapUsd": {
      "state": "locked",
      "value": 2000
    },
    "spend.perUserMonthlyCapUsd": {
      "state": "locked",
      "value": 50
    },
    "spend.warnAtPercent": {
      "state": "default",
      "value": 80
    },
    "spend.onCapReached": {
      "state": "locked",
      "value": "block"
    },
    "spend.personalMonthlyCapUsd": {
      "state": "user_choice"
    },
    "data.sensitivityRules": {
      "state": "locked",
      "value": {
        "public": {
          "llmConnectionTypes": [
            "managed",
            "custom_openai_compat",
            "local"
          ],
          "llmContentMode": "full",
          "minModelCertification": "works",
          "requireZeroRetentionProvider": false,
          "previewBeforeSend": false,
          "sync": "on",
          "approvalMetadataSync": true,
          "exportAllowed": true,
          "requireApprovalBeforeHandoff": false,
          "toolDataFlowCeiling": "ai_cloud"
        },
        "internal": {
          "llmConnectionTypes": [
            "managed",
            "custom_openai_compat",
            "local"
          ],
          "llmContentMode": "full",
          "minModelCertification": "works",
          "requireZeroRetentionProvider": false,
          "previewBeforeSend": false,
          "sync": "on",
          "approvalMetadataSync": true,
          "exportAllowed": true,
          "requireApprovalBeforeHandoff": false,
          "toolDataFlowCeiling": "vendor_cloud"
        },
        "confidential": {
          "llmConnectionTypes": [
            "managed",
            "custom_openai_compat",
            "local"
          ],
          "llmContentMode": "redacted",
          "minModelCertification": "works",
          "requireZeroRetentionProvider": true,
          "previewBeforeSend": true,
          "sync": "on",
          "approvalMetadataSync": true,
          "exportAllowed": true,
          "requireApprovalBeforeHandoff": false,
          "toolDataFlowCeiling": "tenant"
        },
        "restricted": {
          "llmConnectionTypes": [
            "custom_openai_compat",
            "local"
          ],
          "llmContentMode": "redacted",
          "minModelCertification": "works",
          "requireZeroRetentionProvider": true,
          "previewBeforeSend": true,
          "sync": "opt_in",
          "approvalMetadataSync": true,
          "exportAllowed": true,
          "requireApprovalBeforeHandoff": true,
          "toolDataFlowCeiling": "local"
        }
      }
    },
    "data.minimumSensitivity": {
      "state": "locked",
      "value": "internal"
    },
    "data.redaction.builtinPatterns": {
      "state": "locked",
      "value": [
        "secret_keys",
        "private_key_blocks",
        "payment_card",
        "us_ssn",
        "iban"
      ]
    },
    "data.redaction.customPatterns": {
      "state": "locked",
      "value": [
        {
          "id": "employee-id",
          "label": "Employee id",
          "kind": "regex",
          "pattern": "\\bEMP-[0-9]{6}\\b",
          "action": "redact",
          "appliesTo": [
            "prompt",
            "transcript",
            "diagnostics"
          ]
        },
        {
          "id": "project-codenames",
          "label": "Project codenames",
          "kind": "keywords",
          "keywords": [
            "Project Falcon",
            "Project Heron"
          ],
          "caseInsensitive": true,
          "action": "redact",
          "appliesTo": [
            "prompt",
            "transcript",
            "export",
            "diagnostics"
          ]
        }
      ]
    },
    "data.redaction.defaultAction": {
      "state": "default",
      "value": "redact"
    },
    "data.exports.allowedKinds": {
      "state": "locked",
      "value": [
        "handoff_brief",
        "process_document",
        "review_packet",
        "automate_flow_draft"
      ]
    },
    "sync.blueprints.enabled": {
      "state": "locked",
      "value": true
    },
    "sync.transcripts.enabled": {
      "state": "locked",
      "value": false
    },
    "retention.transcripts.days": {
      "state": "default",
      "value": 30
    },
    "retention.blueprints.versionsKept": {
      "state": "locked",
      "value": 100
    },
    "retention.auditLog.days": {
      "state": "locked",
      "value": 730
    },
    "telemetry.crashReports": {
      "state": "locked",
      "value": "off"
    },
    "telemetry.usageAnalytics": {
      "state": "locked",
      "value": "off"
    },
    "coach.aiMode": {
      "state": "locked",
      "value": "full"
    },
    "coach.aiFlows.allowedByMode": {
      "state": "default",
      "value": {
        "off": [],
        "lite_only": [
          "rescue"
        ],
        "full": [
          "rescue",
          "second_opinion"
        ]
      }
    },
    "coach.llmOverride.mode": {
      "state": "locked",
      "value": "approval_required"
    },
    "coach.llmOverride.requireJustificationCard": {
      "state": "locked",
      "value": true
    },
    "coach.llmOverride.approverRole": {
      "state": "locked",
      "value": "coe_reviewer"
    },
    "coach.llmAgent.mode": {
      "state": "locked",
      "value": "approval_required"
    },
    "coach.override.reasonMinChars": {
      "state": "locked",
      "value": 25
    },
    "coach.triageOverride.mode": {
      "state": "locked",
      "value": "approval_required"
    },
    "automate.actions.mode": {
      "state": "default",
      "value": "draft_only"
    },
    "automate.testRuns.mode": {
      "state": "locked",
      "value": "attended_only"
    },
    "automate.testRuns.blockProductionSystems": {
      "state": "locked",
      "value": true
    },
    "governance.approval.mode": {
      "state": "locked",
      "value": "by_rule"
    },
    "governance.approval.requiredBefore": {
      "state": "locked",
      "value": [
        "handoff_brief",
        "automate_flow_draft",
        "automate_apply"
      ]
    },
    "governance.adminContentAccess": {
      "state": "locked",
      "value": "break_glass"
    },
    "governance.breakGlass.timeBoxHours": {
      "state": "locked",
      "value": 2
    },
    "governance.auditLog.clientReportedUsage": {
      "state": "locked",
      "value": "metadata"
    },
    "governance.dataDomains": {
      "state": "locked",
      "value": [
        {
          "id": "payroll",
          "label": "Payroll",
          "keywords": [
            "payroll",
            "salary",
            "pay run"
          ],
          "systemIds": [
            "hris"
          ],
          "sensitivityFloor": "confidential"
        },
        {
          "id": "customer-pii",
          "label": "Customer personal data",
          "keywords": [
            "customer address",
            "date of birth"
          ],
          "sensitivityFloor": "confidential"
        }
      ]
    },
    "governance.orgRules": {
      "state": "locked",
      "value": [
        {
          "id": "payroll-human-checkpoint",
          "name": "Payroll steps need a human checkpoint",
          "source": "template",
          "templateId": "require-adjacent-rung-for-domain",
          "severity": "block",
          "appliesTo": "step",
          "stages": [
            "design",
            "build_handoff"
          ],
          "when": {
            "field": "step.derived.domains[]",
            "op": "contains",
            "value": "payroll"
          },
          "then": [
            {
              "type": "require_adjacent_rung",
              "rungId": "human_checkpoint",
              "placement": "after"
            }
          ],
          "message": "{step.name} touches payroll. Add a human checkpoint right after it.",
          "waiver": {
            "allowed": false,
            "roles": []
          }
        },
        {
          "id": "restricted-no-llm-agent",
          "name": "No LLM agents on restricted processes",
          "source": "custom",
          "severity": "block",
          "appliesTo": "step",
          "when": {
            "field": "blueprint.sensitivity",
            "op": "eq",
            "value": "restricted"
          },
          "then": [
            {
              "type": "forbid_rungs",
              "rungIds": [
                "llm_agent"
              ]
            }
          ],
          "message": "{blueprint.title} is restricted, so an LLM agent is not an option here.",
          "waiver": {
            "allowed": false,
            "roles": []
          }
        },
        {
          "id": "unattended-confidential-review",
          "name": "Unattended confidential work needs CoE review",
          "source": "custom",
          "severity": "block",
          "appliesTo": "step",
          "when": {
            "all": [
              {
                "field": "step.diagnostic.attendance",
                "op": "eq",
                "value": "unattended"
              },
              {
                "field": "blueprint.sensitivity",
                "op": "in",
                "value": [
                  "confidential",
                  "restricted"
                ]
              }
            ]
          },
          "then": [
            {
              "type": "require_approval",
              "role": "coe_reviewer"
            },
            {
              "type": "block_gate",
              "gates": [
                "automate_apply",
                "build_handoff"
              ]
            }
          ],
          "message": "{step.name} would run unattended on confidential data. A CoE reviewer must approve it first.",
          "waiver": {
            "allowed": true,
            "roles": [
              "coe_reviewer"
            ]
          }
        }
      ]
    },
    "environment.profiles": {
      "state": "locked",
      "value": [
        {
          "id": "corp-windows-desktop",
          "name": "Corporate Windows desktop",
          "description": "Managed Windows 11 laptops; unattended work runs on the VM pool.",
          "groupIds": [
            "finance-ops"
          ],
          "preferredToolIds": [
            "builtin.excel_power_query",
            "script.python",
            "ui.automate"
          ],
          "os": {
            "family": "windows",
            "versions": [
              "11 23H2",
              "11 24H2"
            ],
            "managedDevices": true,
            "userHasLocalAdmin": "none",
            "softwareInstallPolicy": "request_approval"
          },
          "scripting": {
            "allowed": true,
            "languages": [
              "powershell",
              "python",
              "sql"
            ],
            "powershellExecutionPolicy": "allsigned",
            "signedScriptsOnly": true,
            "unattendedRequiresReview": true
          },
          "software": [
            {
              "softwareId": "spreadsheet",
              "name": "Spreadsheet application",
              "status": "installed",
              "providesToolIds": [
                "builtin.excel_formulas",
                "builtin.excel_power_query"
              ]
            },
            {
              "softwareId": "automate",
              "name": "AutoMate",
              "status": "installed",
              "providesToolIds": [
                "ui.automate"
              ]
            },
            {
              "softwareId": "python",
              "name": "Python runtime",
              "version": "3.12",
              "status": "licensed_not_deployed",
              "providesToolIds": [
                "script.python"
              ]
            },
            {
              "softwareId": "power-automate-desktop",
              "name": "Power Automate Desktop",
              "status": "prohibited",
              "providesToolIds": [
                "ui.power_automate_desktop"
              ]
            }
          ],
          "tools": {
            "forbiddenToolIds": [
              "script.vba_macro"
            ],
            "forbiddenRungIds": []
          },
          "network": {
            "internetAccess": "proxy_only",
            "egressAllowlist": [
              "llm-gateway.corp.example",
              "*.corp.example"
            ],
            "llmEndpointsReachable": [
              "managed",
              "custom_openai_compat",
              "local"
            ]
          },
          "systems": [
            {
              "systemId": "hris",
              "name": "HR system",
              "api": "restricted",
              "apiKinds": [
                "rest"
              ],
              "uiKinds": [
                "web"
              ],
              "authModel": "sso",
              "isProduction": true,
              "domainIds": [
                "payroll"
              ]
            },
            {
              "systemId": "legacy-erp",
              "name": "Legacy ERP",
              "api": "unavailable",
              "uiKinds": [
                "windows_desktop"
              ],
              "authModel": "shared_login",
              "isProduction": true,
              "domainIds": []
            },
            {
              "systemId": "erp-test",
              "name": "ERP test instance",
              "api": "unavailable",
              "uiKinds": [
                "windows_desktop"
              ],
              "authModel": "shared_login",
              "isProduction": false,
              "domainIds": []
            }
          ],
          "automationRunners": [
            {
              "kind": "end_user_attended",
              "platform": "windows",
              "credentialModel": "user_session",
              "unattendedAllowed": false,
              "supportOwner": "builder"
            },
            {
              "kind": "unattended_vm",
              "platform": "windows",
              "credentialModel": "vaulted_secret",
              "unattendedAllowed": true,
              "supportOwner": "it_operations"
            }
          ]
        },
        {
          "id": "contact-center-kiosk",
          "name": "Contact center kiosk",
          "groupIds": [
            "contact-center"
          ],
          "os": {
            "family": "windows",
            "managedDevices": true,
            "userHasLocalAdmin": "none",
            "softwareInstallPolicy": "locked_down"
          },
          "scripting": {
            "allowed": false
          }
        }
      ]
    },
    "environment.defaultProfileId": {
      "state": "locked",
      "value": "corp-windows-desktop"
    },
    "environment.userMayDeclareSoftware": {
      "state": "default",
      "value": true
    },
    "environment.customTools": {
      "state": "locked",
      "value": [
        {
          "toolId": "org.erp_batch_loader",
          "name": "ERP batch loader",
          "rungId": "api_connector",
          "capabilities": [
            "transfer_data",
            "sync_records"
          ],
          "constraints": [
            "Runs only on the unattended VM pool.",
            "Needs a service account in the ERP."
          ],
          "skillLevel": "intermediate",
          "requiresInstall": false,
          "platforms": [
            "windows"
          ],
          "description": "In-house connector that loads batches into the legacy ERP.",
          "systemKinds": [
            "desktop_app",
            "database"
          ],
          "accessModes": [
            "connector",
            "file_or_db"
          ],
          "unattendedSupport": "needs_host",
          "dataFlow": "tenant",
          "handoff": "config_instructions",
          "limits": {
            "maxItemsPerRun": 5000,
            "maxInputSize": "large"
          }
        },
        {
          "toolId": "org.invoice_ocr_service",
          "name": "Invoice OCR service",
          "rungId": "parser_ocr_ml",
          "capabilities": [
            "extract_fields_document",
            "ocr_text"
          ],
          "constraints": [],
          "skillLevel": "basic",
          "requiresInstall": false,
          "platforms": [
            "cloud"
          ]
        }
      ]
    },
    "policy.onExpiry": {
      "state": "locked",
      "value": "no_llm"
    },
    "prefs.coachingStyle": {
      "state": "default",
      "value": "guided"
    },
    "prefs.verbosity": {
      "state": "user_choice"
    },
    "prefs.skillLevel": {
      "state": "user_choice"
    },
    "prefs.preferredModel": {
      "state": "default",
      "value": {
        "connectionId": "corp-gateway",
        "modelId": "custom/model-large"
      }
    },
    "prefs.showEngineTrace": {
      "state": "default",
      "value": false
    },
    "prefs.alerts.events": {
      "state": "default",
      "value": [
        "spend_threshold",
        "approval_decision",
        "review_requested",
        "policy_updated",
        "policy_expiring",
        "model_certification_changed"
      ]
    },
    "prefs.alerts.channels": {
      "state": "default",
      "value": [
        "in_app",
        "windows_toast",
        "email"
      ]
    },
    "prefs.accessibility.reduceMotion": {
      "state": "default",
      "value": "system"
    },
    "prefs.locale.replyLanguage": {
      "state": "locked",
      "value": "en"
    },
    "x-portal.note": {
      "state": "user_choice"
    }
  }
}
```

### 9.2 Individual baseline bundle

Signed, shipped in the installer, accepted only when no org is attached. ASSUMPTION: 180 days validity, refreshed by updates and the content feed; at expiry the app uses compiled-in defaults identical to the baseline (not `no_llm`).

```json
{
  "schemaVersion": 1,
  "orgId": "baseline",
  "version": 3,
  "issuedAt": "2026-10-25T00:00:00Z",
  "expiresAt": "2027-04-23T00:00:00Z",
  "signature": "eyJhbGciOiJFUzI1NiIsImtpZCI6InBvbC0yMDI2LTEwLWEiLCJ0eXAiOiJjb2FjaC1wb2xpY3krandzIn0..AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
  "settings": {
    "org.tier": {
      "state": "locked",
      "value": "individual"
    }
  }
}
```

### 9.3 Connection examples (`connection.schema.json`)

```json
{
  "managed (built-in)": {
    "id": "managed",
    "type": "managed",
    "label": "Coach gateway",
    "serverKind": "openrouter",
    "authScheme": "token_provider",
    "credentialMode": "integrated_oauth",
    "credentialRef": null,
    "modelIdKind": "model",
    "policyRef": null
  },
  "byok_openrouter": {
    "id": "my-openrouter",
    "type": "byok_openrouter",
    "label": "My OpenRouter key",
    "serverKind": "openrouter",
    "authScheme": "bearer",
    "credentialMode": "user_supplied",
    "credentialRef": "wincred:Coach/my-openrouter",
    "extraHeaders": {
      "X-Title": "Coach"
    },
    "modelIdKind": "model",
    "policyRef": null
  },
  "byok_provider": {
    "id": "provider-a",
    "type": "byok_provider",
    "label": "Provider A direct",
    "providerId": "provider-a",
    "endpoint": "https://api.provider-a.example/v1",
    "serverKind": "openai",
    "authScheme": "bearer",
    "credentialMode": "user_supplied",
    "credentialRef": "dpapi:Coach/provider-a",
    "modelIdKind": "model",
    "allowedModels": [
      "provider-a/model-large"
    ],
    "policyRef": null
  },
  "custom_openai_compat (Azure OpenAI)": {
    "id": "corp-azure",
    "type": "custom_openai_compat",
    "label": "Azure OpenAI (corporate tenant)",
    "endpoint": "https://corp-aoai.example.net/openai",
    "serverKind": "azure_openai",
    "authScheme": "api_key_header",
    "credentialMode": "user_supplied",
    "credentialRef": "wincred:Coach/corp-azure",
    "extraHeaders": {
      "X-Cost-Center": "4410"
    },
    "modelIdKind": "deployment",
    "contextWindowOverride": 128000,
    "allowedModels": [
      "custom/gpt-prod"
    ],
    "policyRef": "corp-azure"
  },
  "local (Ollama)": {
    "id": "ollama-local",
    "type": "local",
    "label": "Ollama on this PC",
    "endpoint": "http://localhost:11434/v1",
    "serverKind": "ollama",
    "authScheme": "none",
    "credentialMode": "none",
    "credentialRef": null,
    "modelIdKind": "model",
    "contextWindowOverride": 16384,
    "allowedModels": [
      "local/qwen3.5:9b"
    ],
    "policyRef": null
  }
}
```

## 10. Validation

Both schemas and every embedded example were checked with a hand-written 2020-12 validator (`jsonschema` was not installed and nothing may be installed). VERIFY: re-run with `jsonschema` or Ajv before release.

- Both schemas lint clean (no unknown keywords, no dangling `$ref`, every regex compiles).
- All 94 setting defaults validate against their own value schema.
- Positive cases (10): Enterprise example (client and authoring profiles); Individual baseline bundle; unknown non-x keys pass the client profile; telemetry keys accept locked off, default off and user_choice; override reason minimum accepts the 400 ceiling; approval gates accept handoff_brief, automate_flow_draft and automate_apply; break-glass time box accepts the 4 hour ceiling; reserved profile.scope is accepted; 5 connection examples (managed, byok_openrouter, byok_provider, Azure OpenAI, Ollama); publish lint clean on the Enterprise example (4 p2 warnings).
- Policy negative cases (72), each rejected for the intended reason: locked or default without value; user_choice with a value; force transcript sync on; lock a default-only preference; default state on a locked-only key; state outside the key's allowed states (approverRole); approverRole admin (only a CoE Reviewer approves); unknown rule operator; unknown rule action; rule action require_approval by admin; rule field path with injection characters; version 0; missing signature; missing schemaVersion (now required); schemaVersion as a string; schemaVersion 2 against the v1 schema; attached-payload JWS instead of detached; signature too short for ES256; missing sensitivity class; unknown rung id; refusal value 'disabled' instead of 'forbidden'; coach.aiMode 'disabled'; aiFlows allows a flow in mode off; override reason minimum below 15; override reason minimum above 400 (the Blueprint reason maximum); telemetry anonymous locked on by an admin; telemetry anonymous seeded as an admin default; break-glass time box longer than 4 hours; break-glass time box of 0 hours; break-glass time box as a user_choice with a value; review_packet as an approval gate; toolId with a hyphen; toolId with two dots; toolId with upper case; org tool id without the org. prefix; org tool id longer than 60 characters after org.; org tool missing required constraints; org tool capability outside the 36 tags; org tool dataFlow invalid; org tool with an unknown field; profile id with a dot; profile id starting with a digit; one-character slug; profile preferredToolIds over 40; profile os family other than windows; skill level 'beginner' (old scale); bare model name in the allow list; bare model name in preferredModel; adminApprovedLocal with a non-local key; old export kind name; restricted tool data-flow ceiling above tenant; unknown ceiling value; v1 field syncToCloud; sync as a boolean; approval before handoff without approval metadata sync; content mode none with connection types; orgConnection carries credentialRef; orgConnection over plain http; orgConnection of type local; orgConnection with the reserved id managed; orgConnection azure_openai without deployment kind; orgConnection Authorization header; orgConnection model key in the wrong namespace; telemetry 'identified'; audit retention below 30 days; admin content access 'full_access'; text scale above 200; reply language as a display name; ui language other than en in v1; org.tier outside the three tiers; string where a boolean belongs; x- extension with a bad shape.
- Authoring-profile negative cases (4): unknown settings key from a newer portal; typo in a known key; unknown root member; unknown key with a malformed shape (rejected by both profiles).
- Publish-check negative cases (10): Team org with two environment profiles; Team org with audit retention 730; Team org with custom (non-template) rules; Individual baseline carrying a Team-only key; Team org carrying the Enterprise-only customTools; unknown toolId in providesToolIds; duplicate orgConnection id; defaultProfileId names no profile; data domain names an unknown system; ceiling looser for a stricter class.
- Connection negative cases (30): custom endpoint over plain http; endpoint with user info; local endpoint on a LAN address; local endpoint on a public https host; custom endpoint missing; local with a custom model key; custom with a local model key; managed with a local model key; byok_provider with an openrouter namespace; bare model name; Authorization header; X-Api-Key header; bearer value in an innocent header; azure_openai addressed by model, not deployment; bearer scheme with no credential; token_provider with a stored credentialRef; credentialRef holding a raw secret; user_supplied key pointing at the org vault; byok_provider without providerId; providerId reserved (local); providerId on a local connection; id with upper case; id longer than 64; missing serverKind; local with serverKind azure_openai; byok_openrouter with serverKind openai; contextWindowOverride below 1024; unknown property; authScheme outside the enum; label empty.
- Pattern table: 73 valid and invalid values across toolId, orgToolId, slug, connectionId, modelKey, modelKeyGlob, credentialRef, httpsEndpoint and loopbackEndpoint.

## 11. Changes since v1

- Bundle settings 82 -> 94. Added: `models.adminApprovedLocal`, `models.adminApprovedLocalCountsAsWorks`, `coach.aiMode`, `coach.aiFlows.allowedByMode`, `governance.adminContentAccess`, `governance.breakGlass.timeBoxHours`, `prefs.accessibility.reduceMotion`, `prefs.accessibility.highContrast`, `prefs.accessibility.textScalePercent`, `prefs.accessibility.screenReaderMode`, `prefs.locale.uiLanguage`, `prefs.locale.replyLanguage`, `prefs.locale.formats`. Removed: `governance.approval.allowSelfApproval`. Keys present in both may have changed type, default or tier; the tables above are authoritative.
- Contract v2 alignment: shared id patterns (`toolId`, `orgToolId`, `slug`, `connectionId`) are textually the contract's; skill scale `none | basic | intermediate | advanced`; `forbidden` is the refusal value in every enum; namespaced model keys; `schemaVersion` is required; `value` rule enforced both ways; unknown non-`x-` keys are ignored by clients (client versus authoring profile); `data.exports.allowedKinds` uses ExportRecord kinds.
- Engine and coach inputs: `data.sensitivityRules[class].toolDataFlowCeiling` (finding F-40), `coach.aiMode` plus `coach.aiFlows.allowedByMode` (F-41, DC-46, DC-50), `coach.override.reasonMinChars` 15 to 400, `preferredToolIds` on an environment profile, `environment.customTools` accepts the catalog extension fields (dataFlow default `vendor_cloud`, unattendedSupport default `no`).
- Governance: `allowSelfApproval` removed (separation of duties is fixed); `approverRole` has one value; `governance.adminContentAccess` (metadata plus audited break-glass); multi-reviewer, review SLA, intake, templates, org rules and data domains are P2 (hidden until built); sensitivity-rule editing starts at Team.
- Data: per-class `sync` (`on | opt_in | forbidden`) replaces the v1 boolean, plus `approvalMetadataSync`; `restricted` defaults to local only with opt-in; telemetry off; audit retention default and Team cap 365 days; deleted-grace wording matches the 35-day backup window.
- Accessibility and localization settings under `prefs.accessibility.*` and `prefs.locale.*`.
- Second patch round (closure reviews): `coach.override.mode` accepts `forbidden`; `coach.override.reasonMinChars` is 15 to 400 (NEW-6); both telemetry keys accept only `off` when locked or defaulted, are selectable as `anonymous` only by the user, and are P2 because no sink exists at launch (N-08); invariant 13 adds the approval-metadata rule for a locked-off `sync.blueprints.enabled` (N-06); the registry key has a placeholder path (N-13); the self-attestation wording follows the contract's SelfAttestation definition (NEW-2).
- Tenant rows added: `tenant.managed.flag`, `tenant.devices.maxPerUser`, `tenant.entitlement.offlineGraceDays`, `tenant.trial.days`; vault, CMK, SSO enforcement, SCIM, role mapping, IP allow-list, SIEM stream and legal hold are P2; `tenant.dataRegion` has one region at launch.
- Third patch round (owner rulings R1 to R9, contract section 10): Individual splits into Free and Paid (`x-minPlan`; four settings need Paid: `connections.managed.enabled`, `spend.personalMonthlyCapUsd`, `sync.blueprints.enabled`, `sync.transcripts.enabled`); new setting `governance.breakGlass.timeBoxHours` (R6); `governance.approval.requiredBefore` gains `handoff_brief` and `automate_flow_draft` (R2); the `restricted` default for `exportAllowed` changes from no to yes because a local export never uploads (R2); invariants 14 to 18 and the gate table; tenant rows `tenant.signIn.methods`, `tenant.billing.paymentFailureGraceDays` and `tenant.viewers.fairUseCap` added, `tenant.trial.days` becomes the Team organization trial, and SAML and OIDC single sign-on, SCIM and role mapping are P2 (R8); managed price mechanics are `DEFERRED (R9)`. Follow-up: the example in 9.1 is labelled as non-default (the `requiredBefore` default stays `["automate_apply"]`); S6 (delete backed-up copies), S7 (break-glass details), S8 (three grace clocks), S10 (purge after the download window) and S14 (org rules are not a gate source at launch) are applied. Before round 3 there were 93 settings (82 launch, 11 P2); now 94 (83 launch, 11 P2).
