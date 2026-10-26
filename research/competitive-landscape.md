# Coach: competitive landscape and positioning research

Research date and access date for every source: **2026-10-25**. Author: research agent (web research, roughly 70 searches and fetches). Conventions follow `design/00-shared-contract.md`: `VERIFY:` = not confirmed from a source I could read; `ASSUMPTION:` = my inference. Source tags like [S7] point to the source index at the end (URL, type, fetch notes). Prices are quoted only where I read them on a vendor page or doc in this session; otherwise they are marked secondary.

---

## 0. Conflicts and flags against the shared contract (read first)

| # | Contract item | Finding | Severity | Source |
|---|---|---|---|---|
| F1 | Decision 4: `managed` = app -> our gateway -> OpenRouter, customer pays "usage at cost + transaction fee" | OpenRouter's Terms of Service (last updated 2026-08-31) prohibit using the service for "reselling API access to Models or otherwise developing a competing service" (section 7). Section 5.1 contemplates incorporating the service into your own products, so a product that adds value may be allowed, but a pass-through credit-plus-fee gateway reads close to resale. | **High.** Needs a written answer from OpenRouter or counsel before the `managed` design is locked. VERIFY: whether OpenRouter treats a Coach gateway as reselling; whether an enterprise agreement or another gateway (direct provider contracts, Azure OpenAI, Bedrock) is needed. | [S44] (read via fetch extract; read section 7 yourself) |
| F2 | Decision 4: "at cost" | OpenRouter itself charges a fee when credits are bought: 5.5% on its Standard plan, 8% on Business; credits may expire 365 days after purchase; unused-credit refunds are available within 24 hours of purchase (and on account termination, subject to terms). So our true cost is above list price before our own payment-processor fees. | Medium. Pricing/margin model must start from list price + 5.5% + card fees + our fee, and decide whether our credits expire. | [S43], [S44] |
| F3 | Decision 6: tiers Individual / Team / Enterprise (no free tier mentioned) | Nearly every comparator has a free tier or a free BYOK/local path: Zed, Cline, Msty (personal use), Make, Zapier, n8n Community, UiPath Community, OpenRouter, Kilo (open source). Cursor's free tier is "limited". | Low-medium. ASSUMPTION: a free or trial path is expected by individual buyers; the contract says local models are free, which may be enough for the engine itself. Decide explicitly. | [S13], [S15], [S16], [S33], [S36], [S41] |
| F4 | Decision 8: full Blueprint backup/sync on our servers | Competitors that win privacy-minded buyers sell "your data stays local or in your key" (Zed and Cline BYOK; Msty local inference). UiPath Basic tier says data may be collected to train its models, with opt-out only from Standard up. We need an unambiguous "no training on customer data" statement. | Low. Not a contradiction; a positioning obligation. | [S7], [S36], [S41] |
| F5 | Thesis: "model talks, engine decides" | No conflict. The market is moving toward the same message (see finding 1 in section 1, and E14 and E16 in section 4.1), which means the thesis alone is **not** a durable moat. | Informational | [S3], [S4], [S10], [S61] |

---

## 1. Executive summary: the five most decision-relevant findings

1. **The "deterministic first" message is being absorbed by incumbents.** Microsoft's own docs describe agent flows as deterministic (same input, same output) and price them at 13 Copilot Credits per 100 actions versus 5 credits per agent action, about 38x cheaper per step (my arithmetic from the published rates) [S3][S4]. A community recap of UiPath's Fusion 2026 frames Maestro as a split of labor: agents reason, robots execute, APIs connect, humans decide [S10]. Salesforce executives reportedly moved Agentforce toward predefined, deterministic workflows after trust in LLMs fell [S61]. Coach should not sell "less AI"; it should sell **independent, auditable, per-step tool choice across everything, including tools the platforms do not sell.**
2. **No product I found does tool-agnostic, per-step "what should do this step" advice.** Opportunity assessors are vendor-bound (UiPath Automation Hub scores the share a robot can run and does not address non-RPA technologies [S9]); copilots build inside their own platform (Maia, Power Automate Copilot, Zapier Canvas/Copilot, n8n AI builder) [S5][S14][S17][S18]; task-mining vendors discover work but sell through sales-led enterprise deals [S24][S25]. Absence claim limited by search depth: VERIFY with demos of the five closest products before using "nobody does this" in public copy.
3. **The failure statistics are real but easy to misquote.** The strongest, safest numbers for a landing page are: Gartner's forecast that over 40% of agentic AI projects will be canceled by end of 2027, plus its analyst's statement that many use cases marketed as agentic do not need agentic implementations [S50]; Stanford AI Index 2026: agents still fail about one attempt in three on structured benchmarks [S56]; MIT NANDA's headline is a **preliminary** study of task-specific enterprise GenAI reaching production, not "95% of AI projects fail" [S53]. Details, exact figures and caveats are in section 4.
4. **Pricing backlash is about opacity and mid-term repricing, not about usage billing itself.** Cursor apologized in July 2025 for an unclear switch from request caps to API-rate usage [S31]; GitHub moved Copilot to token-based "AI Credits" on 2026-06-01 and annual-plan holders are angry about multipliers [S37]; Windsurf moved to daily/weekly quotas in 2026 and users complained about unpredictability [S39]. What works: pass-through at list price with a small disclosed markup (Zed +10%, Kilo no inference markup + 5% card fee, OpenRouter 5.5%), low default spend caps (Zed default $10), BYOK free on every tier (Zed), governance sold on top (Cline, Kilo, Cursor) [S28][S33][S35][S36].
5. **The dev-tool BYOK landscape just consolidated, which opens a neutral niche.** SpaceX agreed to buy Cursor's maker Anysphere for $60B in stock (announced 2026-06-16; closing status conflicting across sources) [S32]. On 2026-10-12 new Cursor customers began starting on an "X Subscription" bundle (existing plans continue unless switched); the $8 entry tier is Grok-only and third-party models bill at API list price from the first request [S28][S29][S30]. Model-neutral, BYOK-first, local-capable tooling is now a cleaner story than it was a year ago. ASSUMPTION: this matters most for Team/Enterprise buyers who dislike single-vendor model lock.

---

## 2. Part 1: products that help people decide WHAT or HOW to automate

### 2.1 Deciding WHAT to automate (discovery, process and task mining, opportunity assessment)

