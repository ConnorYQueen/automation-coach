# Local and enterprise model endpoints: research and v1 recommendation

Prepared 2026-10-25 for the Coach design contract (`design/00-shared-contract.md`). Scope: local inference servers on Windows, open-weight model reliability, constrained decoding, enterprise endpoints, and a v1 recommendation.

Conventions: every factual claim carries a source tag `[S#]`; the Sources table (section 9) gives the URL and the access date (all 2026-10-25). `ASSUMPTION:` marks my guesses and computed estimates. `VERIFY:` marks anything I could not confirm from a source this session (including facts that came only from a third-party page or a summarised fetch). Vendor-reported benchmark numbers are self-reported and not comparable across harnesses.

---

## 0. Conflicts and gaps against the contract (read first)

| # | Contract text | Finding | Proposed resolution (contract not edited) |
|---|---|---|---|
| C1 | Decision 5: capability probe includes "context size" | Plain OpenAI-compatible APIs do not report the loaded context window. Ollama defaults to 4k tokens when VRAM is under 24 GiB, and truncates silently with HTTP 200 [S7][S9 (third-party, VERIFY)]. The OpenAI endpoint cannot set it [S9, VERIFY]. | Probe context by behaviour (needle test compared with `usage.prompt_tokens`) plus server-specific side channels (llama.cpp `/props`, LM Studio `/api/v0/models`, Ollama `/api/ps`, vLLM `max_model_len`). Ollama onboarding must set `OLLAMA_CONTEXT_LENGTH` [S7]. |
| C2 | Connection entity: `id, type, endpoint, credentialRef, allowedModels[], policyRef` | Not enough for enterprise or local. Azure `model` is a deployment name [S38]; auth schemes differ (Bearer, `api-key` header, Entra token, Bedrock short-term key, Vertex OAuth) [S38][S42][S44]; Foundry Local port is dynamic [S16]; each server needs a quirk profile. | Add `serverKind`, `authScheme`, `extraHeaders`, `modelIdKind` (`model` or `deployment`), `contextWindowOverride`, `capabilityProfile`, and a token-provider reference (section 7.6). |
| C3 | Decision 4: `custom_openai_compat` covers "Azure OpenAI" | Not plug-and-play. Key auth can be disabled by tenant (Entra needed); strict structured outputs have schema limits and no parallel calls; Microsoft recommends the Responses API [S38][S39]. | Treat Azure as a named `serverKind` with a quirk profile, not generic. Key auth works at v1; Entra via token provider is v1.1 (section 7.8). |
| C4 | Decision 5: "Certified" labels per model | Server behaviour changes results for the same weights. Ollama issue #14493: Qwen 3.5 tool calls come back as raw XML or plain text because of the wrong renderer/parser; opened 2026-02-27, still active 2026-09-21 [S8]. | Key certification per (model, server kind, server version, quantization). Re-run the golden set when the server version changes. |
| C5 | Decision 4: `byok_provider` (implicitly Anthropic and others through one adapter) | Anthropic calls its OpenAI-compatible layer "primarily intended to test and compare model capabilities" and not production-ready; it ignores `strict` on tools, `response_format` and prompt caching [S46]. | Claude through the compat layer should be capped at Works/Experimental. Native Messages adapter is the first post-launch adapter (section 7.8). |
| C6 | Decision 4: `local` = Ollama, LM Studio, Foundry Local | llama.cpp server is a fourth, MIT-licensed option and is the engine under LM Studio's GGUF path for schema output [S13][S21]. Foundry Local is GA for the SDK but its CLI and REST reference are still labelled preview, and its server port is dynamic [S15][S16][S17]. | Add `llamacpp` as a supported `serverKind`. Add port discovery for Foundry Local. |
| C7 | "Local support is a launch requirement" | A 16 GB RAM, no-GPU corporate laptop can only run 4B-class models comfortably, or a 9B model with a short context and slow first token (section 4). Full coach quality is not achievable on that hardware class. | Launch requirement is met by a "lite coach" mode (section 7.5) plus an honest hardware check, not by promising full coach on every laptop. |
| C8 | (implicit) Copilot+ PCs are good local-LLM hosts | The Copilot+ baseline is 40+ TOPS NPU, 16 GB RAM, 256 GB storage [S20]. That RAM floor is the same 16 GB problem. The NPU path for LLMs is effectively Foundry Local only (section 2). | Do not infer capability from the Copilot+ badge. Probe measured speed. |

---

## 1. Summary of the five most decision-relevant findings

1. **Ollama is the best default local recommendation but needs a context-length onboarding step.** MIT licence, per-user install with no admin rights, OpenAI-compatible `/v1/chat/completions` with tools and `response_format` [S1][S3][S5]. Defaults: 4k context under 24 GiB VRAM, `tool_choice` unsupported, silent truncation [S3][S7].
2. **A 16 GB, no-GPU laptop is a lite-coach machine.** Roughly 4B-class models, or a 9B model with 4 to 8k context and slow first token (ASSUMPTION, section 4). The probe must gate on measured speed, not on spec.
3. **Do not send `tools` and `response_format` json_schema together to open-weight servers.** In a vLLM/SGLang study, every tested open-weight model stopped calling tools when both were enabled [S33]. Use a "JSON-action" single-schema protocol or two-pass calls.
4. **Anthropic compat layer loses the features Coach needs** (strict tool schemas, `response_format`, prompt caching, thinking output) [S46]. A native Messages adapter is the high-value v1.1 item and also reaches Claude on Bedrock (Messages API is offered on both Bedrock endpoints [S40]).
5. **Certify per (model, server, version).** Server template/parser bugs break tool calling for the same weights [S8], and public benchmarks neither cover current models consistently nor test our narrow Blueprint edits (section 3.3). One popular tool-calling model family, xLAM, is CC-BY-NC and must not be recommended commercially [S24].

---

## 2. Local inference servers on Windows

### 2.1 Comparison

