# Deploying DocPilot

DocPilot is a zero-dependency Python web service. It reads the `PORT` environment variable
and binds `0.0.0.0`, so it runs on any PaaS with no code changes.

## Option A — One-click Render Blueprint (recommended for the live demo)

1. Push this repo to GitHub (it already contains `render.yaml`).
2. In [Render](https://render.com): **New → Blueprint**, connect the repo.
3. Render reads `render.yaml` and creates the `docpilot` web service automatically.
4. (Optional) In the service's **Environment** tab, fill the `sync: false` secrets to enable
   the LLM extractor and real PayPal collections:
   - `DOCPILOT_LLM_BASE`, `DOCPILOT_LLM_KEY`, `DOCPILOT_LLM_MODEL`
   - `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET` (sandbox), `PAYPAL_MERCHANT`
5. Health check is wired to `/healthz`; the app works fully offline even with no secrets set.

## Option B — Run locally

```bash
python server.py                 # → http://localhost:8000
PORT=8080 python server.py       # custom port
```

Then open the landing page, click **审票工作台**, paste an invoice, and audit.

## Option C — Any Docker/PaaS

`startCommand: python server.py`, `buildCommand: pip install -r requirements.txt`
(requirements.txt is intentionally empty — stdlib only). Set `PORT` if the platform doesn't
inject it.

## Enable real PayPal collections (sandbox)

1. Create a PayPal app at https://developer.paypal.com (Sandbox).
2. Set `PAYPAL_BASE=https://api-m.sandbox.paypal.com`, `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET`.
3. Re-audit an unpaid invoice — the collection link now comes from a real Orders API
   `approve` URL (`mode=live-sandbox`) instead of a demo deep-link.

## Enable LLM extraction

Set `DOCPILOT_LLM_BASE` (any OpenAI-compatible `/chat/completions` endpoint),
`DOCPILOT_LLM_KEY`, and optionally `DOCPILOT_LLM_MODEL`. With these present, extraction uses
the LLM; on any failure it falls back to the deterministic offline engine automatically.
