# Design

UX and visual design for the Cascade dashboard. The judging criteria ask for a complete product experience, not just a technical proof of concept, so the dashboard is part of the deliverable.

## 1. Design goals

1. **Make routing visible.** A viewer should understand within seconds which model handled each ticket and why.
2. **Make savings obvious.** One headline number: cost so far vs. what Ultra-only would have cost.
3. **Build trust.** Every escalation shows the verifier's reason in plain language.
4. **Stay simple.** One main screen, readable in a 3-minute demo video.

## 2. Primary users and moments

| Moment | What they need to see |
|---|---|
| Demo viewer watching the video | Tickets flowing, tiers lighting up, running cost vs. baseline |
| Developer exploring | Per-ticket history, failure reasons, tier distribution |
| Judge verifying claims | Benchmark table and Pareto chart |

## 3. Screen map

```
Dashboard (default)
├── Header: project name, status, Reset demo
├── Savings banner: Cascade cost vs Ultra-only
├── Left column: Submit ticket + sample tickets
├── Main column: Live feed of tickets with tier path
├── Right column: Tier distribution + cost per tier
└── Results tab: benchmark table + Pareto chart
```

Streamlit pages or tabs: `Live` and `Results`.

## 4. Layout (Live tab)

```
+--------------------------------------------------------------+
| Cascade                                  [Replay sample] [Reset] |
+--------------------------------------------------------------+
| Spent: 47 units   Ultra-only would be: 150   Saved: 69%      |
+----------------+-----------------------------+---------------+
| Submit ticket  | Live feed                   | Tiers         |
| [text box]     |  #A  Nano  PASS   1u  0.9s  | Nano   62%    |
| [Send]         |  #B  Nano FAIL -> Super PASS|  Super 28%    |
|                |       reason: outside 30-day|  Ultra 10%    |
| Samples:       |  #C  Nano > Super > Ultra   | Cost per tier |
| - Order status |       reason chain          | bars          |
| - Late return  |                             |               |
| - Multi-issue  |                             |               |
+----------------+-----------------------------+---------------+
```

## 5. Components

### 5.1 Savings banner

- Three numbers: Cascade cost, Ultra-only cost, percent saved.
- Updates after every completed task.
- Ultra-only cost is computed as the cost of running the same tasks directly on Ultra (measured in the benchmark, estimated from tokens in live mode, labeled "estimate" when estimated).

### 5.2 Ticket card (live feed)

Shows, in order:

1. Ticket ID and the first line of the ticket text.
2. **Tier path**: chips such as `Nano` -> `Super`, with a status icon on each (pass or fail).
3. Verifier reason on any failed chip, in one plain sentence.
4. Final answer (collapsible).
5. Cost and latency.
6. A "Needs review" badge if the last tier also failed.

### 5.3 Tier chip

| State | Appearance |
|---|---|
| Passed | Filled, with a check icon |
| Failed | Outlined, with an x icon and the reason on hover or below |
| Running | Subtle pulse animation |
| Not reached | Hidden |

### 5.4 Tier distribution

Horizontal bars for Nano, Super, Ultra showing share of tasks resolved at each tier, plus cost spent per tier.

### 5.5 Results tab

- Table: Nano only, Super only, Ultra only, Cascade with accuracy, cost and latency.
- Pareto chart: cost on the x axis, accuracy on the y axis, Cascade highlighted.
- Verifier panel: false-pass rate and false-fail rate.
- Short "How to read this" caption under the chart.

## 6. Visual style

| Token | Value | Use |
|---|---|---|
| Nano | Teal | Cheapest tier |
| Super | Blue | Mid tier |
| Ultra | Purple | Expensive tier |
| Pass | Green | Verified |
| Fail | Red or coral | Rejected |
| Neutral | Grays | Backgrounds, text |

- Color alone never carries meaning. Pair each status with an icon and a text label.
- Font: system sans-serif, 14 to 16px body text, monospace for IDs, costs and reasons.
- Support light and dark themes (Streamlit theme config).
- Generous spacing, no decorative effects.

## 7. Content and copy

Keep verifier reasons short, specific and human readable.

| Raw check | Displayed reason |
|---|---|
| `rules.refund_window` | Refund approved outside the 30-day window |
| `grounding.date_mismatch` | Delivery date in the reply does not match the order record |
| `schema.missing_field` | Reply was missing a decision |
| `consistency.disagree` | Three attempts gave different decisions |
| `judge.missing_issue` | Reply did not address the coupon issue |
| `model_error` | Model request failed, escalated |

Labels use sentence case. Currency is shown in units or USD, whichever the pricing config produces, and the unit is always visible.

## 8. States

| State | Behavior |
|---|---|
| Empty | "No tickets yet. Send one or replay the samples." |
| Loading | Running chip pulses, input disabled for that ticket |
| Error | Plain message, no stack traces, with a retry button |
| Rate limited (public demo) | "Demo limit reached. Try the sample tickets." |

## 9. Accessibility

- Text contrast of at least 4.5:1.
- Status conveyed by icon and text, not color alone.
- Keyboard-reachable buttons and inputs.
- Meaningful labels on form fields and charts (alt text for the Pareto image in the README).

## 10. Demo flow (3-minute video)

| Time | On screen |
|---|---|
| 0:00 to 0:20 | Problem statement over the empty dashboard |
| 0:20 to 0:50 | Replay samples. Ticket A lands on Nano. |
| 0:50 to 1:30 | Ticket B fails on Nano, escalates to Super. Zoom on the reason chip. |
| 1:30 to 1:50 | Ticket C climbs to Ultra. Savings banner updates. |
| 1:50 to 2:30 | Results tab: table and Pareto chart, state the headline number |
| 2:30 to 3:00 | What was learned, limitations, and what is next |

## 11. Out of scope for design

Authentication, user accounts, multi-tenant views, mobile layout, and a custom React frontend. If time remains after the MVP, a React rewrite is possible but not planned.
