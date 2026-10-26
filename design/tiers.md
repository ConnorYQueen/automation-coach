# Tiers, roles, enforcement and policy delivery

Status: design v2, 2026-10-25 (patch round against `design/00-shared-contract.md` v2 and the findings in `design/99a-data-contract-review.md` and `design/99b-decision-consistency-review.md`). Companion to `design/settings-catalog.md` (every setting), `design/policy.schema.json` (bundle format) and `design/connection.schema.json` (the Connection entity). Entities use the contract's names. No prices: the owner decides. Section numbers 1 to 9 are stable; other documents cite them. Second patch round (2026-10-25, closure reviews): self-attestation by the owner role (NEW-2), managed as the hard path only once available (N-04), server engine at status transitions only (N-05), certification registry as architecture X2 (N-07), telemetry reserved (N-08), registry placeholder path with script deployment (N-13), one table of grace clocks in section 4.5 (N-14). Third patch round (2026-10-25, owner rulings R1 to R9 in contract section 10, which wins over everything else): Individual Free versus Individual Paid and the Team organization trial (R1), restricted export and approval gates for handoff and AutoMate drafts (R2), break-glass time box and the Enterprise second Admin (R6), self-attestation for a Team with one billable seat and free Viewers (R7), SSO deferred (R8), managed pricing mechanics deferred (R9). Anything not confirmed from a source is marked `ASSUMPTION:` or `VERIFY:`; deferred pricing mechanics are marked `DEFERRED (R9)`.

## 1. Tier feature matrix

Setting counts from the catalog (94 bundle settings): 43 apply from Individual (39 to Free and Paid, 4 only to Individual Paid), 50 more from Team, 1 more from Enterprise (`environment.customTools`). 83 are built at launch and 11 are P2 (in the schema, hidden in the portal, inert in the client until built). A setting below its minimum tier is inert and rejected at publish. In the catalog a minimum tier of "Individual" means Free and Paid; "Individual (Paid)" marks the settings that belong to sync, backup, restore, version history, devices or `managed` and so need Individual Paid or above (ruling R1). Plan (`free`, `individual`, `team`, `enterprise`) is an entitlement fact, separate from the bundle's `org.tier`. Most Enterprise value is not a new toggle but a higher limit, a longer retention or a server-side service; section 1.3 lists honestly what Enterprise adds at launch. Tenant-only settings are in catalog section 5.

Round 3 supersedes the v2 offer of a 14-day Individual trial plus a free wizard. No price point, seat price or fee rate is set anywhere in this design.

| Area | Individual Free | Individual Paid | Team | Enterprise |
|---|---|---|---|---|
| Who it is for | One person on their own machine. No account, no admin. | One person who wants backup, sync, history and several devices. A personal tenant of one. | A department or small company; one org; one or more admins. | Large org with central IT, security and a Center of Excellence. Sold through design-partner pilots at launch (R8). |
| Free offer and trial | Permanent. No account, no card, no trial clock, no free managed credits. | No Individual trial (removed by R1). Starts when the user subscribes. | 14-day trial of Team for a new organization, once per organization (R1). No card at start (owner-confirmed 2026-10-26). When it ends with no subscription, members fall to Individual Free: local data untouched, synced data downloadable for 90 days, then purged (S10). | Design-partner pilot, sales-assisted (R8; ASSUMPTION). |
| Sign-in | None needed. Local, BYOK, `custom_openai_compat` and no-model use never ask for an account. | Required (sync, backup, devices, `managed`). Email or social sign-in. | Required (org membership). Org invites, verified domains, Microsoft and Google sign-in. | Same as Team at launch. SAML and OIDC single sign-on, SCIM and IdP group-to-role mapping are P2 and not sold at launch (R8). |
| Devices | Not managed (no account, nothing to count). | Up to 3. | Up to 3 per user. | Up to 3 per user (ASSUMPTION: same limit). |
| Roles | One owner, acts as Admin and Builder. No role UI. | Same as Free. | `admin`, `coe_reviewer`, `builder`, `viewer`. A person can hold several. Viewer seats are free and not billed (R7). | The same four roles, assigned in the portal. IdP group-to-role mapping is P2. |
| Connection types | `local`, `byok_openrouter`, `byok_provider`, `custom_openai_compat`. No `managed`. | All five. `managed` only once decision 4 is met (behind a flag until written upstream permission is on file). | All five (same `managed` condition). Admin can switch types off and disable personal keys. | All five. Adds org connections with integrated OAuth; the org key vault is P2 (section 5). |
| Chat coach on BYOK, local or custom endpoints | Yes, free forever (R1). | Yes. | Yes. | Yes. |
| Model controls | User-level: preferred model, certification floor. | Same as Free. | Org allow and deny lists, certification floor, price ceiling, zero-retention routing, admin-approved local models. Lockable. | Same. |
| AI mode | No setting (the lockable `coach.aiMode` starts at Team). The user picks wizard, lite or full in the Coach; with no usable connection it is the wizard. | Same as Free. | Lockable by the admin, per-mode allow list for rescue and second opinion. | Same. |
| Spend | BYOK estimate cap only; there is no `managed` use. | Personal cap on `managed` usage (once available) and the BYOK estimate cap. Managed price mechanics: `DEFERRED (R9)`. | Org, per-user and per-session caps on `managed`, usage by user, warn thresholds. The metering ledger and the caps stay; price mechanics `DEFERRED (R9)`. | Same; per-group budgets are deferred (ASSUMPTION). |
| Policy bundle | Signed baseline bundle in the installer (`orgId` `baseline`); user settings stay local. No admin locks. | Same as Free. | Signed org bundle, all three states on every Team-level setting. | Full catalog, offline file distribution, machine enrollment with `PolicyFile`. |
| Machine enrollment | Not applicable (no org). | Not applicable (no org). | Registry `OrgId` and `RequireOrgPolicy` at launch, deployed by script until ADMX and Intune packaging ship (section 4.3). | Same, plus `PolicyFile`. |
| Environment profile | One personal profile, local, user-edited, same schema. | Same as Free. | One org profile. | Many profiles (by portal-managed group at launch, ASSUMPTION; directory groups arrive with SSO), org-owned custom tools. |
| Org rules and data domains | None (engine defaults only). | Same as Free. | Template rules, up to 20. The editor is P2: hidden and inert until built. | Custom declarative predicates, up to 200 rules. Editor P2. |
| Sensitivity rules | Defaults of the signed baseline; **not editable**. | Same as Free. | Org-locked matrix, minimum class, per-class sync, ceiling and export. | Same. |
| Redaction | Built-in detectors. | Same as Free. | Adds org custom patterns. | Adds a gateway-side in-transit scan for `managed` (P2, owner-approved exception, counts only). |
| Blueprint backup and sync | None. Blueprints stay on the device and nothing uploads. Local export of every kind, subject to policy. | Yes, every class; `restricted` stays local until a one-click opt-in; approval metadata may sync for any class; restore and version history; 35-day backup window. Needs an account and an entitlement token. | Same, plus retention, deleted-grace and version controls. | Same; P2: customer-managed keys, data region choice, legal hold. |
| Transcripts | Local, user-set retention. | Local by default; sync only if the user opts in. | Admin can lock sync off and set local retention. | Same. |
| Telemetry | Off. No telemetry sink exists at launch, so both telemetry settings are reserved (P2): hidden and inert. Later, only the user may opt in to `anonymous`. | Same as Free. | An admin can lock or default it to `off`, never to `anonymous`. | Same. |
| Review and approval | Advisory review with a recorded self-attestation by the Blueprint owner (audit action `self_attested`; never sets `approved`). | Same as Free. | One reviewer: a CoE Reviewer, never the author, issues the server-signed ApprovalRecord. A Team with exactly one billable seat may self-attest instead (R7); when a second billable member joins, a CoE Reviewer is needed again. | Same at launch, but self-attestation is never accepted. Multi-reviewer approval and review SLA are P2 (hidden until built). |
| LLM-first override | Justification card, self-attested. | Same as Free. | Approval by a CoE Reviewer (self-attestation with one billable seat, R7). | Approval by a CoE Reviewer only; scoped approvers are deferred. |
| Admin access to Blueprint content | Not applicable. | Not applicable. | Metadata always; content only by audited break-glass: reason required, owner notified, time box (`governance.breakGlass.timeBoxHours`, default 4, can only be shortened), automatic expiry, every read logged. A single Admin may approve their own request. A grant cannot be renewed (S7). An admin can remove break-glass. | Same, but a different Admin (any other user holding Admin) must approve; with only one Admin the request fails closed (R6, S7). |
| Viewer seats | Not applicable. | Not applicable. | Free and not billed (R7). No cap at launch (owner-confirmed 2026-10-26); the terms limit free Viewers to reading and review. | Same. |
| Intake and templates | No. | No. | P2. | P2. |
| Rescue and second opinion | Yes, both (the default per-mode list for full mode). | Same as Free. | Yes, gated per `coach.aiMode` and `coach.aiFlows.allowedByMode`; the cross-model check obeys `data.sensitivityRules`. | Same. |
| Audit log | Per-Blueprint `auditLog[]` only. | Same as Free. | Org audit log in the portal, 365 days, CSV export. | Up to 3650 days; API; SIEM stream and hash chain are P2. |
| AutoMate actions | Draft-only default, diff approval, attended test runs. | Same as Free. | Same; admin can lock the mode and the allowed action kinds; approval records before apply. | Same. |
| Data region | Not applicable. | One region at launch (field present). | One region. | One at launch; choice is P2. |
| Customer-managed keys | No. | No. | No. | P2 add-on, after a security review. Do not sign contracts requiring it before it ships. |
| Accessibility and language | WCAG 2.2 AA target, English UI, replies in the user's language (best effort). | Same as Free. | Same; an org may lock the reply language. | Same. |
| DPA and security review | Standard terms. | Standard terms. | Standard DPA (states the 35-day backup window). | Negotiated DPA, sub-processor notices, security questionnaire support. |