| Product | What it does for "what to automate" | Target user | Pricing model found | Steers toward | Src |
|---|---|---|---|---|---|
| **Microsoft Power Automate Process Mining + task mining** | Process mining (visualize and analyze), task-mining entitlement, Copilot guides data ingestion and generates analytics insights from natural language. 2026 wave 1 plan lists GA of object-centric process mining. | Power Platform makers, analysts, CoE | Included in Power Automate Premium at $15/user/month (billed yearly) with 50 MB per user up to 100 GB per tenant; Process Mining add-on $5,000/tenant/month (100 GB; Premium only). | Power Automate flows and Copilot Studio agents; Microsoft calls agent flows deterministic [S4]. | [S1][S2][S5] |
| **UiPath Automation Hub + Process Mining + Task Mining** | Idea intake, short questionnaire gives an early score, detailed assessment outputs feasibility (yes/no), Automation Potential (%), Ease of Implementation (%; Easy 65-100, Medium 35-65, Difficult 0-35) and one-year savings KPIs. Docs model the share of a process a **robot** can run and do not mention other technologies. Process/Task Mining are in Standard and Enterprise, not Basic. | RPA CoE, business analysts | Community free; Basic from $25 per month (page says the plan is evolving); Standard and Enterprise: contact sales. | UiPath robots, then agents (Maestro). | [S7][S9] |
| **Automation Anywhere Process Discovery** | Computer-vision capture across Windows, web, VDI and mainframe; claims to surface process variations and high-impact opportunities and to prioritize by ROI; a customer story says generative AI identified five processes to automate. Nav places it under "agentic process automation". | Large enterprises | No public price; free Cloud Community Edition (not tied to Discovery). Third-party ACV estimates ($75k-$200k for 5-10 bots) are Vendr-sourced. VERIFY. | Agentic process automation | [S12] |
| **Celonis** | Process Intelligence Graph; 2026 "Context Model"; Agent Toolkit over MCP so external agents (Copilot Studio, Bedrock) can pull process context; Orchestration Engine with branching and looping. | Large enterprise ops, finance, IT | Not public. Third-party estimates range from "$50k/year" to "$400k+/year" and an SMB average near $2k (SpendHound, 160 contracts). VERIFY. | Agents that need process context (Celonis message). | [S22] |
| **ServiceNow Process Mining + AI Workflow Factory** (launched 2026-10-06) | Process Mining finds improvements by business metrics; Autonomous Engineer (early access) and Build Agent build workflow changes; App Engine runs them; humans approve the plan; AI Control Tower governs. | ServiceNow customers | Not public. Consultancies report Foundation / Advanced / Prime tiers (April 2026) with assist pools. VERIFY. | Agents that build deterministic workflows on App Engine. | [S20][S21] |
| **Task-mining specialists: Skan.ai, Mimica, Soroco Scout, KYP.ai** | Observe desktop work. Mimica: process maps produce prioritized recommendations for **elimination, standardization and automation**; adds "Mimica Analyst" (conversational agent) and "Mimica Maker" (automation builder). Gartner's 2026 Market Guide for Task Mining Tools lists five use cases including "designing for AI agents". KYP.ai claims automatic ROI quantification and agent code generation (self-reported). | Large enterprises, transformation teams | Not published for any of them; the only numbers I found come from a competitor's comparison page, so not usable. | "AI agent readiness"; Mimica lists elimination first, similar to our `eliminate` rung. | [S24][S25] |
| **Zapier Canvas** | AI-assisted process diagramming; announcement says it recommends what to automate next from the apps you use and can draft a Zap; page is labelled Beta. | Teams, SMB | Not stated on the page. | Zapier Zaps, then Agents. | [S14] |
| **Pega Blueprint** | Upload documents, code analysis, screenshots and videos of legacy apps; AI proposes workflows and a starting application design; Pega material says experts should refine the generated lifecycles. | Enterprise architects | Pega's 2025 release says expanded capabilities are available now and describes Blueprint as no-cost. VERIFY current packaging. | Pega applications | [S27] |

### 2.2 Deciding HOW to build (copilots, agent builders, platform governance)