| | Ollama | LM Studio | Foundry Local | llama.cpp server |
|---|---|---|---|---|
| Latest seen | v0.40.11, 2026-10-24 [S2] | not recorded | SDK GA 2026-04-09; CLI/REST labelled preview [S15][S16][S17] | not recorded |
| Default endpoint | `http://localhost:11434/v1/` [S3]; binds 127.0.0.1 [S6] | `http://localhost:1234/v1` [S13] | **Dynamic port**; fix with `foundry server start --port N --idle-timeout 0` or read `foundry server status` [S16] | `127.0.0.1:9931` per README (historically 8080) [S21]; VERIFY |
| Chat Completions | Yes [S3] | Yes [S13] | Yes, with `tools`/`functions` [S17] | Yes [S21] |
| Responses API | Yes, stateless only [S3] | Yes [S13] | Responses format listed [S17] | Yes [S21] |
| Tools | Yes; **`tool_choice` unsupported** [S3] | Native for models with tool templates; every other model uses a prompt-based fallback; malformed calls from small models land in `message.content`; `tool_choice` not documented [S13] | `supportsToolCalling` flag per catalog entry [S17]; Qwen reportedly returns tool calls as JSON text in `content` (Tech Community article, URL not recorded, VERIFY) | Needs `--jinja` (default on); native formats for Llama 3.x, Hermes 2/3, Qwen 2.5/Coder, Mistral Nemo, Command R7B, GPT-OSS (Harmony), Functionary, Firefunction; "Generic" fallback is less efficient; parallel calls off by default [S21][S22] |
| JSON schema output | `response_format` on OpenAI endpoint; native `format` field [S3][S4]; cloud does not support it [S4] | `response_format` json_schema; GGUF uses llama.cpp grammar sampling, MLX uses Outlines; warns models under 7B are often incapable [S13] | `response_format` and `tool_choice` **not documented**; VERIFY | `response_format` plain JSON and schema; native `/completion` accepts `json_schema` and `grammar` [S21] |
| Not supported / notes | `logit_bias`, `user`, `n`, logprobs; images base64 only [S3] | Streaming tool calls arrive in fragments [S13] | Optimised for single-user on-device use, curated catalog [S18] | `--api-key`, multi-model router mode, `--reasoning` flags [S21] |
| Context introspection | `ollama ps` (CONTEXT, PROCESSOR) [S7] | `/api/v0/models` returns `max_context_length` [S14] | VERIFY | `/props` exposes `n_ctx` [S21] |

### 2.2 IT deployment friction and licence

| | Ollama | LM Studio | Foundry Local | llama.cpp |
|---|---|---|---|---|
| Install scope / admin | `OllamaSetup.exe`, **no admin rights**, per-user in `%LOCALAPPDATA%\Programs\Ollama`; models and config in `%HOMEPATH%\.ollama`; Windows 10 22H2+ [S5] | Desktop installer; machine-wide install flag reported by third party (below) | `winget install Microsoft.FoundryLocal` (MSIX). Docs say "Make sure you have admin rights"; machine scope fails under winget and needs `Add-AppxProvisionedPackage` [S16]; VERIFY exact source page | Zip of binaries from GitHub releases; asset names not confirmed; VERIFY |
| Silent install | Not documented by Ollama. Third party lists Inno Setup flags `/SP- /VERYSILENT /SUPPRESSMSGBOXES /NORESTART`; winget ID `Ollama.Ollama` [S48]; VERIFY. `/DIR` flag and `OLLAMA_MODELS` documented [S5] | Third party lists `/S` and `/allusers`; winget `ElementLabs.LMStudio` [S48]; VERIFY | winget / MSIX provisioning [S16] | n/a (unzip) |
| Code signing | VERIFY | VERIFY | MSIX package; ASSUMPTION: Microsoft-signed | VERIFY |
| Service / autostart | Login item on Windows; standalone `ollama-windows-amd64.zip` CLI can run as a service via NSSM [S5] | "Run LLM server on login" option; headless `llmster` daemon via `irm https://lmstudio.ai/install.ps1 \| iex`, `lms daemon up`, `lms server start`; JIT model loading with idle TTL [S14] | Server starts on demand; idle timeout flag [S16] | Run as you choose |
| Proxy / data | `HTTPS_PROXY` honoured; `OLLAMA_NO_CLOUD=1` disables cloud features; "We don't see your prompts or data when you run locally" [S6] | Enterprise plan adds SSO and model/MCP gating [S11] | Local, on-device [S18] | Local |
| GPU / NPU | NVIDIA driver 551.61+, or AMD ROCm v7 / Vulkan [S5] | not recorded | ONNX Runtime + Windows ML; execution providers CUDA, WebGPU, Intel OpenVINO, Qualcomm QNN NPU, AMD Vitis NPU, CPU fallback [S15][S16] | not recorded |
| Licence | **MIT**, copyright "Ollama" [S1] | Proprietary freeware. Free for work since 2025-07-08 [S11]. Terms: personal or internal business use; prohibit sublicensing, distributing or bundling, and SaaS use; integration only via "Company published interfaces"; liability cap $50 [S12] | SDK **MIT**; CLI under Microsoft Software License Terms; each model has its own licence; plugin EPs carry third-party licences (NVIDIA EULA, Intel OBL) [S15][S18] | **MIT**, "The ggml authors" [S23] |
| Can Coach recommend it? | Yes. Redistribution allowed by licence. | Recommend only; **do not bundle** [S12]. ASSUMPTION: linking to the vendor's installer is not bundling; legal review VERIFY. | Yes; check each model's licence | Yes; bundleable later |

### 2.3 Notable platform items

- **Windows ML** is an ONNX Runtime-based inference framework, not an API server. CPU and GPU (DirectML) work on all supported Windows versions; NPU and vendor-specific execution providers need Windows 11 24H2 (build 26100) or later [S19]. It does not give Coach an OpenAI-compatible endpoint by itself.
- **Foundry Local SDK**: C# package `Microsoft.AI.Foundry.Local.WinML` plus JS, Python and Rust; the runtime adds about 20 MB and can be embedded in-process [S15]. This is the most plausible v2 route to embedded inference (ASSUMPTION), and it is the only documented NPU path for LLMs here.
- **Phi Silica / Windows AI APIs**: not OpenAI-compatible; defer (ASSUMPTION based on [S19] scope; VERIFY).
- **Ollama also exposes an Anthropic Messages API** according to release notes; VERIFY [S2].
- **Ollama `/api/show` fields**: the docs page returned 404; VERIFY before relying on it for model metadata.

### 2.4 Known server bug that shapes the design

Ollama issue #14493 (opened 2026-02-27, still active 2026-09-21): with Qwen 3.5 (27B and others), tool calls appear as raw XML inside thinking blocks or as plain text, because the Hermes-style renderer/parser is used instead of the Qwen3-Coder XML format. A maintainer disputed "completely non-functional". A workaround Modelfile with `RENDERER qwen3-coder` / `PARSER qwen3-coder` gave 2/5 to 4/5 success in one test, with thinking-leak side effects [S8]. Lesson: the same weights pass or fail depending on server version, so the probe plus golden set must run per (model, server, version).

---

## 3. Models: tool-calling and JSON reliability

### 3.1 Leaderboard data (BFCL V4, Berkeley)

Source: `data_overall.csv`, 109 rows; leaderboard page says last updated 2026-04-12 [S24]. Numbers came through a summarising fetch and were consistent across two fetches; VERIFY against the CSV before quoting externally. The snapshot contains **no Qwen3.5, gpt-oss or Gemma 4**. Top rows were Claude-Opus-4-5 at 77.47% and Claude-Sonnet-4-5 at 73.24% [S24].