### 1.1 Candidate pricing axes (owner decides; no amounts)

Axes only. No price point, seat price or fee rate is set anywhere in this design (R1). Platform subscription billing is live at launch and does not depend on the `managed` flag. Managed usage billing stays dark until decision 4, and its mechanics are `DEFERRED (R9)`: no fee rate, markup, minimum charge, wallet or invoice model, top-up, refund or tax treatment. "Cost plus a transaction fee" stays as product intent only. BYOK and local carry no usage fee.
1. Individual Paid price.
2. Seats by role: Admin, CoE Reviewer and Builder are billable seats; Viewer seats are free and not billed (R7; no cap at launch, owner-confirmed 2026-10-26).
3. Org platform fee by tier.
4. Included Blueprint storage and version history.
5. Number of org rules, profiles and templates (once the editors ship).
6. Audit-log retention length and SIEM export.
7. Add-ons: customer-managed keys, org key vault, data region choice, SSO and SCIM (all after launch).

### 1.2 Plans, sign-in, entitlement token, devices, trial and downgrade

Contract decision 10 and ruling R1: sign-in is not required for local, BYOK, `custom_openai_compat` or no-model use; an account is required for sync, backup, restore, version history, device management, `managed` and orgs; the entitlement token carries its own offline grace (clock 2 in the section 4.5 table); up to 3 devices per user. Architecture 1.6 owns the token design; this is the tier view.

| Use | Plan | Account | Entitlement token | Notes |
|---|---|---|---|---|
| No-model wizard, engine, local Blueprints, local export of every kind (subject to policy), AutoMate draft actions, signed baseline policy, every user setting | `free` | No | No | Permanent; works with no network. |
| Chat coach on `local`, `byok_openrouter`, `byok_provider` or `custom_openai_compat` | `free` | No (yes if the machine is enrolled with `RequireOrgPolicy`) | No | Calls go direct; we are not in the path. Free forever (R1). |
| Blueprint sync, backup (35-day window), restore, version history, up to 3 devices | `individual` or above | Yes | Yes | Sync pauses and goes read-only when the token expires; export always works. |
| `managed` | `individual` or above | Yes | Yes, with the `managed` claim | Only after decision 4 is met (per-tenant flag). |
| Org membership, org policy, review, portal | `team`, `enterprise` | Yes | Yes | |
| Trial of Team | `team`, with `trialEndsAt` set | Yes | Yes | 14 days, once per organization (R1). ASSUMPTION: no card at start. |

- Token claims (R1): `plan` (`free|individual|team|enterprise`; Free needs no token, so in practice the token says `individual`, `team` or `enterprise`), `trialEndsAt` (nullable), `seats` and `devices`. The token is ES256 and device-bound; its other claims and lifetime are architecture 1.6's. ASSUMPTION: `seats` is the number of billable seats (Admin, CoE Reviewer, Builder; not Viewers), which is how the client and the sync service know a Team has exactly one billable seat (R7). ASSUMPTION: `devices` is the allowed device count (3).
- Devices: up to 3 active per user on Individual Paid and above; a 4th registration needs one deactivated (account page or the Users and roles screen). A revoked device is refused online at once and loses paid features at its token expiry. Individual Free has no device management.
- Billing: platform subscription billing is live at launch and does not depend on the `managed` flag (R1). Portal events: `trial_started`, `trial_ended`, `payment_failed`, `plan_changed`.
- Fall to Individual Free: a Team trial that ends with no subscription, a payment failure that outlasts its grace (clock 3 in section 4.5) or a cancelled subscription returns members to Individual Free. The org bundle stops applying and the client returns to the signed baseline (ASSUMPTION). Local Blueprints, local export of every kind, AutoMate draft actions, BYOK, local and custom connections and every user setting keep working, and local data is untouched. Sync, backup, restore, version history, device management and `managed` stop. Synced data stays downloadable for 90 days (owner decision 2026-10-26; the separate 35-day backup window is unaffected). After that it is purged, with in-app and email notice before the purge (S10).
- Unlock floor (closes the former open question 5): chat coaching on `local`, BYOK or `custom_openai_compat` is free forever, so Individual Paid is sync, backup, restore, version history, up to 3 devices and `managed`.

### 1.3 What Enterprise adds over Team at launch (R8)

The honest list is short. SAML and OIDC single sign-on, SCIM, IdP group-to-role mapping, customer-managed keys, the org key vault, the SIEM stream and multi-reviewer approval are all P2 and are not sold at launch. At launch Enterprise is Team plus:
1. Several environment profiles (by portal-managed group) and org-owned custom tools (`environment.customTools`).
2. Audit-log retention up to 3650 days (Team is capped at 365).
3. A policy-bundle grace you can set from 1 to 90 days (Team is fixed at 14), offline policy-file distribution (`PolicyFile`) and the offline activation file for air-gapped sites.
4. Stricter fixed rules: break-glass needs a second Admin, and self-attestation is never accepted.
5. Higher limits ready for the P2 editors (up to 200 org rules, against 20 at Team).
6. A negotiated DPA, sub-processor notices and security questionnaire support.

So Enterprise is sold through design-partner pilots, with no standard contract and no promise of SSO or CMK (R8). A prospect who needs SSO, SCIM or CMK on day one is told "not yet".

### 1.4 Seats for costing, platform ceilings and Enterprise exceptions

