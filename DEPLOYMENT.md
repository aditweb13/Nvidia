# Deployment Guide: Cascade

This guide describes how to run and deploy the **Cascade** cost-aware model router for local testing, containerized environments, and public demo hosting (Render, Hugging Face Spaces, or Railway).

---

## 1. Local Development

### Prerequisites
- Python 3.11+
- Git
- NVIDIA NIM / Token Factory API key in `.env`

### Quick Start

1. **Activate virtual environment & install dependencies:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

2. **Verify environment and API connectivity:**
   ```bash
   python scripts/hello.py
   ```

3. **Start the FastAPI Backend:**
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   Interactive Swagger docs available at: `http://localhost:8000/docs`.

4. **Start the Streamlit Live Dashboard:**
   ```bash
   streamlit run ui/dashboard.py
   ```
   Live dashboard available at: `http://localhost:8501`.

---

## 2. Docker & Container Deployment

Cascade includes a turnkey `Dockerfile` and `docker-compose.yml`.

### Build & Run with Docker Compose
```bash
# 1. Ensure your .env file is configured
# 2. Build and start containers in the background:
docker-compose up --build -d

# 3. Check logs:
docker-compose logs -f
```
- Streamlit Dashboard: `http://localhost:8501`
- FastAPI REST API: `http://localhost:8000`

---

## 3. Public Demo Hosting (Render / Railway / Hugging Face Spaces)

### Security & Rate-Limiting Safeguards
When hosting a public demo, prevent credit exhaustion and denial-of-service:
1. **Input Length Limits:** `app/main.py` enforces a strict 2,000-character ceiling on incoming ticket payloads via Pydantic (`max_length=2000`).
2. **In-Memory Rate Limiting:** Built into `app/main.py` to prevent rapid automated spam.
3. **Mock Mode Fallback:** The dashboard includes an offline toggle (`--mock` or UI toggle) allowing users to inspect the pipeline with pre-recorded responses if credit limits are reached or during high-traffic spikes.
4. **Zero Key Exposure:** API keys are injected solely through environment variables (`TOKEN_FACTORY_API_KEY`) and are never rendered to logs or frontend responses.

### Deploying to Render / Railway
1. Fork or push the repository to GitHub.
2. In the Render / Railway Dashboard, select **New Web Service** and link your repository.
3. **Environment:** Choose **Docker** (using the root `Dockerfile`).
4. **Environment Variables:**
   - `TOKEN_FACTORY_BASE_URL`: `https://integrate.api.nvidia.com/v1`
   - `TOKEN_FACTORY_API_KEY`: `<your_api_key>`
   - `MODEL_NANO`: `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`
   - `MODEL_SUPER`: `nvidia/nemotron-3-super-120b-a12b`
   - `MODEL_ULTRA`: `nvidia/nemotron-3-ultra-550b-a55b`
   - `PRICE_NANO_IN`: `0.20`
   - `PRICE_NANO_OUT`: `0.20`
   - `PRICE_SUPER_IN`: `0.75`
   - `PRICE_SUPER_OUT`: `0.75`
   - `PRICE_ULTRA_IN`: `3.00`
   - `PRICE_ULTRA_OUT`: `3.00`
5. **Port:** Expose port `8501` for the Streamlit web interface.

### Deploying to Hugging Face Spaces
1. Create a new Space with the **Streamlit** SDK.
2. Under **Settings > Variables and secrets**, add `TOKEN_FACTORY_API_KEY` as a secret.
3. Push repository code to the Hugging Face Git remote.

---

## 4. Health Checks & Verification

You can verify API and backend health at any time:
```bash
curl http://localhost:8000/health
# Response: {"status":"healthy","database":"connected","subscribers":0}
```
