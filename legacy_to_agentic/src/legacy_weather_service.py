import requests
import json

def get_weather_data(city: str):
    """
    Fetches raw weather data from wttr.in in JSON format.
    This is a legacy service that returns complex, nested JSON objects.
    """
    url = f"https://wttr.in/{city}?format=j1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

if __name__ == "__main__":
    # Test fetch
    data = get_weather_data("London")
    if data:
        print("Successfully fetched weather data for London.")
        # print(json.dumps(data, indent=2)) # Too long for standard output
    else:
        print("Failed to fetch weather data.")
