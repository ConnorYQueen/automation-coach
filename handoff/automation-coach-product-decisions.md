---
name: automation-coach-product-decisions
description: "Owner-locked decisions for \"Coach\", the automation-advisor product (AI chat coach + deterministic rules engine) that integrates with AutoMate and ships standalone"
metadata:
  node_type: memory
  type: project
  originSessionId: a11be073-c407-4a6d-ba66-ef5202e1339d
  modified: 2026-10-26T20:25:51.023Z
---

Coach (working name) walks employees through deciding whether and how to automate a process and picks the right tool per step, so they stop over-using LLMs. Brainstormed 2026-10-25. The full design set is saved in the private GitHub repo `ConnorYQueen/automation-coach` (pushed 2026-10-26; local clone at `D:/claude/automation-coach`). Start from its `README.md`, which lists status, open owner decisions and how to run the validators; this file is also copied there as `handoff/automation-coach-product-decisions.md`.

Owner-locked decisions:
- Thesis: the model talks, a deterministic rules engine decides; no LLM in the recommendation path. The engine is a pure function over a step diagnostic, with a full trace. Ladder: eliminate, builtin_feature, api_connector, script, ui_automation, parser_ocr_ml, llm_node, human_checkpoint, llm_agent (discouraged).
- Ships standalone and integrated with AutoMate (WinUI 3, local, no AI at runtime; AI only at design time). The coach acts inside AutoMate: draft-only, diff plus a host-minted click approval, attended test runs.
- AI chat coach with a model picker. Connections: managed credits (our gateway to OpenRouter, billed at cost plus a transaction fee), the customer's own OpenRouter or provider key (called direct from the client), custom OpenAI-compatible endpoints, and local models (free, launch requirement).
- Tiers: Individual, Team, Enterprise. Admin and user controls are required at launch (locked / default / user_choice, signed policy bundle, org environment profile).
- Full blueprint backup/sync to our servers is wanted ("we will offer backup so we need the full capability").

Owner rulings of 2026-10-25 round 3 (the owner approved all nine recommended defaults):
- Open core: Individual Free is permanent with no account (engine, wizard, chat coach on local/BYOK, local export, AutoMate draft actions). Individual Paid adds sync, backup, restore, history, 3 devices and managed (after OpenRouter approval). Trial is a 14-day Team org trial. Subscription billing is live at launch, independent of the managed flag.
- `restricted`: owner may export and build a review packet locally (no upload); Individual self-attestation meets the handoff gate; Team and up need a CoE Reviewer (a one-billable-seat Team may self-attest). Viewers are free.
- Imported, shared and restored Blueprints reopen as `proposed` and `draft`; approvals never transfer to a reset copy. The thesis is worded "no LLM output changes a result except through a value the user accepted", with one exception: the model may tighten (never loosen) sensitivity, applied at once with an undo notice and an audit entry.
- Fewer chips: closed-choice fields use host-rendered controls, chips only for free-text extraction, a host-generated 36-tag checklist, read-back before advance, `whyNotCode` written or edited by the user.
- Owner confirmed 2026-10-26: default model floor for `confidential` and `restricted` stays `works`; the certification harness is a launch gate for chat coaching on those classes (until then wizard-only except admin-approved local models).
- Owner decisions of 2026-10-26 (eight questions, contract section 10 "Owner decisions and confirmations"): model identifier is `modelKey` everywhere; the coach schema defaults (outcomes, doc states, teachLevel, pace, ses_ id, capReason names) are accepted; 14-day payment grace confirmed; post-lapse download window is 90 days then purge (changed from 35; the 35-day backup window stays); break-glass is notify-only with no owner veto; ApprovalRecord carries `tenantId` inside the signed bytes; the Team trial takes no card; no cap on free Viewers at launch (terms limit them to reading and review).
- Still lead-designer calls awaiting owner review (S1 to S14): every model is `experimental` until the certification harness ships; delete-backed-up-copies removes history too and is owner-only; 4-hour break-glass time box.
- New requirement 2026-10-26: the design must meet Azure multi-tenant SaaS ISV expectations and support per-tenant and per-seat cost attribution, so cost and price can be set to the seat for every customer. Done in `architecture.md` section 8 (33-row readiness table: 4 met, 18 partly, 11 gap; all gaps closed by design except three that need the owner). Shared PostgreSQL with row-level security stays; tenant directory, per-tenant limits, tenant lifecycle, usage counters beside the ledger and a cost allocation rule were added. Our tenant id claim is `tenantId` (not `tid`, which is Entra's). R9 stands: no price points.
- Owner decided 2026-10-26: launch with our own payment provider; the Azure Marketplace is a later addition through the `ISubscriptionSource` seam (built now). Reasons it waits: one pricing model fixed per offer, metering only on flat-rate plans, transactable trials auto-convert (conflicts with the no-card trial), Microsoft owns seat quantity.
- Open owner decisions from that pass (architecture 7.1 items 18 to 20, plus one in tiers.md): what "Microsoft sign-in" means (an External ID external tenant alone does not sign in work accounts, only single-tenant app registrations); load non-revenue tenants onto paid seats or report separately; the customer availability promise; whether an Admin can assign billable roles past the paid seat count (assumed no).
- SSO/SCIM deferred to P2; Enterprise sold via design-partner pilots. Managed pricing mechanics deferred until OpenRouter approval.

**Why:** people build agents that fail because they use LLMs where code, APIs or deterministic UI automation fit.

**How to apply:** treat the design files as a draft pending owner decisions. Known blockers found in the 2026-10-25 review: OpenRouter ToS section 7 bars reselling API access, so managed credits needs written approval first; `restricted`-sensitivity blueprints default to local-only in the drafts, which conflicts with full backup; model-extracted diagnostics should be user-confirmed value by value so the model cannot steer verdicts. See [[automate-no-coordinates]] and [[automate-no-confidence]] for AutoMate's element-resolution rules.
