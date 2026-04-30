import legacy_weather_service
import legacy_navigation_system

def run_legacy_system(city="London"):
    print(f"--- Starting Legacy Weather-Navigation System for {city} ---")
    
    # Tight coupling: Directly calling services and passing raw data
    print(f"Step 1: Fetching weather data for {city}...")
    weather_json = legacy_weather_service.get_weather_data(city)
    
    if not weather_json:
        print("CRITICAL ERROR: Failed to retrieve weather data. Aborting.")
        return

    print("Step 2: Processing data through navigation logic...")
    navigation_status = legacy_navigation_system.process_weather_data(weather_json)
    
    if isinstance(navigation_status, str):
        print(f"ERROR: {navigation_status}")
        return

    print("\n--- NAVIGATION REPORT ---")
    print(f"Location:      {city}")
    print(f"Current Temp:  {navigation_status['current_temp']}°C")
    print(f"Conditions:    {navigation_status['description']}")
    print(f"Speed Limit:   {navigation_status['speed_limit']} km/h")
    print("Alerts:")
    for alert in navigation_status['alerts']:
        print(f"  - {alert}")
    
    if navigation_status.get('forecast'):
        print("3-Day Forecast:")
        for day in navigation_status['forecast']:
            print(f"  - {day}")
    print("--------------------------\n")

if __name__ == "__main__":
    # We can change the city here to test different hardcoded triggers
    run_legacy_system("Reykjavik")
    # run_legacy_system("Reykjavik") # Likely to trigger ice/snow alerts
    # run_legacy_system("Singapore") # Likely to trigger rain alerts
