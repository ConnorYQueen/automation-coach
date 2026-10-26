# Automation Coach (working name): design handoff

Status on 2026-10-26: **design only, no product code yet.** This repository holds the full design set,
the machine-readable schemas, a validation harness, and the research behind them. A new session can pick
up from here without the conversation that produced it.

## What Coach is

Coach walks an employee through analysing a business process for automation and recommends the right
tool for each step: an LLM, a script, an API, UI automation, or a human. It has an AI chat coach with a
model picker. It ships standalone and also integrates with the owner's WinUI 3 app, AutoMate (separate
private repo, `ConnorYQueen/AutoMate`).

The thesis: **the model talks; the engine decides.** A deterministic rules engine makes every
recommendation as a pure function over a step diagnostic, with a full trace. The LLM only interviews,
proposes and explains. No LLM output changes a result except through a value the user accepted (one
exception: the model may tighten, never loosen, a sensitivity class).

## Read in this order

| # | File | What it is |
|---|---|---|
| 1 | `design/00-shared-contract.md` | **The authority (contract v2.2).** Section 10 holds owner rulings R1 to R9, lead-designer calls S1 to S14, and "Owner decisions and confirmations, 2026-10-26". If two files disagree, the contract wins. |
| 2 | `handoff/automation-coach-product-decisions.md` | Copy of the session memory: owner-locked decisions, blockers, open calls. |
| 3 | `design/architecture.md` | Components, data classification, Blueprint backup and sync, gateway and billing, security and threat model, tech stack and build order (6.2), open owner questions (7.1), VERIFY register V1 to V37 (7.2), and **section 8: Azure multi-tenant SaaS ISV readiness and per-tenant, per-seat cost attribution**. |
| 4 | `design/tiers.md` | Plans, roles, enforcement by connection type, policy bundles, offline grace clocks, seats for costing (1.4). |
| 5 | `design/rules-engine.md` | The deterministic engine: rule ladder, diagnostics, fixtures, approval gates. |
| 6 | `design/pattern-library.md` | Pattern library and engine fixtures. |
| 7 | `design/coach-spec.md`, `design/coach-tools.json` | The AI coach: modes, question bank, session state, lite extraction, 28 tool schemas. |
| 8 | `design/model-certification.md` | Model probes, labels (certified, works, experimental, uncertified) and the CapabilityReport. |
| 9 | `design/settings-catalog.md` | Every setting, its state (locked, default, user_choice) and tier. |
| 10 | `design/*.schema.json`, `design/tool-catalog.seed.json` | Blueprint, connection, policy, capability-report and coach-session schemas (JSON Schema 2020-12) and the tool catalog seed. |
| 11 | `research/` | OpenRouter gateway and billing terms, local and enterprise endpoints, competitive landscape. |
| - | `design/99a`, `99b`, `100a`, `100b` | Historical review passes. Their findings are already applied; kept as the record. |
| - | `design/archive/` | Superseded contract versions (v1, v2.1). |

## Where things stand

Done:
- Contract v2.2 with all owner rulings applied; every design file reconciled to it.
- Five schemas, the 28 coach tool parameter schemas and the tool catalog seed validate against a real
  validator. Every JSON example in the docs and 92 engine fixtures validate.
- A validation harness with **129 accept/reject cases**, all passing (see below).
- Azure multi-tenant ISV readiness: 33-row table (5 met, 18 partly, 10 gap), tenancy model, tenant
  directory, per-tenant limits, tenant lifecycle, usage counters and a per-seat cost model. No prices.
- Sales channel decided: **our own payment provider at launch; the Azure Marketplace is a later addition**
  through the `ISubscriptionSource` seam (built now).

Not done:
- No product code. The engine is specified, not implemented. The validation harness checks that fixtures
  are well formed, **not** that the engine produces the stated verdict; that is the job of the engine's
  own test suite once it exists.
