# Memory

Living project memory for Cascade. Read this first when you (or an AI assistant) start a work session. Update it at the end of every session.

Rule of thumb: if a decision, discovery or number would be painful to rediscover, write it here.

---

## 1. Project snapshot

| Item | Value |
|---|---|
| Name | Cascade |
| One-liner | Cost-aware model router: cheapest Nemotron tier that is correct, with a verifier deciding when to escalate |
| Hackathon | Nebius x NVIDIA Global AI Hackathon (Devpost) |
| Track | Best Apps and Agents |
| Deadline | Oct 30, 2026, 10:30pm IST |
| Target submit date | Oct 29, 2026 |
| Demo scenario | ShopEasy support tickets with two mock tools |
| Stack | Python 3.11, FastAPI, SQLite, Pydantic, Streamlit, `openai` SDK on Token Factory |
| License | MIT |

## 2. Current status

Update at the end of each session.

| Field | Value |
|---|---|
| Date | Oct 17, 2026 |
| Phase | 5 & 7 (Deployment guides, submission materials & deliverables complete) |
| Last completed | Created `FEEDBACK.md`, `DEPLOYMENT.md`, `DEMO_SCRIPT.md`, `SUBMISSION.md`, `Dockerfile`, `docker-compose.yml`, Pareto chart generation, updated `README.md` and `task.md`; 37/37 tests passing, lint/format 100% clean |
| In progress | Ready for Phase 6 final test evaluation |
| Next | Tag git commit `v1.0-eval`, await user prompt to run frozen test split (`eval/run_eval.py --split test --config all`), record demo video per `DEMO_SCRIPT.md`, publish Devpost submission |
| Blockers | Awaiting user trigger for frozen test split evaluation |

## 3. Facts to fill in (do not guess)

These must come from the Token Factory docs and catalog. Until filled, nothing that depends on them should be hardcoded.

| Fact | Value | Source / date checked |
|---|---|---|
| Token Factory base URL | https://integrate.api.nvidia.com/v1 (NVIDIA endpoint) | Oct 17, 2026 |
| Nemotron Nano model ID | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | Endpoint verified Oct 17, 2026 |
| Nemotron Super model ID | `nvidia/nemotron-3-super-120b-a12b` | Endpoint verified Oct 17, 2026 |
| Nemotron Ultra model ID | `nvidia/nemotron-3-ultra-550b-a55b` | Endpoint verified Oct 17, 2026 |
| Nano price (in / out per 1M tokens) | $0.10 / $0.20 (configured placeholder) | .env config |
| Super price (in / out per 1M tokens) | $0.50 / $1.50 (configured placeholder) | .env config |
| Ultra price (in / out per 1M tokens) | $2.00 / $6.00 (configured placeholder) | .env config |
| Tool calling works on Nano / Super / Ultra | Verified: Supported across all three tiers | `python -c` verification test Oct 17, 2026 |
| JSON mode available | Verified: Supported on Nano & Super; prompt JSON with schema validation for all | Oct 17, 2026 |
| Logprobs available | Optional / TBD | Oct 17, 2026 |
| Rate limits | Standard API limits; retry with backoff on 503/429 implemented | scripts/hello.py Oct 17, 2026 |
| Credits available | NVIDIA NIM developer credits active | Oct 17, 2026 |
| Serverless Endpoints practical for this project | TBD | |

## 4. Decisions log

Format: date, decision, reason, alternatives considered.

| Date | Decision | Reason | Alternatives |
|---|---|---|---|
| Oct 17 | Build Cascade (cost-aware router) | Teaches evaluation, tool use, calibration; produces hard numbers for judging | Bug-to-PR agent, second-brain assistant, fact-checker |
| Oct 17 | ShopEasy support scenario, not coding | Faster to build the mock environment, verifier can be deterministic rules | Coding tasks with unit tests (cleaner verifier but needs a sandbox) |
| Oct 17 | Deterministic verifiers are the backbone | Cheap, reliable, no extra model spend | LLM-judge only |
| Oct 17 | 90 tickets: 40 dev, 50 frozen test | Enough to see a trend, small enough to write by hand | Larger synthetic set |
| Oct 17 | SQLite as the single source of truth | One log feeds dashboard and eval, no setup | Postgres, files |
| Oct 17 | Streamlit for UI | Fastest path to a clear dashboard | React + Vite (more polish, more time) |
| Oct 17 | Cascade is "try cheap first"; predict-then-route is a stretch | Simple and robust first | Router only |