Columns we care about are Non-Live AST, Live, Multi-turn and Irrelevance (does the model correctly decline to call). Overall also blends web search and memory, which Coach does not need.

| Model (FC = native function calling) | Overall | Non-Live AST | Live | Multi-turn | Irrelevance | Licence |
|---|---|---|---|---|---|---|
| Qwen3-32B FC | 48.71 | 88.77 | 82.01 | 47.87 | 76.37 | Apache-2.0 |
| Qwen3-14B FC | 41.03 | 84.94 | 80.01 | 34.75 | 81.94 | Apache-2.0 |
| Qwen3-8B FC | 42.57 | 87.58 | 80.53 | 41.75 | 79.07 | Apache-2.0 |
| Qwen3-30B-A3B-2507 FC | 41.39 | 85.77 | 77.94 | 30.00 | 79.90 | Apache-2.0 |
| Qwen3-4B-2507 FC | 35.68 | 87.88 | 76.39 | 22.12 | 84.93 | Apache-2.0 |
| xLAM-2-32b FC | 54.66 | 89.60 | 75.50 | 69.50 | 80.23 | **CC-BY-NC-4.0: cannot use** |
| xLAM-2-8b FC | 46.68 | 84.58 | 67.95 | 70.00 | 63.28 | **CC-BY-NC-4.0: cannot use** |
| Mistral-small-2506 FC | 37.15 | 73.60 | 77.28 | 11.50 | 87.94 | Proprietary (as listed) |
| Gemma-3-12b (prompted) | 30.43 | 79.44 | 74.24 | 5.75 | 70.29 | Gemma terms |
| Gemma-3-27b (prompted) | 29.47 | 87.17 | 74.54 | 10.75 | 73.67 | Gemma terms |
| Phi-4 (prompted) | 28.79 | 69.56 | 60.70 | 3.88 | 87.55 | MIT |
| Llama-3.1-8B (prompted) | 25.83 | 84.00 | 70.76 | 11.12 | 42.70 | Llama community |
| Granite-3.2-8B FC | 26.87 | 79.77 | 60.33 | 7.38 | 80.53 | Apache-2.0 |

Reading: single-call accuracy (Non-Live AST, Live) is roughly 75 to 90% for the 4B to 32B Qwen3 class, but **multi-turn is far lower (22 to 48%)**. Coach is a multi-turn product, so Non-Live scores overstate readiness. Prompted (non-native) tool calling scores much lower on multi-turn [S24].

### 3.2 Newer models (vendor-reported, not comparable to 3.1)

| Model | Reported | Notes | Source |
|---|---|---|---|
| Qwen3.5-27B | BFCL-V4 68.5, TAU2 79.0, IFEval 95.0 | Apache-2.0, 262K context, ~Feb 2026; thinking on by default, disable with `chat_template_kwargs.enable_thinking=false`; `/think` `/nothink` unsupported; vLLM parser `qwen3_coder` | [S25] |
| Qwen3.5-9B | BFCL-V4 66.1, TAU2 79.1, IFEval 91.5 | same | [S25] |
| Qwen3.5-4B | BFCL-V4 50.3, TAU2 79.9 | same | [S25] |
| Qwen3.5-35B-A3B | BFCL-V4 67.3, TAU2 81.2 | MoE | [S25] |
| Qwen3.6-35B-A3B | TAU3-Bench 67.2; no BFCL on card | Apr 2026, Apache-2.0, `preserve_thinking` option | [S25] |
| Gemma 4 (E2B, E4B, 12B Unified, 26B-A4B MoE, 31B) | Tau2 avg of 3 runs: 31B 76.9%, 26B-A4B 68.2%, 12B 69.0%, E4B 42.2%, E2B 24.5% (Gemma 3 27B 16.2%) | Apache 2.0, native function calling; card says its docs are deprecated and points to gemma.ai | [S26] |
| gpt-oss-20b | tau-bench Retail 35.0 / 47.3 / 54.8 at low / medium / high reasoning (120b: 49.4 / 62.0 / 67.8) | 21B total, 3.6B active, Apache 2.0, MXFP4, checkpoint 12.8 GiB, Harmony format required; "runs within 16GB" | [S27] |
| Ministral 3 (3B / 8B / 14B) | no BFCL figure found | Dec 2025, Apache 2.0, native function calling claimed | VERIFY |

These vendor figures use different harnesses and settings. The Qwen3.5 BFCL-V4 values (66 to 69) are not on the same scale as the Berkeley CSV values in 3.1 (VERIFY harness).

### 3.3 Benchmark limits (why we still need the golden set)

