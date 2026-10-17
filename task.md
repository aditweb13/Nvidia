# Tasks

Day-by-day checklist for Cascade. Deadline: **Oct 30, 2026, 10:30pm IST**. Target submission: **Oct 29**.

Legend: `[ ]` to do, `[x]` done. Priority tags: **MUST**, SHOULD, NICE. If behind schedule, cut NICE first, then SHOULD, never MUST.

Assumes about 3 to 4 focused hours a day.

---

## Phase 0: Setup (Sat Oct 17)

- [ ] **MUST** Register for the hackathon on Devpost and join the Discord
- [ ] **MUST** Sign up for the Nebius Builder Program for credits
- [ ] **MUST** Create a Token Factory account and API key
- [ ] **MUST** Read the Token Factory docs (base URL, auth, chat completions, tool calling)
- [ ] **MUST** Record exact model IDs for Nemotron Nano, Super and Ultra in `memory.md`
- [ ] **MUST** Record per-token prices in `memory.md`
- [ ] **MUST** Check: tool/function calling per tier, JSON mode, logprobs availability
- [x] **MUST** Create the GitHub repo with an MIT `LICENSE`
- [x] **MUST** Add `.gitignore` (including `.env`, `data/cascade.db`, `.venv`)
- [x] **MUST** Add `.env.example` and `requirements.txt`
- [x] **MUST** Commit the docs (`README.md`, `PRD.md`, `architecture.md`, `design.md`, `rules.md`, `task.md`, `memory.md`)
- [x] **MUST** Write `scripts/hello.py`: one call per tier, print reply and token usage

**Done when:** `python scripts/hello.py` prints a reply and token counts from all three tiers.

---

## Phase 1: Data and baselines (Sun Oct 18 to Mon Oct 19)

### Sun Oct 18: mock environment

- [ ] **MUST** `data/orders.json`: about 30 orders (dates, items, status, amounts, coupon, charges)
- [ ] **MUST** `data/policy.md`: return window (30 days), store credit window (60 days), damaged item, double charge, coupon rules
- [ ] **MUST** `app/tools.py`: `get_order_status(order_id)` and `get_policy(topic)`
- [ ] **MUST** Unit tests for both tools

### Mon Oct 19: benchmark and baseline

- [ ] **MUST** Write 90 tickets in `eval/tasks.jsonl`: 40 easy, 30 medium, 20 hard
- [ ] **MUST** Gold labels: correct decision, required facts, issue checklist
- [ ] **MUST** Tag splits: 40 dev, 50 test (keep the test set balanced across difficulty)
- [ ] **MUST** `eval/grader.py` (deterministic: decision, facts, checklist)
- [ ] **MUST** `app/models.py` basic `call_model` with token and cost accounting
- [ ] **MUST** `app/db.py` SQLite tables (`tasks`, `calls`)
- [ ] **MUST** Run **Ultra-only** on dev and record accuracy and cost in `memory.md`
- [ ] SHOULD Run Nano-only and Super-only on dev for early comparison

**Done when:** you have a number such as "Ultra-only dev: X% accuracy, Y cost".

---

## Phase 2: Cascade core (Tue Oct 20 to Wed Oct 21)

### Tue Oct 20: controller

- [ ] **MUST** `app/schemas.py`: `Task`, `Reply`, `Verdict`, `ModelResult`, `CascadeResult`
- [ ] **MUST** `app/cascade.py`: loop Nano -> Super -> Ultra, log every call, return `needs_review` if the last tier fails
- [ ] **MUST** Feedback passing: previous failure reason goes into the next tier's prompt
- [ ] **MUST** Retry with backoff on model errors
- [ ] **MUST** Fake model client for tests
- [ ] **MUST** Tests for the controller loop (pass at Nano, escalate once, escalate twice, final-tier failure)

### Wed Oct 21: free verifiers

- [ ] **MUST** `verifiers/schema.py` (Pydantic validation)
- [ ] **MUST** `verifiers/grounding.py` (dates, amounts, statuses must appear in tool output)
- [ ] **MUST** `verifiers/rules.py` (policy logic: refund window, store credit window, damaged, double charge)
- [ ] **MUST** Known-good and known-bad tests for each verifier
- [ ] **MUST** Run full cascade on the dev set and check logs

**Done when:** Cascade runs end to end on all 40 dev tickets and writes logs.

---

## Phase 3: Smarter verifiers (Thu Oct 22 to Fri Oct 23)

### Thu Oct 22: self-consistency

- [ ] SHOULD `verifiers/consistency.py`: 3 parallel Nano samples with `asyncio.gather`, compare structured decisions
- [ ] SHOULD Count extra sample cost in `Verdict.cost`
- [ ] SHOULD Run only after cheaper checks pass, make it configurable

### Fri Oct 23: LLM judge and tuning

- [ ] SHOULD Extract issues from the ticket (Nano call)
- [ ] SHOULD `verifiers/judge.py`: Super checks each issue is addressed
- [ ] **MUST** Measure false-pass and false-fail rates on dev
- [ ] **MUST** Tune prompts and thresholds on dev only
- [ ] **MUST** Record findings in `memory.md`

