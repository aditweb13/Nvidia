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
| Phase | 0 (setup) |
| Last completed | Planning and documentation |
| In progress | Token Factory account and API access |
| Next | `scripts/hello.py`, record model IDs and prices |
| Blockers | None yet |

## 3. Facts to fill in (do not guess)

These must come from the Token Factory docs and catalog. Until filled, nothing that depends on them should be hardcoded.

| Fact | Value | Source / date checked |
|---|---|---|
| Token Factory base URL | TBD | |
| Nemotron Nano model ID | TBD | |
| Nemotron Super model ID | TBD | |
| Nemotron Ultra model ID | TBD | |
| Nano price (in / out per 1M tokens) | TBD | |
| Super price (in / out per 1M tokens) | TBD | |
| Ultra price (in / out per 1M tokens) | TBD | |
| Tool calling works on Nano / Super / Ultra | TBD | |
| JSON mode available | TBD | |
| Logprobs available | TBD | |
| Rate limits | TBD | |
| Credits available | TBD | |
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
| | Ultra only | | | | |
| | Nano only | | | | |
| | Super only | | | | |
| | Cascade v1 (free verifiers) | | | | |
| | Cascade v2 (+ consistency) | | | | |
| | Cascade v3 (+ judge) | | | | |

### Verifier quality (dev)

| Date | Verifier set | False-pass | False-fail | Notes |
|---|---|---|---|---|
| | | | | |

### Final held-out test (run once)

| Config | Accuracy | Cost | Latency | Tier distribution |
|---|---|---|---|---|
| Nano only | | | | |
| Super only | | | | |
| Ultra only | | | | |
| Cascade | | | | |

Git commit and date of the final run: TBD

## 7. Lessons and observations

Use these for the README, the video and the feedback write-up.

### About Token Factory

- (latency, throughput, errors, docs gaps, pricing clarity)

### About the Nemotron models

- (which tier handles which ticket types, failure modes, tool-calling quality)

### About verification and evaluation

- (what the verifier missed, surprising escalations, prompt changes that mattered)

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

### Oct 17, 2026

- Chose project, wrote README, PRD, architecture, design, rules, task and memory files.
- Next: set up Token Factory access and write `scripts/hello.py`.

---

## How to use this file with an AI assistant

Start each session with: "Read `memory.md`, `rules.md` and `architecture.md`, then continue from the Current status section."
End each session with: "Update `memory.md` (status, decisions, results, lessons) and tick items in `task.md`."