- BFCL V4 overall blends web-search and memory tasks Coach does not use; use Non-Live, Live, Multi-turn and Irrelevance columns [S24].
- Vendor numbers use different harnesses [S25][S26].
- Benchmarks run through reference parsers; they do not catch server template/parser bugs (see Ollama #14493) [S8], constrained decoding side effects [S33], long system prompts, or our narrow Blueprint edit tools.
- tau-bench (arXiv 2406.12045) simulates the user with an LLM and compares the final database state; its `pass^k` metric measures reliability across repeated trials. GPT-4o scored under 50% task success and pass^8 under 25% in retail [S28]. Reliability across repeats is the right lens for a coaching product.
- Therefore: public scores pick candidates for the golden set; they never set a certification label.

### 3.4 Candidate list for golden-set trials (ASSUMPTION: selection, not a ranking)

| Class | Candidates | Licence | Why |
|---|---|---|---|
| Lite (4B-class) | Qwen3.5-4B, Gemma 4 E4B, Qwen3-4B-2507 | Apache-2.0 | Fits 16 GB laptops; multi-turn weak (Gemma E4B Tau2 42.2% [S26]) so lite-coach only |
| Core (8 to 14B dense) | Qwen3.5-9B, Gemma 4 12B, Qwen3-14B, Ministral 3 8B/14B | Apache-2.0 | Entry for full coach on 32 GB or small GPU |
| Strong local (26 to 35B) | Qwen3.5-27B, Qwen3.5-35B-A3B, Gemma 4 26B-A4B and 31B, Qwen3-32B | Apache-2.0 | Best published tool-use numbers for open weights in this study [S25][S26] |
| Reasoning MoE | gpt-oss-20b | Apache 2.0 | Needs Harmony parser support; 12.8 GiB checkpoint is heavy for 16 GB laptops [S27] |
| Excluded | xLAM-2 family | CC-BY-NC-4.0 | Non-commercial [S24] |

---

## 4. Hardware, memory and speed

### 4.1 Memory by quantization

Weights, from the llama.cpp quantize README for Llama-3.1-8B [S29]: Q4_K_M 4.58 GiB (4.89 bpw), Q5_K_M 5.33, Q6_K 6.14, Q8_0 7.95, F16 14.96. That is about 0.57 GiB per billion parameters at Q4_K_M (computed from [S29]; scale only roughly to other architectures).

Ollama library sizes (default quantizations) for Qwen3.5: 4b 3.3 to 4.0 GB, 9b 6.6 to 7.6 GB, 27b 17 to 20 GB, 35b 22 GB, 122b 81 GB; tools capability listed for the family [S10].

KV cache (ASSUMPTION: computed from the Llama-3.1-8B architecture, 32 layers, 8 KV heads, head dim 128, fp16): about 131 KB per token, so about 1 GiB at 8k tokens and 4 GiB at 32k. Other architectures differ (hybrid attention, MoE, KV quantization); the probe must measure. Extreme KV-cache quantization (q4_0) hurts tool calling [S22].

| Model size | Weights at Q4_K_M | Plus KV at 8k | Notes |
|---|---|---|---|
| 4B | 3.3 to 4.0 GB [S10] | +about 1 GiB (ASSUMPTION) | Fits 16 GB comfortably |
| 9B | 6.6 to 7.6 GB [S10] | +about 1 GiB (ASSUMPTION) | Tight on 16 GB with Office open |
| 14B | about 8 GiB (computed from 0.57/B, ASSUMPTION) | +about 1.5 GiB (ASSUMPTION) | 32 GB RAM or 12 GB+ VRAM |
| 27B | 17 to 20 GB [S10] | +2 to 4 GiB (ASSUMPTION) | 24 GB VRAM or 48 GB RAM |
| 35B-A3B MoE | about 22 GB [S10] | +about 2 GiB (ASSUMPTION) | Fits 32 GB RAM; only ~3B active per token so decode is faster than a dense 27B (ASSUMPTION: general MoE property) |

### 4.2 What a 16 GB RAM, no-dGPU corporate laptop can run

ASSUMPTION: Windows 11 plus Office, Teams, a browser and an EDR agent consume 6 to 9 GB of 16 GB, leaving 7 to 10 GB for inference. That supports a 4B-class Q4 model with 8k context. A 9B Q4 model (6.6 to 7.6 GB [S10]) plus KV cache leaves almost no headroom and invites paging. gpt-oss-20b's 12.8 GiB checkpoint [S27] does not fit alongside normal work.

Measured speed datapoints (community-reported in llama.cpp discussion #21112; no prefill numbers [S30]):

| Hardware | Model | Decode |
|---|---|---|
| Ryzen 5, 16 GB DDR4, CPU only | gemma-4-E4B Q4_K_M | about 7.8 tok/s |
| Core Ultra 7 255H iGPU | Qwen3-4B Q4 | 13.47 tok/s |
| Ryzen AI 7 PRO 350 + 860M iGPU, 64 GB | Qwen3.6-35B-A3B MXFP4 | about 26 tok/s |
| Older: i7-6700 | Qwen2.5-3B | prefill 43 t/s, decode 11.8 t/s |
| Older: Vega-7 iGPU | (same class) | prefill roughly doubled (34 to 76 t/s), decode about 10 t/s |

ASSUMPTION (not measured): a cold 3k-token prompt (system prompt + tool schemas + Blueprint summary) takes about 20 to 60 s to first token on a 4B-class model on a laptop CPU, and longer on 9B; a cold turn can approach a minute or more. Prefix-cache reuse between turns (same system prompt and tool block) should cut this sharply, but I did not confirm prefix reuse behaviour for each server; VERIFY. Coach should keep the system prompt plus tool schemas small (target under about 2k tokens, ASSUMPTION) and the prefix stable.

### 4.3 Hardware tiers (all thresholds are ASSUMPTION; the probe overrides them)

| Tier | Detected hardware | Recommended local use | Max label (ASSUMPTION) |
|---|---|---|---|
| 0 | Under 12 GB RAM and no usable GPU | Do not offer local; suggest managed or BYOK | n/a |
| 1 | 16 GB RAM, no dGPU | 4B-class models, or 9B Q4 at 4 to 8k context. **Lite coach only** | Works / Experimental |
| 2 | 32 GB RAM, or dGPU with 8 to 12 GB+ VRAM | 9 to 14B at Q4 to Q8 with 16k+ context; 35B-A3B MoE possible on 32 GB | Works / Certified |
| 3 | 16 to 24 GB+ VRAM, or 48 GB+ RAM | 27 to 32B Q4 at 32k | Works / Certified |

The NPU is a bonus path through Foundry Local only [S15][S19], not a tier criterion.

### 4.4 Windows detection methods (for the readiness check)

- RAM: `GlobalMemoryStatusEx` (ASSUMPTION: standard Win32 API; not read from a source this session).
- GPU VRAM: DXGI `DedicatedVideoMemory` (or `QueryVideoMemoryInfo` for budget) from a 64-bit process. Do not use WMI `Win32_VideoController.AdapterRAM` (uint32, overflows above 4 GiB). VERIFY against Microsoft docs.
- NPU: DXCore (`DXCoreCreateAdapterFactory`) with `DXCORE_HARDWARE_TYPE_ATTRIBUTE_NPU`; Chromium queries NPU and `D3D12_GENERIC_ML` / `CORE_COMPUTE` separately and de-duplicates by LUID. From C# this needs P/Invoke or COM interop. VERIFY.
- Also check: free disk for model files, AC power vs battery, CPU AVX2/AVX-512 (ASSUMPTION: relevant to llama.cpp CPU speed).

---

## 5. Constrained decoding

### 5.1 Server support

| Server | Mechanism | Tools together with schema | Source |
|---|---|---|---|
| llama.cpp | `response_format` JSON/schema; native `json_schema` and `grammar` on `/completion` | Lazy-grammar behaviour for tool calls not confirmed; VERIFY | [S21][S22] |
| LM Studio | llama.cpp grammar sampling (GGUF); Outlines (MLX) | VERIFY | [S13] |
| Ollama | `format` field accepts a JSON schema; also via `response_format` on the OpenAI endpoint | VERIFY (engine details unverified) | [S3][S4] |
| Foundry Local | Not documented | VERIFY | [S16][S17] |
| vLLM | Backends xgrammar, guidance, outlines (`lm-format-enforcer` deprecated); `response_format` json_schema; `structural_tag`; `structured_outputs` extra_body options choice/regex/json/grammar/structural_tag. `tool_choice` `required` (since 0.8.3) and named functions use structured outputs; `auto` relies on the parser, so arguments can be malformed unless `strict: true` or `--tool-strict-level` applies. Mistral's official format does not guarantee a call even with `required`. Qwen3 Coder with reasoning may have structured outputs disabled unless `--structured-outputs-config.enable_in_reasoning=True` | **Suppression observed (5.2)** | [S31][S32] |
| Azure OpenAI | Server-side strict structured outputs | Strict function calling not supported with parallel calls | [S39] |
| Vertex Gemini (OpenAI compat) | `response_format` json_schema (no fully recursive schemas) | n/a | [S44] |
| Anthropic compat | `response_format` ignored | n/a | [S46] |

### 5.2 Effect on small-model tool-call reliability

- **Tools + schema suppression.** In a study on SGLang and vLLM only, enabling tools and `response_format` json_schema together made every tested open-weight model stop calling tools (Qwen3.6-35B-A3B, Qwen3.5-122B-A10B, GPT-OSS-20B, Nemotron 3 Super and others): Tool Invocation Rate fell from 100% to 0%, because grammar masking excludes `<` so `<tool_call>` tokens become unreachable. Mitigation: two-pass execution (tools on, schema off; then tools off, schema on). GPT-5.4-mini was unaffected [S33]. Ollama and LM Studio were not covered; whether they behave the same is VERIFY.
- **Rescues form, not substance.** For small models (Qwen3-0.6B, Llama-3.2-1B/3B, Phi-4-mini, Qwen3-4B; transformers with Outlines/XGrammar), constrained decoding gave 100% schema validity but only partly closed the semantic gap; multi-step function calling stayed hard; a "hollow rescue" occurred where valid structure carries empty content [S34].
- Weaker evidence: vLLM JSON grammar latency of 3.6x to 8.2x and accuracy loss on GSM8K (older models, reasoning task) [S35]; format restrictions hurt reasoning but help classification (Tam et al., EMNLP Industry 2024) [S36]; JSONSchemaBench compares six frameworks, with blog-reported hard-schema coverage Guidance 41%, llama.cpp 39%, XGrammar 28%, Outlines 3% (secondary source, VERIFY) [S37]. A further paper titled "Constraint Tax" (arXiv 2605.26128) could not be read; title only [S50].

### 5.3 Design implications

1. Use constrained decoding for **narrow, flat, enum-heavy** schemas (ASSUMPTION: supported by [S34] and the schema coverage caveat in [S37]).
2. Never rely on it for semantics: the engine validates every output and every `toolId` against the catalog regardless (contract thesis).
3. Never send `tools` and `response_format` in the same request to open-weight servers; either use the JSON-action protocol (7.5) or two passes.
4. Expect a latency cost on constrained calls; measure in the probe.

---

## 6. Enterprise endpoints

### 6.1 Gap table against one OpenAI-compatible adapter

| Endpoint | Base URL shape | Auth | `model` field | Gaps and quirks |
|---|---|---|---|---|
| Azure OpenAI / Foundry v1 | `https://{resource}.openai.azure.com/openai/v1/` or `.services.ai.azure.com/openai/v1/`; the standard `OpenAI` client works and `api-version` is no longer required [S38] | `api-key` header in REST examples; OpenAI SDK sends Bearer (Azure accepting Bearer with a key: VERIFY). Entra ID bearer token, scope `https://ai.azure.com/.default` (another doc uses the `cognitiveservices` scope: VERIFY); role `Cognitive Services OpenAI User` [S38] | **Deployment name** [S38] | Microsoft recommends the Responses API; Chat Completions also works, including other providers' models [S38]. Strict structured outputs: all fields required, `additionalProperties:false` mandatory, max 100 properties and 5 nesting levels, `minLength`/`pattern`/`minimum`/`minItems` and similar unsupported, recursive schemas supported; strict function calling not supported with parallel calls, so set `parallel_tool_calls=false` [S39]. Corporate tenants may disable key auth; Entra needs MSAL/WAM (ASSUMPTION: client-side library requirement) |
| AWS Bedrock | `bedrock-runtime.{region}.amazonaws.com/openai/v1/chat/completions` (recommended); `bedrock-mantle.{region}.api.aws/v1/chat/completions` (alternative; some models under `/openai/v1`) [S40][S41] | SigV4 or Bedrock API keys; API keys work as OpenAI-SDK Bearer tokens. Short-term keys last up to 12 h (recommended for production); long-term keys for exploration only; IAM can deny `bedrock:CallWithBearerToken` [S42] | Bedrock model ID | **No `GET /models` on `bedrock-runtime`**, so manual model-ID entry [S41]. Per-model API support varies; read the model card [S41][S43]. Whether Claude works through Chat Completions: VERIFY. Anthropic Messages API is available on both endpoints; guardrails runtime-only; prompt caching on both [S40]. Gemma 4 appears only on bedrock-mantle [S43] |
| Google Vertex AI (now branded "Gemini Enterprise Agent Platform") | Base URL not captured; VERIFY | OAuth access token, about 1 h expiry (not captured; VERIFY) | VERIFY | Supports `tools`, `tool_choice` (`none`/`auto`/`required` plus Google-specific `validated`), `response_format` json_schema (no fully recursive), `stream`, `n`, `reasoning_effort`. **Unsupported parameters silently ignored.** Function `parameters` use the OpenAPI spec, not pure JSON Schema. `thought_signature` lives in `extra_content` and must be round-tripped, so the adapter must preserve unknown fields on assistant messages. Gemini-specific options go in `extra_body` [S44] |
| LiteLLM proxy | Proxy URL | Virtual key (Bearer) (ASSUMPTION: standard) | Alias | MIT core; Enterprise tier adds SSO, audit, guardrails; proxy needs Postgres for keys and spend; **raises on unsupported params unless `drop_params` is set**; `allowed_openai_params` passes a param through [S45] |
| vLLM | Server URL | Optional API key (ASSUMPTION) | Served model name | Server must be started with auto tool choice and a model-matched parser (hermes, `qwen3_coder`, `qwen3_xml`, mistral, `llama3_json`, `openai` for gpt-oss, granite4 and others) [S32]. Constrained-decoding caveats in section 5 |
| Corporate gateways | Varies | Varies (custom headers, possibly mTLS) | Varies | ASSUMPTION: custom headers, mTLS and private CA certificates are the common differences; honour the system proxy and Windows certificate store |
| OpenRouter (`byok_openrouter`) | n/a | n/a | n/a | Routing and per-provider parameter support not researched here; VERIFY |

### 6.2 Anthropic: native API vs OpenAI-compatible layer

Anthropic describes the compat layer as "primarily intended to test and compare model capabilities, and is not considered a long-term or production-ready solution for most use cases"; base URL `https://api.anthropic.com/v1/` [S46].

| Feature | Native Messages API | Via OpenAI compat [S46] | Impact on Coach |
|---|---|---|---|
| Strict tool schemas | `strict: true` tools with constrained decoding; GA; limits of 20 strict tools, 24 optional parameters, 16 union parameters, no recursion | `strict` ignored | Lose guaranteed-valid Blueprint edit calls |
| Structured output | `output_config.format` json_schema, constrained decoding, GA [S46] (also GA on Bedrock, Microsoft Foundry and Google Cloud) | `response_format` ignored | Lose JSON-mode fallback on Claude |
| Prompt caching | Cache write 1.25x base input (5 min) or 2x (1 h); read 0.1x base input (0.05x for Opus 5.5 and Sonnet 5.5); min cacheable length 512 to 4096 tokens by model; default TTL 5 min [S47] | Unsupported | Cost and latency on a long, stable system prompt (see below) |
| Thinking output | Returned | Not returned | Cannot show or audit reasoning |
| System/developer messages | Native `system` | Hoisted | Minor |
| Forced `tool_choice` | Model-dependent | Claude Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1 do not support forced `tool_choice` | Cannot force a tool on those models |
| Sampling | n/a | Claude 4.7+ rejects `temperature` below 1 and non-default `top_p`; `n` must be 1; `reasoning_effort` ignored | Adapter must not send these blindly |
| Other | Audio, PDF, citations | Lost; usage detail fields empty | Minor for Coach |

Illustrative caching arithmetic (computed from [S47] multipliers, ASSUMPTION about the prefix): a 4k-token stable prefix over 30 turns costs about 120k token-equivalents uncached versus about 16.6k cached, roughly 7x less. Actual savings depend on model, TTL and hit rate.

Conclusion: a native Messages adapter pays back in structured-output guarantees and caching, and it extends to Claude on Bedrock (Messages API on both endpoints [S40]) and, per the structured-outputs GA note, likely Google Cloud and Microsoft Foundry (VERIFY URL and auth shape for those two).

---

## 7. Recommendation

### 7.1 v1 support matrix

| Connection type | Server / endpoint | v1 stance | Minimum model class | Max label (ASSUMPTION) |
|---|---|---|---|---|
| `local` | **Ollama** | Default recommendation. Onboarding must set context length (7.4) | Lite: 4B-class tool-capable; Full: 9B+ dense or 26 to 35B MoE | Certified possible, per (model, version) |
| `local` | **LM Studio** | Supported; recommend only, never bundle [S12] | Same | Certified possible |
| `local` | **llama.cpp server** | Supported for IT-managed or advanced users | Same | Certified possible |
| `local` | **Foundry Local** | Supported as Experimental until `response_format` and `tool_choice` are verified and the dynamic port is handled | Same | Works until verified |
| `custom_openai_compat` | **Azure OpenAI / Foundry v1** | Supported with key auth and deployment-name handling; Entra auth v1.1 | Hosted GPT-class | Certified possible |
| `custom_openai_compat` | **LiteLLM, vLLM, corporate gateway** | Supported with quirk profiles; probe decides | Depends on backend | Per probe |
| `custom_openai_compat` | **Bedrock** (`bedrock-runtime` `/openai/v1`, API-key Bearer) | Supported with manual model-ID entry | Per-model | Per probe |
| `custom_openai_compat` | **Vertex** (OpenAI compat) | Defer to v1.1 (token provider needed; base URL unverified) | n/a | n/a |
| `byok_provider` | OpenAI | Standard path | n/a | Certified possible |
| `byok_provider` | Anthropic via compat layer | Allowed, capped at Works/Experimental; native adapter v1.1 | n/a | Works |
| `byok_openrouter` | OpenRouter | Standard path; per-provider parameter support VERIFY | n/a | Per model |

### 7.2 Capability probe design (on connect, per model)

| Check | Method | Records |
|---|---|---|
| Tool round trip | Call a trivial catalog-style tool, return a result, expect a final answer; repeat about 3 times | `toolsNative`, success rate |
| Tool recovery | Detect tool calls emitted inside `content` (JSON/XML text) | `toolsInContent` |
| Forced tool choice | Send `tool_choice` and see if honoured or ignored | `toolChoiceForced` |
| Schema conformance | `response_format` json_schema with an enum and a nested array; validate | `responseFormatSchema` |
| Tools + schema together | One request with both; see if tool call still appears | `toolsPlusSchemaOk` |
| Context size | Needle at about 6k and 12k tokens, compare with `usage.prompt_tokens`; plus server-specific endpoints (`/props` `n_ctx`, LM Studio `/api/v0/models` `max_context_length`, Ollama `/api/ps`, vLLM `max_model_len`) | `contextTokens`, `silentTruncation` |
| Thinking leak | Detect `<think>` or reasoning in `content`; check `reasoning_content` | `thinkLeak` |
| Streaming | Assemble fragmented streaming tool calls | `streamingToolCalls` |
| Speed | TTFT and tokens/s at about 3k prompt | `ttftMsAt3k`, `decodeTps` |
| Identity | Server version, model digest, quantization where exposed | for certification key |

### 7.3 Adapter requirements

- Chat Completions only in v1 (lowest common denominator; Anthropic compat is Chat Completions only [S46]). Defer Responses.
- Send **minimal parameters**; some servers silently ignore unsupported ones (Vertex [S44], Ollama [S3]) and others raise (LiteLLM [S45]).
- Support both `max_tokens` and `max_completion_tokens` (ASSUMPTION: needed for newer OpenAI-family models; VERIFY).
- Strip `<think>` blocks and handle `reasoning_content`; disable thinking for tool and JSON turns on thinking-mode models (`enable_thinking=false` for Qwen3.5 [S25]).
- Recover tool calls embedded in `content` (Foundry Local Qwen report, LM Studio fallback [S13]).
- Store raw assistant messages verbatim so Gemini `thought_signature` in `extra_content` round-trips [S44].
- Auth: Bearer, `api-key` header, custom headers, and a token-provider callback for tokens that expire (Entra, Bedrock short-term keys up to 12 h [S42], Vertex about 1 h: VERIFY).
- Model entry: allow manual model-ID entry (no `/models` on `bedrock-runtime` [S41]); label Azure's field "deployment".
- Local timeouts must tolerate model load (JIT loading and idle TTL exist on LM Studio [S14]; Ollama keep-alive default is 5 min [S6]).
- Honour the system proxy and the Windows certificate store (ASSUMPTION: standard corporate need).
- Per-server quirk profiles keyed by `serverKind` and refined by the probe.

### 7.4 Readiness check and user messaging

Run on first local setup and on demand. Thresholds are ASSUMPTION; show measured numbers.

| Result | Trigger (ASSUMPTION) | Message to user |
|---|---|---|
| Not recommended | Tier 0, or measured decode under 5 tok/s | "This computer is not a good fit for a local model. Use your organisation's endpoint or a managed connection." |
| Lite coach | Tier 1, or TTFT at 3k over 15 s but under 45 s, or decode 5 to 10 tok/s | "Your computer can run a small local model. Coach will ask simple questions and the app will do the structuring. Replies may take up to a minute." |
| Full coach | Tier 2 or 3 with TTFT at 3k at or under 15 s and decode at least 10 tok/s | "Your computer can run Coach with a local model. Pick a model from the list marked Works or Certified." |
| Ollama context warning | Ollama detected with context under the probe-required minimum | "Ollama is using a short memory setting (4k tokens). Raise it to 16k (set `OLLAMA_CONTEXT_LENGTH` and restart Ollama) or Coach will lose track of long conversations." (setting per [S7]) |
| Low RAM warning | Free RAM below model size plus about 3 GB (ASSUMPTION) | "Close other applications or choose a smaller model." |

### 7.5 Fallback ladder when a model lacks reliable tool calling

| Level | Mode | How it works | Used when |
|---|---|---|---|
| L0 | Native tools | Tool calls with engine-side validation and a repair loop; catalog IDs validated | Probe passes tool round trip reliably |
| L1 | **JSON-action** | One `response_format` json_schema object per turn: `{"action": <anyOf up to about 8 flat actions>}`; `toolId` is an enum of catalog IDs; no `tools` in the same request | Tools unreliable or `tool_choice` ignored (Ollama [S3], some Claude compat models [S46]) but schema output passes |
| L2 | JSON-in-prompt | Ask for JSON in the prompt; parse, validate, retry at most 2 times | Schema mode unsupported or unreliable |
| L3 | **Lite coach** | Engine drives the questions in a fixed script; the model only rephrases questions and extracts answers into tiny enum or flat schemas | Tier 1 hardware or low multi-turn reliability |
| L4 | No model | Scripted questionnaire; engine produces the recommendation | No usable connection |

Rules: never combine tools and `response_format` in one request on open-weight servers [S33]; if both are needed, run two passes. Keep the action set small and flat (5.3). The engine, not the model, makes every recommendation (contract thesis), so L3 and L4 lose conversation quality but not correctness.

JSON-action sketch (ASSUMPTION: shape):

```json
{
  "type": "object",
  "required": ["action"],
  "additionalProperties": false,
  "properties": {
    "action": {
      "anyOf": [
        {"type": "object", "required": ["kind","stepId","text"], "additionalProperties": false,
         "properties": {"kind": {"const": "ask_user"}, "stepId": {"type": "string"}, "text": {"type": "string"}}},
        {"type": "object", "required": ["kind","stepId","field","value"], "additionalProperties": false,
         "properties": {"kind": {"const": "set_step_field"}, "stepId": {"type": "string"},
                        "field": {"enum": ["name","description","actor"]}, "value": {"type": "string"}}},
        {"type": "object", "required": ["kind","stepId","toolId"], "additionalProperties": false,
         "properties": {"kind": {"const": "suggest_tool"}, "stepId": {"type": "string"},
                        "toolId": {"enum": ["<catalog ids injected at runtime>"]}}}
      ]
    }
  }
}
```

Azure strict mode requires every field required, `additionalProperties:false`, at most 100 properties and 5 nesting levels, and no `minLength`/`pattern`-style keywords [S39]; the sketch above stays within that.

### 7.6 Proposed Connection extension (for the contract owner)

```json
{
  "id": "conn_01",
  "type": "local",
  "endpoint": "http://127.0.0.1:11434/v1",
  "credentialRef": null,
  "allowedModels": ["qwen3.5:9b"],
  "policyRef": "pol_...",
  "serverKind": "ollama",
  "authScheme": "none",
  "extraHeaders": {},
  "modelIdKind": "model",
  "contextWindowOverride": 16384,
  "tokenProviderRef": null,
  "capabilityProfile": {
    "toolsNative": true, "toolsInContent": false, "toolChoiceForced": false,
    "responseFormatSchema": true, "toolsPlusSchemaOk": false,
    "streamingToolCalls": true, "thinkLeak": false,
    "contextTokens": 16384, "silentTruncation": false,
    "ttftMsAt3k": 18000, "decodeTps": 9.1,
    "serverVersion": "0.40.11", "modelDigest": "sha256:...", "probedAt": "2026-10-25T00:00:00Z"
  }
}
```

`serverKind` values (proposal): `ollama | lmstudio | foundry_local | llamacpp | vllm | litellm | azure_openai | bedrock | vertex_openai | anthropic_compat | openai | openrouter | generic`. `authScheme` values: `none | bearer | api_key_header | token_provider`. Field names are proposals, not contract fields.

### 7.7 Certification interplay

- Golden set (about 30 scenarios, contract decision 5) runs per (model, `serverKind`, server version, quantization).
- Labels cap by probe: if `toolsPlusSchemaOk` is false and tools are unreliable, L1 mode may still reach Works; Certified requires the full-coach path to pass the golden set.
- Re-run on server upgrade; Ollama #14493 shows silent regressions between versions [S8].
- Label hosted models separately from local ones; hardware speed is not part of the model label but is shown beside it (Tier and measured speed).

### 7.8 Defer list

| Item | Target | Reason |
|---|---|---|
| Embedded inference (Foundry Local in-process SDK, ~20 MB runtime [S15], or llama.cpp, MIT [S23]) | v2 | Contract: none at v1; both licences permit it, still VERIFY model licences |
| Native Anthropic Messages adapter | v1.1, first priority | Restores strict tools, structured outputs and caching [S46][S47]; reaches Claude on Bedrock [S40] |
| Responses API | later | Chat Completions is the common denominator; Microsoft's preference for Responses [S38] is a watch item |
| Entra interactive auth (MSAL/WAM) | v1.1, demand-driven | v1 uses a static key or gateway-issued bearer token |
| Vertex OAuth / ADC, SigV4, mTLS | v1.1 or later | Need token providers or signing; Bedrock API keys cover v1 [S42] |
| Model download and management UI | later | Users manage models in their server |
| NPU-specific tuning | later | Only via Foundry Local [S15] |
| Windows AI APIs / Phi Silica | later | Not OpenAI-compatible (VERIFY) |
| OpenRouter parameter-support matrix | v1 QA | Not researched |

---

## 8. Open questions and VERIFY list

1. Foundry Local: are `response_format` json_schema and `tool_choice` supported on `/v1/chat/completions`? Is the Qwen tool-calls-as-JSON-text report current? [S17][S49]
2. Ollama: are tools and `format`/`response_format` usable in one request, and does the tools-plus-schema suppression [S33] apply? Does the OpenAI endpoint really ignore `num_ctx` (third-party only [S9])? Does the Anthropic Messages API exist in Ollama [S2]?
3. Silent-install flags and code-signing status for Ollama, LM Studio and llama.cpp releases: only third-party sources for the first two [S48]; none for signing.
4. llama.cpp: exact Windows release asset names, default port (9931 vs 8080), lazy-grammar behaviour for tool calls [S21][S22].
5. Vertex OpenAI-compat: base URL, token lifetime, model-name format [S44].
6. Whether Claude is reachable via Chat Completions on Bedrock, and Messages API URL/auth on Vertex and Microsoft Foundry [S41][S46].
7. Azure: accepted auth header forms for key auth; correct Entra token scope [S38].
8. Real prefill and TTFT numbers on corporate 16 GB laptops (all speed estimates beyond [S30] are ASSUMPTION); prefix-cache reuse per server.
9. BFCL numbers in 3.1 should be re-checked against the CSV; BFCL paper page was blocked (verification screen), so only the leaderboard was used [S24].
10. Legal review: LM Studio terms on "recommending" and on enterprise use of a free-for-work licence [S11][S12]; model-licence review for each recommended weight set.
11. Hardware tier thresholds and probe pass marks (7.4) are guesses until measured on target machines.

---

## 9. Sources (all accessed 2026-10-25)

| ID | URL | Used for |
|---|---|---|
| S1 | https://github.com/ollama/ollama/blob/main/LICENSE | Ollama MIT licence |
| S2 | https://github.com/ollama/ollama/releases | Version v0.40.11 (2026-10-24); Anthropic API mention |
| S3 | https://docs.ollama.com/api/openai-compatibility | OpenAI compat endpoints, unsupported fields |
| S4 | https://docs.ollama.com/capabilities/structured-outputs | `format`, `response_format`, cloud limitation |
| S5 | https://docs.ollama.com/windows | Install, admin rights, paths, GPU drivers |
| S6 | https://docs.ollama.com/faq | Binding, keep-alive, proxy, no-cloud, data statement |
| S7 | https://docs.ollama.com/context-length | Default context by VRAM, env var |
| S8 | https://github.com/ollama/ollama/issues/14493 | Qwen 3.5 tool-call parser bug |
| S9 | https://github.com/ollama/ollama/issues/11409 and third-party blogs (URLs not recorded) | `num_ctx` ignored on OpenAI endpoint; silent truncation (VERIFY) |
| S10 | https://ollama.com/library/qwen3.5 | Model sizes, tools capability |
| S11 | https://lmstudio.ai/blog/free-for-work | Free for work 2025-07-08; Enterprise plan |
| S12 | https://lmstudio.ai/app-terms | LM Studio terms |
| S13 | https://lmstudio.ai/docs/developer/openai-compat | LM Studio OpenAI compat, tools, structured output |
| S14 | https://lmstudio.ai/docs/app/api/headless | llmster daemon, login server, JIT, REST models |
| S15 | https://devblogs.microsoft.com/foundry/foundry-local-ga/ | Foundry Local GA 2026-04-09, SDKs, EPs |
| S16 | https://learn.microsoft.com/en-us/azure/foundry-local/reference/reference-cli | CLI (preview), server port, install notes |
| S17 | https://learn.microsoft.com/en-us/azure/foundry-local/reference/reference-rest | REST (preview), tools, Responses |
| S18 | https://github.com/microsoft/Foundry-Local | Licences, scope |
| S19 | https://learn.microsoft.com/en-us/windows/ai/new-windows-ml/overview | Windows ML scope and OS requirements |
| S20 | https://support.microsoft.com/help/5039678 | Copilot+ PC baseline |
| S21 | llama.cpp repository, file `tools/server/README.md` (github.com/ggml-org/llama.cpp; exact blob URL not recorded) | Server endpoints, port, flags |
| S22 | llama.cpp repository, file `docs/function-calling.md` | Tool formats, KV quantization caution |
| S23 | llama.cpp repository `LICENSE` | MIT, "The ggml authors" |
| S24 | https://gorilla.cs.berkeley.edu/data_overall.csv (and leaderboard page) | BFCL V4 numbers |
| S25 | https://huggingface.co/Qwen/Qwen3.5-27B (and -9B, -4B, -35B-A3B; Qwen3.6-35B-A3B cards) | Vendor-reported benchmarks, thinking behaviour |
| S26 | https://ai.google.dev/gemma/docs/core/model_card_4 | Gemma 4 sizes, Tau2, licence |
| S27 | https://arxiv.org/html/2508.10925 | gpt-oss model card: size, tau-bench Retail |
| S28 | https://arxiv.org/abs/2406.12045 | tau-bench design and pass^k |
| S29 | llama.cpp repository, quantize README (`tools/quantize`) | Quantization sizes |
| S30 | llama.cpp GitHub discussion #21112 | Community speed datapoints |
| S31 | https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/structured_outputs.md | vLLM structured outputs |
| S32 | https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/tool_calling.md | vLLM tool calling |
| S33 | https://arxiv.org/abs/2606.25605 | Tools plus schema suppression |
| S34 | https://arxiv.org/abs/2609.23742 | Small-model constrained decoding |
| S35 | https://arxiv.org/abs/2605.02363 | Grammar latency/accuracy |
| S36 | https://arxiv.org/abs/2408.02442 | "Let Me Speak Freely" |
| S37 | https://arxiv.org/abs/2501.10868 | JSONSchemaBench |
| S38 | https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle | Azure OpenAI v1, auth |
| S39 | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs | Azure structured outputs limits |
| S40 | https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html | Bedrock endpoints |
| S41 | https://docs.aws.amazon.com/bedrock/latest/userguide/inference-chat-completions.html | Bedrock Chat Completions |
| S42 | https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html | Bedrock API keys |
| S43 | https://docs.aws.amazon.com/bedrock/latest/userguide/models-endpoint-availability.html | Endpoint availability (listing only) |
| S44 | https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/call-gemini-using-openai-library | Vertex OpenAI compat |
| S45 | https://docs.litellm.ai | LiteLLM behaviour, licence |
| S46 | https://platform.claude.com/docs/en/api/openai-sdk | Anthropic OpenAI compat limits; native structured outputs |
| S47 | https://platform.claude.com/docs/en/build-with-claude/prompt-caching | Prompt caching multipliers |
| S48 | Silent Install HQ pages for Ollama and LM Studio (third party; URLs not recorded) | Silent-install flags (VERIFY) |
| S49 | Microsoft Tech Community article on Foundry Local tool calling (URL not recorded) | Qwen tool calls as JSON text (VERIFY) |
| S50 | arXiv 2605.26128 | Title only; PDF unreadable |
