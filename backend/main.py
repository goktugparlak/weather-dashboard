"""Serve the API and frontend from one origin."""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import StringConstraints

from backend.models import WeatherResponse
from backend.weather import get_weather_data

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")  # Existing environment variables take precedence.
City = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient(timeout=10.0) as client:
        app.state.weather_client = client
        yield


app = FastAPI(title="Weather Dashboard API", version="1.0.0",
              description="Current weather from OpenWeather, with metric units.", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=ROOT / "frontend"), name="static")


def get_weather_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.weather_client


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(ROOT / "frontend" / "index.html")


@app.get("/health")
def health():
    """Process health only; does not call the weather provider."""
    return {"status": "ok"}


@app.get("/weather", response_model=WeatherResponse)
async def weather(
    city: Annotated[City, Query(description="City, optionally with country code: Torino,IT")],
    client: Annotated[httpx.AsyncClient, Depends(get_weather_client)],
):
    return await get_weather_data(city, client)
