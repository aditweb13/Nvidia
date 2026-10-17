# Devpost Submission Text: Cascade

> **Hackathon:** Nebius x NVIDIA Global AI Hackathon  
> **Track:** Best Apps and Agents  
> **Target Date:** October 29, 2026  

---

### Project Title
**Cascade: Cost-Aware Model Router for AI Agents**

### Short Elevator Pitch
Cascade is an intelligent, cost-aware model router built on NVIDIA Nemotron and Nebius Token Factory that routes tasks to Nemotron Nano first, verifies replies with layered deterministic and semantic verifiers, and escalates to Super and Ultra only when needed—achieving 92.5% accuracy with a 68% cost reduction.

---

### 1. Inspiration
Modern AI architectures frequently fall into a costly trap: sending every single user request directly to a massive, expensive frontier model. In an enterprise customer support center, that is the equivalent of sending a senior neurosurgeon to apply a band-aid. The vast majority of customer inquiries are simple tracking lookups, return window checks, or routine status questions that a compact, specialized model handles with ease. 

Furthermore, during real-world testing, we observed that 500B+ frontier models suffer from latency spikes (20-40 seconds) and frequent 503 service overloads. We built **Cascade** to prove that by cascading through model tiers with rigorous, layered verification, we can achieve frontier-level accuracy, eliminate availability bottlenecks, and slash operating costs by over two-thirds.

---

### 2. What It Does
Cascade is an end-to-end model routing framework and live operations dashboard:
1. **Try-Cheap-First Routing:** Inbound tickets land on **Nemotron 3 Nano (30B MoE)** first.
2. **Layered Verification Pipeline:** Replies pass through a hierarchy of verifiers (Schema compliance -> Tool Grounding -> Business Policy Rules -> Multi-sample Consistency -> LLM Judge Audit).
3. **Targeted Escalation Feedback:** If a verifier detects a hallucination, calculation error, or policy violation, the failure reason is bundled into a `CRITICAL ESCALATION FEEDBACK` prompt and forwarded to **Nemotron 3 Super (120B MoE)** or **Nemotron 3 Ultra (550B MoE)**.
4. **Live Telemetry & Dashboard:** A Streamlit operations console tracks real-time routing paths, escalation callouts, tier distribution, and a live counter measuring dollars saved compared to an Ultra-only baseline.
5. **Pareto Frontier Benchmarking:** A standalone evaluation harness evaluating cost vs. accuracy tradeoffs on reproducible enterprise support datasets.

---

### 3. How We Built It
- **Model Tiers via Nebius Token Factory:**
  - **Tier 1 (Nano):** `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` (~$0.20/1M tokens)
  - **Tier 2 (Super):** `nvidia/nemotron-3-super-120b-a12b` (~$0.75/1M tokens)
  - **Tier 3 (Ultra):** `nvidia/nemotron-3-ultra-550b-a55b` (~$3.00/1M tokens)
- **Backend Architecture:** Built with Python 3.11, FastAPI (async SSE streaming), Pydantic v2 validation, and SQLite for granular call logs.
- **Verification Engine:**
  - `schema.py`: Extracts and validates JSON, strips markdown fences.
  - `grounding.py`: Fact-checks dollar figures, tracking IDs, carriers, and delivery dates against tool returns.
  - `rules.py`: Deterministically enforces business policies (30-day refund window, 31-60 day store credit, damaged item windows).
  - `consistency.py`: Multi-sample parallel verification on Nano using `asyncio.gather`.
  - `judge.py`: Nemotron Super audit verifying that all customer issues in multi-part complaints are addressed.
- **Frontend Dashboard:** Interactive Streamlit interface featuring Altair visualizations and live SSE feeds.
- **Offline Test Suite:** 37 comprehensive unit tests running without network or API token expenditure.

---

### 4. Challenges We Ran Into
- **503 Availability Cliffs on Ultra Models:** In batch testing, 550B models frequently encountered service overload (503) and 429 concurrency throttles. We engineered robust exponential backoff retries with jitter and recognized that Cascade is essential not just for cost, but as an availability firewall protecting users from frontier outages.
- **Markdown Fences in Small Model JSON Output:** Compact models occasionally wrap structured JSON in ````json ... ```` fences. We built resilient regex-based fence extraction to ensure 100% Pydantic parsing reliability.
- **Windows UTF-8 Code Page Quirks:** Tokenizer outputs for Nemotron occasionally output narrow non-breaking spaces (`\u202f`) before currency signs, triggering `charmap` encode errors on Windows shells. We addressed this by reconfiguring standard output streams to strict UTF-8 across all entrypoints.

---

### 5. Accomplishments That We're Proud Of
- **Optimal Pareto Frontier:** Achieved **92.5% graded accuracy** on the ShopEasy benchmark—within 2.5% of Ultra alone—while reducing overall token spend by **68%**.
- **100% Offline Testability:** Built a comprehensive test suite (37/37 passing) that validates every verifier, database transaction, API endpoint, and state transition without spending a single API credit.
- **Production-Ready Observability:** Real-time visual feedback showing exactly *why* a ticket escalated (e.g., `rules.refund_window: Refund approved outside the 30-day window`) making model decisions transparent and auditable.

---

### 6. What We Learned
- Small models (30B MoE) are surprisingly competent at single-intent tool calling and policy lookups, resolving over 60% of common queries correctly on the first attempt.
- Explicit verifiers run in milliseconds locally with zero incremental LLM cost, making deterministic verifiers the most cost-effective accuracy booster available.
- Providing explicit feedback to higher tiers about *why* the previous tier failed prevents repeated mistakes and accelerates convergence.

---

### 7. What's Next for Cascade
- **Self-Tuning Predictive Router:** Training an upfront lightweight classifier (logistic regression / small embeddings) to route obvious complex multi-issue tickets directly to Super or Ultra, skipping Tier 1 latency.
- **Multi-Domain Expansion:** Expanding Cascade beyond customer support to code generation (escalating based on unit test passes) and document extraction.
- **Enterprise RBAC & Multi-Tenant Logging:** Adding multi-tenant authentication and direct integrations with Zendesk and Salesforce Service Cloud.

---

### Built With
- `python`
- `nvidia-nemotron`
- `nebius-token-factory`
- `fastapi`
- `streamlit`
- `pydantic`
- `sqlite`
- `altair`
- `matplotlib`
- `pytest`
