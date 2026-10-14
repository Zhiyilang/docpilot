"""DocPilot 用量计量与配额门槛（Monetization Engine 的执行层）。

把"订阅计划"变成"可执行的升级闸门"：每次审查前问 check_quota，
超额的要么按 overage 计费、要么提示升级。此处用进程内计数演示逻辑；
生产实现应落到数据库（见 DESIGN.md 的"从演示到生产"一节）。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .pricing import get_plan, Plan


@dataclass
class TenantUsage:
    docs_this_month: int = 0
    plan_key: str = "free"


@dataclass
class QuotaDecision:
    allowed: bool
    remaining: int | None       # None = 无限
    overage_docs: int           # 本次将产生的超量张数
    upgrade_hint: str           # 给前端的升级引导文案


class Meter:
    """进程内租户计量器（演示级）。"""

    def __init__(self) -> None:
        self._usage: dict[str, TenantUsage] = {}

    def usage(self, tenant: str) -> TenantUsage:
        return self._usage.setdefault(tenant, TenantUsage())

    def set_plan(self, tenant: str, plan_key: str) -> None:
        self.usage(tenant).plan_key = plan_key

    def record(self, tenant: str, docs: int) -> None:
        self.usage(tenant).docs_this_month += max(0, docs)

    def check_quota(self, tenant: str, incoming_docs: int = 1) -> QuotaDecision:
        u = self.usage(tenant)
        plan: Plan = get_plan(u.plan_key)
        if plan.docs_per_month is None:                      # 无限套餐
            return QuotaDecision(True, None, 0, "")
        remaining = max(0, plan.docs_per_month - u.docs_this_month)
        if incoming_docs <= remaining:
            return QuotaDecision(True, remaining - incoming_docs, 0, "")
        # 超额：PRO 有 overage 价则放行并计超量；FREE 无 overage → 挡住并引导升级
        overage = incoming_docs - remaining
        if plan.overage_per_doc > 0:
            return QuotaDecision(
                True, 0, overage,
                f"已超出 {plan.name} 月度配额，本次 {overage} 张将按 "
                f"${plan.overage_per_doc:.2f}/张 计费。",
            )
        return QuotaDecision(
            False, 0, overage,
            f"免费档每月限 {plan.docs_per_month} 张，本月已用 {u.docs_this_month} 张。"
            f"升级 Pro（${PLANS_PRO_PRICE}/月，{PLANS_PRO_DOCS} 张）即可继续并解锁一键催收。",
        )


# 供升级文案引用，避免在 Meter 里反向 import 造成噪音
from .pricing import PLANS as _PLANS  # noqa: E402
PLANS_PRO_PRICE = _PLANS["pro"].price_usd_month
PLANS_PRO_DOCS = _PLANS["pro"].docs_per_month