Added 2026-10-26 so cost and price can be set per seat for every customer (architecture section 8, the Azure multi-tenant ISV pass). It sets no price, fee rate or ceiling value (R1, R9).
1. **Seat for costing.** A billable seat is a member in the role Admin, CoE Reviewer or Builder in a Team or Enterprise tenant. An Individual Paid user is one billable seat (a tenant of one). A Viewer is not a seat and is not billed (R7); its cost is loaded onto the tenant's billable seats, and the cost reports show Viewers per billable seat. Individual Free has no account and no tenant, so its cost is a free-tier overhead pool and not a per-seat figure. The entitlement `seats` claim is the number of paid seats; the cost reports compare it with the seats in use (architecture 8.8.1).
2. **Platform ceilings.** Each plan has ceilings on sync and portal requests and on concurrent heavy jobs (export, restore, rebuild). They are service configuration, not tenant settings, so the settings catalog has no row for them and no Admin can change them. A value is published in the terms only where a plan promises one. A request over a ceiling gets HTTP 429 `rate_limited` with `Retry-After` and nothing is lost (architecture 8.4). No value is set at this stage.
3. **Enterprise exceptions priced as separate SKUs, only when offered.** A dedicated stamp and a data region choice. Neither is sold at launch; the design keeps both possible (architecture 8.3, 8.11).
4. **Sales channel (owner-decided 2026-10-26): our own payment provider at launch.** The Azure Marketplace is a later addition through the subscription-source seam (architecture 7.1 item 17, 8.7), so nothing in this file changes for launch. If the Marketplace is added later, two things here would change: a transactable trial converts to paid on its own, which conflicts with the 14-day Team trial that takes no card and falls to Free (a hybrid keeps the trial in the product and creates the Marketplace subscription at purchase; to be verified), and the customer changes seat quantity in Microsoft's admin center, so the `seats` claim follows the accepted quantity. Both would need their own owner decision at that time.

## 2. Roles and permissions

Wire ids: `admin`, `coe_reviewer`, `builder`, `viewer`. Roles are additive and a person can hold several. Admin includes every Builder permission except where marked. CoE Reviewer is Builder plus review. Y = allowed, `-` = not allowed, "own" = own objects only, "draft" = may edit a draft that an Admin publishes. Enforcement is on the server for anything synced (portal, sync service, gateway). Local-only objects cannot be protected from the person on the machine, and the product says so. Rows marked (P2) exist in the schema but their feature is not built at launch.