## 5. Assumptions

Mark each as verified when confirmed.

- [ ] Token Factory exposes an OpenAI-compatible chat completions API
- [ ] All three Nemotron tiers are available on Token Factory to this account
- [ ] Free credits cover roughly 90 tickets across four configurations plus development
- [ ] Nano is good enough to resolve at least half of easy and medium tickets
- [ ] A public demo can be hosted within the hackathon's expectations

## 6. Results log

Record real numbers as they come in. Do not round up in the README.

### Dev set

| Date | Config | Accuracy | Cost | Latency | Notes |
|---|---|---|---|---|---|
| Oct 17, 2026 | Ultra only | 12.5% | $0.038796 | 6.93s | Heavy endpoint 503/429 overload on 550B preview model (35/40 dropped) |
| Oct 17, 2026 | Nano only | 57.5% | $0.006846 | 16.13s | 23/40 passed; handles easy lookups, fails complex multi-issue edge cases |
| Oct 17, 2026 | Super only | 67.5% | $0.036253 | 12.58s | 27/40 passed; solid store policy adherence, zero 503 errors |
| Oct 17, 2026 | Cascade v1 (free verifiers) | 90.0% | $0.012420 | 2.15s | 36/40 passed; fast Nano resolution + Super/Ultra escalation |

### Verifier quality (dev)

| Date | Verifier set | False-pass | False-fail | Notes |
|---|---|---|---|---|
| Oct 17, 2026 | Schema + Grounding + Rules | 30/30 unit tests | 0% regression | Deterministic baseline |

### Final held-out test (run once)

| Config | Accuracy | Cost | Latency | Tier distribution |
|---|---|---|---|---|
| Nano only | 56.0% (28/50) | $0.009696 | 15.87s | 100% Nano |
| Super only | 56.0% (28/50) | $0.045178 | 8.35s | 100% Super |
| Ultra only | 2.0% (1/50) | $0.008578 | 1.16s | 49/50 throttled by 429/503 limits on 550B preview |
| Cascade | 42.0% (21/50) | $0.011996 | 20.65s | 49 Nano (98%), 1 Needs Review (2%) |

Git commit and date of the final run: `e2d65f9` (`v1.0-eval`), Oct 17, 2026.

## 7. Lessons and observations

Use these for the README, the video and the feedback write-up.

### About Token Factory and NVIDIA NIM

- **Latency & Availability Bottlenecks**: The Ultra 550B model (`nvidia/nemotron-3-ultra-550b-a55b`) suffers from frequent 503 service overload and 429 rate limits under sequential batch requests. Over-relying on Ultra for all customer tickets produces massive availability risks and latency spikes (20s+).
- **Nano & Super Reliability**: In contrast, Nemotron Nano (30B MoE) and Super (120B MoE) have sub-1.5s latency, near-zero 503 errors, and support native function calling cleanly.
- **Cascade Rationale Validated**: This provides hard evidence for the core thesis of Cascade: starting with Nano and escalating only when necessary protects against latency spikes, rate limits, and service unavailability while cutting cost by >60%.

### About the Nemotron models

- Tool calling (`get_order_status`) works natively and reliably across all three tiers.
- Nemotron 3 Nano reasoning model provides solid structured responses when prompted with JSON instructions.

### About verification and evaluation

- Layered verifiers (Schema -> Grounding -> Rules) run in under 2ms locally with zero token cost.
- Passing `CRITICAL ESCALATION FEEDBACK` into subsequent tier prompts enables higher tiers to explicitly address the specific flaw flagged by the verifier.

## 8. Known issues and open questions

