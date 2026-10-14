# DocPilot — Executive Briefing

**One-liner:** DocPilot is an AI-powered invoice-auditing and collections SaaS that stops
small businesses from paying duplicate or incorrect invoices — and turns unpaid invoices
into one-click PayPal collection links.

## The problem (quantified)

Accounts-payable errors are a quiet, recurring leak for small businesses and the
bookkeepers who serve them:

- **Duplicate payments** (same vendor + invoice number, or same amount + date) are among
  the most common and most embarrassing AP errors — and they are directly detectable.
- **Invoices that don't add up** (subtotal + tax ≠ total) frequently signal an error or
  tampering, yet are almost never checked by hand before payment.

Manual checking is slow and inconsistent; existing "AI invoice" tools are largely demos
that neither explain their findings nor connect auditing to the money actually moving.

## The solution

Paste an invoice → DocPilot **extracts** the fields (dual-brain: LLM with a deterministic
offline fallback), runs **7 transparent risk checks**, scores risk 0–100, and for unpaid
invoices generates a **one-click PayPal collection link**. Every finding cites the exact
numbers it relied on, so the output is verifiable, not a black box.

## Why it can win (differentiation)

| Typical hackathon project | DocPilot |
|---|---|
| Prototype that runs on the developer's machine | **Live web console**, one-click cloud deploy |
| Black-box "AI says risky" | **Explainable rules**, each finding with evidence |
| Fabricates fields when unsure | **Never fabricates** — negative test enforced in CI |
| Monetization as an afterthought | **Monetization in the architecture** (plans + quota gate + paywall) |
| "Coming soon" payments | **Working PayPal collections** (sandbox Orders API) |

## Business & technical structure

- **ICP:** independent bookkeepers, micro-SMBs, AP clerks — anyone who pays supplier
  invoices and feels duplicate/wrong payments.
- **Revenue:** Free → Pro ($19/mo) → Business ($49/mo), usage-capped with metered overage;
  collections link paywalled to paid tiers. See `MONETIZATION.md`.
- **Architecture:** zero-dependency Python (stdlib only), dual-brain extraction, transparent
  rules engine, stdlib web console reading `PORT`, one-click Render Blueprint deploy.
- **Quality bar:** `python eval.py` runs a **43-assertion** offline suite (including a
  negative test proving it won't fabricate), wired into GitHub Actions CI across Python
  3.8/3.10/3.12.

## Traction & status

- Functional MVP live (web console + CLI + library API).
- Offline engine fully self-tested and deterministic; LLM and PayPal layers are opt-in and
  degrade gracefully.
- Production path documented in `DEPLOY.md`.

## The ask

DocPilot is built to be a real, revenue-generating SaaS — the monetization engine, quota
gate, and payment rails are implemented, not slideware. We're seeking the Galuxium platform
to take it from a validated build to real users and recurring revenue.