| Permission | Admin | CoE Reviewer | Builder | Viewer |
|---|---|---|---|---|
| **Org administration** | | | | |
| Manage plan and billing | Y | - | - | - |
| Invite users, assign roles, deactivate | Y | - | - | - |
| Deactivate a device | any user | own | own | own |
| Claim domains and set invite rules (SAML and OIDC single sign-on, SCIM and group-to-role mapping are P2, R8) | Y | - | - | - |
| Download the signed offline policy bundle and activation files | Y | - | - | - |
| Publish policy (settings, locks, state changes) | Y | draft | - | - |
| Edit environment profile | Y | draft | - | - |
| Edit org rules and data domains (P2) | Y | draft | - | - |
| Manage org connections; manage the org key vault (P2) | Y | - | - | - |
| View org spend and usage | Y | Y | own | - |
| View org audit log | Y | review events | own events | - |
| Export or delete org data, set retention, legal hold (hold P2) | Y | - | - | - |
| **Governance** | | | | |
| Approve or reject Blueprints in the review queue (only this sets `approved`) | - | Y (not own) | - | - |
| Approve LLM-first, triage and other overrides | - | Y (not own) | - | - |
| Waive a rule violation (only where the rule's `waiver` allows) (P2) | Y | Y | - | - |
| Triage the intake queue (P2) | Y | Y | - | - |
| Author org templates (P2) | Y | Y | - | - |
| Request break-glass read (Admin only; Team: the same Admin may approve; Enterprise: a different Admin approves; fails closed with one Admin; R6) | Y | - | - | - |
| Open a `review_packet` read-only and unmodified (R2) | - | Y | - | - |
| **Blueprints** | | | | |
| Create a Blueprint and run the Coach | Y | Y | Y | - |
| Edit own Blueprint | Y | Y | Y | - |
| Edit a Blueprint shared with an edit grant | Y | Y | Y | - |
| Read and comment on Blueprints shared with them | Y | Y | Y | Y (comment too) |
| Read any synced org Blueprint | metadata; content by break-glass | once in review | - | - |
| Submit for review | Y | Y | Y | - |
| Record self-attestation (Blueprint owner, whatever role they hold; Individual Free or Paid, or Team with one billable seat; not Team with two or more billable seats; not Enterprise; never sets `approved`; R7) | own | own | own | - |
| Share inside the org | Y | Y | own | - |
| Export locally and build a `review_packet` locally (owner; unless `data.exports.allowedKinds` excludes the kind or an admin set the class's `exportAllowed` to no; never uploads, including `restricted`; R2) | Y | Y | own | - |
| Raise sensitivity (any role that may edit the Blueprint, including through the model tool; R4) | Y | Y | Y | - |
| Undo a model's sensitivity raise (any role that may edit the Blueprint; it only restores the earlier class; R4, S14) | Y | Y | Y | - |
| Lower sensitivity (Blueprint owner, panel only; R4) | own | own | own | - |
| Delete (soft delete, then `retention.blueprints.trashWindowDays`) | any | - | own | - |
| **Coach and AutoMate** | | | | |
| Use a model connection (spends budget) | Y | Y | Y | - |
| Use `managed` connection (Individual Paid, Team, Enterprise, and only after decision 4; R1) | Y | Y | Y | - |
| AutoMate draft and apply actions | Y | Y | Y | - |
| Start an attended AutoMate test run | Y | Y | Y | - |
| Change own unlocked settings and preferences | Y | Y | Y | Y (UI prefs only) |

The five rows that round 3 changes, with the contract's rule text verbatim (contract section 10, "Permission-matrix rows that change"). The coach agent generates role rules from the matrix above and from this table, so the two must match:

| Action | Rule |
|---|---|
| Record self-attestation | Blueprint owner; Individual (Free or Paid) and Team with one billable seat; not Team with two or more billable seats; not Enterprise |
| Request break-glass read | Admin only; Team: same Admin may approve; Enterprise: a different Admin approves |
| Raise sensitivity | Any role that may edit the Blueprint, including through the model tool (R4) |
| Lower sensitivity | Blueprint owner, panel only |
| Use `managed` connection | Individual Paid, Team, Enterprise, and only after decision 4 |

Rules:
- **Only a CoE Reviewer sets `approved`**, and never on a Blueprint they own (ASSUMPTION: nor on one whose current revision they last edited). An Admin who also holds the CoE Reviewer role approves through that role. This is fixed, not a setting: the v1 key `governance.approval.allowSelfApproval` is removed. The sync server enforces it.
- Approval is a server-issued, signed record appended to `Blueprint.auditLog[]`. The AutoMate adapter checks that record and recomputes `contentHash`, not just `Blueprint.status`, because anyone can edit a local JSON file. Approval metadata (hash, status, signer) syncs for every sensitivity class, including a local-only `restricted` Blueprint, so the check can succeed (default `approvalMetadataSync` yes).
- **Self-attestation (Individual and a one-seat Team; R7)**: Individual (Free or Paid) has one owner and no reviewer. A Team with exactly one billable seat (Admin, CoE Reviewer or Builder; Viewers are not billable) is treated the same way. The owner may record a self-attestation to meet an approval-required gate. It is stored in `Blueprint.auditLog[]` as audit action `self_attested`; the details object is the contract's SelfAttestation, `{blueprintId, contentHash, attestedBy, at, statement}`, with `statement` at most 400 characters. It is labelled "self-attested", never sets `approved`, and satisfies a gate only for the `contentHash` it was recorded against. Only the owner can record one, whatever role they hold, and nobody can record one for someone else. When a second billable member joins a Team, approval-required gates need a CoE Reviewer again and earlier self-attestations stop satisfying them. Enterprise never accepts self-attestation. A rule condition such as `coe_review_required` (org rules are P2) shows as advisory on Individual and does not block there. VERIFY: the Blueprint schema registers `self_attested` in `x-actions` and defines the SelfAttestation shape (the engine agent's file). This closes the former open question about a Team of one.
- **Admin content access and break-glass (R6)**: an Admin always sees Blueprint metadata (title, owner, status, class, dates, size, review state). Content is readable by the owner, explicit shares, and CoE Reviewers once the Blueprint is in review. An Admin reads content only by break-glass, with these fixed rules: a stated reason is required (at least 15 characters, ASSUMPTION); the owner is notified when access starts, naming the Admin and the reason (the owner is told and has no veto; ASSUMPTION); access ends automatically at the time box; and every read is logged. The time box is the one setting, `governance.breakGlass.timeBoxHours` (default 4 hours, ASSUMPTION; policy can only shorten it, never lengthen it). At Team a single Admin may grant themselves access (audited, owner notified). At Enterprise a different Admin must approve, and with only one Admin the request fails closed. The request is made from the portal Review-queue inventory (S7). The second Admin is any other user holding Admin in the tenant, never the requester (S7). A grant cannot be renewed: after expiry a new request with a new reason (and, at Enterprise, a new second-Admin approval) is needed (S7). Portal events, in order: `break_glass_requested`, `break_glass_approved`, `break_glass_read` (one per read), `break_glass_expired`. `governance.adminContentAccess` set to `metadata_only` removes break-glass; no setting widens access beyond this.
- **Restricted data, export and review packets (R2)**: `restricted` content never uploads unless the owner or an admin opts in. The owner may always export locally and build a `review_packet` locally, unless `data.exports.allowedKinds` excludes that kind (or an admin set the class's `exportAllowed` to no). Neither action uploads anything, and `sensitivityAtExport` records `restricted`. To review a local-only restricted Blueprint, the owner gives the packet to a CoE Reviewer outside Coach, or opts in to sync. The packet opens read-only and unmodified in the reviewer's Coach, so the recomputed `contentHash` equals the owner's; the reviewer's ApprovalRecord is bound to that hash and syncs as approval metadata; the owner's client applies it only when its local `contentHash` matches and the record's `tenantId` is the Blueprint's tenant. An approval-required gate for `handoff_brief`, `automate_flow_draft` or `automate_apply` (from `governance.approval.requiredBefore` or the class rule `data.sensitivityRules[class].requireApprovalBeforeHandoff`; an org rule is not a source of approval gates at launch because org rules are P2, S14) is met by exactly one of: `approved` by a CoE Reviewer for the current `contentHash`, or a SelfAttestation for it where R7 allows. This holds for every class including `restricted`. No new setting was needed: `data.exports.allowedKinds` already names all five kinds; the gate list gained `handoff_brief` and `automate_flow_draft` (catalog section 7).
- Viewer cannot export (finding F-52), cannot approve and cannot spend model budget. Viewer seats are free and not billed (R7). No cap on free Viewers at launch (owner-confirmed 2026-10-26); the terms limit them to reading and review.

Changes to this matrix since v1, for anyone generating role rules from it (`coach-tools.json`, `coach-spec.md`):
1. Approve or reject Blueprints: Admin changed from "Y (not own)" to "-"; only a CoE Reviewer (contract decision 9, DC-21).
2. Approve overrides: Admin changed from "Y" to "-"; `coach.llmOverride.approverRole` has the single value `coe_reviewer`; CoE Reviewer is now "(not own)".
3. Read any synced org Blueprint: Admin changed from "Y" to metadata plus audited break-glass (DC-13); CoE Reviewer wording "in the queue" is now "once in review".
4. AutoMate draft and apply actions: CoE Reviewer changed from "-" to "Y" (CoE Reviewer is Builder plus review). Every Coach tool whose rule says "Builder or Admin" should read "Builder, CoE Reviewer or Admin"; the "CoE Reviewer is read-only in the Coach" assumption no longer holds (F-51).
5. New rows: break-glass read; deactivate a device; download offline files; Individual self-attestation (owner role, any column; contract v2). Rows tagged (P2) mark features cut from launch.
6. Unchanged on purpose: Viewer has no export and no Coach use; Builder and Viewer columns are otherwise as in v1.
7. Round 3: "Record self-attestation" now depends on plan and billable seats (R7); "Request break-glass read" replaces the break-glass row and adds the Enterprise second Admin (R6); new rows "Raise sensitivity", "Undo a model's sensitivity raise" (S14) and "Lower sensitivity" (R4), "Use `managed` connection" (R1) and "Open a `review_packet` read-only" (R2); the export row states the local, no-upload rule (R2).

## 3. Enforcement by connection type

### 3.1 Legend

- **Hard** (H): enforced on a server that we or the org run. Bypass needs a server compromise or stolen credentials.
- **Soft** (S): enforced by Coach code on the user's machine. A person who can modify the client, its local state or its network path can defeat it.
- **External** (X): only enforceable at a control the org owns outside Coach (provider key policy, org gateway, firewall). Coach can recommend the setting but cannot verify it.
- `-`: not applicable.

### 3.2 Matrix

| Control | `managed` | `byok_openrouter` | `byok_provider` | `custom_openai_compat` | `local` |
|---|---|---|---|---|---|
| Type switched off for the org | H: gateway refuses the org. | S, plus X: block the host at the firewall. | S, plus X: block provider hosts. | S, plus X: the org decides who gets credentials to its own gateway. | S only. Nothing can stop a localhost process; data stays on the device. |
| AI off (`coach.aiMode` = off) | H: gateway refuses calls for an org that is off. | S. | S. | S. | S. |
| Personal keys disabled (`connections.allowPersonalKeys`) | - | S. | S. | S. | - |
| Model allow and deny lists | H. | S. X: account-level model or provider restrictions at the provider. VERIFY they exist. | S. X: provider project-level restrictions. VERIFY. | S. X: the gateway exposes only approved deployments, which is hard in practice. | S only. The user can load any model. |
| Certification floor | H: the gateway reads the signed certification registry (one file in the content feed, signed with the content key; architecture X2). | S: the client reads the same registry. | S: same registry. | S: same registry. | S: same registry. |
| Spend caps | H: gateway meters and blocks. | S estimate only. X: per-key spend limit at the provider. VERIFY. | S estimate only. X: provider budget. | X: org gateway budgets. | - |
| Sensitivity class to connection routing | H for routing by the class the client declares. The gateway cannot verify that class. | S. | S. | S. | S. |
| Zero-retention routing | H: always forced (data-collection deny); gateway routing. VERIFY provider flags. | S: request flag. VERIFY. | X. | X. | - (data stays local). |
| Redaction before send | S now. H possible later: gateway scans prompts in transit and persists counts only (P2, section 8). | S. | S. | S. | S. |
| Usage visible to the org | H: gateway metadata (user, model, tokens, cost, time). | S client-reported audit data, off by default. X: provider dashboard. | Same. | X: gateway logs. S: client-reported. | S client-reported. |
| Client policy freshness | H: gateway rejects clients older than `tenant.minPolicyVersion`. | S. | S. | S. | S. |

Certification registry, as architecture X2 has it: one signed certification registry file in the content feed (content key), read by clients and by the gateway. The Coach owner confirms its name; this document does not pick one.

The `managed` column describes the design once `managed` is available (`tenant.managed.flag` on, written upstream permission on file; catalog section 7, item 11). Until then no connection type is Hard on infrastructure we run; the hard path is `custom_openai_compat` behind the org's own gateway with egress controls, which the matrix shows as External.

Independent of connection type:

| Control | Level | Note |
|---|---|---|
| Roles and sharing on synced Blueprints | H | Sync service and portal. |
| Approval gates, separation of duties, status transitions | H | Server issues the approval record. Local-only Blueprints are outside this, and only their approval metadata syncs. |
| Admin content access (metadata, break-glass, audit entry, owner notice) | H | Server side. |
| Sensitivity floor and per-class sync rules on upload | H | Based on the class the client declares. |
| Retention, deleted-grace, version limits, audit log | H | Server side. Deleted data persists in backups for the 35-day window stated in the DPA. |
| Entitlement, plan, trial and the 3-device limit | H online, S for the token expiry | Sync and gateway re-check entitlement on every request; the client enforces the token `exp` offline. Individual Free needs no token. |
| Break-glass approval (Enterprise: a different Admin) | H | Server side; fails closed with one Admin. |
| Local export and review packet | S | Local files; nothing uploads (R2). The server never sees a local-only restricted Blueprint. |
| Org rules and environment profile at authoring time | S | Engine runs in the client, offline. Org rules are P2. |
| Org rules (P2) and overrides at status transitions | H | ASSUMPTION: the deterministic engine also runs on the server, at status-transition requests only (submit for review, approve), and re-evaluates that synced Blueprint against current policy. It does not run on every push and never on a merge (architecture X3). A local-only Blueprint is checked on the reviewer's client. |
| Transcript retention, local logs, AutoMate action modes | S | Local files and local adapter. |
| Enrolled device must hold org policy | S, hard against skipping sign-in | Registry `RequireOrgPolicy` puts the app in enrollment-required mode (section 4.3). A local admin can still remove the key or patch the client (bypass 1, 13). |

### 3.3 How a determined local admin can bypass client-side policy

Plainly: a person with administrator rights on their own Windows machine can defeat every Soft control. Coach policy is a guardrail for honest use and an audit trail for dishonest use. It is not data-loss prevention, and it must not be sold as such.

| # | Bypass | What it defeats | What we do about it | Residual risk |
|---|---|---|---|---|
| 1 | Patch or replace the client, or swap the pinned root public key | All Soft controls and bundle verification | Authenticode signing; server-side checks for what matters (gateway, sync, approvals) | Not preventable by software we ship. The org's own endpoint controls (WDAC, AppLocker, MDM) are the answer. |
| 2 | Edit the cached bundle | Locked settings | Signature check on every load | Needs bypass 1 to succeed. |
| 3 | Roll the bundle back, or move the system clock back to stretch the grace window | Newer policy, expiry | Reject lower `version`; keep a forward-only high-water mark of server time; gateway enforces `tenant.minPolicyVersion` for `managed` | Wiping local state resets the marks. |
| 4 | Stay offline on an old bundle | Policy changes | `expiresAt` hard stop, then `policy.onExpiry` | Up to the policy grace clock (section 4.5, clock 1). |
| 5 | Use a BYOK key outside Coach | Model lists, caps, redaction, everything | Disable personal keys; provider-side key limits; egress allow-list; use `managed` (once available) or an org gateway | Not preventable. |
| 6 | Local proxy that rewrites requests to skip redaction or preview | Redaction, preview | Org gateway DLP for `custom_openai_compat`; gateway in-transit scan for `managed` (P2) | Remains for BYOK. |
| 7 | Declare a lower sensitivity class | Class routing and sync rules | `data.minimumSensitivity` floor; detectors; data-domain rules that raise the class (P2); reviewers see class beside content | The class is attested by the user, never verified. |
| 8 | Keep work local and never sync | Org visibility, audit | Approval gates need server-issued records, and the AutoMate adapter checks them | Local-only work stays invisible. |
| 9 | Read the key from the DPAPI store | Key secrecy | DPAPI protects against other users and offline theft, not same-user code. Scoped sub-keys (section 5) limit blast radius. | A BYOK key is the user's key. |
| 10 | Delete local audit, transcripts or logs | Local evidence | Synced events stay in the server audit log; optional client-reported usage | Local-only evidence can be removed. |
| 11 | Second Windows profile, VM or personal install | Everything | Org features only apply when signed in with an org account on a device the org controls | Outside the policy boundary by definition. |
| 12 | Use a `local` model to avoid the model lists | Model allow list | `connections.local.enabled` (Soft) | Data stays on the device; the risk is quality, not leakage. |
| 13 | Skip sign-in or delete the enrollment key to avoid org policy | Org policy on a managed device | Machine enrollment (`RequireOrgPolicy`) forces enrollment-required mode; the portal lists devices with stale or missing policy | A local admin can remove the key; MDM re-applying it is the answer. Unmanaged devices are outside the boundary. |
| 14 | Copy an entitlement token to another machine | Device limit, paid features | Token is device-bound (`cnf`); sync and gateway re-check server-side | Offline use of a copied token fails the binding check in the client only. |
| 15 | Self-attest on Individual or on a one-seat Team | Review | Labelled "self-attested"; never counts as approval; ends when a second billable seat joins; never accepted at Enterprise | By design: with one billable seat there is no second person. |

Defence in depth we do build:
- Code-signed binaries, signed bundles (ES256), a pinned root with a root-signed key-set manifest.
- Every gateway and sync request carries the client's `policyVersion` and bundle hash. An honest client reports truthfully; a modified one can lie, so this is evidence, not enforcement.
- Tamper-evident server audit log (hash chain, Enterprise, P2).
- Server-side re-evaluation by the deterministic engine at status transitions (submit, approve), never on every push or merge.

What to tell customers: `managed` is the hard path only once it is available (it sits behind `tenant.managed.flag` until written upstream permission is on file). Until then the hard path is `custom_openai_compat` behind the org's own gateway with egress controls, plus server-side approvals. For everything else Coach states, in the policy panel, which controls are Hard and which are Soft. The gateway wording is "not stored by us": prompts transit gateway memory, OpenRouter and the model provider; metadata only is persisted.

User transparency panel (client): shows policy version and expiry, every locked setting with "Set by your organization", what the org can see (managed metadata; synced Blueprint content only through break-glass, which notifies the owner; client-reported usage if switched on; transcripts only if the user opted in), the device count and entitlement expiry, and a "check policy now" button.

## 4. Policy bundle: signing, distribution, rotation, offline grace

### 4.1 Format and signature

- Format: the Policy JSON from `policy.schema.json`. Contract fields `schemaVersion`, `orgId`, `version`, `issuedAt`, `expiresAt`, `signature`, `settings`. `schemaVersion` is a required integer (the Blueprint schema version is a "1.x" string; they are separate artifacts).
- Setting shape: `{state, value?}`. `value` is present for `locked` and `default` and absent for `user_choice`.
- Canonicalisation: RFC 8785 JSON Canonicalization Scheme over the object without the `signature` member.
- Signature: detached JWS compact serialization (RFC 7515 appendix F). `alg` is **ES256** (ECDSA P-256 with SHA-256, a 64-byte raw signature, 86 base64url characters) unless Ed25519 support is verified in the chosen KMS and .NET (contract decision 7; VERIFY). Protected header `{alg, kid, typ: "coach-policy+jws"}`. `signature` holds `header..signature`. The signature pattern in the schema fits either algorithm, so a later switch changes the header and the manifest, not the schema.
- The client accepts only the `alg` listed in the key-set manifest entry for the `kid`, never `none`, never a symmetric algorithm.
- `version`: integer, monotonic per org. Rollback publishes old content under a new higher number.

### 4.2 Keys, key-set manifest and rotation

| Item | Design (ASSUMPTION unless stated) |
|---|---|
| Root key | ES256, offline, in an HSM, m-of-n ceremony. Public key compiled into the client. Signs only the key-set manifest. For root rotation the client carries two roots during an overlap release. |
| Signing keys | Held in our KMS or HSM, one set per `purpose`: `policy`, `entitlement`, `approval` (architecture 3.5 shares one manifest across the three; the `purpose` field is the one addition it asks for). Identified by `kid`. One `active`, one `next`. Never leave the signing service. A key is only valid for its own purpose. |
| Key-set manifest | Root-signed. Fields: manifest `version` (monotonic, the client refuses a lower one), `issuedAt`, and per key `kid`, `purpose`, `alg`, public key (JWK), `notBefore`, `notAfter`, `status` (`active`, `next`, `retired`, `revoked`). Fetched with the bundle, cached by the client. |
| Routine rotation | Every 12 months: publish `next`, wait 30 days so clients cache the manifest, promote, retire the old key after the longest bundle TTL has passed. Overlap lets a client with a stale manifest still verify a bundle. |
| Emergency revocation | Mark `kid` revoked in the manifest, re-issue every bundle under a new `kid`, raise `tenant.minClientVersion` if the root is at risk. |
| Per-org keys | Not at launch. Later option for Enterprise: org-held signing key so even we cannot forge its policy. |
| Other trust roots | Content-feed and release keys sit under their own offline root (architecture 3.5); they never sign policy. |

### 4.3 Distribution and machine enrollment

| Channel | How | Tier | Phase |
|---|---|---|---|
| Online pull | `GET /v1/policy` with the user's token. `ETag` and `If-None-Match`. At launch, on connection change, when the gateway or sync service replies with a newer policy version hint, and every 4 hours (ASSUMPTION). A "check now" button exists. | Team, Enterprise | Launch |
| Machine enrollment | Registry values written by IT (Intune or Group Policy), machine-wide, admin-write only: `OrgId`, `RequireOrgPolicy` (DWORD), optional `PolicyFile`. Catalog section 6 lists them. The key is `HKLM\SOFTWARE\Policies\Coach\Enrollment` (PLACEHOLDER with the working name "Coach"; the final path follows the product name). | Team (`OrgId`, `RequireOrgPolicy`), Enterprise (adds `PolicyFile`) | Launch, deployed by script or `.reg` file (below). ADMX templates and Intune packaging after launch. |
| Offline file | Admin downloads the signed bundle and deploys it to the folder named by `PolicyFile` (file share, Intune or Group Policy file copy). The client treats it like a fetched bundle. For air-gapped or locked-down sites; pairs with the offline activation file for the entitlement token. | Enterprise | Launch |
| Baseline | Every install ships a signed baseline bundle (section 4.7). Accepted only when no org is attached. | Individual (Free or Paid) | Launch |

Enrollment states:

| State | Behaviour |
|---|---|
| No enrollment | Normal. A user may attach to an org by signing in. |
| Enrolled, `RequireOrgPolicy` = 0 | The org id is known; the app offers to sign in. No restriction. |
| Enrolled, `RequireOrgPolicy` = 1, no valid policy yet | **Enrollment-required mode**: no direct model connections, Blueprint sync paused (ASSUMPTION: "direct" includes `local`, so an org that locks `connections.local.enabled` off cannot be bypassed before its policy arrives). The no-model wizard and local Blueprints still work. The app asks the user to sign in to `OrgId`. |
| Enrolled, `RequireOrgPolicy` = 1, valid policy held | Normal org mode; the bundle's locks apply. When the policy expires, `policy.onExpiry` applies. |

Enrollment-required mode is deliberately not called "restricted mode", which would collide with the `restricted` sensitivity class. Without enrollment a user can skip sign-in, so the portal and the docs say plainly that client-side controls are for honest-but-careless users.

Manual or script deployment, until ADMX templates and Intune packaging ship. IT runs this once per machine as an administrator, from any endpoint tool: an Intune PowerShell script, a Group Policy startup script or a Group Policy Preferences registry item, or by hand. A `.reg` file with the same three values works too.

```
$k = 'HKLM:\SOFTWARE\Policies\Coach\Enrollment'
New-Item -Path $k -Force | Out-Null
New-ItemProperty -Path $k -Name OrgId -PropertyType String -Value '<org id from the portal>' -Force | Out-Null
New-ItemProperty -Path $k -Name RequireOrgPolicy -PropertyType DWord -Value 1 -Force | Out-Null
# Enterprise only, optional: folder or file that holds the signed offline bundle
New-ItemProperty -Path $k -Name PolicyFile -PropertyType String -Value '<path>' -Force | Out-Null
```

- The key sits under the machine policy hive, so only an administrator can write it. ASSUMPTION: the client reads only this machine-wide key and ignores any per-user copy.
- Check with `Get-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Coach\Enrollment'`. ASSUMPTION: the client's policy panel then shows the enrolled org and, once signed in, the policy version. Removing the values un-enrolls the machine (bypass 13 in section 3.3 covers the local-admin case).
- The path above is a placeholder. If the product name changes, the path changes and IT re-runs the script with the new path. ASSUMPTION: the client reads the old path for one release after a rename, so enrolled machines do not silently drop out.

### 4.4 Client checks, in order

1. The JWS parses; `alg` equals the manifest entry; `kid` is known with `purpose` `policy`, status `active` or `retired`, not `revoked`, and inside `notBefore` and `notAfter`; the signature verifies over the canonical payload.
2. `orgId` equals the signed-in user's org, the enrolled `OrgId`, or `baseline` when no org is attached.
3. `schemaVersion` is known. If higher than the client understands, keep the last good bundle and show "update required".
4. `version` is greater than or equal to the stored version for that `orgId`. Equal versions are ignored.
5. `issuedAt` is not more than 5 minutes ahead of the high-water clock.
6. `expiresAt` is in the future against the high-water clock.
7. The bundle validates under the client profile of the schema (unknown non-`x-` keys ignored with a warning; an unknown enum value drops that setting to its default).
8. Persist, apply, and notify users about changed locks.

Any failure discards the new bundle and keeps the last good one. The high-water clock is the maximum of system time and the latest server `Date` header seen.

### 4.5 Offline grace and expiry

Three grace clocks run side by side. They are independent: one ending never changes another. This table is the only place that states them; every other section refers to it by clock number.

| Clock | What it covers | Length | Set by | When it ends |
|---|---|---|---|---|
| 1. Policy bundle grace | How long a client keeps enforcing a cached org bundle with no refresh. | `expiresAt` = `issuedAt` + `tenant.policy.offlineGraceDays`. Team: 14 days, fixed. Enterprise: 1 to 90 days, default 14 (catalog section 5). A connected client refreshes far earlier and never nears expiry. | The org's policy bundle. | `policy.onExpiry` applies; the default is `no_llm` (next table; S8). A refresh restores normal operation at once. |
| 2. Entitlement token grace | How long a device keeps account-bound features (sync, `managed`, org membership checks) with no online refresh. | `exp` = `iat` + 30 days (architecture 1.6). Fixed by us, not a setting at any tier. Air-gapped sites use the offline activation file. | The entitlement service. | The device loses account-bound features until it refreshes. Free paths never need the token, and export always works. |
| 3. Payment-failure grace | How long a paid plan (Individual Paid, Team, Enterprise) keeps working after a payment fails. | 14 days (owner-confirmed 2026-10-26; R1), counted from the `payment_failed` event. All paid features keep working during it (owner-confirmed 2026-10-26). | Billing policy. | The account falls to Individual Free (section 1.2): local data untouched, synced data downloadable for 90 days, `plan_changed` recorded. Export is always allowed. |

The three clocks match contract ruling S8: policy 14 days then `no_llm` (clock 1), entitlement token 30 days (clock 2), payment failure 14 days (clock 3). Any older single "30-day grace" wording means clock 2 only. The 180-day validity of the Individual baseline bundle (section 4.7) is a bundle expiry, not a grace clock. The 14-day Team trial (section 1.2) is not a grace clock either: it ends at `trialEndsAt` with the same fall to Individual Free as clock 3.

Clock 1 on expiry (`policy.onExpiry`):

| Time | Behaviour |
|---|---|
| Before `expiresAt` | Cached bundle fully enforced. Toast and banner start 3 days before expiry (`policy_expiring`). |
| After `expiresAt`, `policy.onExpiry = no_llm` (default) | No LLM call on any connection type. The deterministic engine, forms, Blueprint editing, local save and export (if the class allows) still work, because the engine has no LLM in it. AutoMate actions limited to `draft_only`; test runs off. Banner until refresh. |
| After `expiresAt`, `last_known_good` | Keep enforcing the cached bundle. Banner. For orgs that value availability over freshness. |
| After `expiresAt`, `read_only` | Blueprints viewable, nothing editable. |
| First run, org account, no bundle yet | Same as `no_llm` until the first successful fetch. |
| Individual baseline past its `expiresAt` | Compiled-in defaults identical to the baseline apply, not `no_llm` (section 4.7). |

Refresh restores normal operation immediately; no re-sign-in.

### 4.6 Publishing workflow (portal)

1. Admin edits a draft in the Policy screen, generated from the schema annotations. P2 settings are hidden.
2. Validate with the authoring profile: JSON Schema, the strict root and setting key sets, tier gating (`x-minTier`), numeric and length limits per tier (`x-tierBounds`), phase (`x-phase`: a P2 setting is accepted with a warning and stays inert), cross-references (toolId exists in the catalog or `environment.customTools`, rule field paths exist in the Blueprint field registry, referenced ids resolve), monotone `toolDataFlowCeiling` across classes with `restricted` capped at `tenant`, and lints: "would this lock out the admin" and "approval required but no CoE Reviewer other than the author exists".
3. Preview: per setting, what changes for users, and which users have a stored value that becomes invalid.
4. Publish: bump `version`, compute `expiresAt`, canonicalise, sign, store, write an audit entry with the diff.
5. Rollback: publish the earlier content as a new version.
6. Enterprise, later: staged rollout to a pilot group before everyone.

Bundle contents are not secret (no credentials), so the bundle is signed and sent over TLS, not encrypted. Redaction patterns and project codenames are visible to org members; admins should know that.

### 4.7 Individual signed baseline bundle

One code path for every tenant (contract decision 7): an Individual install (Free or Paid) runs on a signed baseline bundle shipped in the installer. A Team trial that ends with no subscription, or a lapsed plan, returns members to this baseline.
- `orgId` is `baseline`; `org.tier` is `individual`; the settings are the catalog defaults, including the default sensitivity matrix. No setting is locked.
- Verified exactly like an org bundle, against the same key-set manifest. Accepted only when no org is attached; attaching an org replaces it with the org bundle.
- ASSUMPTION: 180 days validity, refreshed by app updates and the content feed. At expiry the app uses compiled-in defaults identical to the baseline, not `no_llm`, because an Individual has no admin to refresh anything.
- Individuals cannot edit `data.sensitivityRules` or `data.minimumSensitivity` (Team and above). They keep their user-level preferences locally.

## 5. Org-managed key vault (Enterprise, P2)

Goal: let an admin supply provider access once so employees do not paste personal keys, without routing prompts through our servers (the contract promises direct-from-client calls for BYOK and metadata-only gateway persistence). Cut to P2 (contract section 7). It stores org credentials on our servers, which is a named exception to "keys stay on the client"; it ships only after a `security-analyst` review and an owner decision, and `tenant.vault.enabled` stays hidden until then.

| Mode | How it works | Status |
|---|---|---|
| A. Scoped sub-key | Admin stores one provisioning-capable credential in the vault. For each user and device the vault mints a limited key (spend limit, optional expiry, optional model restriction) and revokes it on deactivation. VERIFY which providers offer this; ASSUMPTION: OpenRouter has a key-management API. | The only vault mode in scope (P2). |
| B. Short lease | Client fetches the org key at connect time and holds it for a lease. | **Not built.** The key reaches the endpoint machine and a local admin can read it (bypass 9); mode A limits blast radius better. |
| Integrated OAuth | No key at all. The client obtains a token for the org's gateway through the signed-in identity (`authScheme` `token_provider`, `credentialMode` `integrated_oauth`). | Not a vault feature: a Connection setting. ASSUMPTION: available for org connections at launch where the org runs an identity-aware gateway; this is also how `managed` authenticates. |

Controls and records (mode A):
- Storage: envelope encryption under the tenant data key.
- Each checkout is audited: who, when, which connection, which device name. The key value is never in logs, transcripts, Blueprints, exports or the bundle.
- The org connection in the bundle carries `credentialMode: org_vault` and a `credentialRef` of the form `orgvault:<name>` only on the client's own connection record, never in the bundle (`orgConnections` has no `credentialRef`); the credential is resolved after sign-in.
- Per-user revoke, central rotate, and a kill switch that revokes all sub-keys.
- Rejected: a relay that proxies BYOK traffic through our servers. It would give hard control but breaks the direct-from-client promise and puts prompts on our infrastructure. `managed` will serve orgs that want a hard path once it is available (section 3.3).

Customer-managed keys (CMK, P2): envelope encryption of Blueprint storage under the customer's key; revoking it crypto-shreds Blueprint storage. Trade-off: server-side features that need plaintext (search, server-side engine re-evaluation) need a decrypted working copy. The sync envelope reserves `enc.mode` so the schema does not change. Ships after a security review; do not sign Enterprise contracts that require CMK before it ships.

## 6. SSO, SCIM, audit log and customer-managed keys: placement by tier

R8: SAML and OIDC single sign-on, SCIM and IdP group-to-role mapping are P2 and are not sold at launch.

| Capability | Individual (Free or Paid) | Team | Enterprise |
|---|---|---|---|
| Sign-in | Free: none needed. Paid: email or social. | Adds Microsoft and Google sign-in (launch). | Same as Team at launch. SAML and OIDC single sign-on, with enforcement per verified domain, are P2 (R8). |
| SCIM | - | - | Provisioning and deprovisioning. P2 (R8). |
| IdP group to role mapping | - | - | `tenant.roleMapping`. P2 (R8); roles are assigned in the portal at launch. |
| Groups for environment profiles | - | - | Portal-managed groups at launch (ASSUMPTION; R8). Directory groups arrive with SSO (P2). |
| Audit log | `auditLog[]` in Blueprints only. | Portal viewer, **365 days** (the default and the Team cap), CSV export. | Retention up to 3650 days; API and SIEM stream (`tenant.audit.stream`, P2); hash-chained for tamper evidence (P2). |
| Customer-managed keys | - | - | P2 add-on (`tenant.cmk`). |
| Org key vault | - | - | P2, section 5. |
| Data region | - | One region (field present). | One region at launch; choice is P2 (`tenant.dataRegion`). |
| IP allow-list | - | - | P2 (`tenant.ipAllowlist`). |
| Legal hold | - | - | P2 (`tenant.legalHold`). |
| Devices | Free: not managed. Paid: 3 per user | 3 per user | 3 per user |

Audit event types (every tier with an org log): policy published (with diff), role change, sign-in events (SSO events arrive with SSO, P2), device registered or deactivated, approval, rejection, waiver, override, self-attestation, export, share, delete, connection configured, key checkout (P2), retention or deletion job, client-reported usage (audit data, if on), managed usage summary (from gateway metadata), AutoMate action and test run records written into `Blueprint.auditLog[]`.

Portal audit event names fixed by contract section 10 (use exactly): `break_glass_requested`, `break_glass_approved`, `break_glass_read`, `break_glass_expired` (R6), and `trial_started`, `trial_ended`, `payment_failed`, `plan_changed` (R1). The Blueprint audit actions `blueprint_imported`, `blueprint_share_received`, `blueprint_restored`, `confirmations_reset`, `sensitivity_tightened`, `sensitivity_changed` and `self_attested` are registered by the engine agent, as is `blueprint_backup_deleted` (S6: "Delete backed-up copies" removes every server revision including version history and leaves a tombstone; approval metadata stays) and show in the same viewer.

## 7. Admin portal screens

Contract section 7 fixes the launch portal as thin but real: **Policy, Models, Users and roles, Spend, Audit, Review queue**. Each is a screen with tabs; the Policy screen renders itself from the schema annotations, so the 83 launch settings need no per-setting UI work and a new setting later is a catalog row plus a schema entry.

| Screen | Contents | Phase |
|---|---|---|
| Policy | Settings editor (three-state control per setting, grouped as in the catalog), environment profile form (tools, software, OS, scripting rules, network, systems, who runs automations; one profile for Team), data and privacy (sensitivity matrix, minimum class, redaction, retention, sync, telemetry), diff, publish, version history, rollback, per-user policy rollout list (version, last refresh, client version, stale list), signing-key info, download of the offline bundle. | Launch |
| Models | Connection type switches, personal-key switch, allow and deny lists, certification view, admin-approved local models, org connections. | Launch |
| Users and roles | Invite, assign roles, deactivate, sign-in state, devices (3 per user), domain claim, portal-managed groups (ASSUMPTION; R8), plan and billing link (ASSUMPTION: a hosted payment-provider customer portal, not a built screen). | Launch |
| Spend | `managed` usage by user and model, caps, warnings. Hidden while the `managed` flag is off. Price mechanics: `DEFERRED (R9)`. | Launch (when the flag is on) |
| Audit | Filterable event viewer with CSV export, 365 days at Team. | Launch |
| Review queue | Pending approvals, override approvals, with the engine's rule trace beside each; an org Blueprint inventory (metadata: status, owner, class, last change) with the break-glass request action (Enterprise: a second Admin, any other user holding Admin and never the requester, approves in the same screen; S7). | Launch |
| Intake, Templates | Submissions and triage; org template library. | P2 |
| Org-rule and data-domain editor | Template library at Team; custom predicate editor at Enterprise. | P2 |
| Multi-reviewer and SLA | Quorum, reminders, escalation. | P2 |
| SSO, SCIM, group mapping | SAML and OIDC setup, enforcement, SCIM, IdP group to role mapping (R8: P2, not sold at launch). | P2 |
| Security | Customer-managed keys, org key vault, IP allow-list. | P2 |
| Data controls | Legal hold; org data export and deletion request stay available through support at launch. | P2 |
| Overview | Seats, policy adoption, pending reviews, expiring bundles at a glance. | P2 |

## 8. Proposed phasing

The owner wants admin and user controls at launch. Keep the launch admin surface thin but real: six screens, no bespoke setting widgets.

### Launch

- Client: policy resolver for all three states; bundle verification (ES256, key-set manifest), cache, anti-rollback and offline grace; signed Individual baseline; machine enrollment reader; entitlement-token verifier; every launch setting honoured; policy and transparency panel; redaction engine; sensitivity routing; AI mode and rescue and second-opinion gating; override and justification flows; Individual self-attestation; accessibility and locale settings; AutoMate action modes.
- Gateway: type switch, AI-off refusal, model lists, certification floor, caps, `onCapReached`, minimum policy version, forced data-collection deny, metadata-only persistence, `managed` behind its flag.
- Sync and portal services: RBAC, approval records with one reviewer and separation of duties, admin metadata and break-glass, sensitivity floor, per-class sync, retention, audit log, publish with schema and tier validation, rollback, entitlement and device limit.
- Tiers: Individual Free, Individual Paid and Team self-serve, with platform subscription billing live at launch and independent of the `managed` flag (R1). Enterprise through design-partner pilots (R8): multiple profiles, longer audit retention, offline file distribution, second-Admin break-glass, negotiated DPA (section 1.3).
- Local model support (launch requirement) is covered by `connections.local.enabled`, certification labels and the capability probe.

### After launch (P2), rough order

1. Intake, templates, org-rule editor, multi-reviewer approval and review SLA (hidden until built).
2. SAML and OIDC single sign-on, SCIM, IdP group-to-role mapping and directory groups (R8).
3. Customer-managed keys, data region choice, legal hold.
4. Org key vault, mode A only, after a `security-analyst` review.
5. SIEM stream and hash-chained audit.
6. Gateway in-transit scan for `managed` (counts only, owner-approved exception).
7. Group-scoped policy (`scope`), pilot-group rollout, visual rule builder.
8. ADMX and Intune packaging.
9. A telemetry sink with its consent text. Until then both telemetry settings are reserved: hidden and inert.

### Deliberately not building

- Per-prompt logging at the gateway or anywhere central (contract: metadata only persisted).
- Admin access to local transcripts.
- Routing BYOK traffic through our servers; key-vault short leases.
- Org-forced identified telemetry or forced transcript sync.
- Managed price mechanics (fee rate, markup, minimum charge, wallet or invoice model, top-up, refund, tax): `DEFERRED (R9)` until decision 4.
- Any claim of DLP for Soft controls.
- A setting that lets anyone other than a CoE Reviewer set `approved`, or lets a reviewer approve their own Blueprint.

## 9. Open questions for the owner

Resolved by the contract v2, the owner-approved review defaults and the round 3 rulings, so no longer open: full backup for every class (capability, `restricted` local by default with opt-in), signed Individual baseline, admin content access (metadata plus break-glass), telemetry off everywhere, one region at launch, signing algorithm and enrollment, CoE Reviewer powers, the policy-grace default with `no_llm` (section 4.5).

Closed by the round 3 rulings:
- Is SSO in the launch Enterprise offer? No. SAML and OIDC single sign-on, SCIM and group mapping are P2 and not sold at launch; Enterprise goes through design-partner pilots (R8, section 1.3).
- Break-glass details: the time box is a setting that can only be shortened (default 4 hours, ASSUMPTION); the owner is notified with no veto (owner-confirmed 2026-10-26); at Enterprise a second Admin approves and the request fails closed with one Admin (R6); a grant cannot be renewed and the second Admin is any other Admin in the tenant (S7).
- Does Team get its own trial? Yes: 14 days of Team for a new organization, once per organization; the Individual trial is removed (R1). ASSUMPTION: no card at start.
- Are Viewers a free role? Yes, free and not billed; no cap at launch (R7, owner-confirmed 2026-10-26).
- Is chat coaching on BYOK or local free after the trial? Yes, free forever on Individual Free (R1).
- A Team of one: a Team with exactly one billable seat may self-attest, and a second billable member ends that (R7).
- The unset billing-grace item: the payment-failure grace is 14 days (ASSUMPTION), then the fall to Individual Free (R1, section 4.5).

Still open:
1. Should Enterprise be able to raise clock 2 in the section 4.5 table (the entitlement grace) for air-gapped sites, or only clock 1 (`tenant.policy.offlineGraceDays`, adjustable at Enterprise)?
2. Can an Admin give a billable role to a member beyond the seats paid for? ASSUMPTION: no. The portal blocks the assignment and asks the Admin to raise the quantity first, and a quantity cut below the billable members in use is refused until roles are removed. The cost reports measure paid against used seats either way (architecture 8.8.1).
3. Decisions that touch this file and are owned by architecture 7.1 items 18 to 20: what "Microsoft sign-in" means, how non-revenue tenants are costed, the availability promise. (Item 17, the sales channel, is decided: own payment provider at launch.)

Round 3 assumptions the owner confirmed on 2026-10-26: no card at the start of the Team trial; a payment-failure grace of 14 days with every paid feature working during it; no owner veto on break-glass; no cap on free Viewers at launch. Changed by the owner: synced data stays downloadable for 90 days after the fall to Free (it was 35), then is purged with in-app and email notice (S10). Still assumptions: the 4-hour break-glass time box and portal-managed groups for `environment.profiles[].groupIds` at launch.