| Product | AI builder / copilot features | Pricing model found | Model choice / BYOK | Admin governance | Steers toward | Src |
|---|---|---|---|---|---|---|
| **Microsoft Power Automate + Copilot Studio** | Copilot builds cloud flows from natural language; Copilot in desktop flows (NL to flow, **"Repair with Copilot" for broken UI selectors, preview, US region, attended and unattended**); Copilot Studio agent flows (deterministic) and agents. | Premium $15/user/mo; Process $150/bot/mo; Hosted Process $215/bot/mo (yearly). Copilot Studio: Copilot Credits; agent action 5 credits, generative answer 2, agent flow actions 13 per 100, premium AI tool 100 per 10 responses. Pay-as-you-go $0.01 per credit and $200/month for 25,000 credits come from a secondary source [S47]. 5,000 AI Builder credits per Premium license end 2026-11-01. | Copilot Studio credit rates exclude bring-your-own-model setups, which are billed separately (Azure Foundry). Copilot is on by default in GPU regions; tenant-level off switch needs support/PowerShell. | Power Platform admin center; per-agent monthly credit caps; agents disabled at 125% of prepaid capacity; agent-flow runs blocked at 100%. | Both: deterministic agent flows plus agents; per-step price asymmetry nudges toward deterministic steps. | [S1][S2][S3][S4][S5][S6] |
| **UiPath** | Autopilot, Agent Builder, Maestro (orchestrate/automate/flow), Healing Agent (AI self-healing UI automations; Automation Suite release notes dated 2026-04-15). | Unified (Platform Units) or Flex (Agent Units). UiPath-hosted model: per LLM call, Premium 0.4 PLTU / 2 AU, Standard 0.2 / 1, Basic 0.16 / 0.8, charged per 64k input-token increment. **Customer-managed model: charged once per agent run at 0.2 PLTU / 1 AU.** | Bring-your-own model on Standard and Enterprise. | BYO identity provider, custom roles, audit retention 6 months / 2 years / 5 years (Basic / Standard / Enterprise), BYO encryption keys and credential stores (Enterprise), AI Trust Layer. **Basic tier data may be collected for model training; Standard/Enterprise can opt out.** | Agents + robots; agents reason, robots execute (community recap) [S10]. | [S7][S8][S10][S11] |
| **Zapier** | Copilot (unlimited on paid; daily limit on Free), Agents (400 activities/mo Free, 1,500 Pro), MCP, Canvas, "AI troubleshooting" listed on all plans. | Free 100 tasks; Pro from $19.99/mo (annual, 750 tasks); Team from $69/mo (annual, 2,000 tasks, 25 seats); Enterprise custom. Overage with pay-per-task: 2.5x base on monthly, 1.25x on annual; usage stops at 3x subscription. | **Bring Your Own Model (AWS Bedrock) is Enterprise only.** | Audit log 6 months (Team) / 1 year (Enterprise); SAML SSO from Team; SCIM, action restrictions, app access controls, domain restrictions, custom retention: Enterprise. | Zaps, Agents, Canvas in one product; Zapier's own steering rules not found. | [S13][S14] |
| **Make** | **Maia** (public beta on paid plans per help center): builds scenarios and agents from a prompt, modifies and debugs scenarios; **Plan mode: nothing built until you approve** (Waves '26, 2026-10-20). Agent observability (Make Grid, audit logs for agents and MCP). | Credit-based; Free 1,000 credits/mo; credits expire at term end; scenarios stop at zero credits. Dollar prices were not on the fetched page; Core/Pro/Teams at $9/$16/$29 per month (annual, 10k credits) come from a September 2026 secondary source. VERIFY. | Make says you are not locked to one AI provider; a BYO key is not documented in what I read. VERIFY. | Custom Roles and audit logs available; **"Organization policy" controlling which apps, endpoints and AI models a company can connect to is "coming soon"**; locked connections coming soon. | Both: scenarios (deterministic) and agents. | [S16][S17][S18] |
| **n8n** | AI Workflow Builder (assistant credits), AI Agent node, MCP server/client, human approval on tool calls on all plans. | Per-execution, not per step: Starter EUR20/mo (2.5k executions), Pro EUR50/mo (10k), Business EUR667/mo (40k, self-hosted only), Enterprise custom; Community self-hosted free. Page is internally inconsistent on some features. | **Self-hosted: bring your own key, no credit limits.** Hosted plans use credits. | SSO/LDAP, audit logging and log streaming, custom roles, external secrets: Enterprise. Self-hosted paid licenses ping n8n's license server daily. | Workflows with agent nodes; a third-party tutorial describes a pattern where the agent decides and a deterministic node performs the write. | [S15] |
| **Workato** | Agent Studio (Workato ONE only), Enterprise MCP, AI/MCP gateway. | Editions Standard / Business MCP / Enterprise MCP / Workato ONE plus usage; no public prices (third-party estimates weak). | BYO LLM not mentioned on the pricing page. VERIFY. | RBAC, SAML SSO, MFA, dev/test/prod in Standard; activity audit in Enterprise MCP. | Agents plus integrations | [S19] |
| **Appian** | Process HQ (process mining; Advanced and Premium tiers), AI Agents (formerly Agent Studio). | Priced per user, per month, per app; AI limits moved from token-based to action-based in January 2026 (pricing tracker). | Not found. | Not found. | Appian apps | [S26] |
| **Gumloop** | Agent and workflow builder, 35+ models. | Credits at $0.005; sources disagree on plan contents; one source says BYOK **raises** the orchestration fee from 8% to 16%. VERIFY on gumloop.com (page did not render). | BYOK on Pro (secondary). | Not found. | Agents (workflow builder now under "Legacy" heading per one source) | [S46] |

### 2.3 What the pattern tells us

- **Discovery is sold to executives; deciding the tool for each step is sold by nobody on its own.** Every product above hands the result to its own builder. The one documented scoring algorithm (UiPath) is explicitly about robot executability [S9].
- **Everyone now has an LLM co-builder, and several have an approval gate** (Make Plan mode, ServiceNow plan approval, n8n tool-call approval) [S17][S20][S15]. A "draft, diff, approve" pattern (contract decision 3) is table stakes, not a differentiator.
- **BYO model is rare and usually gated:** n8n self-hosted, UiPath Standard+/customer-managed (still charged a per-run fee), Zapier Enterprise (Bedrock only), Copilot Studio via Azure Foundry (billed separately). Make and Workato are unspecified [S8][S13][S15][S3].
- **Model governance is an Enterprise-tier feature everywhere** (Cursor Enterprise lists repository, model and MCP access controls; Cline Enterprise limits inference providers; Kilo Enterprise limits models/providers; Zapier Enterprise action restrictions; Make Organization policy coming). The contract's three-state `locked / default / user_choice` settings with a signed policy bundle available from the Team tier is stronger than anything I found. I did not find a competitor with an offline-grace signed-policy design. VERIFY [S28][S33][S35][S13][S17].
- **Runtime AI self-repair exists but is narrow:** UiPath Healing Agent and Power Automate "Repair with Copilot" repair UI selectors at run time, with documented limits (US-only, preview, no virtual desktops, no selectors containing variables) [S6][S11]. Neither redesigns a failed AI-agent automation. Freelance marketplaces list paid "fix and rescue your broken n8n/Zapier/Make workflow" gigs, which is anecdotal evidence of demand for a rescue mode [S69].

---

## 3. Part 2: desktop and developer AI apps that combine subscription, BYOK and managed credits

### 3.1 Structures and complaints

| Product | Structure (as found) | BYOK | What works | Complaints / traps | Src |
|---|---|---|---|---|---|
| **Cursor** (owned by SpaceX/xAI pending close) | From 2026-10-12: Free; Plus $8 (Grok models only); Premium $30 (4x Plus usage); Super $100 (15x); Ultra $200 (50x); Teams from $30/user; Enterprise custom. Usage expressed **only as multiples of Plus**, weekly refresh. Third-party models are billed separately by usage at API list price, spend caps available. Existing plans continue unless switched; switching is permanent. | Not mentioned on pricing page | Pass-through API list price; spend caps; weekly refresh (Cursor's stated aim: one heavy day should not exhaust the month) | June 2025: switch from 500 fast requests to $20 of API-rate usage; "unlimited" only applied to Auto mode; surprise overage; CEO apologized and refunded charges from 2025-06-16 onward. 2026: dollar size of each pool is not published; Grok-only entry tier; one forum reply criticizes loss of model freedom (self-selected sample). | [S28][S29][S30][S31] |
| **GitHub Copilot** | From 2026-06-01 usage-based billing: each plan has an allowance of "GitHub AI Credits", budgets for extra use; cost depends on model and tokens. Legacy annual Pro/Pro+ can stay (premium requests + multipliers), cancel with prorated refund, or move to monthly. | Not covered | Budgets; prorated exit for annual holders | Annual holders report multiplier changes draining quotas faster (single outlet, VERIFY); earlier 2025 premium-request limits were seen as pushing users to higher tiers. | [S37] (+ secondary) |
| **Windsurf / Devin Desktop** (Cognition) | Replaced prompt credits with daily and weekly quotas in 2026 (dates vary by source), overage at raw API pricing. | Not covered | n/a | Unpredictability: users cannot tell how much quota a request will use; bursty usage hits daily windows. All from secondary sources. VERIFY. | [S39] |
| **Claude Code on Pro/Max** | Subscription with 5-hour and weekly limits; Anthropic does not publish absolute limits (secondary). A June 2026 bug blocked about 3% of Max and Pro users until limits were reset (secondary). | n/a (API key path separate) | Subscription feels cheap for heavy use | Opaque limits, shared counter across chat and Code, weekly caps. Secondary sources only. | [S40] |
| **Cline** | Free open source; model inference at cost or on your own keys; pay-as-you-go credits; Enterprise custom (SSO, SLA, central billing, RBAC, limits on inference providers, audit logs). ClinePass $9.99/month launched 2026-06-29 and top plan cut from $100 to $20 in Feb 2026 (secondary). | Yes | **Free BYOK client, monetize governance** | No native hard spend stop that halts a session (secondary); frequent plan churn. | [S33][S34] |
| **Kilo Code** | Teams $15/user/month, no inference markup, 5% payment-processing fee on credit purchases, no credits bundled with seats; Enterprise adds model/provider limits, audit logs, SSO/OIDC/SCIM. | Bring-your-own routes bill the provider directly (Kilo's AWS page, secondary) | Transparent: seat price separate from model cost | Seat-plus-usage means two meters to explain. | [S35] |
| **Zed** | Personal free (unlimited with own keys); Pro $10/month including $5 token credit; hosted usage at provider list +10%; default extra-spend limit $10 (max $20 total); Business per seat with org spend limit. | Yes, all plans | **Disclosed markup, low default cap, BYOK on free** | Pricing changed Sept 2025 (prompt limits to tokens); complaints not found. | [S36] |
| **Msty Studio** | Free for personal non-commercial use; Aurum $149/user/year or $349 lifetime; Teams/Enterprise talk-to-us, minimum 5 seats; Go and Stack products in beta/preview. | Local and online models (term "BYOK" not used) | Lifetime option; local inference | Free tier is personal-only, so workplace use needs a paid license (licence wording from a ToS mirror, VERIFY). I found no credible complaint evidence either way. | [S41] |
| **TypingMind** | One-time licenses $39 / $79 / $99 (Premium includes free updates "forever"), bulk $395 for 10 users; 5 devices per key. | Yes, you pay providers directly | **No recurring fee, no usage fee** | Needs the customer's own API key; feature-gated tiers. No credible complaints found. | [S42] |
| **OpenRouter** (gateway) | 5.5% fee on credit purchases (Standard), 8% Business; BYOK free up to $25,000/month list-price inference, then 5%; free models capped (20 requests/min, 50/day, 1,000/day after $10 of credits); per-customer keys with credit limits via the management API; credits can expire after 365 days. | Yes | Management API keys with limits and usage tracking | **ToS section 7 on reselling (see F1).** | [S43][S44][S45] |
| **Microsoft Copilot Studio** (enterprise reference) | Prepaid credit packs and pay-as-you-go; agents disabled at 125% of capacity. | Azure Foundry models billed separately | Per-agent monthly caps | Unit price varies by 100x across features; a CloudZero article attributes to Gartner a forecast that by 2027 40% of enterprises on consumption-priced AI tooling will exceed budget by more than 2x (VERIFY the Gartner original). | [S3][S47] |

### 3.2 Patterns that work

1. **Free BYOK or local path plus paid governance/collaboration** (Zed, Cline, Kilo). The paying customer is the organization that needs allow-lists, SSO and audit, not the individual who needs a key field.
2. **Pass-through at list price with a disclosed, small markup** (Zed +10%, Kilo none + 5% card fee, OpenRouter 5.5%, Cursor third-party models at API list price).
3. **Low default spend caps and visible meters** (Zed default $10 over $5 included; Copilot Studio per-agent caps; Cursor spending caps).
4. **Show money, not abstract units.** Cursor's "multiples of Plus" and UiPath's Platform Units/Agent Units draw questions; Zed shows dollars.
5. **One-time or lifetime option for individuals** (TypingMind, Msty Aurum Lifetime) coexists with team subscriptions.
6. **Prorated, no-penalty exit when pricing changes** (GitHub offers prorated refund to annual holders).

### 3.3 Traps

1. Calling something "unlimited" when a mode or model is excluded (Cursor 2025).
2. Repricing mid-term for annual customers (GitHub 2026).
3. Quotas that reset daily or weekly and punish bursts without telling the user the cost of the next request (Windsurf, Claude Code).
4. Hard cutoffs that disable a production asset (Copilot Studio disables agents at 125%; Make stops scenarios at zero credits; Zapier stops at 3x). For Coach, the analogue is: never let a credit shortfall block read-only access to Blueprints or exports.
5. Credits that expire (Make credits expire at term end; OpenRouter may expire credits after 365 days).
6. Overage multipliers (Zapier 2.5x on monthly plans; Gumloop overage about 2.7x per a secondary source).
7. Free-tier data used for training (UiPath Basic).
8. Single-vendor model lock after acquisition (Cursor Plus tier is Grok-only).
9. Free tier that is personal-only, which surprises workplace users (Msty).

### 3.4 Price anchors (list prices I read, USD unless noted)

| Segment | Anchor | Src |
|---|---|---|
| Individual, subscription | Zed Pro $10/mo; Zapier Pro $19.99/mo annual; Cursor Premium $30/mo; Cline ClinePass $9.99/mo (secondary) | [S36][S13][S28][S34] |
| Individual, perpetual | TypingMind $39-$99 one-time; Msty Aurum $149/yr or $349 lifetime | [S42][S41] |
| Team, per seat | Kilo $15/user/mo; Cursor Teams from $30/user/mo; Zapier Team from $69/mo for 25 seats; Power Automate Premium $15/user/mo | [S35][S28][S13][S1] |
| Enterprise | Custom everywhere; governance features gate it | all |

ASSUMPTION: Individual price in the $10-$30/month band and Team near $15-$30/seat/month would be inside market norms; the right numbers belong to the pricing agent.

---

## 4. Part 3: evidence that LLM and agent automations fail

### 4.1 Evidence register (with exact figures and caveats)

| # | Finding | Figure (as published) | Source and date | Caveat | Landing-page use |
|---|---|---|---|---|---|
| E1 | Gartner forecast on agentic AI | **"Over 40%" of agentic AI projects will be canceled by end of 2027** because of escalating costs, unclear business value or inadequate risk controls | Gartner press release 2025-06-25 [S50] | Forecast, not a measured outcome. Gartner page returned 403 to automated fetch; wording confirmed through Outlook Business syndication. | Yes, phrase as "Gartner predicts". |
| E2 | Gartner on suitability | Analyst Anushree Verma: many use cases positioned as agentic do not require agentic implementations; most current projects are hype-driven early experiments; only about 130 of thousands of agentic vendors are "real" (agent washing) | Same release [S50] | Quotes from syndication; same 403 problem. | Yes. This is the single most useful sentence for our thesis. |
| E3 | Gartner survey behind E1 | 3,412 webinar attendees in Jan 2025: 19% significant investment, 42% conservative, 8% none, 31% wait and see | [S50] | Webinar poll, not a representative sample. | No. |
| E4 | Gartner on governance | 2026-05-26 press release: 40% of enterprises will demote or decommission autonomous agents by 2027 after governance gaps surface in production; four autonomy levels (observe, advise, act with approval, act autonomously) | [S51] | Press-release page not readable; details from secondary coverage. VERIFY wording. | With caveat; the autonomy ladder is useful for our `human_checkpoint` copy. |
| E5 | Gartner Hype Cycle for Agentic AI | Published 2026-04-02; places agentic AI at the Peak of Inflated Expectations; CIO survey: 17% have deployed agents, over 60% expect to within two years | [S52] | Only secondary summaries read. VERIFY. | Maybe. |
| E6 | MIT NANDA "GenAI Divide" | Report states that 95% of organizations get zero return on $30-40B of GenAI spend, and that only 5% of integrated pilots extract millions in value; for enterprise-grade, task-specific tools 60% were evaluated, 20% reached pilot and **5% reached production**; failures attributed to brittle workflows, lack of contextual learning and misalignment with day-to-day operations; external partnerships reached deployment ~67% of the time vs ~33% for internal builds | Project NANDA, titled "Preliminary Findings", research period Jan-Jun 2025, PDF metadata dated 2025-07-13 [S53] (I read the PDF text) | Methodology: 300+ public initiatives, interviews with 52 organizations, 153 leaders surveyed at four conferences; the authors call the figures directionally accurate and based on interviews, not company reporting; "success" = marked and sustained productivity or P&L impact; self-reported; widely criticized. The statistic is about task-specific enterprise GenAI tools reaching production, **not** all AI projects failing. | Use sparingly and accurately, e.g. "only 5% of task-specific enterprise GenAI pilots reached production in one preliminary MIT NANDA study". Never "95% of AI projects fail". |
| E7 | S&P Global Market Intelligence | Share of companies scrapping most AI initiatives rose to **42% from 17%**; average organization scrapped **46%** of proofs of concept before production; 1,000+ respondents, North America and Europe | CIO Dive 2025-03-14 [S54] | Read via trade press, not S&P's report. About "AI initiatives" generally. | Yes with date. |
| E8 | McKinsey State of AI 2025 | 62% at least experimenting with agents; 39% report enterprise-level EBIT impact (64% say AI enables innovation) | McKinsey 2025 report [S55] | My fetch timed out; numbers from search snippet. The "23% scaling an agentic system" figure appeared only in a newsletter. VERIFY. | Not until verified. |
| E9 | Stanford AI Index 2026 | Agents leapt from 12% to about 66% on OSWorld (human baseline 72.35%) but still fail roughly one attempt in three on structured benchmarks (report's wording) | Stanford HAI 2026 report page [S56] | Benchmark results, not enterprise outcomes. The definition of "structured benchmarks" is not confirmed. | Yes, attribute carefully. |
| E10 | TheAgentCompany | Best agent completes **30%** of tasks autonomously (simulated software company) | arXiv 2412.14161, v1 2024-12-18, v3 2025-09-10 [S57] | Models in the paper are older; newer models score higher. | Mechanism evidence only; avoid as headline. |
| E11 | CRMArena-Pro | Leading agents about **58%** single-turn and about **35%** multi-turn success; "near-zero" confidentiality awareness | arXiv 2505.18878 (May 2025) [S58] | Salesforce-authored benchmark on 2025 models. | Mechanism evidence. |
| E12 | tau-bench | Function-calling agents (gpt-4o era) succeed on **<50%** of tasks; pass^8 **<25%** in retail (same task repeated eight times) | arXiv 2406.12045 (2024) [S59] | Old models. The pass^k idea (consistency across repeats) is the durable point. | Mechanism evidence. |
| E13 | Remote Labor Index | 240 real freelance projects; top agent initially automated **2.5%**; a secondary report claims a later model reached 16.1% | CAIS + Scale AI; Epoch page [S60] | Sources conflict on current best score (Epoch page says "low single-digit"); stale. VERIFY. | No. |
| E14 | Salesforce shift to deterministic | Late Dec 2025 report (The Information, via secondary outlets): Salesforce executives said trust in LLMs declined; Agentforce leans more on predefined workflows because of randomness and ignored instructions | Secondary coverage [S61] | Original article not read; do not name Salesforce on a landing page without reading it. | Internal positioning evidence. |
| E15 | Forrester 2026 predictions | Agentic AI will cause a public breach in 2026; finance-gated decisions will delay 25% of planned AI spend into 2027; fewer than one-third can tie AI value to P&L | ITWire summary [S62] | Secondary. VERIFY. | Maybe. |
| E16 | Cost asymmetry in published prices | Copilot Studio: agent action 5 credits vs agent-flow action 0.13 credits (13 per 100) = **about 38x**; premium-model response 10 credits = about 77x a flow action. At $0.01 per credit: $0.05 vs $0.0013 vs $0.10 | Microsoft Learn billing rates, page updated 2026-10-15 [S3] | Ratios are my arithmetic. $0.01 per credit is from a secondary source [S47]. List prices only. | Yes, as "Microsoft's published rates imply...". |
| E17 | Vendor engineering guidance | Anthropic: workflows are LLMs and tools orchestrated through predefined code paths; agents choose their own path; start with the simplest solution; agentic systems trade latency and cost for performance and risk compounding errors | Anthropic engineering post [S63] | Guidance, not data. Publication date not shown in my fetch. | Yes, as authoritative guidance. |
| E18 | Reliability engineering | Post titled "Make your AI agents boring": confine the model to one node; agents propose and a separate layer commits; one fixed graph per capability; the author notes structured output removes parsing failures but not judgment failures. No empirical data in the post | Stack Overflow Blog 2026-10-07 [S64] | Opinion/design post. | Positioning support. |
| E19 | Research on compiling LLM work into code | "Compiled AI": LLM generates code once, then runs without model calls; 96% task completion with zero execution tokens on BFCL (n=400), token use down 57x at 1,000 transactions, breakeven near 17 transactions; document extraction matches direct LLM | arXiv 2604.05150 v2, 2026-07-31 [S65] | Preprint; two benchmarks. | Supports "LLM at design time, code at run time". |
| E20 | Incident | April 2026: a coding agent (Claude Opus 4.6 via Cursor) reportedly deleted a startup's production database and volume-level backups through a cloud API token it found; recovered later by the hosting provider | Newser 2026-04-30, founder's account [S66] | One-sided account; do not name vendors in marketing. | Cautionary anecdote only. |

### 4.2 Mechanism notes (my arithmetic, not measured results)

- **Compounding error:** if each step succeeds independently with probability p, an n-step chain succeeds with p^n. At p = 0.95: 5 steps 77%, 10 steps 60%, 20 steps 36%. At p = 0.90: 59%, 35%, 12%. At p = 0.99: 95%, 90%, 82%. Independence is an assumption; real failures correlate. Use as an explainer, never as a measured claim.
- **What fails in practice, per sources above:** variance across repeated runs (tau-bench pass^k), long multi-step tasks (TheAgentCompany), multi-turn drift and confidentiality (CRMArena-Pro), integration brittleness and missing memory (MIT NANDA), governance and permission scope (Gartner 2026, the database-deletion incident), unpredictable consumption cost (Copilot Studio rates, Gartner forecast via CloudZero).
- **What the failure modes imply for Coach's rungs:** formulas and data transforms belong in `script`; known systems with APIs in `api_connector`; ambiguous language in `llm_node` behind a validator; irreversible actions behind `human_checkpoint`. This lines up with Gartner's four autonomy levels (observe / advise / act with approval / act autonomously) [S51].

### 4.3 Misquote risks to avoid on a landing page

| Do not say | Why | Say instead |
|---|---|---|
| "95% of AI projects fail (MIT)" | NANDA's number is about organizations seeing zero measurable return from GenAI initiatives, and 5% of task-specific enterprise tools reaching production; preliminary, self-reported, 52 interviews. | "In one preliminary MIT NANDA study, only 5% of task-specific enterprise GenAI tools reached production." |
| "40% of agent projects have failed" | Gartner's 40% is a forecast for end of 2027. | "Gartner predicts over 40% will be canceled by the end of 2027." |
| "88%/89% of agent pilots never reach production" | Appears only in secondary blogs attributed to Deloitte and others; I could not trace an original. | Omit. |
| "Agents succeed 2.5% of the time" | Stale, conflicting. | Omit. |

---

## 5. Part 4: gap analysis and positioning

### 5.1 Capability matrix (my assessment from public docs; "?" = not found or not researched)

Legend: Yes = documented; Part = partial or within own platform only; No = not found; ? = unknown.

| Capability | Process / task mining | RPA / IPA suites (UiPath, AA, Power Automate) | iPaaS builders (Zapier, Make, n8n, Workato) | Enterprise workflow (ServiceNow, Appian, Pega) | General LLM chat / coding agents | **Coach (planned)** |
|---|---|---|---|---|---|---|
| Triage with "fix process first / don't automate" verdicts | Part (Mimica: eliminate, standardize) | Part (UiPath feasibility yes/no, On Hold) | No | Part (improvement candidates) | ad hoc | **Yes** |
| Per-step tool choice across eliminate / built-in / API / script / UI / OCR / LLM / human | No | No | No | No | ad hoc, unreliable | **Yes** |
| Recommends tools the vendor does not sell | No | No | No | No | ? | **Yes** |
| Recommendation path is deterministic and auditable | ? | Part (UiPath scoring factors are documented) | No (AI-generated) | No (AI-generated) | No | **Yes** |
| LLM use requires a written justification, validator and fallback | No | No | No | No | No | **Yes** (`llmJustification`) |
| Org environment profile constrains what may be recommended | No | Part (admin centers govern runtime) | Part (Make "Organization policy" coming) | Part | No | **Yes** |
| Admin-controlled locked/default/user_choice settings, signed policy bundle for the design assistant | No | Part (tenant toggles; Copilot off switch is tenant-level) | Part (Enterprise tier) | Part (AI Control Tower) | No | **Yes** |
| "Rescue my failed automation" mode (diagnose an existing LLM/agent automation and re-architect) | No | Part (runtime selector self-healing only) | Part (Maia debugs scenarios; AI troubleshooting) | ? | ad hoc | **Yes** |
| Hybrid pattern library mapped to an engine | No | No | Part (blog patterns) | No | No | **Yes** |
| BYOK + local models + managed credits in one picker | No | Part (UiPath/Standard+, Copilot Studio via Foundry) | Part (n8n self-hosted, Zapier Enterprise Bedrock) | ? | Part (Cline/Zed class) | **Yes** |

Limits: absence claims rest on roughly 70 searches and fetches; I read documentation for Microsoft, UiPath, Zapier, n8n, Make, Workato, Cursor, Cline, Kilo, Zed, OpenRouter and Msty, and secondary summaries for the rest. VERIFY by trial of: Mimica Analyst/Maker, UiPath Autopilot and Agent Builder, Power Automate Copilot, Make Maia, and one general assistant given the same sample process.

### 5.2 Gaps Coach could own

1. **Independent, tool-agnostic per-step advice.** Everyone recommends their own build surface. Coach recommends the cheapest rung that works, including a script, a spreadsheet formula or someone else's product. Evidence: sections 2.1-2.3.
2. **Auditable decisions.** Policy buyers want to know why a tool was chosen. Competitors' recommendations are LLM-generated or opaque scores. A deterministic engine with rule IDs, decision cards and exportable evidence matches Gartner's governance warning [S51].
3. **A written case for every LLM step** (why not code, validator, fallback, cost per run). No competitor requires this. The cost asymmetry in E16 gives it a number.
4. **Rescue mode.** Runtime self-healing handles selector breakage only [S6][S11]; nothing I found takes a failing agent automation, finds which steps should not be LLM steps, and returns a hybrid redesign. Marketplace gigs suggest demand [S69]. ASSUMPTION: the demand is real in the SMB and mid-market segment.
5. **Cross-platform design-time governance.** Admins of mixed estates (M365 plus Zapier/Make/n8n plus RPA) have separate admin centers. A single signed policy for how people decide and design, with an environment profile listing permitted tools, is unaddressed. Make's "Organization policy" and Cursor/Cline/Kilo model allow-lists show buyers want this per product [S17][S28][S33][S35].
6. **Model neutrality with local support.** Cursor's move under an xAI-owned parent with a Grok-only entry tier [S28][S32], plus BYO model being gated to higher tiers elsewhere (Zapier Enterprise only; UiPath Standard and up) [S13][S7], leave room for a BYOK/local-first design assistant.
7. **Honest hybrid positioning on AutoMate.** AutoMate has no AI at runtime (contract decision 1). That is the opposite of runtime self-healing and agentic fallbacks marketed by UiPath and Microsoft, and it can be stated as a feature: nothing probabilistic runs in production.

### 5.3 Recommended positioning

- **Category:** the independent automation architect (design-time advisor), not another builder, not another agent platform.
- **Promise:** "Decide if it is worth automating, and what should do each step, before you build." Rules decide; the AI interviews, explains and drafts; you approve.
- **Primary audiences (ASSUMPTION):** (a) automation/CoE leads and IT admins at mid-size organizations with mixed tool estates and AutoMate users; (b) teams with a failed or fragile agent pilot who need a rescue plan; (c) consultants and ops power users as the Individual tier.
- **Not the target:** large enterprises buying process mining (Celonis, ServiceNow, Pega); their sales motion, data capture and price points are a different game.
- **Proof points to publish:** the tool ladder with the rule that selected each rung; a sample decision card; the cost-per-step comparison; the policy model (locked/default/user_choice); a side-by-side of one process analysed by Coach versus a general assistant. ASSUMPTION: the golden-set eval gives credible numbers.

### 5.4 One-line pitch (pick one; first is recommended)

1. **"Coach decides whether a process is worth automating and which tool should do each step. Rules make the call, AI explains it, and every decision is auditable."**
2. "Before you build an agent, ask Coach which steps need AI at all."
3. "Stop asking an LLM to do a spreadsheet's job: Coach picks the right tool for every step and shows its reasoning."

### 5.5 Three risks of competing with the big platforms' built-in copilots

1. **Bundling and price compression.** Advice and mining are being given away inside platforms users already pay for: Power Automate Premium at $15/user/month includes a process and task mining entitlement and attended RPA [S1], and Copilot in Power Automate is on by default in supported regions [S5]; Zapier Copilot is unlimited on paid plans and Canvas is free to try [S13][S14]; Make's Maia is included on paid plans (beta) [S18]; Pega Blueprint is no-cost [S27]. Users may see "should I automate this?" as a feature, not a product. *Mitigation:* sell what a single platform cannot: cross-tool neutrality, org-wide governance of the design process, rescue, and audit exports. Price on governance and team workflows, not on advice (the Cline/Kilo pattern).
2. **Fast follow on the message and the data advantage.** Platforms already say "deterministic" [S4], hold the process logs and run-time telemetry, own distribution (admin centers, marketplaces) and ship quarterly (Make Waves '26, UiPath Fusion 2026, ServiceNow AI Workflow Factory all landed in October 2026) [S10][S17][S20]. One release note ("check agent vs flow before you build") would erode our differentiation inside that ecosystem. *Mitigation:* anchor on the things platforms are structurally unlikely to do (recommend a competitor's tool, a script, or "don't automate"); deepen the AutoMate integration; keep the rules transparent and exportable so switching away from Coach is easy and trust is high.
3. **Neutrality is expensive to maintain and easy to doubt.** A tool-agnostic catalog must track dozens of tools whose features and prices change monthly (Cursor, GitHub, Windsurf, Zapier, Make and Microsoft all changed pricing or packaging in 2025-2026) [S28][S37][S39][S13][S3]. Stale catalog entries produce wrong advice and legal exposure; buyers will also ask whether Coach favours AutoMate. *Mitigation:* catalog entries with owner, last-verified date and expiry; contribution and review workflow; disclose the AutoMate adapter and that AutoMate is one of the rungs; let the environment profile, not Coach, decide permitted tools.

### 5.6 Other risks surfaced by this research

- **Gateway terms and margin** (F1, F2): OpenRouter resale clause and 5.5% credit fee; model-provider price changes (Cursor and GitHub repricings show how quickly list prices and meters move).
- **Market noise:** Gartner places agentic AI at the Peak of Inflated Expectations [S52]; a trough may bring skeptical buyers (good for us) or budget freezes (bad). Forrester expects finance gates to delay spend [S62].
- **Substitution by general assistants** (not researched in depth): a free ChatGPT/Claude/Copilot conversation can produce a "should I automate this" answer. Our defense is determinism, audit, policy and the environment profile. ASSUMPTION; VERIFY with the side-by-side test in 5.3.
- **Customer process data on our servers** (decision 8): UiPath Enterprise offers bring-your-own encryption keys and credential stores; Enterprise buyers will expect equivalents [S7].

---

## 6. Open questions

1. Will OpenRouter confirm in writing that a Coach-operated gateway with a usage fee is permitted, or must `managed` use direct provider contracts (Azure OpenAI, Bedrock, Anthropic, OpenAI) instead? Who owns that call?
2. Free tier or time-limited trial for Individual? (F3)
3. Who is the first paying buyer: CoE lead, IT admin, AutoMate customer, or consultant? The pricing and the landing-page proof points differ.
4. Do we want a head-to-head benchmark (Coach vs general assistant vs a platform copilot on the same ten sample processes) as the main marketing asset? It needs the golden-set eval to exist first.
5. Verify before public copy: Gartner originals (pages blocked to automated fetch), Salesforce/The Information article, McKinsey 2026 edition, Make and Workato BYO-model support, Make dollar prices, Gumloop pricing, Zapier's own guidance on agent versus Zap.
6. Regulatory angle not researched: EU AI Act timelines and AI literacy duties could matter for the admin/governance pitch. VERIFY with the legal/compliance agent.
7. Should the product name any competitor on its site? Naming platforms in comparisons raises legal and trademark questions (contract: use "Coach" and do not invent brands).

---

## 7. Source index

All accessed 2026-10-25. Type: **P** = primary vendor/institution page or document, **A** = analyst or institution report read in full or in part, **N** = news/trade press, **S** = secondary/blog/aggregator (treat with caution). "Search-level" = I saw the claim in a search result summary but did not open the page.

| ID | URL | Type | Notes |
|---|---|---|---|
| S1 | https://www.microsoft.com/en-us/power-platform/products/power-automate/pricing | P | Prices Premium $15, Process $150, Hosted $215, Process Mining add-on $5,000; page says prices "for marketing purposes only". |
| S2 | https://learn.microsoft.com/en-us/power-platform/admin/powerapps-flow-licensing-faq | P | Updated 2026-10-22; process mining entitlements; 5,000 AI Builder credits removed 2026-11-01. |
| S3 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management | P | Billing rates, 125% enforcement; ms.date 2026-08-03, updated 2026-10-15. |
| S4 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/flows-overview | P | Agent flows described as deterministic; updated 2026-10-17. |
| S5 | https://learn.microsoft.com/en-us/power-automate/copilot-overview ; https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-automate/ | P | Copilot in cloud/desktop flows, process mining; dated 2026-08-17. The wave 1 release plan (object-centric process mining GA) was seen at search level only. |
| S6 | https://learn.microsoft.com/en-us/power-automate/desktop-flows/repair-at-runtime | P | Repair with Copilot (preview), limitations; updated 2025-07-10. |
| S7 | https://www.uipath.com/pricing | P | Plans, governance matrix. |
| S8 | https://docs.uipath.com/agents/automation-cloud/latest/user-guide/licensing | P | PLTU / agent unit rates; BYO model per-run charge. |
| S9 | https://docs.uipath.com/automation-hub/automation-cloud/latest/user-guide/information-about-the-detailed-assessment-algorithm | P | Assessment algorithm. |
| S10 | https://forum.uipath.com/t/uipath-fusion-2026-explained-is-rpa-dead-agentic-automation-maestro-ai-agents/5782357 | S | Community post dated 2026-10-07 summarizing Fusion 2026; not UiPath-authored. |
| S11 | https://docs.uipath.com/agents/automation-suite/2.2510/release-notes-ha/2-2510-2 | P (search-level) | Healing Agent release note; VERIFY. |
| S12 | https://www.automationanywhere.com/products/process-discovery | P | Marketing page. Pricing page returned 404. |
| S13 | https://zapier.com/pricing | P | Plans, AI features, governance table. |
| S14 | https://zapier.com/canvas | P | Canvas labelled Beta. |
| S15 | https://n8n.io/pricing/ | P | Page internally inconsistent on some items. |
| S16 | https://www.make.com/en/pricing | P | No dollar amounts in fetched text; credit rules. |
| S17 | https://www.make.com/blog/waves26-the-glass-box-for-the-agentic-era | P | Dated 2026-10-20. |
| S18 | https://help.make.com/introduction-to-maia-by-make | P (search-level) | Maia scope and beta status. |
| S19 | https://www.workato.com/pricing | P | Editions, no prices. |
| S20 | https://www.infoworld.com/article/4231166/servicenow-takes-aim-at-enterprise-ais-workflow-bottleneck-with-ai-workflow-factory-2.html | N | Dated 2026-10-06. |
| S21 | https://eesel.ai/blog/servicenow-ai-pricing ; https://redresscompliance.com/servicenow-2026-pricing-tiers-pillar | S | ServiceNow tiers and consumption; consultancies disagree. |
| S22 | https://www.celonis.com/news/article/finally-enterprise-ai-gets-the-context-it-needs-to-succeed-celonis-next-2026 ; https://www.erpresearch.com/erp-add-ons/process-mining/celonis/pricing ; https://www.spendhound.com/marketplace/celonis-pricing | P / S | Celonis:NEXT 2026 (search-level); price estimates are secondary. |
| S23 | https://www.celonis.com/news/press/the-enterprise-ai-reality-check-high-ambitions-meet-operational-barriers | P | Vendor-released survey, 1,649 leaders, fieldwork Jun-Jul 2025, released 2026-02-04 (76% say processes hold them back). Not used for headline claims. |
| S24 | https://mimica.ai/articles/mimica-featured-2026-gartner-market-guide-task-mining-tools | P | Vendor announcement dated 2026-05-21 about the Gartner guide. |
| S25 | https://www.bardeen.ai/best/task-mining-tools ; https://kyp.ai/task-mining-tools-compared/ | S | Vendor-adjacent roundups. |
| S26 | https://pricingsaas.com/companies/appian/diffs/2025Q4 | S | Pricing tracker. |
| S27 | https://www.businesswire.com/news/home/20250602244821/en | P (search-level) | Pega Blueprint expansion, 2025. |
| S28 | https://cursor.com/pricing | P | Read twice (HTML via curl and WebFetch); matches. |
| S29 | https://finance.yahoo.com/technology/ai/articles/spacex-bundles-grok-x-cursor-000517004.html | N | Dated 2026-10-12. |
| S30 | https://dev.to/gabrielanhaia/cursors-new-plans-include-grok-claude-and-gpt-now-bill-at-api-list-price-36af | S | Posted 2026-10-14; user-complaint commentary is a small forum sample. |
| S31 | https://techcrunch.com/2025/07/07/cursor-apologizes-for-unclear-pricing-changes-that-upset-users/ | N | Apology and refund. |
| S32 | https://qz.com/spacex-buying-cursor-anysphere-60-billion-deal-061626 | N (search-level) | $60B all-stock; announcement 2026-06-16 per 8-K; closing status conflicting. VERIFY in SEC filings. |
| S33 | https://cline.bot/pricing | P | Free OSS, Enterprise custom, BYOK, "Model Inference at Cost or BYOK". |
| S34 | https://www.usagepricing.com/blueprint/activity/cline-2026-09-18-price-change | S | ClinePass and plan changes. |
| S35 | https://kilo.ai/docs/collaborate/teams/about-plans | P | Teams $15; no inference markup; 5% fee on credit purchases. |
| S36 | https://zed.dev/docs/ai/plans-and-usage.html | P | Pro $10 incl. $5 tokens; +10% markup; default $10 limit; BYOK all plans. |
| S37 | https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/what-changed-with-billing | P | June 1, 2026 usage-based billing. |
| S39 | https://www.verdent.ai/ja/guides/windsurf-pricing-2026 ; https://usagepricing.com/blueprint/activity/windsurf-2026-04-packaging | S | Windsurf quota change; complaints. |
| S40 | https://inventivehq.com/blog/claude-code-rate-limits-explained ; https://pasqualepillitteri.it/en/news/5428/claude-code-weekly-usage-limit-bug-3-percent | S | Claude plan limits and a June 2026 bug. |
| S41 | https://msty.ai/pricing | P | Aurum $149/yr, $349 lifetime; Teams min 5 seats. ToS wording from a mirror (nuxt.dev); VERIFY. |
| S42 | https://checkout.typingmind.com/buy | P | One-time prices, update policy, 5 devices. |
| S43 | https://openrouter.ai/pricing | P | 5.5% / 8% credit fee; BYOK terms; free-model caps. |
| S44 | https://openrouter.ai/terms | P | Last updated 2026-08-31; section 7 reselling clause; credit expiry 365 days. Read through a fetch extract; read the clause yourself. |
| S45 | https://openrouter.ai/docs/guides/overview/auth/provisioning-api-keys | P | Management API keys with limits and usage. |
| S46 | https://www.jetadmin.io/blog/gumloop-review/ | S | Gumloop credits and fees; VERIFY. |
| S47 | https://www.cloudzero.com/blog/copilot-studio-pricing/ | S | $0.01 per credit, $200 pack, Gartner forecast quoted secondhand. |
| S50 | https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027 ; https://www.outlookbusiness.com/artificial-intelligence/over-40-of-agentic-ai-projects-will-be-scrapped-by-2027-says-gartner | A / N | Gartner page returned 403 / a bot check to automated fetch (I did not try to bypass it); text read through the syndicated Outlook Business copy. |
| S51 | https://www.gartner.com/en/newsroom/press-releases/2026-05-26-gartner-says-applying-uniform-governance-across-ai-agents-will-lead-to-enterprise-ai-agent-failure ; https://hostingjournalist.com/news/gartner-warns-ai-agent-governance-failures-ahead-by-2027 | A / N | Gartner page 403; details from secondary (publication 2026-06-01). |
| S52 | https://www.gartner.com/en/articles/hype-cycle-for-agentic-ai | A (search-level) | 403; Peak of Inflated Expectations and 17% deployed figure from secondary summaries. |
| S53 | https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf | A | Mirror of the Project NANDA report; I extracted and read the PDF text. |
| S54 | https://www.ciodive.com/news/AI-project-fail-data-SPGlobal/742590/ | N | S&P Global Market Intelligence survey, 2025-03-14. |
| S55 | https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai | A (search-level) | Fetch timed out. |
| S56 | https://hai.stanford.edu/ai-index/2026-ai-index-report | A | OSWorld and "1 in 3" statements. |
| S57 | https://arxiv.org/abs/2412.14161 | A | TheAgentCompany. |
| S58 | https://arxiv.org/abs/2505.18878 | A | CRMArena-Pro. |
| S59 | https://arxiv.org/abs/2406.12045 | A | tau-bench. |
| S60 | https://epoch.ai/benchmarks/rli ; https://the-decoder.com/ai-agents-can-now-complete-16-percent-of-freelance-jobs-at-pro-quality-up-from-2-5-percent-eight-months-ago/ | A / S | Conflicting scores. |
| S61 | https://www.shopifreaks.com/salesforce-executives-say-trust-in-generative-ai-has-declined/ ; https://opentools.ai/news/salesforce-steps-back-from-ai-executives-reveal-overconfidence-in-llms-pivot-to-deterministic-automation | S | Secondary relays of The Information (late Dec 2025). Original not read. |
| S62 | https://itwire.com/it-industry-news/strategy/forrester-unveils-2026-predictions-for-ai-and-tech-leadership | N (search-level) | Forrester predictions. |
| S63 | https://www.anthropic.com/engineering/building-effective-agents | P | Workflows vs agents guidance. |
| S64 | https://stackoverflow.blog/2026/10/07/part-1-make-your-ai-agents-boring-the-determinism-layer/ | P | Design post, CC BY-SA. |
| S65 | https://arxiv.org/abs/2604.05150 | A | Compiled AI, v2 2026-07-31. |
| S66 | https://www.newser.com/story/388304/company-says-ai-agent-nearly-ruined-it.html | N | 2026-04-30, founder's account. |
| S69 | https://www.upwork.com/services/product/development-it-fix-and-rescue-your-broken-n8n-workflow-within-24-hours-2059989801445105312 | S | Freelance gig listing as anecdotal demand signal. |

Not accessible or not opened (so nothing here depends on them): Gartner newsroom pages (bot-check 403), Notebookcheck (403), Forbes (403), McKinsey page (timeout), Automation Anywhere pricing page (404), TypingMind home and pricing pages (empty render), Gumloop pricing (empty render), Celonis pricing (404 equivalent: contact page only), ServiceNow Process Mining page (403).
