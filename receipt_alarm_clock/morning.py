from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config, resolve_project_path
from .dates import now_in_timezone
from .layouts import build_morning_receipt
from .printer import print_receipt
from .weather import get_daily_forecast


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print or preview the morning receipt.")
    parser.add_argument("--config", help="Path to config JSON.")
    parser.add_argument("--print", action="store_true", dest="do_print", help="Send to the receipt printer.")
    parser.add_argument("--preview", action="store_true", help="Print a terminal preview.")
    parser.add_argument("--html", help="Write an HTML preview to this path.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)
    now = now_in_timezone(config.get("timezone", "America/New_York"))
    image_path = resolve_project_path(config, config.get("morning", {}).get("image_path"))
    forecast = get_daily_forecast(config, now)
    receipt = build_morning_receipt(config, now, forecast, image_path)

    if args.html:
        output = Path(args.html)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(receipt.to_html(), encoding="utf-8")

    if args.do_print:
        print_receipt(receipt, config)
    else:
        print(receipt.to_text())


if __name__ == "__main__":
    main()
