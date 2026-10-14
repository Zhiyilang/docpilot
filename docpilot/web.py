"""DocPilot Web 控制台（零依赖，stdlib http.server）。

路由：
  GET  /          落地页（Hero + 能力 + 定价 + CTA）
  GET  /app       审票仪表盘（粘贴发票 → 一键审票）
  POST /audit     处理并渲染报告（含催收链接）
  GET  /healthz   健康检查（部署探针）

读 PORT 环境变量，绑 0.0.0.0。CSS 用独立常量（非 f-string），从根上避开花括号陷阱。
"""

from __future__ import annotations

import os
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from .agent import DocPilot
from .metering import Meter
from .pricing import PLANS
from .receipts import html_receipt

_CSS = """
:root{--bg:#0f1222;--card:#1a1e38;--ink:#e8eaf6;--muted:#9aa0c3;--acc:#6ea8fe;
--acc2:#7ee787;--warn:#f0a868;--bad:#ff7b72;--line:#2a2f52}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
background:var(--bg);color:var(--ink);line-height:1.6}
.wrap{max-width:920px;margin:0 auto;padding:2rem 1.2rem}
a{color:var(--acc);text-decoration:none}
nav{display:flex;justify-content:space-between;align-items:center;padding:1rem 1.2rem;
border-bottom:1px solid var(--line)}
nav .logo{font-weight:700;font-size:1.15rem}
nav .logo span{color:var(--acc)}
.btn{display:inline-block;background:var(--acc);color:#0b1020;font-weight:600;
padding:.6rem 1.1rem;border-radius:10px;border:0;cursor:pointer}
.btn.ghost{background:transparent;color:var(--acc);border:1px solid var(--acc)}
.hero{padding:3rem 0 2rem;text-align:center}
.hero h1{font-size:2.1rem;margin:.2rem 0}
.hero p{color:var(--muted);font-size:1.05rem;max-width:640px;margin:.6rem auto 1.4rem}
.pill{display:inline-block;background:var(--card);border:1px solid var(--line);
color:var(--acc2);padding:.25rem .7rem;border-radius:999px;font-size:.8rem;margin-bottom:.8rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem;margin:1.6rem 0}
.feature{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:1.1rem}
.feature h3{margin:.2rem 0 .4rem;font-size:1.05rem}
.feature p{color:var(--muted);font-size:.9rem;margin:0}
.plans{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem;margin:1.4rem 0}
.plan{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:1.3rem;position:relative}
.plan.pop{border-color:var(--acc)}
.plan .tag{position:absolute;top:-12px;right:16px;background:var(--acc);color:#0b1020;
font-size:.72rem;font-weight:700;padding:.15rem .6rem;border-radius:999px}
.plan h3{margin:.2rem 0}
.plan .price{font-size:1.8rem;font-weight:700;margin:.3rem 0}
.plan .price small{font-size:.85rem;color:var(--muted);font-weight:400}
.plan ul{list-style:none;padding:0;margin:.6rem 0 1rem;color:var(--muted);font-size:.9rem}
.plan li{padding:.2rem 0}
.plan li::before{content:"✓ ";color:var(--acc2)}
textarea{width:100%;min-height:220px;background:#0b0e1c;color:var(--ink);border:1px solid var(--line);
border-radius:12px;padding:1rem;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.9rem}
select,input[type=text]{background:#0b0e1c;color:var(--ink);border:1px solid var(--line);
border-radius:8px;padding:.5rem .7rem}
.row{display:flex;gap:1rem;flex-wrap:wrap;align-items:center;margin:1rem 0}
label{color:var(--muted);font-size:.9rem}
footer{color:var(--muted);font-size:.8rem;text-align:center;padding:2rem 0;border-top:1px solid var(--line);margin-top:2rem}
.note{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.8rem 1rem;color:var(--muted);font-size:.88rem;margin:1rem 0}
"""


def _nav(active: str) -> str:
    def cls(k):
        return " style='color:var(--acc2)'" if k == active else ""
    return (f"<nav><div class='logo'>🧾 Doc<span>Pilot</span></div>"
            f"<div><a href='/'{cls('home')}>首页</a> &nbsp; "
            f"<a href='/app'{cls('app')}>审票工作台</a> &nbsp; "
            f"<a href='#pricing'{cls('pricing')}>定价</a></div></nav>")


def _plans_html() -> str:
    order = ["free", "pro", "business"]
    names = {"free": "Free", "pro": "Pro", "business": "Business"}
    prices = {"free": "¥0", "pro": "$19", "business": "$49"}
    units = {"free": "/月", "pro": "/月", "business": "/月"}
    caps = {"free": "每月 25 张", "pro": "每月 500 张（超量 $0.02/张）", "business": "无限张"}
    out = []
    for k in order:
        p = PLANS[k]
        pop = " pop" if k == "pro" else ""
        tag = "<div class='tag'>最受欢迎</div>" if k == "pro" else ""
        feats = "".join(f"<li>{f}</li>" for f in p.features)
        out.append(
            f"<div class='plan{pop}'>{tag}<h3>{names[k]}</h3>"
            f"<div class='price'>{prices[k]}<small>{units[k]}</small></div>"
            f"<div style='color:var(--muted);font-size:.85rem'>{caps[k]}</div>"
            f"<ul>{feats}</ul>"
            f"<a class='btn{' ghost' if k != 'pro' else ''}' href='/app'>开始使用</a></div>"
        )
    return "<div class='plans'>" + "".join(out) + "</div>"


