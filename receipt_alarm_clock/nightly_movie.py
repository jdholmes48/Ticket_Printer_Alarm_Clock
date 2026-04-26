from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .dates import now_in_timezone
from .layouts import build_movie_receipt
from .movies import pick_movie
from .printer import print_receipt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print or preview the nightly movie receipt.")
    parser.add_argument("--config", help="Path to config JSON.")
    parser.add_argument("--print", action="store_true", dest="do_print", help="Send to the receipt printer.")
    parser.add_argument("--preview", action="store_true", help="Print a terminal preview.")
    parser.add_argument("--html", help="Write an HTML preview to this path.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)
    now = now_in_timezone(config.get("timezone", "America/New_York"))
    movie = pick_movie(config, now.date())
    receipt = build_movie_receipt(config, now, movie)

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
