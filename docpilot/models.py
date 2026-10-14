"""DocPilot 数据模型（零依赖，纯标准库）。

一张发票的结构化表示 + 一条风控发现 + 一份审查报告。
字段同时服务两个大脑：LLM 提取器与离线正则提取器产出的都是同一份 Invoice，
因此上层（风控/收款/回执）完全不需要关心"这条数据是谁抽出来的"。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Invoice:
    raw: str
    vendor: str = ""
    invoice_no: str = ""
    date_str: str = ""
    due_str: str = ""
    currency: str = "CNY"
    subtotal: Optional[float] = None
    tax_rate: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    status: str = ""
    index: int = 0
    # 溯源：这条记录由哪个大脑抽出、置信度如何（便于回执里给出证据）
    source: str = "offline"        # offline | llm
    confidence: float = 1.0

    def label(self) -> str:
        no = self.invoice_no or f"#{self.index}"
        return f"{self.vendor or '未知供应商'} · {no}"


@dataclass
class Finding:
    severity: str          # HIGH / CAUTION / INFO
    code: str
    label: str
    invoice: str
    detail: str
    advice: str
    evidence: str = ""     # 依据哪些字段/数字得出（可解释性）


@dataclass
class Report:
    invoices: list = field(default_factory=list)
    findings: list = field(default_factory=list)
    score: int = 0
    band: str = "LOW"
    summary: str = ""
    brain: str = "offline"          # 本次审查实际使用的提取大脑
    created_on: Optional[date] = None
