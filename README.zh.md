# DocPilot 🧾 — 付款前 AI 审票 + 一键催收（可盈利的 SaaS）

**付款前，让 AI 先审一遍票。** 把供应商发票丢给 DocPilot：AI 抽取字段 → 7 类风险检查
（重复票/价税不平/税率错/缺字段/大额整数/未来日期/超期未付）→ 未付票一键生成
**PayPal 催收链接**。小老板与代账会计的防错款、防重复付款利器。

按**生产级、可盈利的 SaaS** 标准打造，而非一次性原型：在线 Web 控制台、订阅套餐 + 用量
计量、透明（非黑箱）规则引擎（每条发现都标注依据的字段/数字）、双大脑提取（无 LLM Key
时自动回落确定性离线引擎）。

- 🔗 **在线演示**：见 [`DEPLOY.md`](DEPLOY.md)，Render 一键部署，或本地 `python server.py`
- 🧪 **自测**：`python eval.py` → **43/43 断言全过**，零依赖
- 🧠 **双大脑**：LLM 提取（OpenAI 兼容）+ 永远可用的离线引擎兜底
- 💳 **货币化内建**：Free / Pro / Business 套餐、用量配额门、催收能力付费墙
- 🔒 **隐私优先**：离线引擎 100% 本地运行，发票数据不出本机（除非你主动启用 LLM）

## 快速开始

无需 `pip install` 任何东西，Python 3.8+ 标准库即可：

```bash
python -m docpilot.cli examples/messy_invoice.txt                 # 审一张杂乱发票
python -m docpilot.cli examples/structured_invoices.txt --structured --plan pro  # 多票（含重复+不平）
python -m docpilot.cli examples/structured_invoices.txt --structured --plan pro --html report.html
python eval.py                                                    # 离线自测（43 断言）
python server.py                                                  # 启动 Web 控制台 → http://localhost:8000
```

## 智能体闭环（每步可解释、可复现）

```
PERCEIVE 按 --- 切分单票 → EXTRACT 双大脑抽取 → GATE 配额门（货币化层）
→ AUDIT 7 类风控 + 评分 → ENRICH 未付票生成催收链接（付费能力）
→ EXPLAIN 大白话结论 → RECEIPT 结构化回执（含证据）
```

## 货币化（本项目的核心命题）

| 套餐 | 价格 | 配额 | 解锁 |
|---|---|---|---|
| **Free** | $0 | 25 张/月 | 离线审票、7 类规则、报告带水印 |
| **Pro** | $19/月 | 500 张/月（超量 $0.02/张） | LLM 提取、一键催收、去水印 |
| **Business** | $49/月 | 无限 | REST API、5 席位、自定义规则、优先支持 |

完整蓝图见 [`MONETIZATION.md`](MONETIZATION.md)，商业与技术结构见
[`EXEC_BRIEF.md`](EXEC_BRIEF.md)，架构决策见 [`DESIGN.md`](DESIGN.md)。

## 配置（均可选）

| 环境变量 | 用途 | 不配时的行为 |
|---|---|---|
| `DOCPILOT_LLM_BASE` / `DOCPILOT_LLM_KEY` / `DOCPILOT_LLM_MODEL` | 启用 LLM 提取 | 用确定性离线引擎，功能完整 |
| `PAYPAL_BASE` / `PAYPAL_CLIENT_ID` / `PAYPAL_SECRET` / `PAYPAL_MERCHANT` | 真实 PayPal 催收 | 催收链接降级为演示深链（明确标注 `mode=demo`） |
| `PORT` | Web 端口 | `8000` |

DocPilot 从不伪装：无 PayPal 凭据时给出明确标注的演示链接，而不是假装收款成功。

## 项目结构

```
docpilot/            # 核心包（extract/audit/paylink/pricing/metering/agent/receipts/web/cli）
eval.py              # 43 断言离线自测
server.py            # Web 入口（读 PORT）
examples/            # 示例输入
render.yaml          # 一键云部署
DESIGN.md / MONETIZATION.md / EXEC_BRIEF.md / DEPLOY.md
```

## License

MIT © Zhiyilang — 见 [`LICENSE`](LICENSE)。
