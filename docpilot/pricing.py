"""DocPilot 订阅计划（Monetization Engine 的单一事实来源）。

计费模型：按月订阅 + 用量封顶 + 超量按张计费。
- FREE  ：引流档，给"付款前扫一张票"的轻需求，制造升级诱因（报告带水印、无催收链接）。
- PRO   ：主力档，代账会计/小老板，按处理单据数封顶，含 LLM 提取与一键催收。
- BUSINESS：团队档，无限单据 + API + 多席位 + 自定义规则，走"席位 + 用量"混合。

真实收款用 PayPal（沙盒验证 → 生产 Key）；此处仅定义配额与升级门槛，不碰支付通道细节。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Plan:
    key: str
    name: str
    price_usd_month: float
    docs_per_month: int | None      # None = 无限
    overage_per_doc: float          # 超量单价（美元/张）
    features: tuple
    paylinks: bool                  # 是否解锁"一键催收/PayPal 收款链接"
    watermark: bool                 # 报告是否带水印
    api_access: bool


PLANS: dict[str, Plan] = {
    "free": Plan(
        key="free",
        name="Free",
        price_usd_month=0.0,
        docs_per_month=25,
        overage_per_doc=0.0,
        features=("离线审票引擎", "7 类风险检查", "基础 HTML 报告"),
        paylinks=False,
        watermark=True,
        api_access=False,
    ),
    "pro": Plan(
        key="pro",
        name="Pro",
        price_usd_month=19.0,
        docs_per_month=500,
        overage_per_doc=0.02,
        features=("LLM 智能提取", "无限风险规则", "一键催收链接", "去水印报告", "邮件支持"),
        paylinks=True,
        watermark=False,
        api_access=False,
    ),
    "business": Plan(
        key="business",
        name="Business",
        price_usd_month=49.0,
        docs_per_month=None,          # 无限
        overage_per_doc=0.0,
        features=("PRO 全部功能", "REST API", "5 席位", "自定义风控规则", "优先支持"),
        paylinks=True,
        watermark=False,
        api_access=True,
    ),
}

DEFAULT_PLAN = "free"


def get_plan(key: str) -> Plan:
    return PLANS.get((key or "").lower(), PLANS[DEFAULT_PLAN])
