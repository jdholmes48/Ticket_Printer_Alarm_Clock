from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .movies import Movie
from .renderer import Receipt
from .weather import WeatherForecast


def build_morning_receipt(
    config: Dict[str, Any],
    current_time: datetime,
    forecast: WeatherForecast,
    image_path: Optional[Path] = None,
) -> Receipt:
    columns = int(config["receipt"].get("columns", 42))
    receipt = Receipt(title="Morning Receipt", columns=columns, image_path=image_path)
    receipt.center(config["morning"].get("greeting", "Good morning."))
    receipt.center(current_time.strftime("%A, %B %-d, %Y"))
    receipt.divider()
    receipt.center("TODAY'S FORECAST")
    receipt.label("Where", forecast.location)
    receipt.label("Sky", forecast.summary)
    receipt.label("High", _degrees(forecast.high_f))
    receipt.label("Low", _degrees(forecast.low_f))
    receipt.label("Rain", _percent(forecast.precipitation_probability))
    receipt.divider()
    receipt.text("A small receipt for a large and capable day.")
    receipt.center()
    receipt.center("You have time. Start gently.")
    return receipt


def _degrees(value: Optional[int]) -> str:
    return "N/A" if value is None else f"{value} F"


def _percent(value: Optional[int]) -> str:
    return "N/A" if value is None else f"{value}%"


def build_movie_receipt(config: Dict[str, Any], current_time: datetime, movie: Movie) -> Receipt:
    columns = int(config["receipt"].get("columns", 42))
    receipt = Receipt(title="Nightly Movie Receipt", columns=columns)
    receipt.center("TONIGHT'S MOVIE")
    receipt.center(current_time.strftime("%A, %B %-d, %Y"))
    receipt.divider("=")
    receipt.center(movie.title.upper())
    receipt.center(str(movie.year))
    receipt.divider()
    receipt.label("Runtime", movie.runtime)
    receipt.label("Genre", movie.genre)
    receipt.label("Director", movie.director)
    receipt.label("Starring", ", ".join(movie.starring))
    receipt.divider()
    receipt.text(movie.synopsis)
    receipt.divider()
    receipt.blank_rule("Rating out of 5:", rows=1)
    receipt.blank_rule("One sentence review:", rows=3)
    receipt.center()
    receipt.center("Admit one couch.")
    if movie.source == "tmdb":
        receipt.center()
        receipt.text("Movie data: TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB.")
    return receipt