def _landing() -> str:
    return f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DocPilot · 付款前 AI 审票 + 一键催收</title>
<style>{_CSS}</style></head><body>
{_nav("home")}
<div class="wrap">
<div class="hero">
<div class="pill">🤖 AI 提取 · 🔒 数据可控 · 💸 一键催收</div>
<h1>付款前，让 AI 先审一遍票</h1>
<p>把供应商发票丢给 DocPilot：AI 抽取字段 → 7 类风险检查（重复票/价税不平/税率错…）→
未付票一键生成 PayPal 催收链接。小老板和代账会计的防错款、防重复付款利器。</p>
<a class="btn" href="/app">免费试审（每月 25 张）</a>
&nbsp;<a class="btn ghost" href="#pricing">查看定价</a>
</div>

<div class="grid">
<div class="feature"><h3>🧠 双大脑提取</h3><p>LLM 智能抽取杂乱/扫描件文本；无 Key 时自动回落到确定性离线引擎，永远可用。</p></div>
<div class="feature"><h3>🛡️ 7 类风险检查</h3><p>重复发票（双付风险）、价税合计不平、税率不符、缺字段、大额整数、未来日期、超期未付。</p></div>
<div class="feature"><h3>🔎 透明可解释</h3><p>每条发现都标注依据哪些字段/数字，可复现、可核对，不是黑箱。</p></div>
<div class="feature"><h3>💸 一键催收</h3><p>未付发票秒变 PayPal 收款链接（沙盒 Orders API / 演示降级），直接发给客户。</p></div>
</div>

<h2 id="pricing" style="margin-top:2.4rem">定价</h2>
<p style="color:var(--muted)">按月订阅 + 用量封顶 + 超量按张计费。免费档先体验，付费档解锁 LLM 提取与一键催收。</p>
{_plans_html()}

<div class="note">🔒 隐私：发票是最敏感的商业数据。DocPilot 的离线引擎 100% 本地运行、不联网、不留日志；
启用 LLM 提取时才按需调用你配置的端点。</div>
</div>
<footer>DocPilot · MIT · 生产级货币化 SaaS 示例 ·
<a href="https://github.com/Zhiyilang/docpilot">GitHub</a></footer>
</body></html>"""


def _app_page(prefill: str = "", plan: str = "free", structured: bool = False,
              result_html: str = "", banner: str = "") -> str:
    checked = " checked" if structured else ""
    plan_opts = "".join(
        f"<option value='{k}'{' selected' if k == plan else ''}>{n}</option>"
        for k, n in (("free", "Free（免费档）"), ("pro", "Pro（$19/月）"), ("business", "Business（$49/月）"))
    )
    result_block = f"<div class='note' style='border-color:var(--warn)'>{banner}</div>" if banner else ""
    result_block += result_html
    return f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>审票工作台 · DocPilot</title>
<style>{_CSS}
textarea{{min-height:200px}}
.result{{margin-top:1.4rem}}
</style></head><body>
{_nav("app")}
<div class="wrap">
<h1>审票工作台</h1>
<p style="color:var(--muted)">粘贴一张或多张发票（多张用单独一行 <code>---</code> 分隔），或勾选结构化模式贴 KEY:VALUE。</p>
<form method="post" action="/audit">
<textarea name="text" placeholder="在此粘贴发票文本…">{prefill}</textarea>
<div class="row">
<label>套餐</label><select name="plan">{plan_opts}</select>
<label style="margin-left:1rem"><input type="checkbox" name="structured" value="1"{checked}> 结构化 KEY:VALUE 输入</label>
<label>租户</label><input type="text" name="tenant" value="web-demo" style="width:120px">
<button class="btn" type="submit">🔍 一键审票</button>
</div>
</form>
<div class="result">{result_block}</div>
</div>
<footer>DocPilot · MIT · <a href="/">返回首页</a></footer>
</body></html>"""


class _Handler(BaseHTTPRequestHandler):
    meter = Meter()

    def log_message(self, *a):  # 静音访问日志
        pass

    def _send(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self._send(_landing())
        elif path == "/app":
            self._send(_app_page())
        elif path == "/healthz":
            self._send("{\"ok\":true,\"service\":\"docpilot\"}", 200)
        else:
            self._send(_landing(), 404)

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/audit":
            self._send(_landing(), 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        text = (form.get("text", [""])[0] or "").strip()
        plan = form.get("plan", ["free"])[0]
        structured = form.get("structured", [""])[0] == "1"
        tenant = form.get("tenant", ["web-demo"])[0] or "web-demo"

        if not text:
            self._send(_app_page(banner="请输入至少一张发票文本。"))
            return

        dp = DocPilot(meter=self.meter, tenant=tenant)
        result = dp.weave(text, structured=structured, plan_key=plan, today=date.today())

        if not result.get("ok"):
            hint = result.get("quota", {}).get("upgrade_hint") or result.get("error", "处理失败")
            self._send(_app_page(prefill=text, plan=plan, structured=structured,
                                 banner=hint))
            return

        receipt = html_receipt(result, watermark=(plan == "free"))
        self._send(_app_page(prefill=text, plan=plan, structured=structured,
                             result_html=f"<div class='result'>{receipt}</div>"))


def serve(port: int | None = None) -> None:
    port = port or int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), _Handler)
    print(f"DocPilot 控制台已启动：http://0.0.0.0:{port}  (Ctrl+C 停止)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
