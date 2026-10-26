# Pattern library: hybrid automation shapes

Status: draft 1 of the library, tested against rules pack `0.3.0-draft` and `design/tool-catalog.seed.json` as shipped. Date: 2026-10-25. Companion files: `design/rules-engine.md` (the rules, the fixture format of 15.1 and the hybrid detection of section 14), `design/blueprint.schema.json` (the card and the checkpoints), `design/tool-catalog.seed.json` (the tools), `design/00-shared-contract.md` (contract v2, read only here). Where this file and `rules-engine.md` disagree, `rules-engine.md` wins and this file is stale.

Markers: `ASSUMPTION:` is a guess to be confirmed; `VERIFY:` is a fact that was not checked in this pass.

## 0. Reader notes

| # | Note |
|---|---|
| N1 | **What a pattern is.** A named shape for a process of several steps in which every step that can be written as a rule is on a deterministic rung (built-in feature, connector, script, UI automation, trained extractor), and a language model or a person appears only at the edges, where rules run out. The thesis of the project applies unchanged: the model talks, the engine decides. |
| N2 | **The library does not choose tools.** Every row in every table below is the output of the reference engine for the step as described in the matching `PF-nn` fixture (section 5). A pattern is what you get when steps are described honestly, not a second decision path. If you describe a step differently, the engine may return a different rung, and that answer wins. |
| N3 | **Contract v2 ladder.** `eliminate`, `builtin_feature`, `api_connector`, `script`, `ui_automation`, `parser_ocr_ml`, `llm_node`, `human_checkpoint`, `llm_agent`. A person is tried before the agent. The agent is last, discouraged, and appears here only in PL-11 as the boundary case. No pattern in this file uses an agent as part of its spine. |
| N4 | **Hybrid shapes named by the engine.** Section 14 of `rules-engine.md` detects five: `rules_first_llm_residual`, `rules_first_human_residual`, `llm_draft_human_review`, `ui_read_api_write`, `ml_human_exception`. A pattern here may contain several steps and several shapes. The shape names in the tables are the engine's own output (`recommendation.hybrid.pattern`). |
| N5 | **Numbers in the prose are examples.** Thresholds such as 5,000, 10 percent, three days or a 60-item batch are illustrations. The user states the real values in the step; the library fixes none of them. |
| N6 | **No blocked rule step is rescued by a model.** If policy removes the tool for a rule-based step, the engine returns `no_fit` or `blocked_by_policy` with the manual task as fallback (no downgrade by blockage). Each pattern says what that looks like for its edges. |
| N7 | **Fixture ids.** `PF-nn` fixtures are in the format of 15.1 and run on the same reference engine as the `FX-nn` fixtures. A step marked `variant` in a table is a second description of the same step that shows what a different answer or environment changes. |
| N8 | **Variant runs.** The table 'What changes the answer' under each pattern lists runs of one named fixture with one change (another environment, another sensitivity, another answer). Every row is an output of the reference engine and is asserted the same way as a fixture: a conforming implementation must reproduce rung, tool, tier, companions and warnings. In a row marked 'restricted data', both `Blueprint.sensitivity` and the step's `dataSensitivity` are `restricted`. The rows are not separate fixtures and have no ids. |

## 1. The shape all patterns share

1. **Spine first.** Arithmetic, lookups, routing by an explicit rule, file handling, sending and scheduling are never given to a model. They are on formulas, a flow, a script or UI automation.
2. **A model either reads or writes, and a check follows.** A model step reads fields out of input whose layout cannot be bounded, labels text when there is no labeled history, or drafts wording. What it returns passes a validator (`validator.kind` of the card: `schema_check`, `rule_check`, `lookup_check`, `human_review`, `sampling_audit`) before it moves on. Every model step carries a justification card (`cardRequired`).
3. **A person owns the decision and the leftovers.** Approvals of money or of irreversible actions go through `human.approval_flow`. Cases the spine cannot place go to `human.review_queue`. Work that cannot be written down goes to `human.manual_task`.
4. **The seam has an entry criterion.** Section 14 requires that something decides whether a case stays on the spine or goes to the edge: a rule, a lookup, a threshold from an extractor, a sampling audit. Each pattern lists its seam checks.
5. **The edge may be unavailable.** Policy can remove a model or a service. Each pattern states what the person does then. The spine keeps running; the residual goes to people.

### 1.1 How the Coach uses the library

- When a user describes a process in one blob (`S-MIXED`) or across two kinds of access (`S-ACCESS`), the Coach can name the nearest pattern as a starting shape for the split. The split itself comes from the engine.
- When the engine returns a hybrid shape or a companion, the Coach reads the matching pattern's validators and checkpoint text to draft the test plan and the card's `validator` and `fallback`. The user confirms; the Coach never confirms for the user.
- When the engine returns `no_fit`, the Coach reads the pattern's section 'If the edge is unavailable' for the manual fallback wording.
- The library is reference data. It never selects a tool and it is not an engine input. ASSUMPTION: `coach-spec.md` loads this file as read-only reference data; the engine does not read it.

## 2. Index

