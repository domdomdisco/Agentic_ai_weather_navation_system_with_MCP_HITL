import json
import legacy_weather_service

def handle_request(request_json):
    """
    MCP Adapter for Legacy Weather Service.
    Converts MCP JSON-RPC requests into legacy service calls.
    """
    request = json.loads(request_json)
    method = request.get("method")
    
    if method == "tools/list":
        return json.dumps({
            "tools": [
                {
                    "name": "get_weather",
                    "description": "Fetch live weather data for a city.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string"}
                        },
                        "required": ["city"]
                    }
                },
                {
                    "name": "get_forecast",
                    "description": "Fetch a 3-day weather forecast for a city.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string"}
                        },
                        "required": ["city"]
                    }
                }
            ]
        })
    
    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        city = args.get("city")

        # Calling the legacy service
        raw_data = legacy_weather_service.get_weather_data(city)
        
        if not raw_data:
            return json.dumps({"isError": True, "error": {"message": "Legacy service failed"}})

        if tool_name == "get_weather":
            # Sanitize: Convert complex JSON into a clean Observation string
            curr = raw_data['current_condition'][0]
            result = f"Weather in {city}: {curr['weatherDesc'][0]['value']}, Temp: {curr['temp_C']}°C"
        
        elif tool_name == "get_forecast":
            # Sanitize: Convert forecast list into a clean Observation string
            forecasts = []
            for day in raw_data['weather'][:3]:
                desc = day['hourly'][4]['weatherDesc'][0]['value']
                forecasts.append(f"{day['date']}: {desc} ({day['maxtempC']}°C)")
            result = "3-Day Forecast: " + " | ".join(forecasts)
        
        else:
            return json.dumps({"isError": True, "error": {"message": "Tool not found"}})

        return json.dumps({
            "content": [{"type": "text", "text": result}],
            "isError": False
        })

    return json.dumps({"isError": True, "error": {"message": "Method not found"}})

if __name__ == "__main__":
    # Test tool listing
    print("--- Tool Discovery ---")
    print(handle_request(json.dumps({"method": "tools/list"})))
    
    # Test tool calling
    print("\n--- Tool Call: get_weather ---")
    test_call = {
        "method": "tools/call",
        "params": {"name": "get_weather", "arguments": {"city": "London"}}
    }
    print(handle_request(json.dumps(test_call)))

    print("\n--- Tool Call: get_forecast ---")
    test_call = {
        "method": "tools/call",
        "params": {"name": "get_forecast", "arguments": {"city": "London"}}
    }

    print(handle_request(json.dumps(test_call)))
