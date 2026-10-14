"""DocPilot — 付款前 AI 审票 + 一键催收的货币化 SaaS。

模块：
  extract   提取大脑（离线正则 / LLM / 结构化 KEY:VALUE）
  audit     风控引擎（7 类检查 + 评分，透明可解释）
  paylink   PayPal 催收/收款链接（沙盒 Orders API / 演示降级）
  pricing   订阅计划（Monetization 单一事实来源）
  metering  用量计量 + 配额闸门
  agent     智能体闭环（PERCEIVE→EXTRACT→GATE→AUDIT→ENRICH→EXPLAIN→RECEIPT）
  receipts  文本 / HTML 回执渲染
  web       stdlib Web 控制台（落地页/定价/仪表盘，读 PORT）
  cli       命令行入口
"""

from .agent import DocPilot
from .audit import audit
from .extract import OfflineExtractor, LLMExtractor, get_extractor, parse_structured
from .metering import Meter
from .paylink import make_paylink, PayPalClient
from .pricing import PLANS, get_plan

__version__ = "1.0.0"
__all__ = [
    "DocPilot", "audit", "OfflineExtractor", "LLMExtractor", "get_extractor",
    "parse_structured", "Meter", "make_paylink", "PayPalClient", "PLANS", "get_plan",
]
