"""Public API response: temperatures in degrees Celsius, wind in m/s."""
from pydantic import BaseModel, ConfigDict, Field


class WeatherResponse(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    city: str = Field(min_length=1)
    country: str = Field(min_length=1)
    temperature: float
    feels_like: float
    condition: str = Field(min_length=1)
    description: str = Field(min_length=1)
    humidity: int = Field(ge=0, le=100)
    wind_speed: float = Field(ge=0)
