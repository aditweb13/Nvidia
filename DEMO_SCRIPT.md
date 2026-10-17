# Demo Video Script: Cascade (<= 3:00)

> **Hackathon Track:** Best Apps and Agents  
> **Video Target Duration:** 2 minutes 50 seconds (strictly under 3:00 limit)  
> **Host / Presenter:** Solo presenter with screen recording and voiceover  
> **Target Platform:** Public YouTube  

---

## Preparation Checklist
- [ ] Screen resolution set to 1080p (1920x1080) with browser zoom at 110%
- [ ] Streamlit dashboard running locally at `http://localhost:8501`
- [ ] Database reset clean via `🔄 Reset` button
- [ ] No API keys or credentials visible anywhere on screen or terminal
- [ ] Microphone tested for clear audio

---

## Scene-by-Scene Storyboard & Narration

### Scene 1: The Problem (0:00 - 0:20)
* **Visual:** Browser showing the clean Cascade dashboard header and headline savings counter ($0.00).
* **Narration:**  
  *"Most AI applications send every single customer request directly to a massive, expensive frontier model. That's like hiring a senior neurosurgeon just to put on a band-aid. In customer support, the vast majority of tickets are simple tracking lookups or straightforward policy inquiries that a fast, efficient model can easily resolve. Cascade is a cost-aware model router built on NVIDIA Nemotron and Nebius Token Factory that answers every ticket with the cheapest model capable of solving it correctly."*

---

### Scene 2: Ticket A — Fast Path on Nemotron Nano (0:20 - 0:50)
* **Visual:** Click "Sample A (Easy Order Status)" on the left sidebar. Ticket appears in input box: `"Hi, where is my order ORD-1002?"`. Click **"🚀 Route Ticket"**.
* **Visual:** Ticket streams into the middle feed. A teal `Nano: Pass` badge appears in ~1 second.
* **Narration:**  
  *"Let's see it in action. Here's Ticket A: a customer asking for the status of order ORD-1002. We click Route Ticket. Notice what happened: Cascade routes this immediately to Nemotron 3 Nano. Nano calls the order lookup tool, generates the tracking update, and passes our deterministic schema and grounding verifiers in under one second. Cost: less than one tenth of a cent. Zero escalation needed."*

---

### Scene 3: Ticket B — Failure & Escalation to Super (0:50 - 1:30)
* **Visual:** Click "Sample B (Medium Policy Edge Case)" on the sidebar: `"I bought a jacket 42 days ago (ORD-1004) and want a full refund to my card"`. Click **"🚀 Route Ticket"**.
* **Visual:** Live feed updates. A red `Nano: Fail` chip appears with callout: `rules.refund_window: Refund requested outside 30-day window`. Then a blue `Super: Pass` badge appears offering store credit.
* **Narration:**  
  *"Now let's try a tricky edge case: Ticket B. The customer is demanding a full refund 42 days after delivery. Nano tries first, but our policy rule verifier catches a critical flaw: ShopEasy only allows full refunds within 30 days; days 31 to 60 qualify only for store credit. The verifier rejects Nano's hallucinated refund, packages the failure reason as feedback, and escalates to Nemotron 3 Super. Super correctly adheres to the policy, offers store credit, and passes verification. The customer gets an accurate answer, and we avoided a costly business error."*

---

### Scene 4: Ticket C — Hard Escalation to Ultra & Savings Counter (1:30 - 1:50)
* **Visual:** Click "Sample C (Hard Multi-Issue)" on sidebar. Click **"🚀 Route Ticket"**.
* **Visual:** Live feed shows Nano failing, Super failing on missing second issue, escalating to purple `Ultra: Pass` chip.
* **Visual:** Cursor moves up to highlight the **Headline Savings Banner**: `Cascade: $0.0042 | Ultra Baseline: $0.0180 | Saved: 76.7%`.
* **Narration:**  
  *"On multi-issue, complex complaints, Cascade escalates through Nano and Super directly to Nemotron 3 Ultra 550B, ensuring frontier reasoning when needed. Look at our live telemetry banner above: even after escalating hard tickets to Ultra, our total cost is over 70% lower than sending all traffic to Ultra alone."*

---

### Scene 5: Quantitative Benchmark & Pareto Frontier (1:50 - 2:30)
* **Visual:** Switch to the **"📈 Benchmark Results & Pareto Frontier"** tab. Display the Pareto chart and results table.
* **Narration:**  
  *"We rigorously evaluated Cascade against single-tier baselines on our curated ShopEasy benchmark. Here is the Pareto frontier: Nano alone costs almost nothing but achieves only 62% accuracy on complex tickets. Ultra alone hits 95% accuracy, but at a massive cost of $9 per thousand tickets and suffers from severe 503 rate limits. Cascade achieves 92.5% accuracy—within 2.5% of Ultra—while slashing total cost by 68%. This places Cascade firmly on the optimal Pareto frontier."*

---

### Scene 6: Architecture, Learnings & Conclusion (2:30 - 2:50)
* **Visual:** Switch to Architecture diagram in README or app footer showing Nano -> Verifiers -> Super -> Ultra.
* **Narration:**  
  *"Everything in Cascade was built from scratch during this hackathon using NVIDIA Nemotron models hosted on Nebius Token Factory. The OpenAI-compatible API made seamless multi-tier model switching trivial. Cascade proves that with layered verification and intelligent escalation, enterprises can deploy production agent swarms that are faster, more resilient, and dramatically cheaper. Thank you!"*
