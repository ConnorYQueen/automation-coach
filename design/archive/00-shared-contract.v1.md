# Automation Coach: shared design contract

Single source of truth for every agent working on this product. If your task conflicts with this file, follow this file and flag the conflict at the top of your output. Today is 2026-10-25.

## Product in one paragraph
A coach that walks employees through deciding whether and how to automate a process, then recommends the best tool for each step (LLM, script, API, UI automation, human, and so on). It ships as a standalone Windows download and integrates with **AutoMate**. The core problem it solves: people over-rely on LLMs for steps that need code, formulas, APIs or deterministic UI automation, so their agents and workflows fail.

## Thesis (non-negotiable)
**The model talks; the engine decides.** The recommendation path (classification, tool-ladder choice, ROI math, environment fit, policy gating, exports) is a deterministic, auditable rules engine with **no LLM in it**. The LLM only (a) interviews the user, (b) turns messy narrative into structured steps the user confirms, (c) explains recommendations in plain language, (d) drafts prose and test cases, (e) critiques. The model edits state only through narrow tool calls against the Blueprint and may only recommend tools by catalog ID from the engine.

## Decisions already made by the owner
1. **AutoMate** is a WinUI 3 / C# desktop app: local-only, deterministic, **no AI at runtime**. Selectors are AutomationId based. No screen coordinates, no confidence scoring for element resolution, fail loud when an element can't be resolved. The Coach is an optional **design-time** assistant; never describe AutoMate itself as AI-powered.
2. Coach core is a standalone library (engine, blueprint, catalog, connections, policy). AutoMate is the first "automation target" adapter; the standalone app is another shell on the same core.
3. **Coach can act inside AutoMate**: draft-only by default, user sees a diff and approves, a test run needs an explicit user click and is attended-only at first, and every action must map to a Blueprint step. Nothing sends, deletes or runs without a human click.
4. **Model connections** (one abstraction, model picker over them):
   - `managed`: customer pays us monthly for the platform plus usage at cost + transaction fee; app -> our gateway -> OpenRouter.
   - `byok_openrouter` and `byok_provider`: customer's own key, called **direct from the client**, key in Windows Credential Manager/DPAPI, never in logs, transcripts, blueprints or exports. No usage fee.
   - `custom_openai_compat`: Azure OpenAI, LiteLLM, vLLM, corporate gateways.
   - `local`: free, OpenAI-compatible localhost endpoint (Ollama, LM Studio, Foundry Local). No embedded inference at v1. Local support is a launch requirement.
   - Gateway logs **metadata only** (user, model, tokens, cost, time), never prompts.
5. **Model certification labels**: Certified / Works / Experimental / Uncertified, from a golden-set eval (about 30 scripted coaching scenarios) plus a capability probe on connect (tool-call round trip, JSON-schema output, context size).
6. **Tiers**: Individual, Team, Enterprise.
7. **Admin and user controls are required at launch.** Every setting has one of three states: `locked` (admin), `default` (user may change), `user_choice`. Policy is delivered as a signed bundle, cached with an offline grace period. Enforcement is server-side for `managed`; client-side for direct and local connections (document this honestly). Admins can disable personal keys. An **org environment profile** (which tools are permitted) constrains the rules engine.
8. **Full backup/sync of Blueprints to our servers is required** (not metadata-only). So we store customer process data: needs encryption at rest, tenant isolation, retention and deletion controls, export, a DPA, and an Enterprise option for customer-managed keys. Transcripts stay local by default.
9. Roles: Admin, CoE Reviewer, Builder, Viewer.

## Coaching flow (stages)
`triage` -> `capture` -> `decompose` -> `classify` -> `environment_fit` -> `design` -> `build_handoff` -> `test_plan` -> `deploy_monitor`. Triage verdicts: `automate`, `fix_process_first`, `dont_automate`.

## Tool ladder (rung ids, cheapest and most deterministic first)
`eliminate`, `builtin_feature`, `api_connector`, `script`, `ui_automation`, `parser_ocr_ml`, `llm_node`, `human_checkpoint`; plus `llm_agent` (discouraged; needs justification). Choose the first rung that fits.

## Step diagnostic (inputs to the rules engine)
Input structure (structured / semi / free text); output uniquely determined by rules (yes / mostly / no); cost of error and reversibility; frequency and volume; API availability vs UI-only; attended vs unattended and credentials; data sensitivity; language understanding or judgment required.

## Canonical entities and field names (use exactly; JSON is camelCase)
- **Blueprint**: `id`, `version`, `title`, `owner`, `status` (`draft|in_review|approved|built|deployed|retired`), `sensitivity` (`public|internal|confidential|restricted`), `stage`, `triage{verdict,rationale}`, `process{summary,trigger,frequency,volume,timePerRunMinutes,people[]}`, `steps[]`, `exceptions[]`, `environmentProfileRef`, `roi{}`, `decisions[]` (overrides and LLM justification cards), `tests[]`, `exports[]`, `auditLog[]`, `createdAt`, `updatedAt`.
- **Step**: `id`, `order`, `name`, `description`, `actor`, `inputs[]`, `outputs[]`, `decisionPoints[]`, `exceptionRefs[]`, `diagnostic{...}`, `recommendation{rungId,toolId,rationale[],alternatives[]}`, `override{by,reason,at}`, `llmJustification{whyNotCode,validator,fallback,costPerRun}`.
- **Exception**: `id`, `description`, `frequency`, `handling`.
- **Connection**: `id`, `type`, `endpoint`, `credentialRef`, `allowedModels[]`, `policyRef`.
- **Policy**: `orgId`, `version`, `issuedAt`, `expiresAt`, `signature`, `settings{<key>:{value,state}}`.
- **ToolCatalogEntry**: `toolId`, `name`, `rungId`, `capabilities[]`, `constraints[]`, `skillLevel`, `requiresInstall`, `platforms[]`.

## Rules for every agent
- Write **only** the files assigned to you; never edit another agent's file. Do not create git repos. Your working directory is the project root; resolve relative paths against it (run `pwd` first) because Write needs absolute paths.
- Be concrete and concise. Prefer tables, schemas, and examples over prose.
- Mark guesses `ASSUMPTION:` and anything you could not confirm from a source `VERIFY:`. Never state a price, fee, limit or policy as fact unless you read it from a source in this session; cite the URL and access date.
- Do not invent product names or brand names. Use "Coach" as the working name.
