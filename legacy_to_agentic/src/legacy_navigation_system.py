def process_weather_data(json_blob):
    """
    Legacy navigation logic using hardcoded if-then rules.
    Parses complex JSON from wttr.in and returns navigation alerts.
    """
    if not json_blob:
        return "No data available."

    try:
        # Navigating the complex JSON structure of wttr.in
        current_condition = json_blob['current_condition'][0]
        temp_c = int(current_condition['temp_C'])
        weather_desc = current_condition['weatherDesc'][0]['value'].lower()
        
        alerts = []
        speed_limit = 100 # Default km/h
        
        # Hardcoded logic
        if "rain" in weather_desc or "drizzle" in weather_desc:
            speed_limit = 50
            alerts.append("ALERT: Slippery Road detected due to rain.")
            
        if "snow" in weather_desc or "ice" in weather_desc:
            speed_limit = 30
            alerts.append("CRITICAL: Hazardous road conditions. Snow/Ice reported.")
            
        if temp_c < 0:
            alerts.append("WARNING: Freezing temperatures. Watch for black ice.")
            
        if not alerts:
            alerts.append("Conditions normal. Safe driving.")

        # Forecast Processing (3-day summary)
        forecast_summary = []
        if 'weather' in json_blob:
            for day in json_blob['weather'][:3]:
                date = day['date']
                max_temp = day['maxtempC']
                min_temp = day['mintempC']
                desc = day['hourly'][4]['weatherDesc'][0]['value'] # Mid-day forecast
                forecast_summary.append(f"{date}: {desc} (Max: {max_temp}°C, Min: {min_temp}°C)")

        status = {
            "speed_limit": speed_limit,
            "alerts": alerts,
            "forecast": forecast_summary,
            "current_temp": temp_c,
            "description": weather_desc
        }
        
        return status

    except (KeyError, IndexError, ValueError) as e:
        return f"Error parsing legacy weather data: {e}"

if __name__ == "__main__":
    # Test with dummy blob
    test_blob = {
        'current_condition': [{
            'temp_C': '-2',
            'weatherDesc': [{'value': 'Light Snow'}]
        }]
    }
    print(process_weather_data(test_blob))
