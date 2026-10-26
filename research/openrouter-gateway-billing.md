# OpenRouter gateway + billing research (managed credits connection)

Scope: the `managed` model connection (app -> our gateway -> OpenRouter, platform subscription plus usage at cost + transaction fee), and `byok_openrouter` (customer's own OpenRouter key, called from the client).
Research date: 2026-10-25. Every source below was read in this session and was last accessed 2026-10-25 (source table in section 10; claims cite `[S#]`). Live API figures were fetched on the same date.
Conventions from the shared contract: `VERIFY:` = could not confirm from a source; `ASSUMPTION:` = my guess. Prices are USD.

---

## 0. Conflicts with the shared contract (read first)

| # | Contract says | What the sources say | Severity | Suggested handling |
|---|---|---|---|---|
| C1 | Decision 4: `managed` = customer pays usage at cost + transaction fee, via our gateway to OpenRouter. | OpenRouter ToS (Last Updated 2026-08-31) lists as prohibited conduct accessing the Service for "reselling API access to Models" or building a competing service, and bars selling or transferring the access granted under the Terms (section 7). The same ToS elsewhere contemplates the integrator's own customers using models when the Service is incorporated into the integrator's products and services (sections 5.1, 5.2, 5.5, 5.6). [S1] | Critical. The commercial model is not clearly permitted. | Do not launch `managed` on reading alone. Get written confirmation or an addendum from OpenRouter (section 9, R1). Keep the upstream pluggable (R2). |
| C2 | Terminology: `byok_openrouter` = customer's own OpenRouter key; `byok_provider` = customer's own provider key. | OpenRouter uses "BYOK" for something else: provider keys stored inside an OpenRouter account (free up to $25,000/month list-price inference, then a 5% fee). [S2][S3] | Low (naming). | Keep contract names. Add a glossary line so nobody reads the OpenRouter BYOK fee as applying to `byok_openrouter`. For `byok_openrouter` the customer pays OpenRouter's own 5.5% credit fee on their own account. [S2] |
| C3 | `byok_openrouter` key lives in Windows Credential Manager/DPAPI. | OpenRouter supports an OAuth PKCE flow that returns a user-controlled key; localhost callbacks on any port are supported, so a desktop app can connect without the user pasting a key. [S20] | None (improvement). | Offer OAuth PKCE as the primary way to capture the key; paste as fallback. Still store the resulting key in DPAPI. |
| C4 | "Gateway logs metadata only"; enforcement is server-side for `managed`. | Consistent. OpenRouter stores no prompts unless an account opts in, and can enforce model/provider allowlists, ZDR and budgets per key through guardrails. [S9][S10][S11] | None. | Our OpenRouter account must keep prompt logging and "use of inputs/outputs" OFF (section 5). |
| C5 | Implicit: OpenRouter is a stable independent upstream. | Stripe announced on 2026-08-19 that it agreed to acquire OpenRouter; OpenRouter says closing is expected within weeks (subject to customary conditions) and that nothing changes for existing integrations. I found no closing announcement as of 2026-10-25. [S18][S19] | Medium. Terms, fees and policy could change. | Track the close; ask for a term-change notice commitment (R3). |

---

## 1. Five most decision-relevant findings

1. **Resale is the gating risk.** ToS section 7 prohibits reselling API access to models, while sections 5.1/5.2 allow end customers of products that incorporate the Service. A metered, marked-up pass-through gateway sits on the line. Written OpenRouter approval is required before charging for `managed`. A ToS-violation termination forfeits unused credits and cuts off every customer at once (sections 9, 5.5). [S1]
2. **Per-customer isolation is available today and is good enough.** Management API (`/api/v1/keys`) creates per-customer keys with a USD `limit`, `limit_reset`, `expires_at`, per-key usage fields, and an `external.user` tag. Per-request `usage.cost` and a `/generation` lookup give exact cost. Guardrails (model/provider allowlist, per-model-group ZDR) attach per key. Key limits are available on every plan; there is no per-key prepaid balance, so our own ledger must be the source of truth. [S4][S5][S7][S8][S9][S44]
3. **OpenRouter's fee is 5.5% on credit purchases only** (Standard; 8% Business; discounts on Enterprise; $0.80 minimum fee per non-crypto purchase), with no markup on inference. Credits expire after 365 days and are refundable only within 24 hours. This sets our cost multiplier at about 1.055 per dollar of usage. [S1][S2][S17]
4. **Recommended transaction fee: 20% on OpenRouter-reported cost** (billed = `usage.cost` x 1.20) when processing via Stripe directly, plus a $10 minimum top-up. This yields about +$4.29 (8.6%) on a $50 top-up and only +$0.16 (3.2%) on a $5 top-up before refunds/disputes, so $5 top-ups should not be offered as a normal path. A merchant of record (Paddle/Lemon Squeezy/Stripe Managed Payments) needs about 25% and a $20 minimum. (Section 8.)
5. **Best billing fit: Stripe direct (Billing for the subscription, our own append-only wallet ledger, off-session PaymentIntents for auto top-up, Stripe Tax for calculation).** Stripe Billing credit grants apply at invoice finalization rather than as a live spendable balance; Stripe Managed Payments excludes advanced integrations and several subscription/invoice patterns, so saved-card auto top-up looks unsupported (inference from its eligibility page; VERIFY); Paddle lists virtual currency or stored value (store credit) as prohibited and its native usage billing is on a waitlist. (Section 7.)

---

## 2. Q1: Does OpenRouter permit reselling usage at cost + fee?

**Verdict: not clearly permitted; ambiguous; needs written confirmation. No reseller/ISV program or enterprise-agreement requirement is published.** [S1][S22]

| Topic | What the sources say | Implication |
|---|---|---|
| Resale prohibition | Section 7 (Prohibited Conduct) bars accessing the Service for purposes of reselling API access to Models or otherwise developing a competing service. Section 7 also bars selling or transferring the access granted under the Terms. [S1] | A gateway that re-bills raw model usage reads like resale. |
| Customer use carve-out | Section 5.1: the Service gives the account holder, its Authorized Users and its customers access to Models, the last to the extent the Service is incorporated into the account holder's own products and services. Sections 5.2, 5.5, 5.6 repeat the customer concept (flow-down, suspension, configuration). [S1] | OpenRouter expects products built on it that have customers. Our Coach is a product with its own value (platform subscription), not a bare API proxy. This is the argument to make to OpenRouter, but it is an interpretation, not a grant. |
| Flow-down duty | We must require customers to follow the ToS, OpenRouter documentation and each model provider's terms, and we are responsible for their acts (5.2). We carry sole responsibility for our customers' violations of Model Terms (5.5). [S1] | Our customer terms need an OpenRouter/model-provider flow-down and AUP. |
| Shared-fate suspension | OpenRouter may suspend or restrict access of us and our customers if it believes any customer violated Model Terms (5.5). Section 9: OpenRouter may suspend or terminate access at any time, for any reason or none, with or without notice; termination for a ToS violation means unused credits are not refunded. [S1] | One bad customer can take down all `managed` customers. Per-customer keys + fast disable + customer screening are mandatory. |
| Restricted models/regions | Certain providers do not allow access by some organizations or from some countries; we must not let customers access Restricted Models, including via VPN/proxy (5.7). Breach is a material breach with immediate suspension. [S1] | Gateway must screen customer country/entity and per-model restrictions. VERIFY: how OpenRouter exposes which models are restricted for which regions (not found in the docs read). |
| Attribution | The ToS contains no attribution requirement. Attribution headers (`HTTP-Referer`, `X-OpenRouter-Title`) are optional and only drive public app rankings. [S1][S46] | Skip attribution, or send a generic app name; do not leak customer data in headers. |
| Enterprise agreement | Not required by the ToS. Enterprise offers invoicing, SLAs, custom data policies, DPA review and fee discounts. No ISV/reseller/partner program is listed. [S22] The key-creation API has an `external` object described as a "partner" end-user identifier and partner-supplied key, which suggests a partner mode exists. [S5] | ASK OpenRouter sales whether a partner/reseller arrangement exists (R1). |
| Use-case restrictions | The customer alone decides whether a model suits its use case, including regulated, high-risk, sensitive or customer-facing use (5.6). Red Teaming (prompt injection, jailbreaking or other adversarial action against Models) needs prior written approval (sections 7, 8). [S1] | Coach critique and test-case drafting are normal use. If the Coach ever generates adversarial/prompt-injection tests against customer LLM steps, get Red Teaming approval or exclude it. |
| Positive signal | Stripe documents reselling LLM tokens with your own markup as a supported billing pattern for gateways. Stripe is acquiring OpenRouter. [S33][S19] | Suggests the business model is acceptable to the likely future parent. It is not a license from OpenRouter. |

---

## 3. Q2: Programmatic per-customer isolation (what exists today)

All items verified in docs on 2026-10-25 unless marked VERIFY.

| Capability | Available today? | Endpoint / field | Notes |
|---|---|---|---|
| Provision keys per customer | Yes. Management API keys; plan: Standard and up (pricing table lists "Management API key" as Yes for Standard, No for Free). [S2][S4] | `POST /api/v1/keys`; `GET /api/v1/keys` (100 per page, `offset`); `GET/PATCH/DELETE /api/v1/keys/{hash}` | Management keys cannot call inference. In orgs only Org Admins can create them. Expiry is fixed at creation and cannot be changed (rotate before expiry or you get `401 API key expired`). The plaintext key is returned once. The docs list automatic per-customer-instance key creation for SaaS applications as a use case. [S4] |
| Per-key credit limit | Yes, on every plan. [S44] | `limit` (USD), `limit_reset` (`daily`/`weekly`/`monthly`/null; resets 00:00 UTC, weeks Mon-Sun), `include_byok_in_limit`, `disabled`, `expires_at` (create), `workspace_id` [S5] | Over-limit requests return `403` (`openrouter_key_limit`). [S6][S44] ASSUMPTION: like workspace budgets, requests already in flight may overshoot slightly (documented for workspace budgets only [S23]). |
| Per-key usage reporting | Yes | Key object: `usage`, `usage_daily`, `usage_weekly`, `usage_monthly`, `byok_usage*`, `limit_remaining`, `last_used_at`. A key can read itself at `GET /api/v1/key` (adds `budgets`, `effective_budget`, free-model counters). [S4][S5][S6] | Also `GET /api/v1/credits` (account credits purchased and used, Management key), `GET /api/v1/activity`, `POST /api/v1/analytics/query`. [S4] |
| Per-request cost in responses | Yes, always on | `usage.cost` (credits charged to our account = USD), `usage.cost_details.upstream_inference_cost` (BYOK only), prompt/completion/reasoning/cached/cache-write token counts. In streaming, usage arrives in the final SSE message. Zero-completion insurance means empty or error responses are not charged. [S7][S25] | Bill from `usage.cost`, never from a cached price table: OpenRouter charges the new rate immediately if a provider changes price. [S2 FAQ] |
| Generation/usage lookup | Yes | `GET /api/v1/generation?id=gen-...` returns `total_cost`, `usage`, `upstream_inference_cost`, tokens (native and normalized), `model`, `provider_name`, `latency`, `generation_time`, `finish_reason`, `streamed`, `cancelled`, `is_byok`, `external_user`, `created_at`. [S8] | Use for reconciliation and for streams that end without a final usage chunk. VERIFY: delay before a generation is queryable; the docs read do not state one. |
| End-user tagging | Yes | Request field `user`; key-create field `external.user`; `POST /api/v1/external-users` registers tracking IDs (Management key). Changing a registration's state does not enforce inference access. [S24][S21] | Use an opaque pseudonymous ID, not an email. Tagging is for analytics, not access control. |
| Per-key policy (server-side enforcement) | Yes | Guardrails: model allowlist, provider allowlist, ZDR per model group, budgets (daily/weekly/monthly), data regions (Business+), content filters, sensitive-info redaction. One guardrail per key; combined with member and workspace-default guardrails (stricter wins). Assign via `/api/v1/guardrails/{id}/assignments/keys`. [S9] | Matches contract decision 7 (server-side enforcement for `managed`). A guardrail enforces nothing until assigned. |
| Workspace isolation | Yes, limited by plan | Workspaces: 5 on Free/Standard, 1,000 on Business, custom on Enterprise. [S2] | One workspace per environment is enough. Per-customer workspaces would need Business or Enterprise. Workspace budgets are documented as Enterprise-only [S23], while the pricing table shows "Budgets & Spend Controls" for Standard. [S2] Documentation conflict; key limits are the safe choice. |
| Prepaid funding per key | No | Keys draw on the account's shared credit pool; `limit` is a cap, not a balance. [S21][S6] | Our wallet ledger is authoritative. Set the key `limit` to (usage so far + wallet balance + small headroom) as a backstop and PATCH it on top-up. |
| Low-balance webhook | Not found | "Advanced notifications" are Business+ and the docs describe alerts for workspace budgets. [S2][S23] | VERIFY: whether any push notification exists for account balance. Poll `GET /api/v1/credits` and monitor our own balance instead. |
| Limits on key count / creation rate | Not documented in pages read | n/a | VERIFY with OpenRouter (R8) before designing one key per user. |

**Recommended mapping (ASSUMPTION):**

| Our object | OpenRouter object |
|---|---|
| Gateway tenant (organization) | One key per org (Enterprise: optionally one key per user), created via Management API; plaintext key held only in the gateway secret store, never sent to a client |
| Wallet balance | Our ledger (append-only); mirrored into key `limit` as a backstop |
| Tier / admin policy (locked settings) | One guardrail per tier or per org (model allowlist, ZDR flags), assigned to the org's key |
| End user | `user` request field = opaque ID |
| Per-request billing event | `usage.cost` from the response, keyed idempotently by generation `id`; nightly reconciliation against `GET /generation` and the key `usage` totals |
| Offboarding or abuse | `PATCH /api/v1/keys/{hash}` with `disabled: true`, then `DELETE` |

**Concurrency caveat:** OpenRouter holds an estimated cost for each running paid request against a prepaid account's balance (the "in-flight spending budget") and returns `402` with `in_flight_budget_exhausted` when many requests overlap. It does not apply to enterprise, paid-subscription or invoice-billed accounts, nor above a balance threshold. A multi-tenant gateway should hold a large enough balance, or be on invoice billing. [S6]

---

## 4. Q3: Fees, minimums, payment methods, refunds

| Item | Value | Source |
|---|---|---|
| Credit purchase fee, Standard | 5.5% of order amount, minimum fee $0.80 (non-crypto). Applies at purchase only, never per request | [S2][S17] |
| Credit purchase fee, Business | 8%. Upgrade from account settings, no contract, downgrade allowed after 30 days | [S2] |
| Credit purchase fee, Enterprise | Fee discounts available (no figure published); pricing by contract with volume, prepaid credits and annual commitments | [S2][S22] |
| Crypto (USDC) | 5.0% flat, no minimum. Crypto payments are never refundable | [S17][S1 s4.1] |
| Worked purchase fees | $5 -> $0.80; $10 -> $0.80; $25 -> $1.38; $100 -> $5.50; $1,000 -> $55.00 | [S17] |
| Where the fee lands | VERIFY: whether the fee is added to the amount charged (credits received = order amount) or deducted from it. The fee table is expressed per "order amount". The math in section 8 assumes added on top. | [S17] |
| Inference markup | None; provider list price on every plan | [S2][S3] |
| Fee on OpenRouter-BYOK (provider keys in OpenRouter) | $25,000/month list-price inference free on Standard/Business, then 5% of list price, deducted from credits. Enterprise custom. A 2025 blog post says this will become a fixed subscription (pricing TBD). Not relevant to our `byok_*` connections | [S2][S3][S17] |
| Minimum / maximum purchase | $5 minimum, $25,000 maximum per transaction | [S1 s4.1] |
| Payment methods | Major cards, AliPay, USDC; PayPal "in progress". Enterprise: invoicing and purchase orders | [S3][S2] |
| Auto top-up | Yes: Auto Recharge when balance is below a threshold | [S1 s4.2][S2] |
| Refund policy | Unused credits refundable only within 24 hours of the transaction; platform fee not refunded; crypto never. Remaining credits refunded within 30 days of account termination, unless OpenRouter terminated for a ToS violation | [S1 s4.1, s9][S3] |
| Credit expiry | OpenRouter reserves the right to expire unused credits 365 days after purchase. Credits are non-transferable, including between accounts | [S1 s4.2, s4.4][S3] |
| Taxes | Prices exclude VAT/GST; added on invoices where required | [S2] |

Implication: buy OpenRouter credits in batches of at least $14.55 (5.5% x $14.55 = $0.80) to avoid the minimum fee, and do not over-stock (no refunds after 24 hours, 365-day expiry). Any customer wallet balance we later refund has already cost us the 5.5% if we pre-bought the matching credits. Buy just in time, keep a buffer sized to a few days of peak spend plus the in-flight budget need.

---

## 5. Q4: Data handling

### 5.1 OpenRouter's own handling

| Topic | Facts | Source |
|---|---|---|
| Prompt/completion logging default | Off. OpenRouter stores prompts and responses only if the account opts into Private Input & Output Logging or "OpenRouter use of inputs/outputs" (the latter gives a 1% usage discount). Metadata (tokens, latency, model, timestamps) is always stored | [S11][S3] |
| Opt-in license risk | Opting into prompt logging grants OpenRouter a perpetual, irrevocable license including the right to license or sell anonymized content (ToS 6.2) | [S1] |
| Anonymous categorization | A small sample of prompts is categorized by a zero-data-retention model for rankings; if not opted in, it is stored anonymously and never tied to an account. ToS 6.5 grants OpenRouter a license for anonymized input categorization | [S11][S1] |
| Retention of logged content | Varies by feature and is described in per-feature docs (ToS 6.3(c)). Processing-related storage exists for batch/large requests (6.3(b)); availability for ZDR accounts is documented per feature | [S1] |
| Org-level configuration | Organizational accounts can enable prompt logging, chat logging, ZDR and model training settings for Authorized Users (3.1). Org admins can view logged data | [S1][S11] |
| SOC 2, DPA | SOC 2 Type II; DPA incorporated by the ToS for organizations; Business: signed copy available on request; Enterprise: customizations, or OpenRouter reviews yours. DPA includes SCCs | [S22][S2][S3] |
| EU residency | Requests to `eu.openrouter.ai` are decrypted in the EU and routed only to shared provider endpoints in the EU/EEA/UK/Switzerland. Business and Enterprise plans only. Account and billing data may be stored in the US; DPA Exhibit A covers API payloads when elected in writing. `us.openrouter.ai` also exists | [S3][S2][S12] |

### 5.2 Provider-level controls and how to enforce them

| Control | Per request | Per key | Per account / workspace | Notes |
|---|---|---|---|---|
| Exclude providers that may store or train on data | `provider.data_collection: "deny"` (default is `"allow"`) | Via guardrail provider allowlist | Account privacy setting; separate settings for paid and free models | Default is permissive, so the gateway must set `deny` on every `managed` request. [S13][S12] |
| Zero Data Retention routing | `provider.zdr: true`. It is OR-ed with account/guardrail ZDR, so a request can add ZDR but cannot weaken it | Guardrail: `enforce_zdr_anthropic`, `_openai`, `_google`, `_xai`, `_other` (per model group; legacy `enforce_zdr` deprecated) | Account privacy settings, per model group | ZDR is available on every plan. In-memory prompt caching is not treated as retention. ZDR covers inference routing only, not plugins or server tools (web search etc.). If OpenRouter cannot establish a provider's policy it assumes the endpoint retains and trains. [S10] |
| Provider / model allowlist | `provider.only`, `provider.ignore`, `models` | Guardrail model and provider allowlists (intersection with other guardrails) | Account provider restrictions | [S13][S9] |
| Region | Hostname (`eu.` / `us.openrouter.ai`) | Guardrail `allowed_data_regions` (Business+) | n/a | Requests on a non-permitted hostname get `403`. [S9] |
| Content filters | n/a | Guardrail custom regex redact/block; sensitive-info (PII) redaction/block | n/a | Optional extra for Enterprise tier. [S9] |
| Live ZDR endpoint list | n/a | n/a | `GET /api/v1/endpoints/zdr` (public): on 2026-10-25 it listed 1,074 endpoints covering 377 distinct models, versus 467 text-output models in the catalog (about 81% of models have at least one ZDR endpoint) | [S26][S16] |

**Recommended gateway policy (ASSUMPTION):**
- Every `managed` request: `provider.data_collection="deny"`; the gateway strips any client-supplied `provider` overrides and sets its own.
- Tier defaults: Individual/Team = `data_collection=deny` plus catalog filtered to such endpoints; Enterprise = ZDR on all model groups via guardrail, optional `eu.openrouter.ai` (needs Business or Enterprise plan on our account).
- Our OpenRouter account: prompt logging OFF, "use of inputs/outputs" OFF (do not take the 1% discount), no observability/Broadcast destinations that carry content.
- Disclose the chain on the sub-processor list: customer -> us -> OpenRouter -> model provider. Disclose OpenRouter's anonymized categorization (ToS 6.5).
- Customers with `custom_openai_compat` or `local` connections never touch OpenRouter.

---

## 6. Q5: Limits and reliability

### 6.1 Rate limits

| Item | Value | Source |
|---|---|---|
| Paid models | No plan-based platform rate limit; limits come from the upstream provider; OpenRouter's DDoS protection can return 429 for extreme bursts | [S2][S6] |
| Capacity is global | Extra accounts or API keys do not change rate limits because capacity is governed globally. All our customers share our account's capacity | [S6] |
| Provider-side 429s | Handled by provider fallback, then model fallback | [S6][S14] |
| Enterprise | Higher allowances available; contractual SLAs (Enterprise only) | [S2] |
| Model availability | Provided on an as-available basis with no guarantee (ToS 5.4). A deprecated model returns `404` | [S1][S2] |

### 6.2 Free models (`:free`): not viable for `managed`

| Item | Value | Source |
|---|---|---|
| Limits | 20 requests/minute; 50 requests/day if less than $10 of credits ever purchased, else 1,000/day. Failed attempts count. A negative balance blocks free models | [S6][S2] |
| Scope | Per account. Because capacity is global, 1,000 requests/day would be shared by every customer of the gateway | [S6] |
| Billing trap | If a `:free` model is in a `models` fallback array, a fallback to a paid model is billed | [S15] |
| Data policy | Free and paid models have separate training/data settings; the FAQ says free models are usually not suitable for production | [S12][S3] |
| Catalog | 17 `:free` entries among 467 text-output models on 2026-10-25 (16 of them advertise `tools`) | [S16 live] |
| Recommendation | Do not route `managed` traffic to `:free`. Acceptable only on a customer's own account (`byok_openrouter`), where the daily cap belongs to the customer, and for synthetic demo data. Label as Experimental in the certification scheme | ASSUMPTION |

### 6.3 Fallback and routing features

| Feature | Detail | Source |
|---|---|---|
| Model fallbacks | `models: [...]` in priority order; next model tried on provider down, rate limit, or moderation refusal | [S14] |
| Provider fallback | On by default (`allow_fallbacks: true`); `only`, `ignore`, `order`, `sort` (price/throughput/latency), `max_price`, `preferred_min_throughput`, `quantizations`, `require_parameters` | [S13] |
| Tool-call support in routing | With `tools`, OpenRouter routes on a best-effort basis to providers known to support them. `require_parameters: true` restricts to endpoints supporting every parameter in the request (use it for `tools` and `response_format`). An "Auto Exacto" feature optimizes provider choice for tool calling | [S13][S45] |
| Cost control | `max_price` per request; per-key `limit`; pin a model and provider for consistent behavior | [S13][S2] |
| Failure billing | Zero-completion insurance: no charge for empty or errored responses | [S25] |

### 6.4 Model catalog API

`GET https://openrouter.ai/api/v1/models` (public, no key) and `GET /api/v1/model/{author}/{slug}`. [S16]

| Needed by Coach | In the catalog? | Detail |
|---|---|---|
| Tool-calling support | Yes | `supported_parameters` contains `tools`, `tool_choice`. Filter: `?supported_parameters=tools` |
| Structured output support | Yes | `supported_parameters` contains `structured_outputs`, `response_format`. Support is per endpoint and can change; the docs recommend `require_parameters: true` |
| Context length | Yes | `context_length`; `top_provider` has provider limits |
| Pricing per model | Yes | `pricing.prompt`, `completion`, `request`, `image`, `web_search`, `internal_reasoning`, `input_cache_read`, `input_cache_write` (USD per token as strings), plus `pricing.overrides` for long-context and time-of-day pricing |
| Other | Yes | `architecture.input_modalities`, `expiration_date`, `knowledge_cutoff`, `benchmarks`, `default_parameters`; sort options include price, context, throughput, latency |

Live snapshot, 2026-10-25 (default text-output filter): 467 models; 399 with `tools`; 389 with `structured_outputs`; 401 with `response_format`; 349 with both tools and structured outputs; 346 with context of 200k tokens or more. [S16 live]

Implication for the contract's capability probe: catalog flags are a good prefilter for the model picker, but endpoint-level support varies, so the connect-time probe (tool-call round trip, JSON-schema output, context) is still needed. Re-fetch the catalog on a schedule; the pricing shown is for the "top provider" and can change.

---

## 7. Q6: Billing stack for subscription + prepaid usage wallet with auto top-up

### 7.1 Requirement summary

(a) monthly platform subscription per seat/org; (b) prepaid wallet in USD; (c) auto top-up when balance falls under a threshold, charged off-session; (d) per-request debits at cost x (1 + m); (e) tax compliance across countries; (f) works for $5 to $500 payments.

### 7.2 Comparison

| | Stripe direct (Payments + Billing + Tax) | Stripe Managed Payments (MoR) | Paddle (MoR) | Lemon Squeezy (MoR, Stripe-owned) |
|---|---|---|---|---|
| Who is merchant of record | Us | Stripe ("Sold through Link") | Paddle | Lemon Squeezy / Stripe |
| Headline fee | 2.9% + $0.30 per US domestic card; +1.5% international cards; +1% currency conversion. [S27] | 3.5% per successful transaction on top of standard Stripe processing fees (about 6.4% + $0.30 US domestic card). No setup fee or monthly minimum; Billing is priced separately. [S29][S27] | 5% + $0.50 per checkout transaction, all-inclusive (tax, fraud, chargebacks, buyer support). [S35] | 5% + $0.50 per transaction; the page says some payments, such as those outside the US, may carry additional fees (specific surcharge amounts appear only in third-party sources: VERIFY). [S40] |
| Fee on $5 / $50 payment (US card) | $0.445 (8.9%) / $1.75 (3.5%) | $0.62 (12.4%) / $3.50 (7.0%) | $0.75 (15.0%) / $3.00 (6.0%) | $0.75 (15.0%) / $3.00 (6.0%) |
| Subscription billing | Stripe Billing: 0.7% of Billing volume pay-as-you-go, or from $620/month on a 1-year contract. [S28] | Supported through Billing, but only via Checkout/Payment Links. [S30][S31] | Yes | Yes |
| Tax | Stripe Tax: 0.5% per transaction (no-code) or $0.50 per transaction (API) where registered; calculation, with us still registering and filing (Tax Complete from $90/month adds more). [S27] | Included for 80+ countries: calculates, collects, files and remits. Eligible tax codes include an AI-as-a-Service category (cloud, and cloud plus downloaded; business and personal use). [S30][S31] | Included | Included |
| Prepaid/usage support | Billing credit grants: prepaid or promotional credits, but applied to subscription items with metered prices only, at invoice finalization; cannot apply to one-off invoices or licensed prices. Customers can hold up to 100 unused grants. [S32] Meters API is included in Billing pricing up to 100M events/month. [S27] Metronome token billing (public preview) supports AI credit packs and top-ups. [S33][S34] | The docs read do not address usage-based billing; invoice items on a Managed Payments subscription, one-off invoices outside the billing period, and subscriptions created outside Checkout/Payment Links are unsupported. [S30] | Native usage-based billing is in early access or on a waitlist, no GA date. Credit packs are sold as one-time products and the balance is tracked in our own app. [S36][S37] | Usage-based billing is listed as a feature. [S40] VERIFY details. |
| Auto top-up path | Not a documented built-in. Standard pattern: save the card (SetupIntent), then create an off-session PaymentIntent when our ledger drops below the threshold, with an SCA/3DS failure fallback. Billing alerts cover meter usage thresholds; I found no credit-balance alert type. [S43] | Unsupported as far as documented: advanced integrations and embeddable components are excluded, and no off-session flow is documented. VERIFY with Stripe. | One-time charges can be collected automatically on the subscription's saved payment method (`effective_from: immediately`), so a threshold job can charge the card without the customer present. Requires an existing, non-`past_due` subscription (a $0 subscription is a common workaround, VERIFY). [S38] | VERIFY |
| Policy risk for a prepaid wallet | Billing credits must be spent on our own products; no stored value, gift cards, third-party payments or wallet linking. [S32] A closed-loop wallet for our own usage fits. | Product must be a fully automated digital product sold directly to customers; Connect not supported. [S30] | Prohibited list includes virtual currency or stored value (store credit, gift cards, vouchers); also resale of any product without a valid reseller certificate; usage-based AI access is not addressed. Confirm in writing. [S39] | Prohibited list excludes services of any kind and any product restricted by its payment partners; prepaid credits not addressed. [S42] |
| Status / maturity | Mature | Third-party reports say public preview since early 2026 (VERIFY); access is gated by an eligibility review. [S30] | Mature, but wallet logic is ours | Lemon Squeezy says Stripe Managed Payments is the future of its MoR offering (2026-01-28). [S41] Do not start a new build on it. |
| Fit for "subscription + prepaid wallet + auto top-up" | **Best** | Poor for auto top-up; good for the subscription only | Workable technically; policy and fee risk on the wallet | Weak |

### 7.3 Recommendation

1. **Stripe direct.** Use Stripe Billing for the Individual/Team/Enterprise subscriptions. Run the wallet as our own ledger (append-only, double-entry style; debit on each `usage.cost`; credit on payment success). Charge top-ups with PaymentIntents: manual top-up via Checkout/Payment Element; auto top-up via the saved card off-session, with idempotency keys derived from a "pending top-up" row, a monthly cap, and a pause-and-notify after any failure or authentication request. Enterprise: invoice or ACH (ACH is 0.8% capped at $5.00 per Stripe's list). [S27]
2. **Tax.** We are seller of record, so use Stripe Tax for calculation and budget for registration/filing (Tax Basic does not file). If that burden is unacceptable, revisit a merchant of record after OpenRouter confirms resale (R1) and after Stripe confirms Managed Payments supports saved-card auto top-up. ASSUMPTION: a $5-$50 B2B wallet is taxable as SaaS/AIaaS in most US states and the EU; confirm with a tax adviser.
3. **Do not rely on Stripe credit grants as the live wallet.** They apply at invoice finalization, not at request time. They are usable only for promotions or for netting the subscription invoice.
4. **Metronome is an optional later step** if invoicing-style metering is wanted: public preview; Startup plan $0.04 per 1,000 ingest events plus 0.8% of billing volume. [S27][S33][S34] Real-time gating still needs our own balance check. VERIFY before committing.
5. **Legal flag:** a prepaid wallet is stored value. A closed-loop balance spendable only on our own service is usually treated differently from money transmission, but confirm (section 9, R10). Align the wallet expiry with OpenRouter's 365-day credit expiry, and document that unspent balances are refundable or not (consumer-law dependent).
6. **Concentration note:** Stripe now owns Lemon Squeezy, is acquiring OpenRouter, and processes our payments. A single parent for the PSP, the MoR and the model gateway is a dependency to disclose to our risk review. [S19][S41]

### 7.4 Wallet flow sketch

| Step | Event | System of record |
|---|---|---|
| 1 | Customer buys subscription | Stripe Billing |
| 2 | Customer tops up $T (min $10), or auto top-up fires at threshold | Stripe PaymentIntent; on `payment_intent.succeeded` write ledger credit |
| 3 | Gateway pre-checks balance >= estimate; sends request with `user` tag and policy params | Gateway ledger |
| 4 | Response `usage.cost` arrives (stream: last chunk) | Debit ledger: `usage.cost` x (1 + m), keyed by generation `id` |
| 5 | Stream dropped without usage chunk | Backfill via `GET /generation?id=` |
| 6 | Balance below threshold | Auto top-up job (idempotent) |
| 7 | Nightly | Reconcile our ledger vs OpenRouter key `usage_daily` and `/credits`; top up our OpenRouter balance (batches of at least $14.55) |

---

## 8. Q7: Margin math and transaction-fee recommendation

### 8.1 Model

Definitions: customer tops up T; the wallet is debited `usage.cost x (1 + m)` per request (m = our transaction fee as a percentage of OpenRouter cost). Assume T is fully consumed.

- List-price usage covered by T: `U = T / (1 + m)`
- Our OpenRouter cost: `U x (1 + f)` with f = 5.5% (Standard) [S2]; ASSUMPTION: the fee is paid on credit purchases we make in large batches, so the $0.80 minimum fee does not bite.
- Payment processing: `p x T + fixed` (Stripe direct 2.9% + $0.30 [S27]).
- Net = `T - U(1 + f) - (pT + fixed)`.
- Break-even fee: `m* = T(1+f) / (T - pT - fixed) - 1`.

Not included: subscription revenue, Stripe Billing 0.7% [S28], Stripe Tax 0.5% [S27] (shown as a variant), refunds, disputes ($15 each per [S27]), international card surcharge (+1.5%) and currency conversion (+1%), our infrastructure cost.

### 8.2 Break-even and target fee by top-up size (f = 5.5%)

| Top-up | Processor | Break-even m | m for 5% net margin | m for 10% net margin |
|---|---|---|---|---|
| $5 | Stripe direct | 15.8% | 22.5% | 30.1% |
| $5 | Stripe Managed Payments | 20.4% | 27.7% | 36.0% |
| $5 | Paddle / Lemon Squeezy | 24.1% | 31.9% | 40.7% |
| $10 | Stripe direct | 12.1% | 18.4% | 25.4% |
| $10 | Stripe Managed Payments | 16.4% | 23.2% | 30.9% |
| $10 | Paddle / Lemon Squeezy | 17.2% | 24.1% | 31.9% |
| $20 | Stripe direct | 10.4% | 16.4% | 23.2% |
| $20 | Paddle / Lemon Squeezy | 14.1% | 20.6% | 27.9% |
| $50 | Stripe direct | 9.3% | 15.3% | 22.0% |
| $50 | Stripe Managed Payments | 13.4% | 19.9% | 27.1% |
| $50 | Paddle / Lemon Squeezy | 12.2% | 18.5% | 25.6% |

### 8.3 Net profit per top-up at candidate fees (Stripe direct, f = 5.5%)

| Top-up | m = 10% | m = 15% | m = 20% | m = 25% | m = 30% |
|---|---|---|---|---|---|
| $5 | -$0.24 (-4.8%) | -$0.03 (-0.6%) | +$0.16 (+3.2%) | +$0.34 (+6.7%) | +$0.50 (+9.9%) |
| $10 | -$0.18 (-1.8%) | +$0.24 (+2.4%) | +$0.62 (+6.2%) | +$0.97 (+9.7%) | +$1.29 (+12.9%) |
| $20 | -$0.06 (-0.3%) | +$0.77 (+3.9%) | +$1.54 (+7.7%) | +$2.24 (+11.2%) | +$2.89 (+14.4%) |
| $50 | +$0.30 (+0.6%) | +$2.38 (+4.8%) | +$4.29 (+8.6%) | +$6.05 (+12.1%) | +$7.67 (+15.3%) |

Same table through a merchant of record (net per top-up):

| Top-up | Processor | m = 20% | m = 25% | m = 30% |
|---|---|---|---|---|
| $5 | Stripe Managed Payments | -$0.02 | +$0.16 | +$0.32 |
| $5 | Paddle / Lemon Squeezy | -$0.15 | +$0.03 | +$0.19 |
| $50 | Stripe Managed Payments | +$2.54 (5.1%) | +$4.30 (8.6%) | +$5.92 (11.8%) |
| $50 | Paddle / Lemon Squeezy | +$3.04 (6.1%) | +$4.80 (9.6%) | +$6.42 (12.8%) |

### 8.4 Worked examples (recommended 20% fee, Stripe direct)

| Line | $5 top-up | $50 top-up |
|---|---|---|
| Customer pays | $5.00 | $50.00 |
| List-price usage purchased (T / 1.20) | $4.1667 | $41.6667 |
| OpenRouter credit fee on that usage (5.5%) | $0.2292 | $2.2917 |
| Total OpenRouter cost | $4.3958 | $43.9583 |
| Stripe processing (2.9% + $0.30) | $0.4450 | $1.7500 |
| Net to us | **$0.1592 (3.2%)** | **$4.2917 (8.6%)** |
| With Stripe Tax Basic (+0.5% of T) | $0.1342 | $4.0417 |
| If OpenRouter Business plan (8% fee) were needed for EU routing | $0.05 | $3.25 |

What the customer sees: "cost + 20%". Against buying credits directly from OpenRouter (5.5% fee, no markup) the managed convenience costs about 13.7 percentage points more per dollar of usage (1.20 vs 1.055).

### 8.5 Recommendation

| Item | Recommendation | Why |
|---|---|---|
| Transaction fee (Individual and Team) | **20% on OpenRouter-reported cost** (billed = `usage.cost` x 1.20; equivalent to 16.7% of the billed amount) | Covers the 5.5% OpenRouter fee, 2.9% + $0.30 processing and leaves about 6% to 9% net on typical top-ups before refunds/disputes; break-even is 9% to 16% depending on top-up size |
| If a merchant of record is chosen | 25% and $20 minimum top-up | Paddle/Lemon Squeezy 5% + $0.50 and Stripe Managed Payments 6.4% + $0.30 add 2 to 3.5 points |
| Minimum top-up | $10 (default auto top-up $25; threshold about 20% of the top-up amount) | $5 payments earn $0.16 at best and one $15 dispute wipes out roughly 90 of them. Offer $5 only as a one-time starter credit if wanted |
| Enterprise (prepay by ACH or invoice) | 10% to 12% | At $500 via ACH (0.8%, $4.00) and a 12% fee the net is about $25 (5.0%); break-even is about 6.3%. OpenRouter Enterprise fee discounts would improve this |
| Review trigger | Re-run the table if OpenRouter's fee changes (Stripe deal), if we move to the Business plan (8%), or if the mix shifts to international cards (+1.5% processing, +1% conversion) | |
| Buffer | Keep 1.5% to 2% of top-up volume as a reserve for refunds, disputes and international surcharges (ASSUMPTION) | |

---

## 9. Risks / things to confirm with OpenRouter sales or legal

| ID | Item | Why it matters | Who to ask |
|---|---|---|---|
| R1 | **Written confirmation that a product like the Coach may re-bill model usage to its customers at cost + fee** under ToS sections 5 and 7, or a reseller/partner addendum. Ask about the `external` partner fields on key creation. | If prohibited: breach, termination, forfeited credits, all `managed` customers lose service (sections 5.5, 9). | OpenRouter sales/legal (enterprise form) |
| R2 | Single-upstream dependency: OpenRouter can suspend or terminate at any time, for any reason, with or without notice (section 9). Keep the `managed` backend behind an interface so a second upstream (direct provider contracts, another gateway) can be swapped in. | Business continuity | Engineering, legal |
| R3 | Stripe acquisition: confirm closing status and request notice and price-lock commitments for ToS and fee changes. Ask for an Enterprise fee discount. | Fee and policy drift (fee is the biggest COGS line) | OpenRouter sales |
| R4 | Flow-down and shared fate: customer terms must bind to ToS and Model Terms; need customer country/entity screening and a fast per-customer kill switch (sections 5.2, 5.5, 5.7). Ask how Restricted Models are published per region. | One violation can suspend our whole account | Legal, engineering |
| R5 | Red Teaming clause: does Coach-generated adversarial/prompt-injection test content count? If so, get approval or exclude it. | Section 7/8 needs prior written approval | Legal, product |
| R6 | Data chain for enterprise customers: customer -> us -> OpenRouter -> provider. Need OpenRouter DPA (Business: signed copy available on request; Enterprise: negotiable), sub-processor list, EU residency scope (billing/account data may be US), retention periods per feature. Confirm anonymized input categorization (ToS 6.5) can be described to customers and whether it can be switched off for our account. | Required for DPA to Enterprise customers | OpenRouter, legal |
| R7 | In-flight spending budget (402s) and rate-limit allowances for a multi-tenant account; ask for invoice billing or a credit line (Enterprise). | Reliability at launch scale | OpenRouter sales |
| R8 | Key management limits: maximum keys per account/workspace, key creation rate limits, whether per-key limits can overshoot with concurrent requests, generation-lookup delay, low-balance notifications, plan needed for guardrails and workspaces (pricing table and docs disagree on budgets). | Design of one key per org versus per user | OpenRouter support/sales |
| R9 | Fee mechanics: is the 5.5% added to or deducted from the credit amount; behavior of minimum fee on auto-recharge; refund of the platform fee (non-refundable per ToS); 365-day expiry handling. | COGS accuracy | OpenRouter support |
| R10 | Stored-value and tax: legal review of the prepaid wallet (money-transmitter exposure, state gift-card/stored-value rules, refund rights, sales tax timing on prepaid usage, revenue recognition). | Compliance | Legal, tax adviser |
| R11 | Stripe Managed Payments and auto top-up: ask Stripe whether off-session saved-card charges and wallet top-ups are supported; confirm the 3.5% fee and country eligibility if considering it. | Billing architecture choice | Stripe |
| R12 | Paddle/Lemon Squeezy: written approval that a prepaid usage wallet and AI usage resale are acceptable (Paddle prohibits virtual currency or stored value including store credit; sub-$10 products need bespoke pricing). | Only if an MoR is pursued | Paddle |
| R13 | Model-provider terms (Anthropic, OpenAI, Google, etc.) apply to our customers via flow-down (ToS 5.1, 5.8). Review the ones in the Certified list. | Passes through usage restrictions | Legal |
| R14 | Source quality caveat: Lemon Squeezy surcharge amounts and the Stripe Managed Payments public-preview-since-February-2026 status came from search summaries or third-party pages, not from primary pages I fetched. The Stripe Managed Payments 3.5% fee was read on Stripe's own page. | Do not quote these externally without checking | Research |
| R15 | The OpenRouter FAQ page rendered its fee as a template placeholder, so the fee figures were taken from the pricing page and fee blog post instead (the blog post carries both a 2025 date and a 2026 update stamp). Re-read the fee on the live checkout page before publishing price sheets. | Accuracy | Research |

---

## 10. Sources (all accessed 2026-10-25)

| ID | URL | Used for |
|---|---|---|
| S1 | https://openrouter.ai/terms (Last Updated August 31, 2026) | ToS sections 3, 4, 5, 6, 7, 8, 9, 10 |
| S2 | https://openrouter.ai/pricing | Plans, fees, features, FAQ |
| S3 | https://openrouter.ai/docs/faq | Fees, refunds, free limits, privacy, payment methods |
| S4 | https://openrouter.ai/docs/guides/overview/auth/management-api-keys | Management keys, routes, key fields |
| S5 | https://openrouter.ai/docs/api/api-reference/api-keys/create-a-new-api-key | Key create parameters (`limit`, `limit_reset`, `expires_at`, `external`, `workspace_id`) |
| S6 | https://openrouter.ai/docs/api_reference/limits | Credit, budget and rate limits, in-flight budget, free tiers |
| S7 | https://openrouter.ai/docs/use-cases/usage-accounting | `usage.cost` in responses |
| S8 | https://openrouter.ai/docs/api/api-reference/generations/get-request-&-usage-metadata-for-a-generation | `/generation` lookup |
| S9 | https://openrouter.ai/docs/guides/features/guardrails | Guardrails |
| S10 | https://openrouter.ai/docs/guides/features/zdr | Zero Data Retention |
| S11 | https://openrouter.ai/docs/guides/privacy/data-collection | OpenRouter data collection |
| S12 | https://openrouter.ai/docs/guides/privacy/provider-logging | Provider logging, in-region routing |
| S13 | https://openrouter.ai/docs/guides/routing/provider-selection | Provider routing parameters |
| S14 | https://openrouter.ai/docs/guides/routing/model-fallbacks | Model fallbacks |
| S15 | https://openrouter.ai/docs/guides/routing/model-variants/free | `:free` variant |
| S16 | https://openrouter.ai/docs/guides/overview/models and live https://openrouter.ai/api/v1/models | Catalog schema and live counts |
| S17 | https://openrouter.ai/blog/announcements/simplifying-our-platform-fee/ | 5.5% / $0.80 / 5% crypto fee table |
| S18 | https://openrouter.ai/blog/announcements/openrouter-is-joining-stripe/ | Acquisition statement |
| S19 | https://stripe.com/newsroom/news/stripe-agrees-to-acquire-openrouter | Acquisition announcement (2026-08-19) |
| S20 | https://openrouter.ai/docs/guides/overview/auth/oauth | OAuth PKCE for user-controlled keys |
| S21 | https://openrouter.ai/docs/cookbook/get-started/enterprise-quickstart.md | Shared credit pools, `user` param, key provisioning |
| S22 | https://openrouter.ai/enterprise | Enterprise offering |
| S23 | https://openrouter.ai/docs/guides/features/workspaces/workspace-budgets | Workspace budgets (Enterprise), overshoot note |
| S24 | https://openrouter.ai/docs/api/api-reference/external-users/register-an-external-user | External users |
| S25 | https://openrouter.ai/docs/guides/features/zero-completion-insurance | Zero completion insurance |
| S26 | https://openrouter.ai/api/v1/endpoints/zdr | Live ZDR endpoint list |
| S27 | https://stripe.com/pricing | Stripe processing, Tax, Billing, Radar, disputes, ACH, Metronome |
| S28 | https://stripe.com/billing/pricing | Stripe Billing 0.7% and tiers |
| S29 | https://stripe.com/managed-payments | Managed Payments 3.5% |
| S30 | https://docs.stripe.com/payments/managed-payments/eligibility | MP eligibility, unsupported integrations, AIaaS tax codes |
| S31 | https://docs.stripe.com/payments/managed-payments/how-it-works | MP behavior, recurring payments, refunds |
| S32 | https://docs.stripe.com/billing/subscriptions/usage-based/billing-credits | Stripe billing credits |
| S33 | https://docs.stripe.com/billing/token-billing | Stripe LLM token billing (Metronome, public preview) |
| S34 | https://docs.metronome.com/guides/pricing-packaging/billing-model-guides/token-billing | Metronome token billing |
| S35 | https://www.paddle.com/pricing | Paddle fee |
| S36 | https://developer.paddle.com/get-started/how-paddle-works/ai-companies/ | Paddle for AI companies |
| S37 | https://www.paddle.com/ubb | Paddle native usage-based billing waitlist |
| S38 | https://developer.paddle.com/build/subscriptions/bill-add-one-time-charge/ | Paddle one-time charges |
| S39 | https://paddle.com/help/start/intro-to-paddle/what-am-i-not-allowed-to-sell-on-paddle | Paddle prohibited products |
| S40 | https://www.lemonsqueezy.com/pricing | Lemon Squeezy fee |
| S41 | https://www.lemonsqueezy.com/blog/2026-update | Lemon Squeezy and Stripe Managed Payments (2026-01-28) |
| S42 | https://docs.lemonsqueezy.com/help/getting-started/prohibited-products | Lemon Squeezy prohibited products (from search result summary only) |
| S43 | https://docs.stripe.com/api/billing/alert | Stripe billing alerts (from search result summary only) |
| S44 | https://openrouter.ai/docs/guides/best-practices/capping-shared-agent-keys | Key credit limits available on every plan |
| S45 | https://openrouter.ai/docs/llms.txt | Docs index (Auto Exacto and other feature listings) |
| S46 | https://openrouter.ai/docs/app-attribution | Optional attribution headers |
