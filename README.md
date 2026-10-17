# Cascade

**A cost-aware model router for AI agents, built on NVIDIA Nemotron and Nebius Token Factory.**

Cascade answers each task with the cheapest model that can do it correctly. A small model tries first, a verifier checks the answer, and only failures escalate to a stronger model. Easy tasks never pay for the expensive model, and hard tasks still get it.

> Built for the **Nebius x NVIDIA Global AI Hackathon** (Track: Best Apps and Agents).

---

## Why this exists

Most AI apps send every request to one large model. That is like asking a senior surgeon to put on a band-aid. In a typical support inbox, a large share of requests are simple lookups that a small model handles fine. Cascade measures that gap and captures the savings without giving up quality.

## How it works

```
Task -> Controller -> Nano -> Verifier --pass--> Answer
                        |         |
                        |        fail
                        v         v
                      Super -> Verifier --pass--> Answer
                        |         |
                        |        fail
                        v         v
                      Ultra -> Verifier --> Answer (or flag for human review)

Every call is logged: tier, tokens, cost, latency, verifier result.
```

1. The **controller** starts at the cheapest tier (Nemotron Nano).
2. The **verifier** runs cheap checks first (schema, tool grounding, policy rules) and more expensive ones only when needed (self-consistency, LLM judge).
3. On failure, the task **escalates** to the next tier together with the reason for the failure.
4. Every call is logged to SQLite. The dashboard and the evaluation harness both read from this log.

See [architecture.md](architecture.md) for the full design.

## Demo scenario: ShopEasy support tickets

| Ticket | Difficulty | Expected path |
|---|---|---|
| "Where is my order #4821?" | Easy | Nano, passes |
| "Return a jacket I bought 40 days ago" | Medium | Nano fails a policy check, Super passes |
| "Charged twice, coupon failed, item damaged" | Hard | Nano and Super fail, Ultra passes |

## Results

> Fill this in after the final held-out run (see [rules.md](rules.md), section "Evaluation").

| Configuration | Accuracy | Total cost | Avg latency |
|---|---|---|---|
| Nano only | TBD | TBD | TBD |
| Super only | TBD | TBD | TBD |
| Ultra only | TBD | TBD | TBD |
| **Cascade** | TBD | TBD | TBD |

![Cost vs accuracy](eval/results/pareto.png)

Cascade costs more than Ultra alone on tasks that fail at every tier. We report this honestly in the results.

## Quickstart

### Prerequisites

- Python 3.11+
- A Nebius Token Factory API key
- Git

### Install

```bash
git clone https://github.com/<your-username>/cascade.git
cd cascade
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
```

Edit `.env` and fill in the values. Check the Token Factory docs and model catalog for the base URL and the exact model IDs.

```env
TOKEN_FACTORY_BASE_URL=<from Token Factory docs>
TOKEN_FACTORY_API_KEY=<your key>

MODEL_NANO=<exact Nemotron Nano model id>
MODEL_SUPER=<exact Nemotron Super model id>
MODEL_ULTRA=<exact Nemotron Ultra model id>

# Prices in USD per 1M tokens (copy from Token Factory pricing)
PRICE_NANO_IN=0
PRICE_NANO_OUT=0
PRICE_SUPER_IN=0
PRICE_SUPER_OUT=0
PRICE_ULTRA_IN=0
PRICE_ULTRA_OUT=0

DB_PATH=data/cascade.db
```

Never commit `.env`.

### Verify the setup

```bash
python scripts/hello.py
```

This calls each tier once and prints the reply and token usage.

### Run the app

```bash
uvicorn app.main:app --reload          # API on http://localhost:8000
streamlit run ui/app.py                # Dashboard on http://localhost:8501
```

### Run the evaluation

```bash
python eval/run_eval.py --split dev --config all
python eval/run_eval.py --split test --config all   # only for final results
python eval/plot.py
```

Results are written to `eval/results/`.

## Project structure

```
cascade/
├── app/
│   ├── main.py          FastAPI app and SSE stream
│   ├── models.py        Token Factory client, tiers, cost calculation
│   ├── cascade.py       Controller and escalation loop
│   ├── router.py        Predict-then-route classifier (stretch)
│   ├── tools.py         get_order_status, get_policy
│   ├── schemas.py       Pydantic models
│   ├── db.py            SQLite logging
│   └── verifiers/       schema, grounding, rules, consistency, judge
├── data/                Mock orders, policy, SQLite file
├── eval/                Benchmark tasks, grader, runner, plots
├── ui/                  Streamlit dashboard
├── scripts/             Setup and helper scripts
├── README.md
├── PRD.md
├── architecture.md
├── design.md
├── rules.md
├── memory.md
└── LICENSE
```

## How we use NVIDIA and Nebius

- **NVIDIA Nemotron (Nano, Super, Ultra):** the three model tiers.
- **Nebius Token Factory:** serves all models through one OpenAI-compatible API, so switching tiers only changes the model name.
- **Where Token Factory helped:** TBD (fill in with real observations, such as latency, throughput and the cost of trying models in sequence).
- **Other Nebius services used:** TBD (for example Serverless Endpoints for deployment).

## What was built during the submission period

Everything in this repository was created during the hackathon submission period (starting Oct 17, 2026). Update this section if that changes.

## Feedback on Token Factory and NVIDIA tools

> Fill in during development. Be specific: tool-calling quality per tier, latency, documentation gaps, pricing clarity, and anything that surprised you.

## Limitations

- The benchmark uses a mock store with synthetic tickets. Real-world traffic would need its own benchmark.
- Verifier quality bounds system quality. See the false-pass and false-fail rates in the results.
- Escalation adds latency for tasks that climb several tiers.

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgements

Nebius, NVIDIA, and Devpost for the hackathon.
