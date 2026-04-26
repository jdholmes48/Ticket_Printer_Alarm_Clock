from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import date
from typing import Any, Dict, List


class TmdbError(RuntimeError):
    pass


class TmdbClient:
    base_url = "https://api.themoviedb.org/3"

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.access_token = config.get("access_token", "").strip()
        if not self.access_token:
            raise TmdbError("TMDb access token is not configured.")

    def discover_movies(self, current_date: date) -> List[Dict[str, Any]]:
        params = {
            "language": self.config.get("language", "en-US"),
            "region": self.config.get("region", "US"),
            "include_adult": "false",
            "include_video": "false",
            "sort_by": "vote_average.desc",
            "vote_count.gte": self.config.get("minimum_vote_count", 250),
            "vote_average.gte": self.config.get("minimum_vote_average", 6.8),
            "page": _page_for_date(current_date),
        }
        _copy_if_present(params, self.config, "include_genres", "with_genres")
        _copy_if_present(params, self.config, "exclude_genres", "without_genres")
        _copy_if_present(params, self.config, "watch_region", "watch_region")
        _copy_if_present(params, self.config, "with_watch_monetization_types", "with_watch_monetization_types")

        payload = self._get("/discover/movie", params)
        return payload.get("results", [])

    def movie_details(self, movie_id: int) -> Dict[str, Any]:
        return self._get(
            f"/movie/{movie_id}",
            {
                "language": self.config.get("language", "en-US"),
            },
        )

    def movie_credits(self, movie_id: int) -> Dict[str, Any]:
        return self._get(
            f"/movie/{movie_id}/credits",
            {
                "language": self.config.get("language", "en-US"),
            },
        )

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        query = urllib.parse.urlencode(params)
        request = urllib.request.Request(
            f"{self.base_url}{path}?{query}",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=12) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise TmdbError(f"TMDb request failed for {path}.") from exc


def _copy_if_present(target: Dict[str, Any], source: Dict[str, Any], source_key: str, target_key: str) -> None:
    value = source.get(source_key)
    if value:
        target[target_key] = value


def _page_for_date(current_date: date) -> int:
    return (current_date.toordinal() % 10) + 1
