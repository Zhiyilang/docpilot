# DocPilot — Galuxium Nexus V2 提交指南（逐字段可粘贴）

> 真实入口：**Devpost `galuxium-nexus-v2`**（平台 ID `devpost29411`）
> 提交截止：**2026-10-31 07:30 EDT = 北京时间 10-31 19:30**
> 奖池：**名义 $14,644**（1st Nexus Sovereign $6,768 / 2nd $4,884 / 3rd $2,992）——⚠️ **2026-10-17 官方页复核：各奖项 Procurement Mandate 逐字说明奖金以 "live enterprise infrastructure keys, production API credits, and active licenses" 发放，名义 cash 实为 credits/licenses，按含实物口径不计现金池**；组织度黄旗：评委区仍在 "Looking for judges!"
> 资格：**面向所有年龄段 / 全球开放**（官方 Devpost 规则页明文覆盖"students only"标签；排除标准例外地区，中国可参加）
> 硬性交付：**公开 GitHub 仓库 + 实时部署 Demo + 2–5 分钟演示视频**——三者缺一即不完整

---

## 一、六项交付物 ↔ 仓库文件对照（评委逐项核对）

| Galuxium 要求 | DocPilot 对应物 | 状态 |
|---|---|---|
| **1. Production-Ready Deployment（实时 Demo）** | `server.py`（读 `PORT`、绑 `0.0.0.0 的 stdlib 生产级 Web 控制台）+ `render.yaml`（一键 Blueprint 部署） | ✅ 代码就绪，**需用户侧在 Render 点一次部署** |
| **2. Verifiable Infrastructure（公开仓库）** | `github.com/Zhiyilang/docpilot`（MIT，含 `README.md` 架构/依赖/本地复现说明 + 完整提交历史） | ✅ 已公开 |
| **3. Operational MVP（可用原型）** | Web 控制台 + CLI + library API 三入口，端到端跑通"贴发票→抽字段→7 项风险检查→评分→催收链接" | ✅ `eval.py` 43 断言覆盖 |
| **4. Executive Briefing（高管简报）** | `EXEC_BRIEF.md`（问题量化 / 方案 / 差异化 / 商业技术结构 / 诉求） | ✅ |
| **5. Fiscal Architecture（货币化引擎）** | `MONETIZATION.md`（定价模型 + 代码位置 `pricing.py`/`metering.py` + 支付通道 + 单位经济 + 增长飞轮） | ✅ |
| **6. Technical Keynote（2–5 分钟视频）** | **`docpilot_demo_long.mp4` 已由产线生成：2 分 24 秒**（终端风、真命令真输出：定价卡→干净票 0 分→问题票 2 HIGH 带证据+催收墙→HTML 报告→43 断言→收尾；脚本 `_videotool/scripts/docpilot_video_long.json`） | ✅ 成片就绪，**需用户侧上传 YouTube** |

---

## 二、Devpost 提交表逐字段（直接复制）

**Submission title**
```
DocPilot — AI invoice auditing that stops double payments and collects what's owed
```

**Tagline（一句话）**
```
Pre-payment AI invoice audit + one-click PayPal collections for small business.
```

**Demo video URL**（录完上传 YouTube 后填）
```
https://youtu.be/<你的视频ID>     # 上传 docpilot/docpilot_demo_long.mp4（2:24，已生成，勿再录屏）
```

**Demo URL（实时部署，Render 部署后填）**
```
https://docpilot.onrender.com      # 或你的 Render 实际域名
```

**Code repository URL**
```
https://github.com/Zhiyilang/docpilot
```

**Description（长描述，可直接粘贴）**
```
DocPilot is a live, monetizable SaaS that stops small businesses from paying
duplicate or incorrect invoices — and turns unpaid invoices into one-click PayPal
collection links.

Paste an invoice → DocPilot extracts the fields (dual-brain: LLM with a deterministic
offline fallback), runs 7 transparent risk checks (duplicate detection, subtotal/tax
mismatch, round-number anomalies, missing fields, payee/amount inconsistencies,
vendor collision, tax miscalculation), scores risk 0–100, and for unpaid invoices
generates a one-click PayPal collection link. Every finding cites the exact numbers
it relied on, so the output is verifiable, not a black box — a negative test in CI
proves it never fabricates fields.

Why it fits Galuxium: this is not a prototype. The monetization engine is implemented
in code — three tiers (Free $0 / Pro $19 / Business $49) with a usage cap and metered
overage, an executable quota gate (metering.py), and a paywall placed at the point of
highest value (collections). The same PayPal integration serves both subscription
revenue and the product's own collections feature.

Architecture: zero third-party dependencies (Python stdlib only), dual-brain
extraction with graceful degradation, stdlib web console reading PORT, one-click
Render Blueprint deploy, and a 43-assertion offline test suite wired into GitHub
Actions CI. Full executive briefing in EXEC_BRIEF.md and fiscal architecture in
MONETIZATION.md.
```

**Built with / 技术栈标签**（Galuxium 偏向 AI/企业，勾选）
```
Python · Artificial Intelligence · Web · SaaS · FinTech
```

---

## 三、评分维度对照（Galuxium 评委会看这六项）

| 评分维度 | DocPilot 的对应证据（在提交里点出来） |
|---|---|
| **Technical Architecture** | 零依赖 stdlib、双大脑抽取、7 项透明规则引擎、`/healthz` 探针、`render.yaml` 一键部署；`DESIGN.md` 详述 |
| **Enterprise Governance** | `pricing.py` 单一事实源 + `metering.py` 配额门 + 环境变量管理（`.env.example`）；不编造的 CI 负测试 |
| **Product Innovation** | "审计→收款"闭环：不仅发现错误，还把未付票变成真金白银的催收链接 |
| **Monetization** | `MONETIZATION.md` 完整蓝图 + 代码级实现（计划/配额门/付费墙/集合链接）；单位经济 >90% 毛利 |
| **UI/UX** | Web 控制台三入口、风险徽章、证据展开、定价表即产品；`DEMO_SCRIPT.md` 0:20 段专门讲"定价即产品" |
| **Keynote Pitch & Demo** | `DEMO_SCRIPT.md` 2–5 分钟分镜，展示真实运行 + 货币化即产品 + 工程自测 |

---

## 四、用户侧动作清单（3 步，约 40 分钟）

1. **Render 部署**（~10 分钟）：见 `DEPLOY.md` —— 连 GitHub 仓 → New Web Service → `Build: pip install -r requirements.txt`（实际零依赖，可留空）→ `Start: python server.py` → 设 `PORT` 环境变量 → 部署。拿到 `https://docpilot.onrender.com`。
2. **传视频**（~5 分钟）：`docpilot/docpilot_demo_long.mp4`（2 分 24 秒，已由终端录屏产线生成，含全部官方要求的能力展示：审票/重复/证据/催收/HTML 报告/43 断言）→ 传 YouTube（可"不列出"）→ 拿链接。**无需自己录屏**；`DEMO_SCRIPT.md` 仅作内容对照。
3. **填表提交**（~5 分钟）：把上面"二"里的字段粘贴进 Devpost 提交表 → 勾选技术栈标签 → 提交。

> AI 侧已就绪：仓库已公开、所有交付文档齐全、代码自测 43/43 通过。你只需完成"部署 + 录制 + 点提交"这三件必须是真人的动作。
