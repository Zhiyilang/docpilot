# DocPilot — Design & Architecture

## Guiding principles

1. **Explainability over magic.** Every risk finding cites the exact fields/numbers it used
   (`evidence`). A user can verify the machine. This is what separates a tool people trust
   with money from a demo.
2. **Never fabricate.** If a field can't be extracted, it stays empty and the audit flags it
   (`MISSING_FIELD`) — it is never guessed. Enforced by a negative test in `eval.py`.
3. **Graceful degradation (dual brain).** LLM extraction is powerful but needs a key and a
   network. The deterministic offline engine is always available, so the product is fully
   functional out of the box and reproducible in tests/CI.
4. **Honest integrations.** With no PayPal credentials, collections degrade to a clearly
   labeled demo deep-link (`mode=demo`) rather than pretending a charge succeeded.
5. **Zero dependencies.** Pure Python standard library — trivial to deploy anywhere, no
   supply-chain surface, fast CI.

## Module map

| Module | Responsibility | Key idea |
|---|---|---|
| `extract.py` | text → structured `Invoice` | `OfflineExtractor` (regex/heuristics), `LLMExtractor` (OpenAI-compatible), `parse_structured` (KEY:VALUE) |
| `audit.py` | `Invoice[]` → findings + score | 7 transparent rules, evidence-citing, deterministic |
| `paylink.py` | unpaid invoice → collection link | PayPal Orders API, demo fallback |
| `pricing.py` | plan definitions | single source of truth for monetization |
| `metering.py` | usage → quota decision | executable upgrade gate |
| `agent.py` | orchestration | `DocPilot.weave()` runs the full loop |
| `receipts.py` | result → text/HTML | f-string based (avoids the `%`-format CSS trap) |
| `web.py` | HTTP console | stdlib `ThreadingHTTPServer`, reads `PORT` |
| `cli.py` | command line | `python -m docpilot.cli` |

## The extraction brain — why regex + guards

Offline extraction of invoices is deceptively tricky. Three concrete pitfalls the engine
guards against (each covered by a test):

- **`Subtotal` contains the substring `total`** → a naive "find the total label" would grab
  the subtotal. Guard: skip subtotal lines when matching `total`.
- **`VAT (13%): 1742.00`** → grabbing "the first number after the label" yields `13`, not the
  amount. Guard: take the value *after the last colon*; if no colon, take the last
  money-like number on the line.
- **`unpaid` contains the substring `paid`** → status would flip to paid. Guard: test
  unpaid keywords before paid.

These are exactly the kinds of bugs that make "AI extraction" demos silently wrong. DocPilot
treats them as first-class test cases.

## The audit rules

Per-invoice: missing fields, `subtotal + tax ≠ total` (HIGH), implied-vs-declared tax rate,
round thousand amounts, future dates, stale unpaid (>180d). Cross-invoice: duplicate
detection on (vendor + invoice_no) or (vendor + amount + date) — the double-payment guard,
highest priority. Score = `min(100, 30×HIGH + 10×CAUTION)`; band = HIGH/MEDIUM/LOW.

## The monetization gate

`Meter.check_quota` is the single enforcement point. The agent calls it before processing;
the collections link is generated only for plans with `paylinks=True`. This keeps the
paywall logic in one testable place rather than scattered through the UI.

## Data model

A single `Invoice` dataclass is produced by *all* extractors (offline, LLM, structured), so
audit/paylink/receipts never branch on the data's origin. `Invoice.source` and `.confidence`
are carried through for provenance in receipts.

## Testing philosophy

`eval.py` is an offline, deterministic, dependency-free assertion suite — runnable in CI and
by judges in one command. It covers extraction correctness (including the three guard bugs),
audit rule firing, quota gating (Free block / Pro overage), paylink modes, the full agent
loop with the paywall, a **negative test** (empty invoice → no fabrication, no paylink), and
HTML receipt rendering (proving the `%`-format CSS trap is avoided).

## From demo to production

In-memory metering demonstrates the logic; production would persist tenants/usage in a DB
behind an atomic counter, and swap demo deep-links for live PayPal capture. These concerns
are already isolated (metering, paylink) so the swap is localized.
