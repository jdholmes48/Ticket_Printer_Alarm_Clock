from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import resolve_project_path
from .tmdb import TmdbClient, TmdbError


@dataclass
class Movie:
    title: str
    year: int
    runtime: str
    genre: str
    director: str
    starring: List[str]
    synopsis: str
    source: str = "local"


def load_movies(config: Dict[str, Any]) -> List[Movie]:
    source = resolve_project_path(config, config["movie"]["source_file"])
    if source is None or not source.exists():
        raise FileNotFoundError("Movie source file is missing.")

    with Path(source).open("r", encoding="utf-8") as handle:
        rows = json.load(handle)

    return [Movie(**row) for row in rows]


def pick_movie(config: Dict[str, Any], current_date: date) -> Movie:
    movie_config = config.get("movie", {})
    source = movie_config.get("source", "local").lower()

    if source == "tmdb":
        try:
            return pick_tmdb_movie(config, current_date)
        except TmdbError:
            if not movie_config.get("fallback_to_local", True):
                raise

    return pick_local_movie(config, current_date)


def pick_local_movie(config: Dict[str, Any], current_date: date) -> Movie:
    movies = load_movies(config)
    if not movies:
        raise ValueError("Movie source file has no recommendations.")

    day_number = current_date.toordinal()
    return movies[day_number % len(movies)]


def pick_tmdb_movie(config: Dict[str, Any], current_date: date) -> Movie:
    client = TmdbClient(config.get("tmdb", {}))
    discovered = client.discover_movies(current_date)
    if not discovered:
        raise TmdbError("TMDb returned no movie recommendations.")

    selection = _deterministic_pick(discovered, current_date)
    details = client.movie_details(selection["id"])
    credits = client.movie_credits(selection["id"])
    director = _find_director(credits) or "Unknown"
    starring = _find_starring(credits)

    release_date = details.get("release_date") or selection.get("release_date") or ""
    year = _year_from_release_date(release_date)
    genres = ", ".join(genre["name"] for genre in details.get("genres", []) if genre.get("name"))

    return Movie(
        title=details.get("title") or selection.get("title") or "Untitled",
        year=year,
        runtime=_format_runtime(details.get("runtime")),
        genre=genres or "Unknown",
        director=director,
        starring=starring or ["Unknown"],
        synopsis=details.get("overview") or selection.get("overview") or "No synopsis available.",
        source="tmdb",
    )


def _deterministic_pick(results: List[Dict[str, Any]], current_date: date) -> Dict[str, Any]:
    index = current_date.toordinal() % len(results)
    return results[index]


def _find_director(credits: Dict[str, Any]) -> Optional[str]:
    for person in credits.get("crew", []):
        if person.get("job") == "Director" and person.get("name"):
            return person["name"]
    return None


def _find_starring(credits: Dict[str, Any]) -> List[str]:
    names = []
    for person in credits.get("cast", [])[:3]:
        if person.get("name"):
            names.append(person["name"])
    return names


def _year_from_release_date(value: str) -> int:
    try:
        return int(value[:4])
    except (TypeError, ValueError):
        return 0


def _format_runtime(minutes: Any) -> str:
    if not minutes:
        return "Unknown"
    return f"{int(minutes)} min"