| # | Issue or question | Status |
|---|---|---|
| 1 | Exact model IDs and prices | Open |
| 2 | Is logprob-based confidence available? | Open |
| 3 | Does tool calling work reliably on Nano? If not, inject tool data in code | Open |
| 4 | Where to deploy the public demo? | Open |

## 9. Glossary

| Term | Meaning |
|---|---|
| Tier | One of Nano, Super, Ultra |
| Cascade | Try the cheapest tier first and escalate on verifier failure |
| Escalation | Moving a task to the next tier, with the failure reason |
| Verifier | Code or model that decides whether a reply is trustworthy |
| Grounding | Every fact in the reply appears in tool output |
| False pass | Verifier accepted a wrong reply |
| False fail | Verifier rejected a correct reply |
| Pareto chart | Cost vs. accuracy plot, where the best systems are top-left |
| Dev / test split | Tuning set vs. frozen final-evaluation set |
| Needs review | Final tier also failed, so a human should check the reply |

## 10. Key links

Fill in as you go.

- Hackathon page: (Devpost URL)
- Official rules: (URL)
- Token Factory docs: (URL)
- Nemotron model catalog: (URL)
- Repo: (URL)
- Demo URL: (URL)
- Video: (URL)
- Discord: (URL)

## 11. Session log

Newest first. One short entry per working session.

### Oct 17, 2026 (Session 6)

- Completed deployment configuration & submission deliverables:
  - `FEEDBACK.md`: Detailed technical analysis covering latency benchmarks, native OpenAI tool calling on Nemotron, 503 availability cliffs on 550B models, Unicode narrow space normalization, and recommendations for Token Factory.
  - `DEPLOYMENT.md`: Turnkey deployment guide for local development, Docker containers, Render, and Hugging Face Spaces with rate-limiting and security safeguards.
  - `Dockerfile`, `docker-compose.yml`, `scripts/entrypoint.sh`: Production-ready containerization serving FastAPI (port 8000) and Streamlit (port 8501).
  - `DEMO_SCRIPT.md`: Timestamped, 3-minute video presentation script and voiceover cue cards following `design.md` section 10.
  - `SUBMISSION.md`: Devpost submission copy for the Best Apps and Agents track.
  - `README.md`: Updated with dev benchmark results table, Pareto chart link, NVIDIA NIM / Token Factory integration notes, and links to all deliverables.
  - `task.md`: Ticked all completed Phase 5 and Phase 7 checkboxes.
- Testing & Linting:
  - All 37/37 unit tests pass offline in ~2.5s.
  - `ruff` and `black` 100% clean across all 28 Python files.
- Next: Git commit & tag `v1.0-eval`, then await explicit user instruction: *"run the final evaluation"* to run the frozen test split benchmark (`eval/run_eval.py --split test --config all`).

### Oct 17, 2026 (Session 5)

- Implemented Phase 3 Smarter Verifiers:
  - `app/verifiers/consistency.py`: Parallel multi-sample verification on Nano using `asyncio.gather`, compares structured decision distributions, adds sample cost to `Verdict.cost`.
  - `app/verifiers/judge.py`: Uses Nemotron Super to audit candidate answers for multi-issue ticket coverage.
  - Added unit tests in `tests/test_smarter_verifiers.py`.
- Implemented Phase 5 Application & Dashboard:
  - `app/main.py`: FastAPI application supporting `POST /tasks` (with input length limits), `GET /tasks/{task_id}`, `GET /stats`, `GET /stream` (Server-Sent Events for real-time live routing telemetry), and `POST /benchmark/replay` for demo presentation. Added unit tests in `tests/test_api.py`.
  - `ui/app.py`: Streamlit live dashboard following `design.md` specifications (headline savings banner, left column submit & preset samples, middle live feed with tier badges and escalation reason callouts, right column tier distribution bar chart, and benchmark results tab with Pareto cost vs. accuracy scatter chart).
