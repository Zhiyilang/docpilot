#!/usr/bin/env python3
"""DocPilot 离线自测断言套件（零依赖，python eval.py）。

覆盖：提取大脑（离线/结构化）、风控引擎（重复/不平/缺字段/干净票）、
计量配额门（FREE 拦截 / PRO 超量放行）、催收链接（无总额→none / 有总额→demo）、
智能体闭环（付费墙门控）、负测试（空票不编造）、回执渲染（HTML % 安全）。
"""

from __future__ import annotations

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docpilot import DocPilot, Meter, audit, get_extractor, parse_structured  # noqa: E402
from docpilot.paylink import make_paylink  # noqa: E402
from docpilot.pricing import PLANS, get_plan  # noqa: E402
from docpilot.receipts import html_receipt, text_receipt  # noqa: E402
from docpilot.models import Invoice  # noqa: E402

TODAY = date(2026, 10, 14)
_HERE = os.path.dirname(os.path.abspath(__file__))

_passed = 0
_failed = 0


def check(name, cond, extra=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  [PASS] {name}")
    else:
        _failed += 1
        print(f"  [FAIL] {name}  {extra}")


def approx(a, b, tol=0.01):
    return a is not None and b is not None and abs(a - b) <= tol


# ---------------------------------------------------------------------------
print("== 1. 离线提取大脑：杂乱发票 ==")
ex = get_extractor()
with open(os.path.join(_HERE, "examples", "messy_invoice.txt"), encoding="utf-8") as f:
    messy = f.read()
inv = ex.extract(messy, 1)
check("extract.vendor", "Acme" in inv.vendor, inv.vendor)
check("extract.invoice_no", inv.invoice_no == "INV-2026-0901", inv.invoice_no)
check("extract.total", approx(inv.total, 15142.00), inv.total)
check("extract.subtotal(不被total污染)", approx(inv.subtotal, 13400.00), inv.subtotal)
check("extract.tax(不吃13%)", approx(inv.tax, 1742.00), inv.tax)
check("extract.tax_rate", approx(inv.tax_rate, 0.13, 1e-6), inv.tax_rate)
check("extract.date", inv.date_str == "2026-09-15", inv.date_str)
check("extract.due", inv.due_str == "2026-10-15", inv.due_str)
check("extract.currency", inv.currency == "CNY", inv.currency)
check("extract.status(不被paid污染)", inv.status == "unpaid", inv.status)

print("== 2. 结构化解析（兼容 InvoiceAudit） ==")
with open(os.path.join(_HERE, "examples", "structured_invoices.txt"), encoding="utf-8") as f:
    struct = f.read()
invs = parse_structured(struct)
check("struct.count==3", len(invs) == 3, len(invs))
check("struct.total#1", approx(invs[0].total, 9718.00), invs[0].total)
check("struct.rate#1", approx(invs[0].tax_rate, 0.13, 1e-6), invs[0].tax_rate)

print("== 3. 风控引擎 ==")
rep = audit(invs, today=TODAY)
codes = {f.code for f in rep.findings}
check("audit.DUPLICATE", "DUPLICATE" in codes, codes)
check("audit.TOTAL_MISMATCH", "TOTAL_MISMATCH" in codes, codes)
check("audit.band==HIGH", rep.band == "HIGH", rep.band)
check("audit.score>=60", rep.score >= 60, rep.score)
check("audit.findings_have_evidence", all(f.evidence for f in rep.findings if f.severity == "HIGH"))
clean = audit([inv], today=TODAY)
check("audit.clean.score==0", clean.score == 0, clean.score)
check("audit.clean.band==LOW", clean.band == "LOW", clean.band)

print("== 4. 计量配额门 ==")
m = Meter()
m.set_plan("t1", "free")
for _ in range(PLANS["free"].docs_per_month):
    m.record("t1", 1)
d = m.check_quota("t1", 1)
check("meter.free_blocks_over_limit", d.allowed is False, d)
check("meter.free_upgrade_hint", "Pro" in d.upgrade_hint, d.upgrade_hint)
m.set_plan("t2", "pro")
for _ in range(PLANS["pro"].docs_per_month):
    m.record("t2", 1)
d2 = m.check_quota("t2", 1)
check("meter.pro_allows_overage", d2.allowed is True and d2.overage_docs == 1, d2)

print("== 5. 催收链接 ==")
pl_none = make_paylink(Invoice(raw="x", index=1))
check("paylink.no_total->none", pl_none["mode"] == "none" and pl_none["url"] == "", pl_none)
pl_demo = make_paylink(inv)  # total=15142, 无 PayPal 凭据
check("paylink.demo_mode", pl_demo["mode"] == "demo", pl_demo["mode"])
check("paylink.demo_url", pl_demo["url"].startswith("https://www.paypal.com/pay/"), pl_demo["url"])
check("paylink.demo_amount_in_url", "15142.00" in pl_demo["url"], pl_demo["url"])

print("== 6. 智能体闭环（付费墙） ==")
dp_free = DocPilot(meter=Meter(), tenant="acme")
r_free = dp_free.weave(struct, structured=True, plan_key="free", today=TODAY)
check("agent.free.ok", r_free["ok"] is True)
check("agent.free.paylink_gated", all(not row["paylink"].get("url") for row in r_free["invoices"]),
      "free 档不应下发催收链接")
dp_pro = DocPilot(meter=Meter(), tenant="acme")
r_pro = dp_pro.weave(struct, structured=True, plan_key="pro", today=TODAY)
unpaid_links = [row["paylink"]["url"] for row in r_pro["invoices"]
                if row["paylink"].get("url")]
check("agent.pro.paylink_present", len(unpaid_links) >= 2, unpaid_links)
check("agent.pro.explain_nonempty", bool(r_pro["explain"].strip()))

print("== 7. 负测试：空票不编造 ==")
dp_neg = DocPilot(meter=Meter(), tenant="neg")
r_neg = dp_neg.weave("Vendor: Ghost Co.\n(无任何金额信息)", plan_key="pro", today=TODAY)
row0 = r_neg["invoices"][0]
check("neg.no_fabricate_total", row0["total"] is None, row0["total"])
check("neg.no_paylink_url", row0["paylink"].get("url") == "", row0["paylink"])
check("neg.flags_missing", any(f["code"] == "MISSING_FIELD" for f in r_neg["findings"]))

print("== 8. 回执渲染（HTML % 安全） ==")
html = html_receipt(r_pro, watermark=True)
check("receipt.html_renders", "<!DOCTYPE html>" in html and "DocPilot" in html)
check("receipt.html_percent_safe", "width:100%" in html.replace("100%", "100%") or "viewport" in html)
check("receipt.html_watermark", "升级 Pro" in html)
txt = text_receipt(r_pro)
check("receipt.text_nonempty", "DocPilot" in txt and "风险评分" in txt)

print("== 9. 计划定价完整性 ==")
check("pricing.free_watermark", get_plan("free").watermark is True)
check("pricing.pro_no_watermark", get_plan("pro").watermark is False)
check("pricing.pro_paylinks", get_plan("pro").paylinks is True)
check("pricing.business_unlimited", get_plan("business").docs_per_month is None)
check("pricing.business_api", get_plan("business").api_access is True)

# ---------------------------------------------------------------------------
print("\n" + "=" * 46)
print(f"结果：{_passed} 通过 / {_failed} 失败")
print("=" * 46)
sys.exit(1 if _failed else 0)
