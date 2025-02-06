from pipecat_flows import FlowArgs, FlowResult
import aiohttp, os
from typing import Union
from dotenv import load_dotenv
from loguru import logger

load_dotenv(override=True)

# OpenWeatherMap API setup

# Type definitions for API responses
class WeatherResult(FlowResult):
    city: str
    temperature: float
    description: str
    humidity: int

class ErrorResult(FlowResult):
    status: str
    error: str

class WeatherApi:
    def __init__(self, api_key: str, base_url: str = os.getenv("OPENWEATHER_BASE_URL")):
        self.api_key = api_key
        self.base_url = base_url

    async def fetch_weather(self, session: aiohttp.ClientSession, city: str) -> dict:
        params = {"q": city, "appid": self.api_key, "units": "metric"}
        async with session.get(self.base_url, params=params) as response:
            if response.status != 200:
                raise ValueError(f"API returned status {response.status}")
            return await response.json()

weather_api = WeatherApi(os.getenv("OPENWEATHER_API_KEY"))

async def get_weather(args: FlowArgs) -> Union[WeatherResult, ErrorResult]:
    city = args["city"]
    logger.debug(f"Calling OpenWeatherMap API: get_weather for {city}")
    async with aiohttp.ClientSession() as session:
        try:
            weather_data = await weather_api.fetch_weather(session, city)
            logger.debug(f"OpenWeatherMap API Response: {weather_data}")
            return WeatherResult(
                city=weather_data["name"],
                temperature=weather_data["main"]["temp"],
                description=weather_data["weather"][0]["description"],
                humidity=weather_data["main"]["humidity"]
            )
        except Exception as e:
            logger.error(f"OpenWeatherMap API Error: {e}")
            return ErrorResult(status="error", error=f"Failed to fetch weather for {city}")