**Done when:** on dev, Cascade is close to Ultra's accuracy at a clearly lower cost, and the false-pass rate is known.

---

## Phase 4: Predict-then-route (Sat Oct 24, stretch)

- [ ] NICE Features: ticket length, number of order IDs, keywords ("also", "twice", "damaged")
- [ ] NICE Train logistic regression on dev outcomes (scikit-learn)
- [ ] NICE `app/router.py` and a `--strategy` flag
- [ ] NICE Compare against try-cheap-first on dev

Skip this phase if more than half a day behind.

---

## Phase 5: App and deployment (Sun Oct 25 to Mon Oct 26)

### Sun Oct 25: backend and dashboard

- [ ] **MUST** `app/main.py`: `POST /tasks`, `GET /tasks/{id}`, `GET /stream` (SSE), `GET /stats`
- [ ] **MUST** `ui/app.py` Live tab per `design.md`: submit box, samples, live feed, savings banner, tier distribution
- [ ] SHOULD `POST /benchmark/replay` for the demo
- [ ] **MUST** Plain error and empty states

### Mon Oct 26: deploy

- [ ] SHOULD Deploy a public demo (Nebius Serverless Endpoints if quick, otherwise Render, Railway or Hugging Face Spaces)
- [ ] **MUST** Keys only in environment variables
- [ ] **MUST** Rate limit and input length limit on the public demo
- [ ] **MUST** Test the URL from a different device or network
- [ ] **MUST** Fallback plan if deployment fails: read-only demo with precomputed results

**Done when:** a stranger can open the URL and watch tickets route live.

---

## Phase 6: Final evaluation (Tue Oct 27)

- [ ] **MUST** Freeze code and config. Tag `v1.0-eval`.
- [ ] **MUST** Disable response caching
- [ ] **MUST** `eval/run_eval.py --split test --config all` (run once)
- [ ] **MUST** Save results to `eval/results/` with model IDs, prices, date and commit hash
- [ ] **MUST** `eval/plot.py`: Pareto chart (`eval/results/pareto.png`)
- [ ] **MUST** Compute accuracy, cost, latency, tier distribution, false-pass and false-fail rates
- [ ] **MUST** List tasks where Cascade cost more than Ultra alone
- [ ] SHOULD Ablation: free verifiers only vs. with consistency and judge
- [ ] **MUST** Fill in the README results table with the real numbers

**Done when:** every number in the README comes from saved result files.

---

## Phase 7: Submission materials (Wed Oct 28)

### README

- [ ] **MUST** Results table and chart
- [ ] **MUST** "How we use NVIDIA and Nebius" with real observations
- [ ] **MUST** "What was built during the submission period"
- [ ] **MUST** Test the setup steps on a clean machine or fresh clone
- [ ] **MUST** Confirm the license is visible at the top of the repo page

### Video (3 minutes or less, public YouTube)

- [ ] **MUST** Script following the flow in `design.md` section 10
- [ ] **MUST** Record the live dashboard with an escalation highlighted
- [ ] **MUST** Show the results chart and state the headline number
- [ ] **MUST** Show how Token Factory and Nemotron are used
- [ ] **MUST** Upload as public, check the length is under 3:00, check no keys on screen

### Feedback

- [ ] **MUST** `FEEDBACK.md` on Token Factory, Nemotron and any NVIDIA tools used: latency, tool-calling quality per tier, documentation gaps, pricing clarity, bugs hit

---

## Phase 8: Submit (Thu Oct 29, buffer Oct 30)

- [ ] **MUST** Devpost form: project description (what, why, how)
- [ ] **MUST** Select the Best Apps and Agents track
- [ ] **MUST** Add demo URL, YouTube link, repo URL
- [ ] **MUST** Add the feedback and pre-existing work statement
- [ ] **MUST** Re-read the official rules once
- [ ] **MUST** Open all links in a private window to confirm they are public
- [ ] **MUST** Submit, then confirm the submission shows on the project gallery

---

## Submission checklist

- [ ] Public repo with the license visible at the top
- [ ] README with setup steps and Nemotron/Token Factory usage
- [ ] Runs on Nebius Token Factory with at least one NVIDIA open model
- [ ] Working demo URL
- [ ] Public YouTube video, 3 minutes or less
- [ ] Project description
- [ ] Track selected
- [ ] Feedback on Token Factory and NVIDIA tools
- [ ] No API keys anywhere (repo, video, screenshots)

---

## Cut list (in order if time runs short)

1. Predict-then-route classifier
2. Verifier ablation
3. Nebius Serverless deployment (use another host)
4. LLM-judge verifier
5. Self-consistency verifier

Never cut: benchmark, honest results, README, demo video, feedback.

---

## Backlog (after the hackathon)

- Real traffic benchmark
- Learned router using more features and embeddings
- Support for other tool sets and domains (invoice extraction, coding tasks with unit-test verifiers)
- React frontend
