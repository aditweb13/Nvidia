"""FastAPI application for Cascade model router.

Endpoints:
- POST /tasks: Intake support ticket and run Cascade
- GET  /tasks/{task_id}: Fetch task resolution and call history
- GET  /stats: Aggregated metrics (cost, latency, tier distribution, savings)
- GET  /stream: Server-Sent Events (SSE) live feed
- POST /benchmark/replay: Replay demo scenarios
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.cascade import run_cascade
from app.config import get_settings
from app.db import (
    get_stats,
    get_task,
    init_db,
    reset_db,
)
from app.schemas import CascadeResult, Task

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("cascade.api")

# In-memory queue for SSE broadcast
_sse_subscribers: list[asyncio.Queue] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite database tables are created
    init_db()
    logger.info("Cascade database initialized.")
    yield
    # Shutdown
    logger.info("Cascade API shutting down.")


app = FastAPI(
    title="Cascade Router API",
    description="Cost-aware Nemotron model routing with layered verifiers",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TicketRequest(BaseModel):
    ticket_text: str = Field(
        ..., max_length=2000, description="Customer message (max 2000 chars)"
    )
    task_id: str | None = Field(
        default=None, description="Optional custom task identifier"
    )
    order_id: str | None = Field(
        default=None, description="Optional associated order ID"
    )
    mock: bool = Field(default=False, description="Run in offline mock mode")


async def _broadcast_event(event_type: str, data: dict[str, Any]):
    message = json.dumps({"event": event_type, "data": data})
    for queue in list(_sse_subscribers):
        try:
            await queue.put(message)
        except Exception:  # noqa: BLE001
            _sse_subscribers.remove(queue)


@app.get("/")
def health_check():
    settings = get_settings()
    return {
        "status": "online",
        "service": "Cascade Model Router",
        "tiers": {
            "nano": settings.model_nano,
            "super": settings.model_super,
            "ultra": settings.model_ultra,
        },
    }


@app.post("/tasks", response_model=CascadeResult)
async def submit_ticket(req: TicketRequest):
    """Submit a support ticket to be routed through Cascade."""
    if not req.ticket_text.strip():
        raise HTTPException(status_code=400, detail="ticket_text cannot be empty")

    task_id = req.task_id or f"live_{int(asyncio.get_event_loop().time() * 1000)}"
    task = Task(
        task_id=task_id,
        ticket_text=req.ticket_text.strip(),
        order_id=req.order_id,
        split="live",
        config="cascade",
    )

    try:
        result = await run_cascade(task, mock=req.mock)
        # Broadcast to SSE listeners
        await _broadcast_event("task_completed", result.model_dump())
        return result
    except Exception as e:
        logger.error("Error processing task %s: %s", task_id, e)
        raise HTTPException(status_code=500, detail=f"Routing error: {e}") from e


@app.get("/tasks/{task_id}")
def get_task_details(task_id: str):
    """Retrieve full history and verifier records for a given task ID."""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.get("/stats")
def get_dashboard_stats(split: str | None = None):
    """Retrieve aggregate statistics: total tasks, cost, latency, tier distribution, and savings."""
    settings = get_settings()
    stats = get_stats(split=split)
    ultra_pricing = settings.get_pricing_for_tier("ultra")

    # Calculate Ultra-only baseline comparison
    # Ultra cost estimate: average tokens (~250) * ultra price per token * total tasks
    total_tasks = stats.get("total_tasks", 0)
    actual_cost = stats.get("total_cost", 0.0)

    # Ultra baseline cost if all tasks had run directly on Ultra
    avg_tokens_per_task = 250
    ultra_baseline_cost = total_tasks * (
        (avg_tokens_per_task * 0.6 * (ultra_pricing.price_in / 1_000_000.0))
        + (avg_tokens_per_task * 0.4 * (ultra_pricing.price_out / 1_000_000.0))
    )

    savings_dollars = max(0.0, ultra_baseline_cost - actual_cost)
    savings_pct = (
        (savings_dollars / ultra_baseline_cost * 100.0)
        if ultra_baseline_cost > 0
        else 0.0
    )

    return {
        "stats": stats,
        "ultra_baseline_cost": round(ultra_baseline_cost, 6),
        "actual_cost": round(actual_cost, 6),
        "savings_dollars": round(savings_dollars, 6),
        "savings_percentage": round(savings_pct, 1),
    }


@app.post("/benchmark/replay")
async def replay_demo_tickets(mock: bool = True):
    """Replay 3 canonical demo tickets to illustrate routing and escalation in the dashboard."""
    samples = [
        # Sample A: Lands on Nano
        {
            "task_id": "demo_A_nano",
            "ticket_text": "Where is my order ORD-1001? I haven't received any tracking updates.",
            "order_id": "ORD-1001",
        },
        # Sample B: Fails Nano (rules check), escalates to Super
        {
            "task_id": "demo_B_super",
            "ticket_text": "I want to return order ORD-1002. Delivered on Aug 20 (58 days ago). I want a full refund to my credit card.",
            "order_id": "ORD-1002",
        },
        # Sample C: Hard multi-issue climbs to Ultra
        {
            "task_id": "demo_C_ultra",
            "ticket_text": "You charged me twice for order ORD-1006 ($50.99 each)! Also, when will this coffee set ship?",
            "order_id": "ORD-1006",
        },
    ]

    results = []
    for s in samples:
        t = Task(
            task_id=s["task_id"],
            ticket_text=s["ticket_text"],
            order_id=s["order_id"],
            split="live",
            config="cascade",
        )
        res = await run_cascade(t, mock=mock)
        results.append(res)
        await _broadcast_event("task_completed", res.model_dump())

    return {"replayed": len(results), "results": results}


@app.post("/reset")
def reset_database():
    """Clear demo database records."""
    reset_db()
    return {"status": "cleared"}


@app.get("/stream")
async def sse_event_stream(request: Request):
    """Server-Sent Events endpoint streaming live task and call events."""
    queue: asyncio.Queue = asyncio.Queue()
    _sse_subscribers.append(queue)

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            while True:
                if await request.is_disconnected():
                    break
                message = await queue.get()
                yield f"data: {message}\n\n"
        finally:
            if queue in _sse_subscribers:
                _sse_subscribers.remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