- Rules that compare two fields (a probe's `passed` not exceeding `trials`, a follow-up of 20 words or
  fewer, a `quote` being a substring of the user's message) cannot be written in JSON Schema. The host
  must check them, and so must its tests.

## Open decisions for the owner (ask these first)

1. **What "Microsoft sign-in" means** (architecture 7.1 item 18). An Entra External ID external tenant
   alone does not sign in work accounts of other organisations; that needs a multitenant app
   registration (readiness row C3, 8.6).
2. **Costing non-revenue tenants** (7.1 item 19): load trial and lapsed tenants onto paid seats, or
   report them separately. The reports show both.
3. **The customer availability promise** (7.1 item 20).
4. **Seat overage** (`tiers.md` section 9 item 2): can an Admin assign billable roles past the paid seat
   count? Assumed no.
5. **Rename `prefs.preferredModel.modelId` to `modelKey`?** The owner ruled `modelKey` everywhere, applied
   to audit details and `SessionState.lastModel`. This policy setting still says `modelId` because renaming
   it changes the signed policy format (`policy.schema.json`, `settings-catalog.md`).
6. **Lead-designer calls still awaiting owner review:** every model is `experimental` until the
   certification harness ships (S1); "Delete backed-up copies" removes history and is owner-only (S14);
   the 4-hour break-glass time box (ASSUMPTION); portal-managed groups for
   `environment.profiles[].groupIds`.
7. **Payment provider** (which company): architecture 0.1(c), V9, V25. Enterprise clock 2 for air-gapped
   sites: `tiers.md` section 9 item 1. The rest of architecture 7.1 lists further questions.

Known blockers: OpenRouter's terms (section 7) bar reselling API access, so **managed credits need
written approval first**. Managed pricing mechanics stay deferred (R9: no price points or fee rates
anywhere in the design).

## Owner decisions already locked (do not re-ask)

Full text is in contract section 10 and the memory copy. In short: open core (Individual Free is
permanent, no account; Paid adds sync, backup, restore, history, 3 devices); 14-day Team trial with
**no card**; 14-day payment-failure grace; post-lapse download window **90 days** then purge (the 35-day
infrastructure backup window is separate and unchanged); break-glass is notify-only with no owner veto;
the ApprovalRecord carries `tenantId` inside the signed bytes; model identifier is `modelKey`; no cap on
free Viewer seats at launch; certification floor for `confidential` and `restricted` stays `works`; SSO
and SCIM are P2; Enterprise is sold through design-partner pilots; sales channel is our own payment
provider.

## Run the validators

Create a throwaway virtual environment with a **short path** (a long path fails with WinError 267 on
Windows) and install the pinned library:

    python -m venv <short-path>/coach-jsonschema-venv
    <short-path>/coach-jsonschema-venv/Scripts/python -m pip install -r design/validation/requirements.txt
    <short-path>/coach-jsonschema-venv/Scripts/python design/validation/run_all.py

Python 3.12 and `jsonschema[format-nongpl]==4.26.0`. Expected: `validate_docs.py` PASS,
`check_cases.py` 0 mismatches of 129, `probe_untyped.py` informational, `OVERALL: PASS`. Details are in
`design/validation/README.md`.

Cross-file drift check (stdlib only, from the repo root):

    python -I tools/drift_check.py .

It is informational. About 20 `[REF]` flags (cross-schema `urn:coach:schema:...` references it cannot
resolve) and about 23 `[ENUM]` flags (conditional subsets inside `if/then`, and the unrelated `teachLevel`
enum) are known false positives. A new kind of flag is worth reading.

## Conventions the design follows

- **One writer per file when work runs in parallel.** Give each parallel writing session its own git
  worktree and branch.
- Design documents are **ASCII only with no em dashes** (the old `99a` review is the one exception).
- **Line endings are mixed on purpose**: some files are CRLF (`coach-spec.md`, `coach-tools.json`,
  `blueprint.schema.json`, `coach-session.schema.json`, `tool-catalog.seed.json`, part of `validation/`),
  the rest LF. `.gitattributes` keeps the bytes as they are. Preserve each file's endings when editing.
- A statement that is not settled is marked `ASSUMPTION`; an unchecked outside fact is marked `VERIFY`
  with an id in the architecture register. Do not state a Microsoft price, limit or SLA as fact.
- Add a validator case when a schema rule changes. Never write credentials into any file.

## Suggested next steps

1. Ask the owner the open decisions above, one at a time with the consequences of each, and apply the
   answers (contract section 10, `tiers.md`, architecture 7.1, memory copy).
2. Settle the `modelId` rename (item 5) before any policy bundle is signed.
3. Build in the order in `architecture.md` section 6.2. Phase 0 is the written non-code gates (row 0.1,
   including OpenRouter written permission or a direct provider agreement) and three spikes (0.2 to
   0.4: sync and approval round trip, gateway ledger, AutoMate draft round trip). Phase 1 is the client
   and engine (repo and CI, Blueprint model and merge library, engine and catalog, shell with the trusted
   approval UI, connections, orchestrator, packaging). Phase 2 is the Azure foundation and cloud services
   (rows 2.0 to 2.8; row 2.9, the Marketplace, is a later addition). Phase 3 is the managed gateway and
   Phase 4 is the AutoMate adapter, the certification harness and hardening.
4. When the engine exists (row 1.3), add the test that runs every fixture in `rules-engine.md` and
   `pattern-library.md` and compares verdicts, plus the host checks listed under "Not done".
