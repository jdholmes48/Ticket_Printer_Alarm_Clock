from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class WeatherForecast:
    location: str
    high_f: Optional[int]
    low_f: Optional[int]
    precipitation_probability: Optional[int]
    summary: str


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    80: "Light showers",
    81: "Showers",
    82: "Heavy showers",
    95: "Thunderstorm",
}


def get_daily_forecast(config: Dict[str, Any], target_date: datetime) -> WeatherForecast:
    location = config["location"]
    query = urllib.parse.urlencode(
        {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "temperature_unit": "fahrenheit",
            "timezone": config.get("timezone", "America/New_York"),
            "forecast_days": 1,
        }
    )
    url = f"https://api.open-meteo.com/v1/forecast?{query}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        daily = payload["daily"]
        weather_code = int(daily["weather_code"][0])
        return WeatherForecast(
            location=location["name"],
            high_f=round(daily["temperature_2m_max"][0]),
            low_f=round(daily["temperature_2m_min"][0]),
            precipitation_probability=round(daily["precipitation_probability_max"][0]),
            summary=WEATHER_CODES.get(weather_code, "Forecast unavailable"),
        )
    except Exception:
        return WeatherForecast(
            location=location["name"],
            high_f=None,
            low_f=None,
            precipitation_probability=None,
            summary=f"Weather unavailable for {target_date:%b %-d}. Check network on the Pi.",
        )
