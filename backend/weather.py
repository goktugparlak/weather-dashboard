"""OpenWeather integration and translation of provider failures."""
import logging
import os

import httpx
from fastapi import HTTPException
from pydantic import ValidationError

from backend.models import WeatherResponse

logger = logging.getLogger(__name__)
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


async def get_weather_data(city: str, client: httpx.AsyncClient) -> WeatherResponse:
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        raise HTTPException(500, "Weather API key is not configured")
    try:
        response = await client.get(BASE_URL, params={"q": city, "appid": api_key, "units": "metric"})
    except httpx.TimeoutException:
        raise HTTPException(504, "Weather service timed out. Please try again.") from None
    except httpx.RequestError:
        raise HTTPException(503, "Weather service is currently unavailable") from None
    if response.status_code == 404:
        raise HTTPException(404, "City not found. Check the name or add a country code.")
    if response.status_code == 429:
        raise HTTPException(503, "Weather service is busy. Please try again later.")
    if response.status_code in (401, 403):
        # The provider request URL contains the key: never log it or raw exceptions.
        logger.warning("Weather provider rejected credentials (status %s)", response.status_code)
        raise HTTPException(502, "Weather service configuration error")
    if response.status_code != 200:
        raise HTTPException(502, "Weather provider returned an error")
    try:
        data = response.json()
        return WeatherResponse(
            city=data["name"], country=data["sys"]["country"],
            temperature=data["main"]["temp"], feels_like=data["main"]["feels_like"],
            condition=data["weather"][0]["main"], description=data["weather"][0]["description"],
            humidity=data["main"]["humidity"], wind_speed=data["wind"]["speed"],
        )
    except (ValueError, KeyError, IndexError, TypeError, ValidationError):
        raise HTTPException(502, "Weather provider returned an invalid response") from None