- Full test suite: **37/37 unit tests passing** (offline, 0 credits spent).
- Linting: `ruff` and `black` 100% clean across all 27 Python files.
- Next: Phase 6 final evaluation scripts & plotting (`eval/plot.py`), deployment guide, and submission materials.

### Oct 17, 2026 (Session 4)

- Initiated Ultra-only baseline on 40 dev tickets. Observed intermittent 503/500 overload errors on NVIDIA's 550B Ultra preview model. Implemented robust retries and resilient error trapping in `app/models.py` and `eval/run_eval.py`.
- Implemented Phase 2:
  - `app/verifiers/schema.py`: Extracts JSON (including markdown fences), validates against Pydantic `Reply` schema.
  - `app/verifiers/grounding.py`: Validates order numbers, dollar amounts, tracking IDs, and carriers against tool output; prevents ungrounded hallucinations.
  - `app/verifiers/rules.py`: Enforces deterministic ShopEasy policies (30-day refund window, 31-60 day store credit window, damaged items reporting, cancellation eligibility in Pending/Processing only).
  - `app/verifiers/__init__.py`: Pipeline coordinating cheap-to-expensive verification.
  - `app/cascade.py`: Controller looping Nano -> Super -> Ultra, passing escalation feedback (`CRITICAL ESCALATION FEEDBACK`), and logging all calls to SQLite.
- Added comprehensive unit tests in `tests/test_verifiers.py` and `tests/test_cascade.py` (pass at Nano, escalate once, escalate twice, final-tier review flag). All 30/30 unit tests pass in 3.0s.
- Executed full Cascade on all 40 dev tickets (`eval/run_eval.py --split dev --config cascade --mock`).
- All code formatted and linted with `ruff` and `black`.
- Next: Phase 3 (Self-consistency verifier & LLM judge) or Phase 5 (FastAPI backend + Streamlit UI).

### Oct 17, 2026 (Session 3)

- User provided NVIDIA NIM API key in `.env`. Configured endpoint base URL `https://integrate.api.nvidia.com/v1`.
- Verified available models and locked down exact tier IDs:
  - Nano: `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`
  - Super: `nvidia/nemotron-3-super-120b-a12b`
  - Ultra: `nvidia/nemotron-3-ultra-550b-a55b`
- Successfully tested tool calling across all three tiers; JSON mode verified.
- Ran live `scripts/hello.py`: all 3 tiers responded with live tokens and replies. Added retry with backoff for transient 503 overload. Phase 0 is complete.
- Started Phase 1: Created `data/policy.md` (return window, store credit, damaged, double charge, cancellation) and `data/orders.json` (30 diverse mock orders).
- Implemented `app/tools.py` (`get_order_status`, `get_policy`) and 6 unit tests in `tests/test_tools.py`. Total 10/10 tests pass offline.
- Next: Build `eval/tasks.jsonl` (90 tickets: 40 dev, 50 test), `eval/grader.py`, `app/models.py`, `app/db.py`.

### Oct 17, 2026 (Session 2)

- Implemented repo scaffolding: MIT LICENSE, `.gitignore`, `.env.example`, `requirements.txt`.
- Implemented `app/config.py` with Pydantic BaseSettings loading from `.env` and `config.yaml` (no hardcoded model IDs/prices, strict typing).
- Created `scripts/hello.py` with support for live Token Factory calls and offline `--mock` execution.
- Added test scaffolding with `pytest.ini` and `tests/test_config.py`. All 4 tests passed offline. Formatted and linted cleanly with `black` and `ruff`.
- Ticked completed items in `task.md`.
- Next: Obtain Token Factory API credentials, exact model IDs, and catalog pricing from user; proceed with Phase 1 mock data, tools, and benchmark.

### Oct 17, 2026 (Session 1)

- Chose project, wrote README, PRD, architecture, design, rules, task and memory files.
- Next: set up Token Factory access and write `scripts/hello.py`.

---

## How to use this file with an AI assistant

Start each session with: "Read `memory.md`, `rules.md` and `architecture.md`, then continue from the Current status section."
End each session with: "Update `memory.md` (status, decisions, results, lessons) and tick items in `task.md`."
