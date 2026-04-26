from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

from .config import resolve_project_path


@dataclass
class Movie:
    title: str
    year: int
    runtime: str
    genre: str
    director: str
    starring: List[str]
    synopsis: str


def load_movies(config: Dict[str, Any]) -> List[Movie]:
    source = resolve_project_path(config, config["movie"]["source_file"])
    if source is None or not source.exists():
        raise FileNotFoundError("Movie source file is missing.")

    with Path(source).open("r", encoding="utf-8") as handle:
        rows = json.load(handle)

    return [Movie(**row) for row in rows]


def pick_movie(config: Dict[str, Any], current_date: date) -> Movie:
    movies = load_movies(config)
    if not movies:
        raise ValueError("Movie source file has no recommendations.")

    day_number = current_date.toordinal()
    return movies[day_number % len(movies)]
