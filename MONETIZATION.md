# DocPilot — Monetization Engine Blueprint

> Galuxium deliverable: how DocPilot is architected to **capture market value and produce
> recurring revenue**. This document is the "financial architecture" of the product; the
> matching code lives in `docpilot/pricing.py` (single source of truth) and
> `docpilot/metering.py` (executable quota gate).

## 1. Value proposition → willingness to pay

DocPilot sits on a **loss-avoidance** value prop, which converts better than "nice to have":

- **Prevents double payments** — the single most embarrassing and measurable AP error.
- **Prevents paying wrong/tampered invoices** — arithmetic mismatches before money leaves.
- **Turns receivables into cash faster** — one-click collection links chase unpaid invoices.

A bookkeeper who catches even one duplicate invoice per month has covered the Pro
subscription many times over. That asymmetry (small recurring fee vs. large avoided loss)
is why SMBs and accounting firms pay for this category.

## 2. Pricing model

**Monthly subscription + usage cap + metered overage**, three tiers:

| | Free | Pro | Business |
|---|---|---|---|
| Price | $0 | **$19/mo** | **$49/mo** |
| Docs / month | 25 | 500 (+$0.02/doc overage) | Unlimited |
| Offline audit + 7 rules | ✅ | ✅ | ✅ |
| LLM extraction | ❌ | ✅ | ✅ |
| One-click collections | ❌ | ✅ | ✅ |
| Watermark on report | ✅ (upgrade hook) | ❌ | ❌ |
| REST API | ❌ | ❌ | ✅ |
| Seats | 1 | 1 | 5 |
| Custom risk rules | ❌ | ❌ | ✅ |

### Why this shape

- **Free tier as acquisition + upgrade engine.** 25 docs/mo covers "scan a bill before I
  pay it" — enough to feel the value, capped to create the upgrade trigger. The watermark
  and the paywalled collections link are the two persistent, non-annoying upgrade hooks.
- **Pro as the revenue core.** Priced against the avoided-loss value, not against cost.
  Overage pricing ($0.02/doc) keeps heavy users monetized without a hard cliff.
- **Business for teams & integration.** Seat-based + API access targets accounting firms
  and ERPs — higher ACV, lower churn, expansion revenue.

## 3. Where monetization lives in the code

- **`pricing.py`** — every plan is data (price, quota, overage, feature flags, watermark,
  paylink/API gates). Change pricing without touching logic.
- **`metering.py`** — `Meter.check_quota(tenant, n)` returns a `QuotaDecision`:
  - Free + over limit → **blocked** + upgrade hint (drives conversion).
  - Pro + over limit → **allowed** + overage count (drives metered revenue).
  - Business → always allowed.
- **`agent.py`** — the collections link is generated only when `plan.paylinks` is true;
  otherwise the invoice row carries an upgrade CTA. The paywall is enforced at the point of
  highest value, not arbitrarily.

## 4. Payment & collection rails

- **Customer → DocPilot (subscriptions):** PayPal Subscriptions/billing against the sandbox
  first (`PAYPAL_*` env), then production keys. The same PayPal integration powers the
  product's collections feature, so one integration serves both revenue directions.
- **DocPilot's users → their customers (collections):** PayPal Orders API creates a real
  capture-intent order per unpaid invoice; with no credentials the app degrades to a clearly
  labeled demo deep-link rather than faking success.

## 5. Unit economics (illustrative)

| Input | Value |
|---|---|
| Pro ARPU | $19/mo |
| Variable cost / doc (LLM extraction, amortized) | ~$0.005 |
| Overage revenue / heavy Pro user | ~$0.02/doc |
| Target gross margin | >90% (software + metered LLM calls) |

Break-even on operating costs is reached at a low hundreds of Pro subscribers — realistic
for a focused loss-avoidance tool with a clear ICP (independent bookkeepers, micro-SMBs,
AP clerks).

## 6. Growth loop

1. Free user audits invoices → hits value (catches a real issue).
2. Hits the 25-doc cap **or** wants the collections link → upgrade prompt at the exact
   moment of need.
3. Pro user chases receivables via collection links → sees cash come in → retention.
4. Business/API tier captures firms that standardize on it → expansion.

## 7. From demo to production (honest roadmap)

The current build demonstrates the **full monetization logic** (plans, quota gate, paywall,
collection-link generation) with in-memory metering and sandbox payments. To operate at
scale: persist tenants/usage/subscriptions in a database, move metering behind an atomic
counter, swap the demo deep-link for live PayPal capture, and add Stripe as an alternative
rail. The architecture already separates these concerns so the swap is localized.
