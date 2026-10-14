"""DocPilot 命令行入口。

用法：
  python -m docpilot.cli examples/messy_invoice.txt
  python -m docpilot.cli examples/structured_invoices.txt --structured --plan pro
  python -m docpilot.cli examples/structured_invoices.txt --structured --html report.html
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from .agent import DocPilot
from .metering import Meter
from .receipts import html_receipt, text_receipt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="docpilot", description="付款前 AI 审票 + 一键催收")
    ap.add_argument("path", nargs="?", help="发票文本文件（--- 分隔多张）")
    ap.add_argument("--structured", action="store_true", help="按 KEY:VALUE 结构化格式解析")
    ap.add_argument("--plan", default="free", choices=["free", "pro", "business"])
    ap.add_argument("--tenant", default="cli")
    ap.add_argument("--html", metavar="OUT", help="同时输出 HTML 报告")
    ap.add_argument("--demo", action="store_true", help="无文件时跑内置示例")
    args = ap.parse_args(argv)

    if args.path:
        with open(args.path, encoding="utf-8") as f:
            text = f.read()
    elif args.demo:
        import os
        sample = "structured_invoices.txt" if args.structured else "messy_invoice.txt"
        p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "examples", sample)
        with open(p, encoding="utf-8") as f:
            text = f.read()
    else:
        ap.error("请提供发票文件路径，或用 --demo 跑内置示例")

    dp = DocPilot(meter=Meter(), tenant=args.tenant)
    result = dp.weave(text, structured=args.structured, plan_key=args.plan, today=date.today())

    print(text_receipt(result))
    if args.html:
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(html_receipt(result, watermark=(args.plan == "free")))
        print(f"\nHTML 报告已写入：{args.html}")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
