# PRD: Cascade

Product requirements document. Version 1.0. Last updated: Oct 17, 2026.

## 1. Summary

Cascade is a cost-aware model router. It answers each task with the cheapest Nemotron model that can do it correctly, using a verifier to decide when to escalate to a stronger model. It ships with a live dashboard and a reproducible benchmark that proves the cost and quality tradeoff.

## 2. Problem

- Teams default to their largest model for every request because it is the safe choice.
- Most requests (in support, extraction, FAQ and similar workloads) are simple and do not need it.
- Cost and latency scale with volume, so over-using a large model gets expensive quickly.
- Existing "router" ideas are rarely measured. Teams cannot tell whether a cheaper path hurts quality.

## 3. Target users

| User | Need |
|---|---|
| Developer building an LLM app | Reduce inference cost without a quality drop, and see proof |
| Support or operations lead | Handle ticket volume affordably with fewer wrong answers |
| Hackathon judge | See a complete, working, well-evaluated use of Token Factory and Nemotron |

Primary demo persona: the operator of ShopEasy, a fictional online store with 1,000 tickets a day.

## 4. Goals and non-goals

### Goals

1. Route tasks across Nemotron Nano, Super and Ultra through Nebius Token Factory.
2. Verify answers automatically and escalate only on failure.
3. Show per-task and aggregate cost, latency and tier usage live.
4. Prove the tradeoff on a held-out benchmark against single-model baselines.
5. Deliver all hackathon submission requirements by Oct 29, 2026.

### Non-goals

- Production-grade multi-tenant SaaS (auth, billing, scaling).
- Fine-tuning or training models.
- Supporting non-NVIDIA models as tiers.
- Real customer data or real store integrations. Orders and policy are mocked.
- Beating Ultra's accuracy. The target is matching it closely at lower cost.

## 5. User stories

1. As a developer, I submit a ticket and get an answer plus the tier that produced it, so I can see the routing.
2. As an operator, I watch tickets stream in and see a running cost compared with an Ultra-only baseline.
3. As a developer, I can see why a tier was rejected (for example "refund approved outside 30-day window"), so I can trust the verifier.
4. As a developer, I can run the benchmark with one command and get a cost vs. accuracy chart.
5. As an operator, tickets that fail even at the top tier are flagged for human review instead of being sent.

## 6. Functional requirements

### Must have (MVP)

| ID | Requirement |
|---|---|
| F1 | Accept a task via `POST /tasks` and return the final answer, tier, cost and latency |
| F2 | Run the cascade Nano -> Super -> Ultra, starting at Nano by default |
| F3 | Pass the previous failure reason into the next tier's prompt |
| F4 | Verifiers: schema check, tool-grounding check, policy-rule check, run cheapest first |
| F5 | Log every model call to SQLite (tier, tokens, cost, latency, verdict, reason) |
| F6 | Mock tools: `get_order_status`, `get_policy` |
| F7 | Benchmark runner for four configurations: Nano only, Super only, Ultra only, Cascade |
| F8 | Deterministic grader using gold labels and checklists |
| F9 | Pareto chart (cost vs. accuracy) generated from logs |
| F10 | Streamlit dashboard showing live routing and cost counter |
| F11 | Flag a task for human review if the final tier fails verification |

### Should have

| ID | Requirement |
|---|---|
| F12 | Self-consistency verifier (3 parallel Nano samples) |
| F13 | LLM-judge verifier that checks issue coverage |
| F14 | Public deployed demo URL with a rate limit |
| F15 | False-pass and false-fail reporting for the verifier |

### Nice to have

| ID | Requirement |
|---|---|
| F16 | Predict-then-route classifier as a second routing strategy |
| F17 | Verifier ablation study |
| F18 | Deployment on Nebius Serverless Endpoints |

## 6.1 Non-functional requirements

- **Reproducibility:** one command runs the benchmark, and results are written to `eval/results/`.
- **Cost accuracy:** reported cost includes verifier overhead (extra samples and judge calls).
- **Latency:** a Nano-only path should answer in a few seconds. Report the average for every configuration.
- **Security:** no API keys in the repo, rate limit on the public demo.
- **Honesty:** results report all four configurations and the cases where Cascade is worse.

## 7. Success metrics

| Metric | Target |
|---|---|
| Accuracy of Cascade vs. Ultra-only on the held-out set | Within 3 percentage points |
| Cost of Cascade vs. Ultra-only | At least 40% lower (stretch: 60%) |
| Verifier false-pass rate on the dev set | Below 5% |
| Share of tasks resolved at Nano | At least 50% |
| Benchmark size | 90 tickets (40 dev, 50 held-out test) |

If targets are missed, the results are reported as measured and the analysis explains why.

## 8. Scope and milestones

| Date | Milestone |
|---|---|
| Oct 17 | Setup, API access, repo with license |
| Oct 18 to 19 | Mock data, 90-ticket benchmark, Ultra baseline |
| Oct 20 to 21 | Controller, logger, free verifiers |
| Oct 22 to 23 | Self-consistency and judge verifiers |
| Oct 24 | Predict-then-route (stretch) |
| Oct 25 to 26 | Dashboard, deployment |
| Oct 27 | Final held-out evaluation |
| Oct 28 | README, video, feedback write-up |
| Oct 29 | Submit (Oct 30, 10:30pm IST is the hard deadline) |

Details are in [`task.md`](task.md).

## 9. Hackathon requirements mapping

| Requirement | How it is met |
|---|---|
| Runs on Nebius Token Factory or AI Cloud | All model calls go through Token Factory |
| Uses at least one NVIDIA open model | Nemotron Nano, Super and Ultra |
| Track | Best Apps and Agents |
| Working demo URL | Deployed dashboard (F14) |
| Public YouTube video, 3 minutes or less | See the video plan in [`task.md`](task.md) |
| Public repo with open source license | MIT, visible at the top of the repository |
| README with setup and Nemotron/Token Factory usage | [`README.md`](README.md) |
| Feedback on tools | `FEEDBACK.md` and the README section |
| Pre-existing work explanation | README section "What was built during the submission period" |

## 10. Judging criteria alignment

| Criterion | Our evidence |
|---|---|
| Technological implementation | Three-tier routing, layered verifiers, async calls, full cost accounting |
| Design | Live dashboard with clear tier badges, cost counter and escalation reasons |
| Potential impact | Quantified cost saving on a realistic support workload |
| Quality of the idea | Measured routing and verification, not just a wrapper around one model |

## 11. Risks

| Risk | Mitigation |
|---|---|
| Tool calling unreliable on a tier | Fetch tool data in code and inject it into the prompt |
| Verifier too lenient or too strict | Tune on the dev set, track false-pass and false-fail rates |
| Credits run out | Cache responses during development, use the dev set only |
| Cascade not cheaper than Ultra | Inspect tier distribution, improve Nano prompt, report honestly |
| Deployment fails | Fall back to a read-only demo with precomputed results plus a few live calls |
| Time runs short | Cut stretch items, never the benchmark, README or video |

## 12. Open questions

- Exact Nemotron model IDs and per-token prices in the Token Factory catalog.
- Whether logprobs and JSON mode are available on each tier.
- Whether Serverless Endpoints deployment is quick enough to be worth it.

Record answers in [`memory.md`](memory.md).
