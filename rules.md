# Rules

Working rules for the Cascade project. They apply to the developer and to any AI coding assistant working in this repository. When a rule here conflicts with a convenience, the rule wins.

## 1. Hackathon rules (hard requirements)

Source: the Nebius x NVIDIA Global AI Hackathon page on Devpost. Re-read the official rules before submitting.

- [ ] Deadline: **Oct 30, 2026, 10:30pm IST**. Internal target: submit on Oct 29.
- [ ] Everything runs on **Nebius Token Factory** (or AI Cloud) and uses **at least one NVIDIA open source model** (Nemotron).
- [ ] Pick one track: **Best Apps and Agents**.
- [ ] Public repository (GitHub, GitLab or Bitbucket) with an **open source license visible at the top** (MIT).
- [ ] README with setup instructions and how Nemotron and Token Factory were used.
- [ ] Working demo URL.
- [ ] Public YouTube demo video, **3 minutes or less**, showing the project working and how Token Factory and Nemotron are used.
- [ ] Project description: what, why, how.
- [ ] Feedback on Token Factory, AI Cloud and any NVIDIA tools used.
- [ ] If any work existed before the submission period, explain what changed. (Plan: nothing pre-exists.)
- [ ] Do not submit anything that violates the official rules. Check eligibility and third-party content rules.

## 2. Security rules

1. Never commit API keys, tokens or `.env`. `.env` must be in `.gitignore` from the first commit.
2. Never paste keys into prompts, issues, videos or screenshots.
3. Mock data only. No real customer data.
4. The public demo must have input length limits and a rate limit so it cannot drain credits.
5. If a key leaks, rotate it immediately.

## 3. Code rules

### General

- Python 3.11+, type hints on all public functions.
- Format with `black` and lint with `ruff` before each commit.
- Small modules with one responsibility, as laid out in `architecture.md`.
- No hidden global state. Configuration comes from `.env` and `config.yaml`.
- No hardcoded model IDs or prices. They come from configuration.
- Prefer `async` for model calls. Use `asyncio.gather` for parallel samples.
- Handle errors explicitly: retry transient errors, never swallow exceptions silently.
- Log with the `logging` module, not `print`, outside scripts.

### Interfaces

Keep these stable so components can be built in parallel.

- `call_model(tier, messages, tools=None) -> ModelResult`
- `verify(task, reply, tool_outputs) -> Verdict`
- `run_cascade(task) -> CascadeResult`

Changing one of these requires updating `architecture.md` and `memory.md` in the same commit.

### Verifiers

- Every verifier returns a `Verdict` with a short, human-readable `reason`.
- Run cheapest first. Stop at the first failure.
- Deterministic checks (schema, grounding, rules) are the backbone. LLM-based checks are additions, not replacements.
- Any extra model spend by a verifier must be returned as `Verdict.cost` and counted in task cost.

### Prompts

- Store prompts in files or constants, not scattered inline strings.
- Include the previous failure reason when escalating.
- Ask for structured JSON replies and validate them with Pydantic.
- Keep prompts identical across the four benchmark configurations except where the configuration requires otherwise.

### Tests

- `pytest` for verifiers, cost calculation, the controller loop (with a fake model client) and the grader.
- Verifier tests include known-bad examples that must fail and known-good examples that must pass.
- A test suite that runs without network access and without spending credits.

### Git

- Small commits with clear messages (`feat:`, `fix:`, `docs:`, `eval:`, `chore:`).
- Work on `main` or short-lived branches. Merge only working code.
- Tag the commit used for the final benchmark (`v1.0-eval`).

## 4. Evaluation

These rules protect the credibility of the results.

1. **Splits.** 90 tickets: 40 dev, 50 test. Tag every ticket with its split in `eval/tasks.jsonl`.
2. **Freeze the test set.** Do not read, tune against or modify the test set until the final run. Run it **once** with final settings.
3. **Tune on dev only.** Verifier thresholds, prompts and routing are tuned on dev.
4. **Deterministic grading first.** Grade with gold labels, required facts and issue checklists. If an LLM judge is used for grading, it must not be the same model as the one being graded.
5. **Count everything.** Cascade cost includes failed attempts, extra samples and judge calls.
6. **Four configurations, same tasks.** Nano only, Super only, Ultra only, Cascade.
7. **Report honestly.** Include accuracy, cost, latency, tier distribution, false-pass rate, false-fail rate. Also report tasks where Cascade cost more than Ultra alone.
8. **Disable cache for the final run.** Response caching is for development only.
9. **Record the setup.** Save model IDs, prices, date, config and git commit with the results.
10. **No cherry-picking.** If a rerun is needed, say so in the write-up and why.

### Metrics definitions

| Metric | Definition |
|---|---|
| Accuracy | Share of tickets where the final reply passes the grader |
| Total cost | Sum of all model call costs, including verifier overhead |
| False pass | Verifier passed a reply that the grader marked wrong |
| False fail | Verifier rejected a reply that the grader marked right |
| Tier distribution | Share of tickets resolved at each tier |

## 5. Documentation rules

- README stays accurate. Update it whenever setup or commands change.
- `memory.md` gets an entry for every important decision, discovery or change of plan.
- Do not state a number in the README or the video that is not in the saved results.
- Fill in the "How we use NVIDIA and Nebius" and feedback sections with real observations, as you go.

## 6. Working agreements with an AI assistant

If you use Claude or another assistant on this repo:

1. Read `memory.md`, `architecture.md` and `rules.md` first.
2. Do not invent model IDs, prices or API details. Ask or check the Token Factory docs.
3. Do not touch the test split or its results.
4. Keep changes small and tell what was changed and why.
5. Update `memory.md` and `task.md` after meaningful work.
6. When unsure about a requirement, check the hackathon page and the official rules, not memory.

## 7. Scope rules

- MVP first, stretch goals later. See the priority table in `PRD.md`.
- If more than half a day behind schedule, cut stretch items (predict-then-route, ablation, Serverless deployment) before touching the benchmark, README or video.
- Never cut: benchmark, honest results, README, demo video, feedback write-up.

## 8. Definition of done

A task is done when:

- It works and has tests where applicable.
- It follows these rules.
- Docs and `task.md` are updated.
- Nothing secret is committed.
