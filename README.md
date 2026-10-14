# DocPilot 🧾 — AI invoice auditing & one-click collections, as a real SaaS

**Catch the costly mistakes *before* you pay.** Paste a supplier invoice; DocPilot
extracts the fields with AI, runs 7 risk checks (duplicate invoices, subtotal+tax≠total,
wrong tax rate, missing fields, round amounts, future dates, stale unpaid), and turns
every unpaid invoice into a one-click **PayPal collection link**.

Built as a **production-minded, monetizable SaaS** — not a throwaway prototype: a live
web console, subscription plans with usage metering, a transparent (non-black-box)
rules engine where every finding cites the exact fields it relied on, and a dual-brain
extractor that degrades gracefully when no LLM key is present.

- 🔗 **Live demo:** see `DEPLOY.md` — one-click Render Blueprint, or `python server.py`
- 🧪 **Self-test:** `python eval.py` → **43/43 assertions pass**, zero dependencies
- 🧠 **Dual brain:** LLM extraction (OpenAI-compatible) with a deterministic offline engine as always-on fallback
- 💳 **Monetization in the product:** Free / Pro / Business plans, usage quota gate, paywalled collections
- 🔒 **Privacy-first:** the offline engine runs 100% locally — invoice data never leaves the machine unless you opt into the LLM path

---

## Why this exists

Small-business owners and bookkeepers lose real money to two failure modes that software
rarely catches:

1. **Paying a duplicate invoice** (same vendor + invoice number, or same amount + date) — pure double payment.
2. **Paying an invoice whose numbers don't add up** (subtotal + tax ≠ total) — a sign of error or tampering.

Most "AI invoice tools" are demos. DocPilot is engineered like a product: it explains
every finding, never fabricates a field it couldn't extract, meters usage against a plan,
and gates the highest-value action (collections) behind the paid tier.

---

## The agent loop (every step is explainable & reproducible)

```
PERCEIVE  →  split input into single invoices (--- separated)
EXTRACT   →  dual brain: LLM (optional) / deterministic offline engine → structured Invoice
GATE      →  usage-quota check against the tenant's plan (monetization layer)
AUDIT     →  7 risk rules → findings + 0–100 risk score + band
ENRICH    →  unpaid invoices → PayPal collection link (paid-tier capability)
EXPLAIN   →  plain-language conclusion + advice
RECEIPT   →  structured receipt, each finding carrying its evidence
```

Every HIGH-severity finding ships with an `evidence` string, e.g.
`subtotal=8600.0 tax=1118.0 total=9800.0` — so a human can verify the machine's claim.

---

## Quick start

No `pip install` anything — pure Python 3.8+ standard library.

```bash
# Audit the bundled messy invoice (free tier)
python -m docpilot.cli examples/messy_invoice.txt

# Audit structured multi-invoice input (plants a duplicate + a total mismatch)
python -m docpilot.cli examples/structured_invoices.txt --structured --plan pro

# Produce an HTML report
python -m docpilot.cli examples/structured_invoices.txt --structured --plan pro --html report.html

# Run the offline self-test suite
python eval.py

# Launch the web console (landing + pricing + dashboard)
python server.py         # → http://localhost:8000
```

Expected output for the structured sample:

```
风险评分：60/100    等级：HIGH
审查 3 张发票，发现 2 个高风险、0 个待留意项，风险等级 HIGH。
🔴 [HIGH] 价税合计不平 — 宏图办公用品 · INV-2026-0901
    📎 证据：subtotal=8600.0 tax=1118.0 total=9800.0
🔴 [HIGH] 疑似重复发票（双付风险） — 宏图办公用品 · INV-2026-0901
    📎 证据：dup_key=('宏图办公用品', 'inv-2026-0901')
```

---

## As a library

```python
from docpilot import DocPilot, Meter

dp = DocPilot(meter=Meter(), tenant="acme-bookkeeping")
result = dp.weave(open("invoices.txt", encoding="utf-8").read(),
                  structured=True, plan_key="pro")
print(result["score"], result["band"])
for f in result["findings"]:
    print(f["severity"], f["code"], f["detail"], "|", f["evidence"])
```

---

## Monetization (the point of the exercise)

DocPilot is designed so the code maps directly onto a revenue engine:

| Plan | Price | Quota | Unlocks |
|---|---|---|---|
| **Free** | $0 | 25 docs/mo | offline audit, 7 risk rules, watermarked report |
| **Pro** | $19/mo | 500 docs/mo (+$0.02/doc overage) | LLM extraction, one-click collections, no watermark |
| **Business** | $49/mo | unlimited | REST API, 5 seats, custom rules, priority support |

- **Quota gate** (`metering.py`) turns a plan into an executable upgrade wall — Free users
  who exceed 25 docs are blocked with an upgrade prompt; Pro users are charged overage.
- **Paywalled action** — the one-click PayPal collection link (the single highest-value
  feature) is a Pro/Business capability, shown as an upgrade CTA on Free.
- Full breakdown in [`MONETIZATION.md`](MONETIZATION.md).

---

## Configuration (all optional)

| Env var | Purpose | Default behavior if unset |
|---|---|---|
| `DOCPILOT_LLM_BASE` / `DOCPILOT_LLM_KEY` / `DOCPILOT_LLM_MODEL` | enable LLM extraction | deterministic offline engine (fully functional) |
| `PAYPAL_BASE` / `PAYPAL_CLIENT_ID` / `PAYPAL_SECRET` / `PAYPAL_MERCHANT` | real PayPal Orders API collections | collection links degrade to demo deep-links (honestly labeled `mode=demo`) |
| `PORT` | web server port | `8000` |

DocPilot never pretends: with no PayPal credentials it emits a clearly-marked demo link
rather than faking a successful charge.

---

## Project layout

```
docpilot/
├── docpilot/
│   ├── extract.py     # dual-brain extraction (offline regex / LLM / structured KEY:VALUE)
│   ├── audit.py       # 7 risk rules + scoring (transparent, evidence-citing)
│   ├── paylink.py     # PayPal collections (Orders API / demo fallback)
│   ├── pricing.py     # subscription plans (single source of truth)
│   ├── metering.py    # usage metering + quota gate
│   ├── agent.py       # the DocPilot.weave() agent loop
│   ├── receipts.py    # text + HTML report rendering
│   ├── web.py         # stdlib web console (landing/pricing/dashboard)
│   └── cli.py         # command-line entry
├── eval.py            # 43-assertion offline self-test suite
├── server.py          # web entry point (reads PORT)
├── examples/          # sample inputs
├── render.yaml        # one-click cloud deploy (Render Blueprint)
├── DESIGN.md          # architecture & design decisions
├── MONETIZATION.md    # monetization engine blueprint
├── EXEC_BRIEF.md      # executive briefing
└── DEPLOY.md          # deployment guide
```

## License

MIT © Zhiyilang — see [`LICENSE`](LICENSE).
