from __future__ import annotations

import argparse
from pathlib import Path

from .config import PROJECT_ROOT, load_config, resolve_project_path
from .dates import now_in_timezone
from .layouts import build_morning_receipt, build_movie_receipt
from .movies import pick_movie
from .weather import get_daily_forecast


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate local HTML receipt previews.")
    parser.add_argument("--config", help="Path to config JSON.")
    parser.add_argument("--all", action="store_true", help="Generate all previews.")
    parser.add_argument("--morning", action="store_true", help="Generate the morning preview.")
    parser.add_argument("--movie", action="store_true", help="Generate the movie preview.")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "previews"), help="Preview output directory.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)
    now = now_in_timezone(config.get("timezone", "America/New_York"))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    render_all = args.all or not (args.morning or args.movie)

    if render_all or args.morning:
        image_path = resolve_project_path(config, config.get("morning", {}).get("image_path"))
        forecast = get_daily_forecast(config, now)
        morning = build_morning_receipt(config, now, forecast, image_path)
        (output_dir / "morning.html").write_text(morning.to_html(), encoding="utf-8")
        print(output_dir / "morning.html")

    if render_all or args.movie:
        movie = pick_movie(config, now.date())
        nightly = build_movie_receipt(config, now, movie)
        (output_dir / "nightly_movie.html").write_text(nightly.to_html(), encoding="utf-8")
        print(output_dir / "nightly_movie.html")


if __name__ == "__main__":
    main()
