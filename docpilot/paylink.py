"""DocPilot 收款链接大脑：给"未付发票"一键生成 PayPal 催收/收款链接。

两档能力（与整体双大脑哲学一致）：
- 有 PayPal 沙盒/生产凭据（PAYPAL_CLIENT_ID / PAYPAL_SECRET / PAYPAL_BASE）：
  走真实 Orders API（OAuth2 client_credentials → v2/checkout/orders），返回 approve 链接。
- 无凭据或调用失败：降级为 PayPal.me 演示深链，明确标注 mode=demo，绝不假装已收款。

这把"审票"和"催收"闭环起来，也是产品货币化的直接证据（客户为此付费）。
"""

from __future__ import annotations

import base64
import json
import os
import urllib.request
from typing import Optional

from .models import Invoice


class PayPalClient:
    def __init__(self, base: str, client_id: str, secret: str,
                 merchant: str = "docpilot", timeout: int = 30) -> None:
        self.base = base.rstrip("/")
        self.client_id = client_id
        self.secret = secret
        self.merchant = merchant
        self.timeout = timeout
        self._token: Optional[str] = None

    def _token_value(self) -> str:
        if self._token:
            return self._token
        cred = base64.b64encode(f"{self.client_id}:{self.secret}".encode()).decode()
        req = urllib.request.Request(
            f"{self.base}/v1/oauth2/token", data=b"grant_type=client_credentials",
            method="POST",
            headers={"Authorization": f"Basic {cred}",
                     "Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            self._token = json.loads(resp.read().decode())["access_token"]
        return self._token

    def create_order(self, amount: float, currency: str, reference: str) -> Optional[str]:
        """创建 PayPal 订单，返回 approve 链接；失败返回 None（由上层降级）。"""
        body = json.dumps({
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {"currency_code": currency, "value": f"{amount:.2f}"},
                "description": f"DocPilot collection for {reference}"[:127],
            }],
        }).encode()
        req = urllib.request.Request(
            f"{self.base}/v2/checkout/orders", data=body, method="POST",
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self._token_value()}"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            order = json.loads(resp.read().decode())
        for link in order.get("links", []):
            if link.get("rel") == "approve":
                return link.get("href")
        return None


def _demo_link(inv: Invoice, merchant: str) -> str:
    amt = f"{inv.total:.2f}" if inv.total is not None else "0.00"
    cur = (inv.currency or "USD").upper()
    return f"https://www.paypal.com/pay/{merchant}/{amt}{cur}"


def make_paylink(inv: Invoice) -> dict:
    """为一张发票生成催收链接。返回 {mode, url, note, gated}。

    gated=True 表示该能力属于付费档（Free 用户在 UI 里看到升级引导）。
    """
    if inv.total is None or inv.total <= 0:
        return {"mode": "none", "url": "", "note": "缺少有效总额，无法生成收款链接。", "gated": False}

    base = os.environ.get("PAYPAL_BASE", "https://api-m.sandbox.paypal.com")
    cid = os.environ.get("PAYPAL_CLIENT_ID")
    sec = os.environ.get("PAYPAL_SECRET")
    merchant = os.environ.get("PAYPAL_MERCHANT", "docpilot")

    if cid and sec:
        try:
            client = PayPalClient(base, cid, sec, merchant)
            url = client.create_order(inv.total, inv.currency or "USD",
                                      inv.invoice_no or inv.label())
            if url:
                return {"mode": "live-sandbox", "url": url,
                        "note": "已通过 PayPal Orders API 创建待收款订单（沙盒）。", "gated": True}
        except Exception as exc:  # 网络/鉴权失败 → 降级，不假装成功
            return {"mode": "demo", "url": _demo_link(inv, merchant),
                    "note": f"PayPal API 调用失败（{exc.__class__.__name__}），已降级为演示链接。",
                    "gated": True}

    return {"mode": "demo", "url": _demo_link(inv, merchant),
            "note": "未配置 PayPal 凭据，生成演示催收链接（配置沙盒 Key 后可一键真实收款）。",
            "gated": True}