| Id | Pattern | Engine shapes shown | Rungs used | Human checkpoint | Fixtures |
|---|---|---|---|---|---|
| PL-01 | [Invoice processing](#pl-01-invoice-processing) | `ml_human_exception` | `api_connector`, `script`, `parser_ocr_ml`, `llm_node`, `human_checkpoint` | review queue, approval flow | PF-01a to PF-01f |
| PL-02 | [Support-email triage](#pl-02-support-email-triage) | `rules_first_llm_residual`, `llm_draft_human_review` | `api_connector`, `llm_node`, `human_checkpoint` | review queue | PF-02a to PF-02c |
| PL-03 | [Contract summarization](#pl-03-contract-summarization) | `llm_draft_human_review` | `script`, `llm_node`, `human_checkpoint` | approval flow | PF-03a to PF-03d |
| PL-04 | [Report generation](#pl-04-report-generation) | `llm_draft_human_review` | `builtin_feature`, `api_connector`, `llm_node`, `human_checkpoint` | review queue, approval flow | PF-04a to PF-04e |
| PL-05 | [Data entry across a legacy application](#pl-05-data-entry-across-a-legacy-application) | `ui_read_api_write`, `rules_first_human_residual` | `builtin_feature`, `api_connector`, `ui_automation` | review queue | PF-05a to PF-05d |
| PL-06 | [Approval routing](#pl-06-approval-routing) | `rules_first_human_residual` | `api_connector`, `script`, `human_checkpoint` | review queue, approval flow | PF-06a to PF-06d |
| PL-07 | [Reply drafting with approval](#pl-07-reply-drafting-with-approval) | `llm_draft_human_review` | `api_connector`, `llm_node` | approval flow | PF-07a to PF-07b |
| PL-08 | [Document classification and filing](#pl-08-document-classification-and-filing) | `ml_human_exception` | `script`, `parser_ocr_ml` | review queue | PF-08a to PF-08c |
| PL-09 | [Two-list reconciliation with an exceptions queue](#pl-09-two-list-reconciliation-with-an-exceptions-queue) | `rules_first_human_residual` | `builtin_feature`, `human_checkpoint` | review queue, approval flow | PF-09a to PF-09c |
| PL-10 | [Supplier price monitoring](#pl-10-supplier-price-monitoring) | `rules_first_human_residual` | `builtin_feature`, `script`, `llm_node`, `human_checkpoint` | review queue | PF-10a to PF-10d |
| PL-11 | [Open-ended research, person first](#pl-11-open-ended-research-person-first) | none (boundary case) | `human_checkpoint` | manual task, review queue | PF-11a to PF-11c |

Rung coverage of the library: `builtin_feature` in PL-04, PL-05, PL-09, PL-10; `api_connector` in PL-01, PL-02, PL-04, PL-05, PL-06, PL-07; `script` in PL-01, PL-03, PL-06, PL-08, PL-10; `ui_automation` in PL-05; `parser_ocr_ml` in PL-01, PL-08; `llm_node` in PL-01, PL-02, PL-03, PL-04, PL-07, PL-08, PL-10; `human_checkpoint` in PL-01, PL-02, PL-03, PL-04, PL-06, PL-09, PL-10, PL-11; `llm_agent` in PL-11. Not shown by any pattern: `eliminate` (a pattern is a shape for a process, and removing a step is not one; see FX-22 and FX-23 for `eliminate`).

## 3. The patterns

### PL-01 Invoice processing

**Use.** Supplier invoices arrive as PDFs, are read, matched to purchase orders, approved when large, and answered when rejected.

**Shape.** A deterministic chain (connector, extractor, script lookup). The extractor is the first edge. The invoices it flags go to a model that reads only those, and the same rule check validates both. Whatever still fails goes to a person. A last model use drafts text for a clerk to read. Money never moves on a model's say-so: a named manager approves. Engine shapes shown by the steps: `ml_human_exception`.

| # | Step | Fixture | Role in the pattern | Rung / tool | Tier | Companion, card, warnings | Seam check |
|---|---|---|---|---|---|---|---|
| 1 | Save invoice PDFs from the shared mailbox | `PF-01a` | Spine: trigger and transfer | api_connector / api.power_automate_cloud_flow | A | - | File arrived and is a PDF |
| 2 | Read the fields from each invoice PDF | `PF-01b` | Edge 1: extractor; flagged invoices go to step 3 | parser_ocr_ml / ml.document_intelligence_prebuilt in script.powershell | B | review queue | Required fields present, total equals line items |
| 3 | Read the invoices the extractor flagged | `PF-01c` | Edge 2: model reads the odd layouts | llm_node / llm.cloud_model in script.powershell | B | card | Same fields check as step 2 |
| 4 | Match each invoice to its purchase order | `PF-01d` | Spine: lookup | script / script.powershell | B | - | Amount and supplier within tolerance |
| 5 | Approve invoices over 5,000 | `PF-01e` | Human checkpoint | human_checkpoint / human.approval_flow | D | - | Approver decision recorded with a timestamp |
| 6 | Draft the rejection note to the supplier | `PF-01f` | Edge 3: text only | llm_node / llm.cloud_model in script.powershell | B | card | Clerk reads every draft |

**Validators.**

- After extraction (steps 2 and 3): required fields present, total equals the sum of line items, date parses, purchase order number exists in the list (a rule check, not a score). An invoice the extractor flags goes to step 3; one that still fails the check goes to the review queue.
- After matching: amount and supplier equal the purchase order within the stated tolerance. A failure marks the row rejected with a reason code.
- Rejection note: the clerk reads every draft before it is sent (`human_review`).

**Card sketch for the model steps** (the user confirms the card; kinds are the schema's `validator.kind` and `fallback.kind`):

| Fixture | `validator.kind` | `validator.description` | `fallback.kind` | `fallback.description` |
|---|---|---|---|---|
| `PF-01c` | `rule_check` | Required fields are present, the total equals the sum of line items and the purchase order number exists in the list. | `human_checkpoint` | Invoices that fail the check go to the review queue. |
| `PF-01f` | `human_review` | The clerk reads every draft beside the invoice before it is sent. | `human_checkpoint` | If the model is unavailable the clerk writes the note by hand. |

**Human checkpoint.** Review queue for invoices that still fail the check after step 3 (companion of step 2). Finance manager approval above the threshold (step 5). The clerk reads each rejection note (step 6).

**If the edge is unavailable.** If the extraction service is unavailable the clerks key the invoices by hand from the review queue; the flow keeps saving the PDFs. If the model is unavailable, flagged invoices go to the review queue and the clerk writes the notes.

**What changes the answer.** A model never rescues a blocked extractor: restricted data or forbidden hosts end in the manual fallback. When every layout is different, the model rung replaces the extractor for the whole step (FX-12). A high and irreversible cost of error replaces the review queue with an approval flow (`RK-D`).

Variant runs (see N8):

| Change | Fixture | Environment | Answers changed | Result | Notes |
|---|---|---|---|---|---|
| Every layout is different (hundreds of small suppliers) | `PF-01b` | OPEN | `{"inputVariability": "unbounded"}` | llm_node / llm.cloud_model in script.powershell | tier B, card |
| Data is restricted | `PF-01b` | OPEN, restricted data | `{"dataSensitivity": "restricted"}` | no_fit (blocked_by_policy) | blocked by T-FLOW, fallback manual task |
| Every host for the extractor is forbidden | `PF-01b` | NO-HOSTS | - | no_fit (blocked_by_policy) | blocked by T-HOST, fallback manual task |
| No model connection is configured | `PF-01f` | NO-LLM | - | no_fit | blocked by T-FLOW, fallback manual task |
| Cost of error on extraction is high and irreversible | `PF-01b` | OPEN | `{"costOfError": "high", "reversibility": "irreversible"}` | parser_ocr_ml / ml.document_intelligence_prebuilt in script.powershell | tier D, approval flow |

**Fixtures.** Proof: `PF-01a`, `PF-01b`, `PF-01c`, `PF-01d`, `PF-01e`, `PF-01f`. Related engine fixtures: `FX-10`, `FX-11`, `FX-12`, `FX-36`, `FX-46`.

### PL-02 Support-email triage

**Use.** A shared mailbox receives support requests that must be routed to the right queue, answered with a first reply, and handed to a person when the system cannot place them.

**Shape.** Routing by explicit rules runs in a flow. A model is allowed only on the narrow residual edge (tickets the rules cannot place) and on the first-reply draft. A person owns whatever neither can place. Engine shapes shown by the steps: `rules_first_llm_residual`, `llm_draft_human_review`.

| # | Step | Fixture | Role in the pattern | Rung / tool | Tier | Companion, card, warnings | Seam check |
|---|---|---|---|---|---|---|---|
| 1 | Route each ticket to a queue | `PF-02a` | Spine: rules; edge: model for the residual | api_connector / api.power_automate_cloud_flow | A | llm.cloud_model, card | Answer is one of the queue labels |
| 2 | Draft a first reply for the routed ticket | `PF-02b` | Edge: draft, person decides | llm_node / llm.cloud_model in script.powershell | C | review queue, card | Sampling audit; nothing sent unattended |
| 3 | Work the tickets nobody could place | `PF-02c` | Human checkpoint | human_checkpoint / human.review_queue | C | - | Entry criterion: rule found nothing and the label check failed |

**Validators.**

- Routing: the model's answer must be one of the queue labels in the list (a schema check). Any other answer, or an empty one, counts as unplaced.
- Reply draft: a sampling audit by the team lead plus a review queue at tier C; the draft is never sent by the flow.
- Unplaced tickets: entry criterion for the person's queue is exactly 'rule found nothing and the label check failed'.

**Card sketch for the model steps** (the user confirms the card; kinds are the schema's `validator.kind` and `fallback.kind`):

| Fixture | `validator.kind` | `validator.description` | `fallback.kind` | `fallback.description` |
|---|---|---|---|---|
| `PF-02a` | `schema_check` | The answer must be one of the queue labels in the routing table; any other answer counts as unplaced. | `human_checkpoint` | Unplaced tickets go to the review queue. |
| `PF-02b` | `human_review` | Each draft waits in the review queue and a person approves or edits it before it goes out. | `human_checkpoint` | If the model is unavailable the support staff write the reply by hand. |

**Human checkpoint.** Review queue for unplaced tickets (step 3). Reply drafts wait in a review queue before sending (step 2).

**If the edge is unavailable.** Every unplaced ticket goes to the person's queue. If the reply model is unavailable the support staff write the reply.

**What changes the answer.** Without a model the routing stays on the connector and the engine warns `W-RESIDUAL-UNAVAILABLE`: the residual goes to people. With restricted data the cloud flow is dropped for a script and the residual edge is unavailable too. The reply draft has no fallback except the manual task.

Variant runs (see N8):

| Change | Fixture | Environment | Answers changed | Result | Notes |
|---|---|---|---|---|---|
| No model connection is configured | `PF-02a` | NO-LLM | - | api_connector / api.power_automate_cloud_flow | tier A, W-RESIDUAL-UNAVAILABLE |
| Data is restricted | `PF-02a` | OPEN, restricted data | `{"dataSensitivity": "restricted"}` | script / script.powershell | tier A, W-ENV-DOWNGRADE, W-RESIDUAL-UNAVAILABLE |
| The org forbids the connector rung | `PF-02a` | NO-API-RUNG | - | script / script.powershell | tier A, llm.cloud_model, card, W-ENV-DOWNGRADE |
| No model connection (reply draft) | `PF-02b` | NO-LLM | - | no_fit | blocked by T-FLOW, fallback manual task |

**Fixtures.** Proof: `PF-02a`, `PF-02b`, `PF-02c`. Related engine fixtures: `FX-24`, `FX-25`, `FX-28`, `FX-42`.

### PL-03 Contract summarization

**Use.** New contracts must be summarized for a lawyer or a manager who then decides.

**Shape.** File handling is plain automation. The model produces a summary and nothing else; a named reviewer reads the summary against the contract and owns the conclusion. Because the cost of a wrong summary is high, the review is an approval, not a sample. Engine shapes shown by the steps: `llm_draft_human_review`.

| # | Step | Fixture | Role in the pattern | Rung / tool | Tier | Companion, card, warnings | Seam check |
|---|---|---|---|---|---|---|---|
| 1 | Copy new contract files to the review folder | `PF-03a` | Spine: file handling | script / script.powershell | A | W-NO-TRIGGER | File arrived and opens |
| 2 | Summarize each contract | `PF-03b` | Edge: model drafts | llm_node / llm.cloud_model in script.powershell | D | approval flow, card | Every figure and name appears in the source |
| 3 | Review the summary against the contract | `PF-03c` | Human checkpoint | human_checkpoint / human.approval_flow | D | - | Approval recorded |
| - | Summarize each contract when the data is restricted (variant: restricted data) | `PF-03d` | What changes the answer | no_fit (blocked_by_policy) | - | - | - |

**Validators.**

- Summary: every figure, date and party name in the summary must appear in the contract text (a deterministic string check run before the reviewer sees it).
- Reviewer: reads the summary beside the source and approves or sends it back; the approval is recorded.

**Card sketch for the model steps** (the user confirms the card; kinds are the schema's `validator.kind` and `fallback.kind`):

| Fixture | `validator.kind` | `validator.description` | `fallback.kind` | `fallback.description` |
|---|---|---|---|---|
| `PF-03b` | `rule_check` | Every figure, date and party name in the summary must appear in the contract text. | `human_checkpoint` | If the check fails or the model is unavailable the reviewer reads the contract directly. |

**Human checkpoint.** The reviewer (step 3) is an approval flow at tier D; nothing downstream consumes the summary until it is approved.

**If the edge is unavailable.** If the model is unavailable or blocked, the reviewer reads the contract directly (manual task). The engine does not substitute another rung.

**What changes the answer.** No permitted model means no summary step. With restricted data and no local model connection the step is blocked by policy (PF-03d); the trace names `llm.local_model` as the tool that would fit if a local connection existed. A lower cost of error moves the tier from D to C and the approval flow becomes a review queue; the card is required either way.

Variant runs (see N8):

| Change | Fixture | Environment | Answers changed | Result | Notes |
|---|---|---|---|---|---|
| No model connection is configured | `PF-03b` | NO-LLM | - | no_fit | blocked by T-FLOW, fallback manual task |
| Cost of error is medium instead of high | `PF-03b` | OPEN | `{"costOfError": "medium"}` | llm_node / llm.cloud_model in script.powershell | tier C, review queue, card |

**Fixtures.** Proof: `PF-03a`, `PF-03b`, `PF-03c`, `PF-03d`. Related engine fixtures: `FX-15`, `FX-16`, `FX-28`, `FX-36`.

### PL-04 Report generation

**Use.** A recurring report: figures are pulled, calculated and assembled; someone may want a short written commentary; a manager signs off before it goes out.

**Shape.** Numbers come only from deterministic steps (query, formulas, script). A model may write the commentary text, never a figure. A manager signs off, and a script sends the signed-off pack on a schedule. Engine shapes shown by the steps: `llm_draft_human_review`.

| # | Step | Fixture | Role in the pattern | Rung / tool | Tier | Companion, card, warnings | Seam check |
|---|---|---|---|---|---|---|---|
| 1 | Pull last month's figures into the workbook | `PF-04a` | Spine: pull | builtin_feature / builtin.excel_power_query | A | - | Row counts equal the source |
| 2 | Calculate totals and variances | `PF-04b` | Spine: figures | builtin_feature / builtin.excel_formulas | A | - | Totals row equals source totals |
| 3 | Write a short commentary on the variances | `PF-04c` | Edge: commentary text | llm_node / llm.cloud_model in script.powershell | C | review queue, card | Every quoted number appears in the pack |
| 4 | Sign off the report pack | `PF-04d` | Human checkpoint | human_checkpoint / human.approval_flow | C | - | Sign-off recorded with the pack hash |
| 5 | Email the signed-off pack on the first working day | `PF-04e` | Spine: send | api_connector / api.power_automate_cloud_flow | B | - | Pack hash equals the sign-off hash |

**Validators.**

- Figures: the totals row of the pack must equal the totals in the source (a rule check in the formulas).
- Commentary: every number quoted in the text must appear in the pack (a string check); the manager reads the text at sign-off.
- Send: the file hash of the pack equals the hash recorded at sign-off.

**Card sketch for the model steps** (the user confirms the card; kinds are the schema's `validator.kind` and `fallback.kind`):

| Fixture | `validator.kind` | `validator.description` | `fallback.kind` | `fallback.description` |
|---|---|---|---|---|
| `PF-04c` | `rule_check` | Every number quoted in the commentary must appear in the report pack. | `flag_and_skip` | If the check fails the report goes out without commentary and the manager is told. |

**Human checkpoint.** Sign-off (step 4) is an approval flow; the commentary is reviewed in the same moment.

**If the edge is unavailable.** If the model is blocked the report goes out without commentary, or the manager writes it. The numbers are unaffected.

**What changes the answer.** Only the commentary depends on a model. The pull, the formulas and the send stay on built-in features and connectors when scripting is off; if the connector rung is forbidden the send moves to a script plus a scheduler.

Variant runs (see N8):

| Change | Fixture | Environment | Answers changed | Result | Notes |
|---|---|---|---|---|---|
| Scripting is switched off (pull) | `PF-04a` | LOCKED | - | builtin_feature / builtin.excel_power_query | tier A |
| Scripting is switched off (send) | `PF-04e` | LOCKED | - | api_connector / api.power_automate_cloud_flow | tier B |
| The org forbids the connector rung (send) | `PF-04e` | NO-API-RUNG | - | script / script.powershell | tier B, builtin.windows_task_scheduler, W-ENV-DOWNGRADE |
| No model connection is configured | `PF-04c` | NO-LLM | - | no_fit | blocked by T-FLOW, fallback manual task |

**Fixtures.** Proof: `PF-04a`, `PF-04b`, `PF-04c`, `PF-04d`, `PF-04e`. Related engine fixtures: `FX-01`, `FX-05`, `FX-15`, `FX-28`.

### PL-05 Data entry across a legacy application

**Use.** Records must move from a screen-only desktop application into a modern system that has an API, or between two screen-only applications.

**Shape.** Read through the screen with stable element locators; write through the API wherever one exists. The seam is a split, so each half is tested and owned separately. A count-and-compare step closes the loop, and mismatches go to a person. Engine shapes shown by the steps: `ui_read_api_write`, `rules_first_human_residual`.

| # | Step | Fixture | Role in the pattern | Rung / tool | Tier | Companion, card, warnings | Seam check |
|---|---|---|---|---|---|---|---|
| - | Copy new orders from the legacy order screen into the CRM (before the split) | `PF-05a` | The seam | split (S-ACCESS) | - | - | - |
| 1 | Read the new orders from the legacy order screen | `PF-05b` | Spine: read | ui_automation / ui.automate | A | - | Rows read equal the on-screen counter |
| 2 | Create the orders in the CRM | `PF-05c` | Spine: write | api_connector / api.power_automate_cloud_flow | C | - | Every row returns an id |
| 3 | Compare the counts and list the mismatches | `PF-05d` | Edge: person for mismatches | builtin_feature / builtin.excel_formulas | B | review queue | Counts equal for the run |

**Validators.**

- Read: the number of rows read equals the number shown on the screen's own counter.
- Write: the API returns an id for every row; rows without an id are listed as failed.
- Close: counts in the source and the target are equal for the run; unequal runs raise the mismatch list.

**Human checkpoint.** A clerk works the mismatch list (step 3). Selector breakage is a build-time and monitoring problem, not a runtime judgment.

**If the edge is unavailable.** If a screen element cannot be found the run fails loudly (no coordinates, no confidence scoring) and a clerk enters the rows by hand. Image or coordinate targeting is never accepted (`T-LOC`).

**What changes the answer.** The screen half needs UI automation: an org rule that forbids it blocks the step. An unattended read needs an unattended runner (`T-EXEC`); with one, the engine warns `W-HOST-UNATTENDED`.

Variant runs (see N8):

| Change | Fixture | Environment | Answers changed | Result | Notes |
|---|---|---|---|---|---|
| The org forbids UI automation (read) | `PF-05b` | ORG-NO-UI | - | no_fit (blocked_by_policy) | blocked by ORG-no-ui, fallback manual task |
| The read must run unattended and only attended runners exist | `PF-05b` | ATTENDED-ONLY | `{"attendance": "unattended"}` | no_fit | blocked by T-EXEC, fallback manual task |
| The read must run unattended and an unattended runner exists | `PF-05b` | OPEN | `{"attendance": "unattended"}` | ui_automation / ui.automate | tier A, W-HOST-UNATTENDED |

**Fixtures.** Proof: `PF-05a`, `PF-05b`, `PF-05c`, `PF-05d`. Related engine fixtures: `FX-07`, `FX-08`, `FX-09`, `FX-31`.

### PL-06 Approval routing

**Use.** Requests (purchases, expenses, access) must reach the right approver, wait for a decision, escalate when ignored, and be recorded.

**Shape.** Routing, reminders and recording are rules in a flow. The decision itself is a person's. Requests the rules cannot route go to a person, not to a model, because the cost of sending money to the wrong approver is high. Engine shapes shown by the steps: `rules_first_human_residual`.

| # | Step | Fixture | Role in the pattern | Rung / tool | Tier | Companion, card, warnings | Seam check |
|---|---|---|---|---|---|---|---|
| 1 | Route each purchase request to the approver by amount and cost center | `PF-06a` | Spine: rules; edge: person for the unplaced | api_connector / api.power_automate_cloud_flow | A | review queue | Cost center exists in the approver table |
| 2 | The approver approves or rejects the request | `PF-06b` | Human checkpoint | human_checkpoint / human.approval_flow | D | - | Decision and approver id recorded |
| 3 | Remind and escalate requests with no answer after three days | `PF-06c` | Spine: escalation | script / script.powershell | A | builtin.windows_task_scheduler | No decision after the stated days |
| 4 | Record the decision in the finance system | `PF-06d` | Spine: record | api_connector / api.power_automate_cloud_flow | C | - | Write returns an id |

**Validators.**

- Routing: the cost center on the request exists in the approver table; otherwise the request is unplaced.
- Escalation: no decision after the stated number of days.
- Recording: the decision and approver id are written to the system of record before the request closes.

**Human checkpoint.** Approver (step 2) at tier D; a coordinator works the unplaced requests (step 1 residual).

**If the edge is unavailable.** If the approver is away the escalation rule names a backup. If the flow is down, requests wait in the mailbox and the coordinator routes them by hand.

**What changes the answer.** If the connector rung is forbidden, the routing moves to a script with the same hybrid shape and the warning `W-ENV-DOWNGRADE`.

Variant runs (see N8):

| Change | Fixture | Environment | Answers changed | Result | Notes |
|---|---|---|---|---|---|
| The org forbids the connector rung (routing) | `PF-06a` | NO-API-RUNG | - | script / script.powershell | tier A, review queue, W-ENV-DOWNGRADE |

**Fixtures.** Proof: `PF-06a`, `PF-06b`, `PF-06c`, `PF-06d`. Related engine fixtures: `FX-24`, `FX-30`, `FX-36`.

### PL-07 Reply drafting with approval

**Use.** Replies to customers, suppliers or staff where wording matters (complaints, legal notices, sensitive HR answers).

**Shape.** The model drafts; a person approves before anything is sent; a flow sends only what was approved. The approval is part of the design at tier D, not an optional review. Engine shapes shown by the steps: `llm_draft_human_review`.

| # | Step | Fixture | Role in the pattern | Rung / tool | Tier | Companion, card, warnings | Seam check |
|---|---|---|---|---|---|---|---|
| 1 | Draft the reply to the complaint | `PF-07a` | Edge: draft | llm_node / llm.cloud_model in script.powershell | D | approval flow, card | No figure or name outside the case file |
| 2 | Send the approved reply | `PF-07b` | Spine: send | api_connector / api.power_automate_cloud_flow | C | - | Hash of the text equals the approved hash |

**Validators.**

- Draft: contains no figure, date or name that is not in the case file (a string check); length within the stated bounds.
- Approval: the approver id and the hash of the approved text are recorded; the send step refuses text whose hash differs.

**Card sketch for the model steps** (the user confirms the card; kinds are the schema's `validator.kind` and `fallback.kind`):

| Fixture | `validator.kind` | `validator.description` | `fallback.kind` | `fallback.description` |
|---|---|---|---|---|
| `PF-07a` | `rule_check` | The draft contains no figure, date or name that is not in the case file. | `human_checkpoint` | If the check fails the case owner writes the reply. |

**Human checkpoint.** Approval flow before sending (step 1 companion). Legal or HR owns the approval where the case mentions a claim.

**If the edge is unavailable.** If the model is blocked, a person writes the reply; the approval step stays.

**What changes the answer.** A lower cost of error moves the tier from D to C: the approval flow becomes a review queue (`RK-C`). Restricted data or no model connection removes the draft step and a person writes the reply.

Variant runs (see N8):

| Change | Fixture | Environment | Answers changed | Result | Notes |
|---|---|---|---|---|---|
| Cost of error is medium instead of high | `PF-07a` | OPEN | `{"costOfError": "medium"}` | llm_node / llm.cloud_model in script.powershell | tier C, review queue, card |
| Data is restricted | `PF-07a` | OPEN, restricted data | `{"dataSensitivity": "restricted"}` | no_fit (blocked_by_policy) | blocked by T-FLOW, fallback manual task |
| No model connection is configured | `PF-07a` | NO-LLM | - | no_fit | blocked by T-FLOW, fallback manual task |

**Fixtures.** Proof: `PF-07a`, `PF-07b`. Related engine fixtures: `FX-28`.

### PL-08 Document classification and filing

**Use.** Mixed incoming documents must be labeled and filed in the right place.

**Shape.** With labeled history and a stable set of labels, a trained classifier labels the documents and a script files them. Without history the model labels them under a card. In both cases anything the classifier or model cannot place goes to a person. Engine shapes shown by the steps: `ml_human_exception`.

| # | Step | Fixture | Role in the pattern | Rung / tool | Tier | Companion, card, warnings | Seam check |
|---|---|---|---|---|---|---|---|
| 1 | Label each incoming document by type, with labeled history | `PF-08a` | Edge 1: classifier | parser_ocr_ml / ml.trained_text_classifier in script.python | A | review queue, W-SKILL | Label is in the stable set |
| - | Label each incoming document by type, no labeled history (variant: no labeled history) | `PF-08b` | Alternative when there is no history | llm_node / llm.cloud_model in script.powershell | A | card | Label is in the stable set |
| 2 | File each document in the folder for its label | `PF-08c` | Spine: filing | script / script.powershell | A | - | File arrived in the target folder |

**Validators.**

- Label: the label is one of the stable set; anything else is unplaced.
- Filing: the target folder exists and the file arrived there (a rule check).
- Sample: a monthly audit of a fixed number of filed documents by a person.

**Card sketch for the model steps** (the user confirms the card; kinds are the schema's `validator.kind` and `fallback.kind`):

| Fixture | `validator.kind` | `validator.description` | `fallback.kind` | `fallback.description` |
|---|---|---|---|---|
| `PF-08b` | `schema_check` | The label must be one of the stable set of labels; any other answer counts as unplaced. | `human_checkpoint` | Unplaced documents go to the review queue. |

**Human checkpoint.** Review queue for unplaced documents.

**If the edge is unavailable.** Documents the classifier or model cannot place go to the review queue and are labeled by hand. Without a model connection and without labeled history, all documents are labeled by hand.

**What changes the answer.** Labeled history decides the rung. With enough stable labeled examples (the minimum is `max(100, 30 x classes)`, an ASSUMPTION of the rules pack) the trained classifier wins; with too few examples, or a label set that keeps changing, the model step wins and needs a card.

Variant runs (see N8):

| Change | Fixture | Environment | Answers changed | Result | Notes |
|---|---|---|---|---|---|
| 100 labeled examples for 6 labels | `PF-08a` | OPEN | `{"training": {"examples": 100, "classCount": 6, "labelSetStable": true}}` | llm_node / llm.cloud_model in script.powershell | tier A, card |
| 400 examples but the label set keeps changing | `PF-08a` | OPEN | `{"training": {"examples": 400, "classCount": 6, "labelSetStable": false}}` | llm_node / llm.cloud_model in script.powershell | tier A, card |
| No labeled history and no model connection | `PF-08b` | NO-LLM | - | no_fit | blocked by T-FLOW, fallback manual task |

**Fixtures.** Proof: `PF-08a`, `PF-08b`, `PF-08c`. Related engine fixtures: `FX-13`, `FX-14`, `FX-25`.

### PL-09 Two-list reconciliation with an exceptions queue

**Use.** Two lists (bank lines and ledger lines, orders and shipments) must be matched, and the differences cleared.

**Shape.** Matching is a deterministic join with explicit tolerances. Everything that does not match goes to a person; no model is needed because the questions are about data, not wording. A person approves adjustments. Engine shapes shown by the steps: `rules_first_human_residual`.

| # | Step | Fixture | Role in the pattern | Rung / tool | Tier | Companion, card, warnings | Seam check |
|---|---|---|---|---|---|---|---|
| 1 | Match bank lines to ledger lines | `PF-09a` | Spine: join; edge: exceptions to a person | builtin_feature / builtin.excel_formulas | B | review queue | Key, amount tolerance, date window |
| 2 | Clear the unmatched lines | `PF-09b` | Human checkpoint | human_checkpoint / human.review_queue | C | - | Each line has a reason and an owner |
| 3 | Approve the adjustments | `PF-09c` | Human checkpoint | human_checkpoint / human.approval_flow | D | - | Approver id recorded |

**Validators.**

- Match: key equality plus amount within the stated tolerance and date within the stated window.
- Residual: every unmatched line appears on the exceptions list with the reason (no match, several matches, outside tolerance).
- Adjustment: needs an approver above the stated amount.

**Human checkpoint.** Exceptions queue (step 2); approval of adjustments (step 3).

**If the edge is unavailable.** If the join cannot run, the accountants match by hand from the two exports; the exception lists are still produced.

**What changes the answer.** Formulas cannot run unattended. If the match runs on a schedule and a wrong booking cannot be undone, the engine moves to a script and warns `W-TIER-D-CODE`: dry run, a limit and an alert.

Variant runs (see N8):

| Change | Fixture | Environment | Answers changed | Result | Notes |
|---|---|---|---|---|---|
| The match runs unattended and a wrong booking cannot be undone | `PF-09a` | OPEN | `{"attendance": "unattended", "costOfError": "high", "reversibility": "irreversible"}` | script / script.powershell | tier D, review queue, W-TIER-D-CODE |

**Fixtures.** Proof: `PF-09a`, `PF-09b`, `PF-09c`. Related engine fixtures: `FX-01`, `FX-24`, `FX-36`.

### PL-10 Supplier price monitoring

**Use.** Prices on supplier websites must be collected on a schedule, turned into rows, compared with the last collection, and the odd ones checked by a person.

**Shape.** Collection, comparison and alerting are code and formulas. The only model step is reading fields out of page text whose layout is not bounded, and its output goes through a rule check before it reaches the comparison. A person decides about every price that moved or failed the check. Engine shapes shown by the steps: `rules_first_human_residual`.

| # | Step | Fixture | Role in the pattern | Rung / tool | Tier | Companion, card, warnings | Seam check |
|---|---|---|---|---|---|---|---|
| 1 | Collect the supplier price pages every night | `PF-10a` | Spine: collect | script / script.powershell | A | builtin.windows_task_scheduler, W-SCRAPE-TERMS | Page saved and not empty |
| 2 | Read product, price and stock from each saved page | `PF-10b` | Edge 1: model reads | llm_node / llm.cloud_model in script.powershell | B | card | Price parses and lies in range |
| 3 | Flag prices that moved more than 10 percent since the last collection | `PF-10c` | Spine: compare | builtin_feature / builtin.excel_formulas | B | review queue | Previous row exists for the same product key |
| 4 | Check each flagged price on the supplier site | `PF-10d` | Human checkpoint | human_checkpoint / human.review_queue | C | - | Who looked and what they decided |

**Validators.**

- Read: the price parses as a number, lies between the stated floor and ceiling, and the currency is one of the expected set (a rule check); a failure goes to the person's queue.
- Compare: the previous collection exists for the same product key; a missing key is listed, not guessed.
- Check: each flagged row records who looked and what they decided.

**Card sketch for the model steps** (the user confirms the card; kinds are the schema's `validator.kind` and `fallback.kind`):

| Fixture | `validator.kind` | `validator.description` | `fallback.kind` | `fallback.description` |
|---|---|---|---|---|
| `PF-10b` | `rule_check` | The price parses as a number, lies between the floor and the ceiling, and the currency is one of the expected set. | `human_checkpoint` | Pages that fail the check go to the buyer's review queue. |

**Human checkpoint.** Review queue for moved or unreadable prices (step 4).

**If the edge is unavailable.** If the terms of a site forbid automated access (the engine warns with `W-SCRAPE-TERMS`; a person reads the terms), that site is collected by hand. If the model is blocked the person copies the prices by hand; collection and comparison still run.

**What changes the answer.** A site that renders with JavaScript moves the collection to browser automation with DOM selectors. If every supplier uses one known layout, the read step becomes a template parser and the model disappears. Without a model connection the read step is manual.

Variant runs (see N8):

| Change | Fixture | Environment | Answers changed | Result | Notes |
|---|---|---|---|---|---|
| The supplier pages need JavaScript to render | `PF-10a` | OPEN | `{"operations": ["scrape_web", "read_from_ui", "schedule_trigger"]}` systems: Supplier price sites (web_app, modes ui, locator dom_selector) | ui_automation / ui.playwright_browser | tier A, builtin.windows_task_scheduler, W-SCRAPE-TERMS |
| No model connection is configured | `PF-10b` | NO-LLM | - | no_fit | blocked by T-FLOW, fallback manual task |
| Every supplier uses one known layout | `PF-10b` | OPEN | `{"operations": ["extract_fields_pattern"], "inputVariability": "fixed_layout", "outputDeterminism": "yes"}` | parser_ocr_ml / parser.regex_template in script.powershell | tier B, review queue |

**Fixtures.** Proof: `PF-10a`, `PF-10b`, `PF-10c`, `PF-10d`. Related engine fixtures: `FX-10`, `FX-12`, `FX-19`, `FX-20`.

### PL-11 Open-ended research, person first

**Use.** One-off or occasional investigations whose steps cannot be written down in advance (market scan, supplier comparison, incident look-back).

**Shape.** There is no deterministic spine to build, so the pattern is about who does the work. Contract v2 puts a person before the agent: the engine recommends the person with a checklist and lists the agent as a discouraged alternative. The agent is reached only where a person is forbidden or the volume is too large, and then it is bounded, supervised and carries a justification card.

| # | Step | Fixture | Role in the pattern | Rung / tool | Tier | Companion, card, warnings | Seam check |
|---|---|---|---|---|---|---|---|
| 1 | Research three suppliers and draft a comparison | `PF-11a` | Default worker: a person | human_checkpoint / human.manual_task | A | - | Each claim cites an openable source |
| - | Research three suppliers when the org forbids the manual-task tool (variant: the person is forbidden) | `PF-11b` | Last resort: bounded agent | llm_agent / agent.bounded_llm_agent in script.python | A | review queue, card, W-SKILL, W-ENV-DOWNGRADE, W-AGENT-DISCOURAGED | Allowlist, budget, stop condition in the card |
| 2 | Check the draft against its sources | `PF-11c` | Human checkpoint | human_checkpoint / human.review_queue | C | - | Each claim cites an openable source |

**Validators.**

- Output check: every claim in the draft cites a source the checker can open (a person ticks each citation).
- Agent runs only: a tool allowlist, a step budget and a stop condition are written into the card; the review queue reads the transcript.

**Card sketch for the model steps** (the user confirms the card; kinds are the schema's `validator.kind` and `fallback.kind`):

| Fixture | `validator.kind` | `validator.description` | `fallback.kind` | `fallback.description` |
|---|---|---|---|---|
| `PF-11b` | `human_review` | A reviewer reads the transcript and ticks each citation before the draft is used. | `halt_run` | The run stops at the step budget or on any tool outside the allowlist and hands over to the researcher. |

**Human checkpoint.** The researcher is the default worker. When the agent is used, a reviewer works the review queue (tier A or B only; the agent is rejected at tier C or D by `RA-RISK`).

**If the edge is unavailable.** If neither a person nor the agent can take the step (the run must be unattended, or the org forbids both), the engine returns `no_fit` and the work is not automated.

**What changes the answer.** Volume above the person limit, or an org rule that removes the manual task, reaches the agent; an unattended run closes both doors. A high cost of error keeps the work with a person, because the agent is rejected at tier C or D (`RA-RISK`).

Variant runs (see N8):

| Change | Fixture | Environment | Answers changed | Result | Notes |
|---|---|---|---|---|---|
| The research must run unattended | `PF-11a` | OPEN | `{"attendance": "unattended"}` | no_fit | blocked by T-COVER, fallback manual task |
| 120 items per run | `PF-11a` | OPEN | `{"volumePerRun": 120}` | llm_agent / agent.bounded_llm_agent in script.python | tier A, review queue, card, W-SKILL, W-AGENT-DISCOURAGED |
| Cost of error is high | `PF-11a` | OPEN | `{"costOfError": "high"}` | human_checkpoint / human.manual_task | tier C |

**Fixtures.** Proof: `PF-11a`, `PF-11b`, `PF-11c`. Related engine fixtures: `FX-27`, `FX-47`, `FX-48`.

## 4. Adding a pattern

1. Write each step's diagnostic the way a user would answer the Coach, including the `attractorCheck` for every step where the output is not fully determined or where wording matters. Do not tune answers to reach a rung.
2. Run the engine (the reference implementation or any conforming one) on each step. The table is the output. If a step lands on a rung you did not expect, the pattern or the answers are wrong, not the engine.
3. Add the validator for every seam, the human checkpoint with its entry criterion, and the card sketch for every model step. Check the sketch against the schema's `validator` and `fallback` definitions.
4. Run the same steps in the environments that matter (restricted data, no model connection, scripting off, no unattended runner) and write what changes under 'What changes the answer'. Do not describe an environment you did not run.
5. Add the `PF-nn` fixtures in the format of 15.1 of `rules-engine.md`, with the full result asserted (rung, tool, host, tier, card, companions, warnings, hybrid shape).
6. Do not add a pattern whose spine is a model, or whose edge is an agent, unless it is explicitly the boundary case and says so.

## 5. Pattern fixtures

Format and assertions as in 15.1 of `rules-engine.md`. `BASE` (the suite defaults) is the same as there. Environments are those of 15.2. Every step is `confirmationState = confirmed` and `builderSkill = intermediate` unless the card says otherwise. Each card shows the diagnostic as a delta from `BASE`, the systems, the asserted result, and the abridged reference-engine trace.

### 5.1 Results at a glance

| Id | Case | Env | Result | Rung / tool | Tier |
|---|---|---|---|---|---|
| PF-01a | Save invoice PDFs from the shared mailbox | OPEN | recommended | api_connector / api.power_automate_cloud_flow | A |
| PF-01b | Read the fields from each invoice PDF | OPEN | recommended | parser_ocr_ml / ml.document_intelligence_prebuilt in script.powershell | B |
| PF-01c | Read the invoices the extractor flagged | OPEN | recommended | llm_node / llm.cloud_model in script.powershell | B |
| PF-01d | Match each invoice to its purchase order | OPEN | recommended | script / script.powershell | B |
| PF-01e | Approve invoices over 5,000 | OPEN | recommended | human_checkpoint / human.approval_flow | D |
| PF-01f | Draft the rejection note to the supplier | OPEN | recommended | llm_node / llm.cloud_model in script.powershell | B |
| PF-02a | Route each ticket to a queue | OPEN | recommended | api_connector / api.power_automate_cloud_flow | A |
| PF-02b | Draft a first reply for the routed ticket | OPEN | recommended | llm_node / llm.cloud_model in script.powershell | C |
| PF-02c | Work the tickets nobody could place | OPEN | recommended | human_checkpoint / human.review_queue | C |
| PF-03a | Copy new contract files to the review folder | OPEN | recommended | script / script.powershell | A |
| PF-03b | Summarize each contract | OPEN | recommended | llm_node / llm.cloud_model in script.powershell | D |
| PF-03c | Review the summary against the contract | OPEN | recommended | human_checkpoint / human.approval_flow | D |
| PF-03d | Summarize each contract when the data is restricted (variant: restricted data) | OPEN | no_fit | - | - |
| PF-04a | Pull last month's figures into the workbook | OPEN | recommended | builtin_feature / builtin.excel_power_query | A |
| PF-04b | Calculate totals and variances | OPEN | recommended | builtin_feature / builtin.excel_formulas | A |
| PF-04c | Write a short commentary on the variances | OPEN | recommended | llm_node / llm.cloud_model in script.powershell | C |
| PF-04d | Sign off the report pack | OPEN | recommended | human_checkpoint / human.approval_flow | C |
| PF-04e | Email the signed-off pack on the first working day | OPEN | recommended | api_connector / api.power_automate_cloud_flow | B |
| PF-05a | Copy new orders from the legacy order screen into the CRM | OPEN | split_required | - | - |
| PF-05b | Read the new orders from the legacy order screen | OPEN | recommended | ui_automation / ui.automate | A |
| PF-05c | Create the orders in the CRM | OPEN | recommended | api_connector / api.power_automate_cloud_flow | C |
| PF-05d | Compare the counts and list the mismatches | OPEN | recommended | builtin_feature / builtin.excel_formulas | B |
| PF-06a | Route each purchase request to the approver by amount and cost center | OPEN | recommended | api_connector / api.power_automate_cloud_flow | A |
| PF-06b | The approver approves or rejects the request | OPEN | recommended | human_checkpoint / human.approval_flow | D |
| PF-06c | Remind and escalate requests with no answer after three days | OPEN | recommended | script / script.powershell | A |
| PF-06d | Record the decision in the finance system | OPEN | recommended | api_connector / api.power_automate_cloud_flow | C |
| PF-07a | Draft the reply to the complaint | OPEN | recommended | llm_node / llm.cloud_model in script.powershell | D |
| PF-07b | Send the approved reply | OPEN | recommended | api_connector / api.power_automate_cloud_flow | C |
| PF-08a | Label each incoming document by type, with labeled history | OPEN | recommended | parser_ocr_ml / ml.trained_text_classifier in script.python | A |
| PF-08b | Label each incoming document by type, no labeled history (variant: no labeled history) | OPEN | recommended | llm_node / llm.cloud_model in script.powershell | A |
| PF-08c | File each document in the folder for its label | OPEN | recommended | script / script.powershell | A |
| PF-09a | Match bank lines to ledger lines | OPEN | recommended | builtin_feature / builtin.excel_formulas | B |
| PF-09b | Clear the unmatched lines | OPEN | recommended | human_checkpoint / human.review_queue | C |
| PF-09c | Approve the adjustments | OPEN | recommended | human_checkpoint / human.approval_flow | D |
| PF-10a | Collect the supplier price pages every night | OPEN | recommended | script / script.powershell | A |
| PF-10b | Read product, price and stock from each saved page | OPEN | recommended | llm_node / llm.cloud_model in script.powershell | B |
| PF-10c | Flag prices that moved more than 10 percent since the last collection | OPEN | recommended | builtin_feature / builtin.excel_formulas | B |
| PF-10d | Check each flagged price on the supplier site | OPEN | recommended | human_checkpoint / human.review_queue | C |
| PF-11a | Research three suppliers and draft a comparison | OPEN | recommended | human_checkpoint / human.manual_task | A |
| PF-11b | Research three suppliers when the org forbids the manual-task tool (variant: the person is forbidden) | ORG-NO-MANUAL | recommended | llm_agent / agent.bounded_llm_agent in script.python | A |
| PF-11c | Check the draft against its sources | OPEN | recommended | human_checkpoint / human.review_queue | C |

### 5.2 Fixture cards

#### PL-01 Invoice processing

##### PF-01a  Save invoice PDFs from the shared mailbox

*Edge case:* trigger plus move: a connector covers both.

```json
{
  "id": "PF-01a",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "confidential",
  "stepName": "Save invoice PDFs from the shared mailbox",
  "diagnosticDelta": {
    "interfaceAvailability": "api_available",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "dataSensitivity": "confidential",
    "frequency": "daily",
    "operations": ["transfer_data", "event_trigger"],
    "volumePerRun": 40
  },
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
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "api_connector", "toolId": "api.power_automate_cloud_flow", "tier": "A", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-EXEC`: builtin.excel_power_query cannot run unattended
- chosen `api.power_automate_cloud_flow` at rung `api_connector` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- riskTier A; cardRequired false

##### PF-01b  Read the fields from each invoice PDF

*Edge case:* extractor with a human exception queue.

```json
{
  "id": "PF-01b",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "confidential",
  "stepName": "Read the fields from each invoice PDF",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "costOfError": "medium",
    "attendance": "unattended",
    "dataSensitivity": "confidential",
    "operations": ["extract_fields_document"],
    "residualHandling": "human_review",
    "inputVariability": "many_templates",
    "attractorCheck": {"ruleAttempt": "look for the word Total followed by a number", "whereItBreaks": "some suppliers put the total in a table and others print it twice"},
    "volumePerRun": 40
  },
  "systems": [{"name": "Invoice folder", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "parser_ocr_ml",
    "toolId": "ml.document_intelligence_prebuilt",
    "hostToolId": "script.powershell",
    "tier": "B",
    "cardRequired": false,
    "companions": ["human.review_queue"],
    "hybridPattern": "ml_human_exception"
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

##### PF-01c  Read the invoices the extractor flagged

*Edge case:* the odd layouts only: a model reads, the same rule check follows.

```json
{
  "id": "PF-01c",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "confidential",
  "stepName": "Read the invoices the extractor flagged",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "costOfError": "medium",
    "attendance": "unattended",
    "dataSensitivity": "confidential",
    "operations": ["extract_fields_document"],
    "residualHandling": "human_review",
    "inputVariability": "unbounded",
    "attractorCheck": {"ruleAttempt": "one template per supplier, as for the other invoices", "whereItBreaks": "the flagged invoices come from one-off suppliers and no two layouts repeat"},
    "volumePerRun": 8
  },
  "systems": [{"name": "Flagged invoice folder", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "llm_node",
    "toolId": "llm.cloud_model",
    "hostToolId": "script.powershell",
    "tier": "B",
    "cardRequired": true,
    "rejectedRules": ["RP-CODE", "RP-PARSE"]
  }
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

##### PF-01d  Match each invoice to its purchase order

*Edge case:* plain lookup and rule check, no model.

```json
{
  "id": "PF-01d",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "confidential",
  "stepName": "Match each invoice to its purchase order",
  "diagnosticDelta": {"costOfError": "medium", "attendance": "unattended", "dataSensitivity": "confidential", "operations": ["lookup_join", "validate_rules"], "volumePerRun": 40},
  "systems": [{"name": "Invoice rows and purchase order list", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "script", "toolId": "script.powershell", "tier": "B", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-EXEC`: builtin.excel_formulas cannot run unattended
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- chosen `script.powershell` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.python` (script): same rung; tie-breakers ranked script.powershell first
- alternative `script.office_scripts` (script): same rung; tie-breakers ranked script.powershell first
- riskTier B; cardRequired false

##### PF-01e  Approve invoices over 5,000

*Edge case:* a named person owns the decision.

```json
{
  "id": "PF-01e",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "confidential",
  "stepName": "Approve invoices over 5,000",
  "diagnosticDelta": {
    "costOfError": "high",
    "reversibility": "partly",
    "attendance": "either",
    "dataSensitivity": "confidential",
    "frequency": "daily",
    "operations": ["approve_decision"],
    "humanAuthority": "approval_required"
  },
  "systems": [{"name": "Approval inbox", "kind": "email_or_calendar", "role": "both", "accessEvidence": "verified", "authModel": "sso"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "human_checkpoint", "toolId": "human.approval_flow", "tier": "D", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['approve_decision']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- rejected `script` by `T-COVER`: no single tool or same-rung bundle covers ['approve_decision']
- rejected `ui_automation` by `RP-ACC-4`: needs one of ['ui']; step access is ['builtin', 'file_or_db', 'scriptable']
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- rejected `llm_node` by `RL-NEED`: languageUnderstanding=none, language ops=False, unbounded extraction=False
- chosen `human.approval_flow` at rung `human_checkpoint` (first tool passing every hard predicate; tie-breakers applied)
- riskTier D; cardRequired false

##### PF-01f  Draft the rejection note to the supplier

*Edge case:* model drafts, the clerk reads before sending.

```json
{
  "id": "PF-01f",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "confidential",
  "stepName": "Draft the rejection note to the supplier",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "reversibility": "irreversible",
    "dataSensitivity": "confidential",
    "languageUnderstanding": "core",
    "judgmentRequired": "sometimes",
    "frequency": "daily",
    "operations": ["generate_text"],
    "attractorCheck": {"ruleAttempt": "pick a canned rejection text by reason code", "whereItBreaks": "the supplier needs the specific mismatch explained in plain words"}
  },
  "systems": [{"name": "Shared invoices mailbox", "kind": "email_or_calendar", "role": "target", "accessEvidence": "verified", "authModel": "sso"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "llm_node", "toolId": "llm.cloud_model", "hostToolId": "script.powershell", "tier": "B", "cardRequired": true}
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

#### PL-02 Support-email triage

##### PF-02a  Route each ticket to a queue

*Edge case:* rules spine with a model on the residual edge.

```json
{
  "id": "PF-02a",
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
    "tier": "A",
    "cardRequired": true,
    "companions": ["llm.cloud_model"],
    "hybridPattern": "rules_first_llm_residual"
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

##### PF-02b  Draft a first reply for the routed ticket

*Edge case:* model drafts, a review queue catches it at tier C.

```json
{
  "id": "PF-02b",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Draft a first reply for the routed ticket",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "costOfError": "medium",
    "reversibility": "partly",
    "languageUnderstanding": "core",
    "judgmentRequired": "sometimes",
    "frequency": "daily",
    "operations": ["generate_text"],
    "attractorCheck": {"ruleAttempt": "pick a template by complaint type", "whereItBreaks": "legal threats need wording specific to the claim"}
  },
  "systems": [{"name": "Ticket mailbox", "kind": "email_or_calendar", "role": "target", "accessEvidence": "verified", "authModel": "sso"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "llm_node",
    "toolId": "llm.cloud_model",
    "hostToolId": "script.powershell",
    "tier": "C",
    "cardRequired": true,
    "companions": ["human.review_queue"],
    "hybridPattern": "llm_draft_human_review"
  }
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
- companion `human.review_queue` (review, RK-C): risk tier C with a non-deterministic rung: a person reviews outputs (sampling or exceptions)
- hybrid pattern: `llm_draft_human_review`
- riskTier C; cardRequired true

##### PF-02c  Work the tickets nobody could place

*Edge case:* exception review is a person's job.

```json
{
  "id": "PF-02c",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Work the tickets nobody could place",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "costOfError": "medium",
    "reversibility": "partly",
    "judgmentRequired": "yes",
    "frequency": "daily",
    "operations": ["exception_review"],
    "attractorCheck": {"ruleAttempt": "route by the sender and subject keywords", "whereItBreaks": "forwarded threads and mixed requests match no keyword or several at once"}
  },
  "systems": [{"name": "Ticket mailbox", "kind": "email_or_calendar", "role": "both", "accessEvidence": "verified", "authModel": "sso"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "human_checkpoint", "toolId": "human.review_queue", "tier": "C", "cardRequired": false}
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
- chosen `human.review_queue` at rung `human_checkpoint` (first tool passing every hard predicate; tie-breakers applied)
- alternative `human.manual_task` (human_checkpoint): same rung; tie-breakers ranked human.review_queue first
- riskTier C; cardRequired false

#### PL-03 Contract summarization

##### PF-03a  Copy new contract files to the review folder

*Edge case:* plain file handling, no model.

```json
{
  "id": "PF-03a",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "confidential",
  "stepName": "Copy new contract files to the review folder",
  "diagnosticDelta": {"attendance": "unattended", "credentialsRequired": "yes", "dataSensitivity": "confidential", "frequency": "daily", "operations": ["file_operations", "event_trigger"]},
  "systems": [
    {"name": "Legal share", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified", "authModel": "service_account"},
    {"name": "Review folder", "kind": "spreadsheet_or_file", "role": "target", "accessEvidence": "verified", "authModel": "service_account"}
  ],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "script", "toolId": "script.powershell", "tier": "A", "cardRequired": false, "warningsInclude": ["W-NO-TRIGGER"]}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['file_operations']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- chosen `script.powershell` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.python` (script): same rung; tie-breakers ranked script.powershell first
- warning `W-NO-TRIGGER`: No permitted tool provides event_trigger; start the run manually.
- riskTier A; cardRequired false

##### PF-03b  Summarize each contract

*Edge case:* model produces the draft, a reviewer follows at tier D.

```json
{
  "id": "PF-03b",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "confidential",
  "stepName": "Summarize each contract",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "costOfError": "high",
    "reversibility": "partly",
    "dataSensitivity": "confidential",
    "languageUnderstanding": "core",
    "judgmentRequired": "sometimes",
    "operations": ["summarize_text"],
    "attractorCheck": {"ruleAttempt": "copy the clauses that follow a fixed list of headings", "whereItBreaks": "each counterparty words the clauses differently and the headings vary"},
    "inputSize": "large"
  },
  "systems": [{"name": "Review folder", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "llm_node",
    "toolId": "llm.cloud_model",
    "hostToolId": "script.powershell",
    "tier": "D",
    "cardRequired": true,
    "companions": ["human.approval_flow"],
    "hybridPattern": "llm_draft_human_review"
  }
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
- companion `human.approval_flow` (approve, RK-D): risk tier D: the model produces, a person approves before anything is committed
- hybrid pattern: `llm_draft_human_review`
- riskTier D; cardRequired true

##### PF-03c  Review the summary against the contract

*Edge case:* the lawyer owns the conclusion.

```json
{
  "id": "PF-03c",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "confidential",
  "stepName": "Review the summary against the contract",
  "diagnosticDelta": {"costOfError": "high", "reversibility": "partly", "dataSensitivity": "confidential", "operations": ["approve_decision"], "humanAuthority": "accountable_decision"},
  "systems": [{"name": "Review folder", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "human_checkpoint", "toolId": "human.approval_flow", "tier": "D", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['approve_decision']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- rejected `script` by `T-COVER`: no single tool or same-rung bundle covers ['approve_decision']
- rejected `ui_automation` by `RP-ACC-4`: needs one of ['ui']; step access is ['builtin', 'file_or_db', 'scriptable']
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- rejected `llm_node` by `RL-NEED`: languageUnderstanding=none, language ops=False, unbounded extraction=False
- chosen `human.approval_flow` at rung `human_checkpoint` (first tool passing every hard predicate; tie-breakers applied)
- riskTier D; cardRequired false

##### PF-03d  Summarize each contract when the data is restricted (variant: restricted data)

*Edge case:* restricted data and no local model: blocked by policy, a person reads the contract.

```json
{
  "id": "PF-03d",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "restricted",
  "stepName": "Summarize each contract",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "costOfError": "high",
    "reversibility": "partly",
    "dataSensitivity": "restricted",
    "languageUnderstanding": "core",
    "judgmentRequired": "sometimes",
    "operations": ["summarize_text"],
    "attractorCheck": {"ruleAttempt": "copy the clauses that follow a fixed list of headings", "whereItBreaks": "each counterparty words the clauses differently and the headings vary"}
  },
  "systems": [{"name": "Review folder", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified"}],
  "expect": {"status": "blocked_by_policy", "outcome": "no_fit", "envDeltaRules": ["T-FLOW"]}
}
```

Reference engine output (abridged trace):

- Without this environment the engine would choose llm.local_model (llm_node). It cannot be used here, and the engine does not substitute a less deterministic rung for a blocked one.
- Policy is what blocks it: with the policy rules relaxed, llm.cloud_model would fit.
- envDelta `llm_node` / `llm.local_model` [ideal] blocked by `T-FLOW` (environmental): no local connection is configured or reachable here (class allows ['local'])
- envDelta `llm_node` / `llm.cloud_model` blocked by `T-FLOW` (policy): restricted data may use only ['local'] model connections; llm.cloud_model uses ['managed', 'byok_openrouter', 'byok_provider']
- envDelta `llm_node` / `llm.org_endpoint` blocked by `T-FLOW` (policy): restricted data may use only ['local'] model connections; llm.org_endpoint uses ['custom_openai_compat']
- policyRelaxedFit: `llm.cloud_model`
- manualFallback: `human.manual_task`

#### PL-04 Report generation

##### PF-04a  Pull last month's figures into the workbook

*Edge case:* query plus transfer, rules only.

```json
{
  "id": "PF-04a",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Pull last month's figures into the workbook",
  "diagnosticDelta": {"frequency": "monthly", "operations": ["query_database", "transfer_data"]},
  "systems": [
    {"name": "Finance database", "kind": "database", "role": "source", "accessModes": ["file_or_db"], "accessEvidence": "verified"},
    {"name": "Monthly report workbook", "kind": "spreadsheet_or_file", "role": "target", "accessEvidence": "verified"}
  ],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "builtin_feature", "toolId": "builtin.excel_power_query", "tier": "A", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- chosen `builtin.excel_power_query` at rung `builtin_feature` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- riskTier A; cardRequired false

##### PF-04b  Calculate totals and variances

*Edge case:* formulas, no code.

```json
{
  "id": "PF-04b",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Calculate totals and variances",
  "diagnosticDelta": {"frequency": "monthly", "operations": ["calculate", "aggregate_group"]},
  "systems": [{"name": "Monthly report workbook", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "builtin_feature", "toolId": "builtin.excel_formulas", "tier": "A", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- chosen `builtin.excel_formulas` at rung `builtin_feature` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.vba_macro` (script): a lower rung is chosen first (first rung that fits wins)
- riskTier A; cardRequired false

##### PF-04c  Write a short commentary on the variances

*Edge case:* text only, the manager reads it.

```json
{
  "id": "PF-04c",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Write a short commentary on the variances",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "no",
    "costOfError": "medium",
    "reversibility": "partly",
    "languageUnderstanding": "core",
    "judgmentRequired": "sometimes",
    "frequency": "monthly",
    "operations": ["generate_text"],
    "attractorCheck": {"ruleAttempt": "fill a sentence template with the largest variance", "whereItBreaks": "the reason for a variance is only in the notes people typed"}
  },
  "systems": [{"name": "Monthly report workbook", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "llm_node",
    "toolId": "llm.cloud_model",
    "hostToolId": "script.powershell",
    "tier": "C",
    "cardRequired": true,
    "companions": ["human.review_queue"],
    "hybridPattern": "llm_draft_human_review"
  }
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
- companion `human.review_queue` (review, RK-C): risk tier C with a non-deterministic rung: a person reviews outputs (sampling or exceptions)
- hybrid pattern: `llm_draft_human_review`
- riskTier C; cardRequired true

##### PF-04d  Sign off the report pack

*Edge case:* a manager owns the release.

```json
{
  "id": "PF-04d",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Sign off the report pack",
  "diagnosticDelta": {"costOfError": "medium", "reversibility": "partly", "frequency": "monthly", "operations": ["approve_decision"], "humanAuthority": "approval_required"},
  "systems": [{"name": "Approval inbox", "kind": "email_or_calendar", "role": "both", "accessEvidence": "verified", "authModel": "sso"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "human_checkpoint", "toolId": "human.approval_flow", "tier": "C", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['approve_decision']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- rejected `script` by `T-COVER`: no single tool or same-rung bundle covers ['approve_decision']
- rejected `ui_automation` by `RP-ACC-4`: needs one of ['ui']; step access is ['builtin', 'file_or_db', 'scriptable']
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- rejected `llm_node` by `RL-NEED`: languageUnderstanding=none, language ops=False, unbounded extraction=False
- chosen `human.approval_flow` at rung `human_checkpoint` (first tool passing every hard predicate; tie-breakers applied)
- riskTier C; cardRequired false

##### PF-04e  Email the signed-off pack on the first working day

*Edge case:* scheduled send, code.

```json
{
  "id": "PF-04e",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Email the signed-off pack on the first working day",
  "diagnosticDelta": {
    "reversibility": "irreversible",
    "interfaceAvailability": "api_available",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "frequency": "monthly",
    "operations": ["send_message", "schedule_trigger", "validate_rules"]
  },
  "systems": [
    {
      "name": "Report folder",
      "kind": "spreadsheet_or_file",
      "role": "source",
      "accessModes": ["connector", "file_or_db"],
      "accessEvidence": "verified",
      "authModel": "service_account"
    },
    {
      "name": "Outlook mailbox",
      "kind": "email_or_calendar",
      "role": "target",
      "accessModes": ["connector", "api"],
      "accessEvidence": "verified",
      "authModel": "service_account"
    }
  ],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "api_connector", "toolId": "api.power_automate_cloud_flow", "tier": "B", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-EXEC`: builtin.excel_power_query cannot run unattended
- chosen `api.power_automate_cloud_flow` at rung `api_connector` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- riskTier B; cardRequired false

#### PL-05 Data entry across a legacy application

##### PF-05a  Copy new orders from the legacy order screen into the CRM

*Edge case:* one step, two kinds of access: the engine asks for a split.

```json
{
  "id": "PF-05a",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Copy new orders from the legacy order screen into the CRM",
  "diagnosticDelta": {"interfaceAvailability": "ui_only", "frequency": "daily", "operations": ["transfer_data"]},
  "systems": [
    {"name": "Legacy order app", "kind": "desktop_app", "role": "source", "accessModes": ["ui"], "accessEvidence": "verified", "uiLocator": {"kind": "automation_id"}},
    {"name": "CRM", "kind": "web_app", "role": "target", "accessModes": ["connector", "api"], "accessEvidence": "verified", "authModel": "sso"}
  ],
  "expect": {"status": "ok", "outcome": "split_required", "splitCode": "S-ACCESS", "hybridPattern": "ui_read_api_write"}
}
```

Reference engine output (abridged trace):

- `S-ACCESS` fired: the systems in this step need different rungs (Legacy order app -> ui_automation, CRM -> builtin_feature).
- proposed step 1: Read from Legacy order app, operations ["read_from_ui"]
- proposed step 2: Write to CRM, operations ["call_api"]
- hybrid pattern: `ui_read_api_write`

##### PF-05b  Read the new orders from the legacy order screen

*Edge case:* screen-only source: UI automation with stable locators.

```json
{
  "id": "PF-05b",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Read the new orders from the legacy order screen",
  "diagnosticDelta": {"interfaceAvailability": "ui_only", "frequency": "daily", "operations": ["read_from_ui"]},
  "systems": [{"name": "Legacy order app", "kind": "desktop_app", "role": "source", "accessModes": ["ui"], "accessEvidence": "verified", "uiLocator": {"kind": "automation_id"}}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "ui_automation", "toolId": "ui.automate", "tier": "A", "cardRequired": false}
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

##### PF-05c  Create the orders in the CRM

*Edge case:* target with an API: a connector, not the screen.

```json
{
  "id": "PF-05c",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Create the orders in the CRM",
  "diagnosticDelta": {"costOfError": "medium", "reversibility": "partly", "interfaceAvailability": "api_available", "frequency": "daily", "operations": ["call_api"]},
  "systems": [{"name": "CRM", "kind": "web_app", "role": "target", "accessModes": ["connector", "api"], "accessEvidence": "verified", "authModel": "sso"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "api_connector", "toolId": "api.power_automate_cloud_flow", "tier": "C", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['call_api']
- chosen `api.power_automate_cloud_flow` at rung `api_connector` (first tool passing every hard predicate; tie-breakers applied)
- alternative `api.third_party_ipaas` (api_connector): same rung; tie-breakers ranked api.power_automate_cloud_flow first
- alternative `api.rest_http_request` (api_connector): same rung; tie-breakers ranked api.power_automate_cloud_flow first
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- riskTier C; cardRequired false

##### PF-05d  Compare the counts and list the mismatches

*Edge case:* rules with a person for the leftovers.

```json
{
  "id": "PF-05d",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Compare the counts and list the mismatches",
  "diagnosticDelta": {
    "outputDeterminism": "mostly",
    "costOfError": "medium",
    "frequency": "daily",
    "operations": ["lookup_join", "validate_rules"],
    "residualHandling": "human_review",
    "attractorCheck": {"ruleAttempt": "compare the row count of the two exports", "whereItBreaks": "equal counts can hide one missing row and one duplicate"}
  },
  "systems": [{"name": "Order export and CRM export", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "builtin_feature",
    "toolId": "builtin.excel_formulas",
    "tier": "B",
    "cardRequired": false,
    "companions": ["human.review_queue"],
    "hybridPattern": "rules_first_human_residual"
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- chosen `builtin.excel_formulas` at rung `builtin_feature` (first tool passing every hard predicate; tie-breakers applied)
- alternative `builtin.excel_power_query` (builtin_feature): same rung; tie-breakers ranked builtin.excel_formulas first
- alternative `script.vba_macro` (script): a lower rung is chosen first (first rung that fits wins)
- companion `human.review_queue` (residual, H-RESID): cases the rule cannot decide go to a person
- hybrid pattern: `rules_first_human_residual`
- riskTier B; cardRequired false

#### PL-06 Approval routing

##### PF-06a  Route each purchase request to the approver by amount and cost center

*Edge case:* rules first; leftovers to a person.

```json
{
  "id": "PF-06a",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Route each purchase request to the approver by amount and cost center",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "interfaceAvailability": "api_available",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "frequency": "continuous",
    "operations": ["route_by_rule"],
    "residualHandling": "human_review",
    "attractorCheck": {
      "ruleAttempt": "send to the approver listed for the cost center on the request",
      "whereItBreaks": "about one request in twenty has a missing or misspelled cost center"
    }
  },
  "systems": [{"name": "Request mailbox", "kind": "email_or_calendar", "role": "source", "accessEvidence": "verified", "authModel": "service_account"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "api_connector",
    "toolId": "api.power_automate_cloud_flow",
    "tier": "A",
    "cardRequired": false,
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
- riskTier A; cardRequired false

##### PF-06b  The approver approves or rejects the request

*Edge case:* a named person decides.

```json
{
  "id": "PF-06b",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "The approver approves or rejects the request",
  "diagnosticDelta": {
    "costOfError": "high",
    "reversibility": "partly",
    "attendance": "either",
    "frequency": "daily",
    "operations": ["approve_decision"],
    "humanAuthority": "approval_required"
  },
  "systems": [{"name": "Approval inbox", "kind": "email_or_calendar", "role": "both", "accessEvidence": "verified", "authModel": "sso"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "human_checkpoint", "toolId": "human.approval_flow", "tier": "D", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['approve_decision']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- rejected `script` by `T-COVER`: no single tool or same-rung bundle covers ['approve_decision']
- rejected `ui_automation` by `RP-ACC-4`: needs one of ['ui']; step access is ['builtin', 'file_or_db', 'scriptable']
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- rejected `llm_node` by `RL-NEED`: languageUnderstanding=none, language ops=False, unbounded extraction=False
- chosen `human.approval_flow` at rung `human_checkpoint` (first tool passing every hard predicate; tie-breakers applied)
- riskTier D; cardRequired false

##### PF-06c  Remind and escalate requests with no answer after three days

*Edge case:* scheduled rules, plain automation.

```json
{
  "id": "PF-06c",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Remind and escalate requests with no answer after three days",
  "diagnosticDelta": {
    "interfaceAvailability": "api_available",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "frequency": "daily",
    "operations": ["send_message", "schedule_trigger", "lookup_join"]
  },
  "systems": [{"name": "Approval inbox", "kind": "email_or_calendar", "role": "both", "accessEvidence": "verified", "authModel": "service_account"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "script",
    "toolId": "script.powershell",
    "tier": "A",
    "cardRequired": false,
    "companions": ["builtin.windows_task_scheduler"]
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['send_message', 'lookup_join']
- rejected `api_connector` by `T-COVER`: no single tool or same-rung bundle covers ['send_message', 'lookup_join']
- chosen `script.powershell` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.python` (script): same rung; tie-breakers ranked script.powershell first
- alternative `script.vba_macro` (script): same rung; tie-breakers ranked script.powershell first
- companion `builtin.windows_task_scheduler` (trigger, T-WRAP): schedule_trigger is not covered by script.powershell
- riskTier A; cardRequired false

##### PF-06d  Record the decision in the finance system

*Edge case:* write through the API, no screen.

```json
{
  "id": "PF-06d",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Record the decision in the finance system",
  "diagnosticDelta": {
    "costOfError": "medium",
    "reversibility": "partly",
    "interfaceAvailability": "api_available",
    "attendance": "unattended",
    "credentialsRequired": "yes",
    "frequency": "daily",
    "operations": ["call_api"]
  },
  "systems": [{"name": "Finance system", "kind": "web_app", "role": "target", "accessModes": ["connector", "api"], "accessEvidence": "verified", "authModel": "service_account"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "api_connector", "toolId": "api.power_automate_cloud_flow", "tier": "C", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['call_api']
- chosen `api.power_automate_cloud_flow` at rung `api_connector` (first tool passing every hard predicate; tie-breakers applied)
- alternative `api.third_party_ipaas` (api_connector): same rung; tie-breakers ranked api.power_automate_cloud_flow first
- alternative `api.rest_http_request` (api_connector): same rung; tie-breakers ranked api.power_automate_cloud_flow first
- alternative `script.powershell` (script): a lower rung is chosen first (first rung that fits wins)
- riskTier C; cardRequired false

#### PL-07 Reply drafting with approval

##### PF-07a  Draft the reply to the complaint

*Edge case:* tier D: draft, then approval flow.

```json
{
  "id": "PF-07a",
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
    "hostToolId": "script.powershell",
    "tier": "D",
    "cardRequired": true,
    "companions": ["human.approval_flow"],
    "hybridPattern": "llm_draft_human_review"
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

##### PF-07b  Send the approved reply

*Edge case:* plain send, only after approval.

```json
{
  "id": "PF-07b",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Send the approved reply",
  "diagnosticDelta": {
    "costOfError": "medium",
    "reversibility": "irreversible",
    "interfaceAvailability": "api_available",
    "frequency": "ad_hoc",
    "operations": ["send_message", "validate_rules"]
  },
  "systems": [{"name": "Complaint inbox", "kind": "email_or_calendar", "role": "target", "accessEvidence": "verified", "authModel": "sso"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "api_connector", "toolId": "api.power_automate_cloud_flow", "tier": "C", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['send_message', 'validate_rules']
- chosen `api.power_automate_cloud_flow` at rung `api_connector` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.vba_macro` (script): a lower rung is chosen first (first rung that fits wins)
- riskTier C; cardRequired false

#### PL-08 Document classification and filing

##### PF-08a  Label each incoming document by type, with labeled history

*Edge case:* classify path of the parser rung.

```json
{
  "id": "PF-08a",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Label each incoming document by type",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "mostly",
    "attendance": "unattended",
    "languageUnderstanding": "some",
    "frequency": "daily",
    "operations": ["classify_text"],
    "residualHandling": "human_review",
    "training": {"examples": 400, "classCount": 6, "labelSetStable": true},
    "volumePerRun": 60,
    "attractorCheck": {"ruleAttempt": "look for a keyword per document type", "whereItBreaks": "scans and emails mix several types and the keywords overlap"}
  },
  "systems": [{"name": "Scan inbox", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "parser_ocr_ml",
    "toolId": "ml.trained_text_classifier",
    "hostToolId": "script.python",
    "tier": "A",
    "cardRequired": false,
    "companions": ["human.review_queue"],
    "warningsInclude": ["W-SKILL"],
    "hybridPattern": "ml_human_exception"
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=no
- rejected `api_connector` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=no
- rejected `script` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=no
- rejected `ui_automation` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=no
- chosen `ml.trained_text_classifier (runs in script.python)` at rung `parser_ocr_ml` (first tool passing every hard predicate; tie-breakers applied)
- alternative `llm.cloud_model` (llm_node): a lower rung is chosen first (first rung that fits wins)
- companion `human.review_queue` (residual, H-RESID): fields the extractor is unsure of or fails validation go to a person
- warning `W-SKILL`: ml.trained_text_classifier needs advanced skill; builder has intermediate
- hybrid pattern: `ml_human_exception`
- riskTier A; cardRequired false

##### PF-08b  Label each incoming document by type, no labeled history (variant: no labeled history)

*Edge case:* the same step without history: the model rung, with a card.

```json
{
  "id": "PF-08b",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Label each incoming document by type",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "mostly",
    "attendance": "unattended",
    "languageUnderstanding": "some",
    "frequency": "daily",
    "operations": ["classify_text"],
    "residualHandling": "human_review",
    "training": {"examples": 0, "classCount": 6, "labelSetStable": true},
    "volumePerRun": 60,
    "attractorCheck": {"ruleAttempt": "look for a keyword per document type", "whereItBreaks": "scans and emails mix several types and the keywords overlap"}
  },
  "systems": [{"name": "Scan inbox", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "llm_node", "toolId": "llm.cloud_model", "hostToolId": "script.powershell", "tier": "A", "cardRequired": true}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=no
- rejected `api_connector` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=no
- rejected `script` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=no
- rejected `ui_automation` by `RP-CODE`: needsUnderstanding=True, outputDeterminism=mostly, judgmentRequired=no
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=180 examples)
- chosen `llm.cloud_model (runs in script.powershell)` at rung `llm_node` (first tool passing every hard predicate; tie-breakers applied)
- riskTier A; cardRequired true

##### PF-08c  File each document in the folder for its label

*Edge case:* rules and file handling.

```json
{
  "id": "PF-08c",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "File each document in the folder for its label",
  "diagnosticDelta": {"attendance": "unattended", "frequency": "daily", "operations": ["file_operations", "route_by_rule"], "volumePerRun": 60},
  "systems": [
    {"name": "Scan inbox", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified"},
    {"name": "Filing share", "kind": "spreadsheet_or_file", "role": "target", "accessEvidence": "verified"}
  ],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "script", "toolId": "script.powershell", "tier": "A", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['file_operations', 'route_by_rule']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- chosen `script.powershell` at rung `script` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.python` (script): same rung; tie-breakers ranked script.powershell first
- riskTier A; cardRequired false

#### PL-09 Two-list reconciliation with an exceptions queue

##### PF-09a  Match bank lines to ledger lines

*Edge case:* lookup and rule check; leftovers to a person.

```json
{
  "id": "PF-09a",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Match bank lines to ledger lines",
  "diagnosticDelta": {
    "outputDeterminism": "mostly",
    "costOfError": "medium",
    "frequency": "monthly",
    "operations": ["lookup_join", "validate_rules", "filter_sort_dedupe"],
    "residualHandling": "human_review",
    "volumePerRun": 2000,
    "attractorCheck": {"ruleAttempt": "match on key, amount and date window", "whereItBreaks": "split payments, rounding and reused references leave lines no rule can settle"}
  },
  "systems": [{"name": "Bank export and ledger export", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "builtin_feature",
    "toolId": "builtin.excel_formulas",
    "tier": "B",
    "cardRequired": false,
    "companions": ["human.review_queue"],
    "hybridPattern": "rules_first_human_residual"
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- chosen `builtin.excel_formulas` at rung `builtin_feature` (first tool passing every hard predicate; tie-breakers applied)
- alternative `builtin.excel_power_query` (builtin_feature): same rung; tie-breakers ranked builtin.excel_formulas first
- alternative `script.vba_macro` (script): a lower rung is chosen first (first rung that fits wins)
- companion `human.review_queue` (residual, H-RESID): cases the rule cannot decide go to a person
- hybrid pattern: `rules_first_human_residual`
- riskTier B; cardRequired false

##### PF-09b  Clear the unmatched lines

*Edge case:* exception review is a person's job.

```json
{
  "id": "PF-09b",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Clear the unmatched lines",
  "diagnosticDelta": {
    "outputDeterminism": "no",
    "costOfError": "medium",
    "reversibility": "partly",
    "judgmentRequired": "yes",
    "frequency": "monthly",
    "operations": ["exception_review"],
    "attractorCheck": {"ruleAttempt": "match on key, amount and date window", "whereItBreaks": "split payments, rounding and reused references leave lines no rule can settle"}
  },
  "systems": [{"name": "Exceptions list", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "human_checkpoint", "toolId": "human.review_queue", "tier": "C", "cardRequired": false}
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
- chosen `human.review_queue` at rung `human_checkpoint` (first tool passing every hard predicate; tie-breakers applied)
- alternative `human.manual_task` (human_checkpoint): same rung; tie-breakers ranked human.review_queue first
- riskTier C; cardRequired false

##### PF-09c  Approve the adjustments

*Edge case:* a named person owns the booking.

```json
{
  "id": "PF-09c",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Approve the adjustments",
  "diagnosticDelta": {"costOfError": "high", "reversibility": "partly", "frequency": "monthly", "operations": ["approve_decision"], "humanAuthority": "approval_required"},
  "systems": [{"name": "Approval inbox", "kind": "email_or_calendar", "role": "both", "accessEvidence": "verified", "authModel": "sso"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "human_checkpoint", "toolId": "human.approval_flow", "tier": "D", "cardRequired": false}
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- rejected `builtin_feature` by `T-COVER`: no single tool or same-rung bundle covers ['approve_decision']
- rejected `api_connector` by `RP-ACC-2`: needs one of ['api', 'connector']; step access is ['builtin', 'file_or_db', 'scriptable']
- rejected `script` by `T-COVER`: no single tool or same-rung bundle covers ['approve_decision']
- rejected `ui_automation` by `RP-ACC-4`: needs one of ['ui']; step access is ['builtin', 'file_or_db', 'scriptable']
- rejected `parser_ocr_ml` by `RP-PARSE`: extract path=False, classify path=False (needs labelSetStable and >=100 examples)
- rejected `llm_node` by `RL-NEED`: languageUnderstanding=none, language ops=False, unbounded extraction=False
- chosen `human.approval_flow` at rung `human_checkpoint` (first tool passing every hard predicate; tie-breakers applied)
- riskTier D; cardRequired false

#### PL-10 Supplier price monitoring

##### PF-10a  Collect the supplier price pages every night

*Edge case:* static HTML: a script, with a terms-of-use warning.

```json
{
  "id": "PF-10a",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Collect the supplier price pages every night",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "interfaceAvailability": "ui_only",
    "attendance": "unattended",
    "frequency": "daily",
    "operations": ["scrape_web", "schedule_trigger"]
  },
  "systems": [{"name": "Supplier price sites", "kind": "web_app", "role": "source", "accessModes": ["http_html", "ui"], "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "script",
    "toolId": "script.powershell",
    "tier": "A",
    "cardRequired": false,
    "companions": ["builtin.windows_task_scheduler"],
    "warningsInclude": ["W-SCRAPE-TERMS"]
  }
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

##### PF-10b  Read product, price and stock from each saved page

*Edge case:* layouts without bound: the model reads, a rule check follows.

```json
{
  "id": "PF-10b",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Read product, price and stock from each saved page",
  "diagnosticDelta": {
    "inputStructure": "semi_structured",
    "outputDeterminism": "mostly",
    "costOfError": "medium",
    "attendance": "unattended",
    "frequency": "daily",
    "operations": ["extract_fields_document"],
    "residualHandling": "human_review",
    "inputVariability": "unbounded",
    "attractorCheck": {
      "ruleAttempt": "find the price next to the word Price in the page text",
      "whereItBreaks": "each small supplier lays the page out differently and the layouts keep changing"
    },
    "volumePerRun": 300
  },
  "systems": [{"name": "Saved supplier pages", "kind": "spreadsheet_or_file", "role": "source", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "llm_node",
    "toolId": "llm.cloud_model",
    "hostToolId": "script.powershell",
    "tier": "B",
    "cardRequired": true,
    "rejectedRules": ["RP-CODE", "RP-PARSE"]
  }
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

##### PF-10c  Flag prices that moved more than 10 percent since the last collection

*Edge case:* formulas on a table.

```json
{
  "id": "PF-10c",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Flag prices that moved more than 10 percent since the last collection",
  "diagnosticDelta": {
    "outputDeterminism": "mostly",
    "costOfError": "medium",
    "frequency": "daily",
    "operations": ["lookup_join", "calculate", "validate_rules"],
    "residualHandling": "human_review",
    "volumePerRun": 300,
    "attractorCheck": {"ruleAttempt": "compare each price with last week's price", "whereItBreaks": "a pack-size change looks like a price change"}
  },
  "systems": [{"name": "Price table", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "builtin_feature",
    "toolId": "builtin.excel_formulas",
    "tier": "B",
    "cardRequired": false,
    "companions": ["human.review_queue"],
    "hybridPattern": "rules_first_human_residual"
  }
}
```

Reference engine output (abridged trace):

- rejected `eliminate` by `E-1`: necessity=required, requiredByControl=False
- chosen `builtin.excel_formulas` at rung `builtin_feature` (first tool passing every hard predicate; tie-breakers applied)
- alternative `script.vba_macro` (script): a lower rung is chosen first (first rung that fits wins)
- companion `human.review_queue` (residual, H-RESID): cases the rule cannot decide go to a person
- hybrid pattern: `rules_first_human_residual`
- riskTier B; cardRequired false

##### PF-10d  Check each flagged price on the supplier site

*Edge case:* a person decides about every moved price.

```json
{
  "id": "PF-10d",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Check each flagged price on the supplier site",
  "diagnosticDelta": {
    "outputDeterminism": "no",
    "costOfError": "medium",
    "reversibility": "partly",
    "judgmentRequired": "yes",
    "frequency": "daily",
    "operations": ["exception_review"],
    "attractorCheck": {"ruleAttempt": "compare each price with last week's price", "whereItBreaks": "a pack-size change looks like a price change"}
  },
  "systems": [{"name": "Price table", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "human_checkpoint", "toolId": "human.review_queue", "tier": "C", "cardRequired": false}
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
- chosen `human.review_queue` at rung `human_checkpoint` (first tool passing every hard predicate; tie-breakers applied)
- alternative `human.manual_task` (human_checkpoint): same rung; tie-breakers ranked human.review_queue first
- riskTier C; cardRequired false

#### PL-11 Open-ended research, person first

##### PF-11a  Research three suppliers and draft a comparison

*Edge case:* default: a person with a checklist, the agent listed as an alternative.

```json
{
  "id": "PF-11a",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Research three suppliers and draft a comparison",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "languageUnderstanding": "core",
    "judgmentRequired": "yes",
    "frequency": "ad_hoc",
    "operations": ["plan_open_ended"],
    "pathPredictability": "open_ended",
    "attractorCheck": {"ruleAttempt": "search a fixed list of sites and copy the pricing page", "whereItBreaks": "each supplier hides pricing somewhere different and the sites change"}
  },
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "human_checkpoint",
    "toolId": "human.manual_task",
    "tier": "A",
    "cardRequired": false,
    "alternativeTools": ["agent.bounded_llm_agent"]
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

##### PF-11b  Research three suppliers when the org forbids the manual-task tool (variant: the person is forbidden)

*Edge case:* the person is forbidden, so the bounded agent is reached.

```json
{
  "id": "PF-11b",
  "env": "ENV-ORG-NO-MANUAL",
  "blueprintSensitivity": "internal",
  "stepName": "Research three suppliers and draft a comparison",
  "diagnosticDelta": {
    "inputStructure": "free_text",
    "outputDeterminism": "no",
    "languageUnderstanding": "core",
    "judgmentRequired": "yes",
    "frequency": "ad_hoc",
    "operations": ["plan_open_ended"],
    "pathPredictability": "open_ended",
    "attractorCheck": {"ruleAttempt": "search a fixed list of sites and copy the pricing page", "whereItBreaks": "each supplier hides pricing somewhere different and the sites change"}
  },
  "expect": {
    "status": "ok",
    "outcome": "recommended",
    "rungId": "llm_agent",
    "toolId": "agent.bounded_llm_agent",
    "hostToolId": "script.python",
    "tier": "A",
    "cardRequired": true,
    "companions": ["human.review_queue"],
    "warningsInclude": ["W-SKILL", "W-ENV-DOWNGRADE", "W-AGENT-DISCOURAGED"],
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

##### PF-11c  Check the draft against its sources

*Edge case:* a person reads and ticks each citation.

```json
{
  "id": "PF-11c",
  "env": "ENV-OPEN",
  "blueprintSensitivity": "internal",
  "stepName": "Check the draft against its sources",
  "diagnosticDelta": {
    "outputDeterminism": "no",
    "costOfError": "medium",
    "reversibility": "partly",
    "judgmentRequired": "yes",
    "frequency": "ad_hoc",
    "operations": ["exception_review"],
    "attractorCheck": {"ruleAttempt": "check that each claim has a link", "whereItBreaks": "a link can exist and still not support the claim"}
  },
  "systems": [{"name": "Draft document", "kind": "spreadsheet_or_file", "role": "both", "accessEvidence": "verified"}],
  "expect": {"status": "ok", "outcome": "recommended", "rungId": "human_checkpoint", "toolId": "human.review_queue", "tier": "C", "cardRequired": false}
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
- chosen `human.review_queue` at rung `human_checkpoint` (first tool passing every hard predicate; tie-breakers applied)
- alternative `human.manual_task` (human_checkpoint): same rung; tie-breakers ranked human.review_queue first
- riskTier C; cardRequired false

## 6. Assumptions and things to verify

| # | Kind | Item |
|---|---|---|
| A1 | ASSUMPTION | The thresholds and periods in the patterns (5,000 for approval, 10 percent for price movement, three days for escalation, 60 or 300 items per run) are examples. They are inputs to a step, not constants of the library. |
| A2 | ASSUMPTION | `humanMaxItemsPerRun = 50` (rules-engine.md 18.1) decides when a person no longer fits an open-ended step; it is the constant behind PL-11 and it is unconfirmed. |
| A3 | ASSUMPTION | The card sketches use the validator and fallback kinds of the schema. The wording is a starting point for the user to edit; no sketch is stored until the user confirms a card. |
| A4 | ASSUMPTION | The library is read by the Coach as reference data (see 1.1). If the owner prefers that the Coach never mentions patterns, remove 1.1 and keep the file as documentation for builders. |
| V1 | VERIFY | Whether the prebuilt document extraction service named in PL-01 and the trained classifier named in PL-08 are what the org licenses. The engine only checks that the catalog tool fits; availability and cost are not checked. Their catalog entries carry their own VERIFY notes. |
| V2 | VERIFY | The accuracy of any extractor or model on the org's own documents. The library names validators, not accuracy. Measure it on a sample before relying on a pattern. |
| V3 | VERIFY | Terms of use of any site collected in PL-10. The engine raises `W-SCRAPE-TERMS`; a person has to read the terms. |
