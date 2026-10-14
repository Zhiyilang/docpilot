"""DocPilot 回执渲染：把 weave() 结果渲染成文本 / HTML 报告。

用 f-string 拼接（不用 % 运算符），从根上规避 CSS 里 width:100% 撞 % 格式化的老坑。
Free 档报告带水印（ Monetization：水印是升级诱因之一）。
"""

from __future__ import annotations

from .pricing import get_plan

_SEV_EMOJI = {"HIGH": "🔴", "CAUTION": "🟡", "INFO": "🔵"}


def text_receipt(result: dict) -> str:
    if not result.get("ok"):
        return f"DocPilot\n{'=' * 40}\n{result.get('explain') or result.get('error', '无法处理')}\n"
    out = [
        "DocPilot · 付款前审票回执",
        "=" * 46,
        f"大脑：{result['brain']}    套餐：{result['plan']}    处理：{result['docs']} 张",
        f"风险评分：{result['score']}/100    等级：{result['band']}",
        "-" * 46,
        result["summary"],
    ]
    if result["findings"]:
        out.append("")
        for f in result["findings"]:
            emoji = _SEV_EMOJI.get(f["severity"], "•")
            out.append(f"{emoji} [{f['severity']}] {f['label']} — {f['invoice']}")
            out.append(f"    {f['detail']}")
            out.append(f"    👉 {f['advice']}")
            if f.get("evidence"):
                out.append(f"    📎 证据：{f['evidence']}")
    links = [r for r in result["invoices"] if r.get("paylink", {}).get("url")]
    if links:
        out.append("")
        out.append("催收链接：")
        for r in links:
            out.append(f"  - {r['vendor']} {r['invoice_no']}：{r['paylink']['url']}"
                       f"（{r['paylink']['mode']}）")
    out.append("")
    out.append(result["explain"])
    out.append("=" * 46)
    return "\n".join(out)


def html_receipt(result: dict, watermark: bool = False) -> str:
    if not result.get("ok"):
        return (f"<html><body style=\"font-family:sans-serif;padding:2rem\">"
                f"<h2>DocPilot</h2><p>{result.get('explain') or result.get('error', '')}</p>"
                f"</body></html>")

    band_color = {"HIGH": "#dc2626", "MEDIUM": "#d97706", "LOW": "#16a34a"}.get(result["band"], "#333")
    findings_html = ""
    for f in result["findings"]:
        color = {"HIGH": "#dc2626", "CAUTION": "#d97706", "INFO": "#2563eb"}.get(f["severity"], "#333")
        ev = f"<div class='ev'>📎 证据：{f['evidence']}</div>" if f.get("evidence") else ""
        findings_html += (
            f"<div class='finding' style='border-left-color:{color}'>"
            f"<div class='fhead'><span class='sev' style='background:{color}'>{f['severity']}</span>"
            f"<strong>{f['label']}</strong> <span class='inv'>{f['invoice']}</span></div>"
            f"<div class='detail'>{f['detail']}</div>"
            f"<div class='advice'>👉 {f['advice']}</div>{ev}</div>"
        )
    if not findings_html:
        findings_html = "<p class='clean'>✅ 未发现明显风险。</p>"

    links_html = ""
    for r in result["invoices"]:
        pl = r.get("paylink", {})
        if pl.get("url"):
            links_html += (f"<li>{r['vendor']} {r['invoice_no']} — "
                           f"<a href='{pl['url']}' target='_blank'>{pl['url']}</a> "
                           f"<span class='mode'>({pl['mode']})</span></li>")
    links_block = f"<h3>💸 催收链接</h3><ul>{links_html}</ul>" if links_html else ""

    wm = ("<div class='watermark'>DocPilot Free · "
          "<a href='#pricing'>升级 Pro 去水印 + 解锁一键催收</a></div>") if watermark else ""

    return f"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DocPilot 审票报告</title>
<style>
 body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#f6f7f9;color:#1f2937;margin:0;padding:2rem}}
 .card{{max-width:760px;margin:0 auto;background:#fff;border-radius:14px;box-shadow:0 6px 24px rgba(0,0,0,.08);padding:1.6rem 1.8rem;position:relative}}
 h1{{font-size:1.4rem;margin:0 0 .2rem}} .meta{{color:#6b7280;font-size:.85rem;margin-bottom:1rem}}
 .score{{display:flex;align-items:center;gap:1rem;margin:1rem 0}}
 .badge{{color:#fff;padding:.3rem .8rem;border-radius:999px;font-weight:600;background:{band_color}}}
 .summary{{background:#f3f4f6;padding:.7rem 1rem;border-radius:8px;margin:.6rem 0 1rem}}
 .finding{{border-left:4px solid #ccc;padding:.6rem .9rem;margin:.6rem 0;background:#fafafa;border-radius:0 8px 8px 0}}
 .fhead{{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap}} .sev{{color:#fff;font-size:.72rem;padding:.1rem .5rem;border-radius:6px}}
 .inv{{color:#6b7280;font-size:.85rem}} .detail{{margin:.35rem 0}} .advice{{color:#065f46;font-size:.9rem}}
 .ev{{color:#6b7280;font-size:.8rem;margin-top:.3rem;font-family:monospace}}
 .clean{{color:#16a34a;font-weight:600}} ul{{line-height:1.7}} .mode{{color:#9ca3af;font-size:.8rem}}
 .explain{{white-space:pre-wrap;background:#eff6ff;border:1px solid #bfdbfe;padding:.8rem 1rem;border-radius:8px;margin-top:1rem}}
 .watermark{{position:absolute;top:12px;right:16px;font-size:.72rem;color:#9ca3af}}
 a{{color:#2563eb}}
</style></head><body>
<div class='card'>{wm}
<h1>🧾 DocPilot 审票报告</h1>
<div class='meta'>大脑：{result['brain']} · 套餐：{result['plan']} · 处理 {result['docs']} 张 · 租户 {result['tenant']}</div>
<div class='score'><span class='badge'>{result['band']}</span>
<span>风险评分 <strong>{result['score']}</strong>/100</span></div>
<div class='summary'>{result['summary']}</div>
{findings_html}
{links_block}
<div class='explain'>{result['explain']}</div>
</div></body></html>"""
