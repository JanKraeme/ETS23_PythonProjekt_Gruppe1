import python_weather
import asyncio

async def get_current_weather(city): # Get current temperature in city
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        weather = await client.get(city)
        return weather.temperature

city = "oldenburg"
temperature = asyncio.run(get_current_weather(city))
print(f"The temperature in {city} is {temperature}°C")