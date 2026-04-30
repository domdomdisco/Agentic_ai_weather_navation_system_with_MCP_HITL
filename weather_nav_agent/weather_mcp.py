import json

def handle_request(request_json):
    """
    STRICT MCP COMPLIANT SERVER
    """
    request = json.loads(request_json)
    method = request.get("method")
    
    print(f"[WEATHER SERVER] MCP INbound: {method}")

    if method == "tools/list":
        return json.dumps({
            "tools": [
                {
                    "name": "get_weather",
                    "description": "Get current weather and environmental hazards.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "The city name"}
                        },
                        "required": ["city"]
                    }
                },
                {
                    "name": "get_forecast",
                    "description": "Get a 3-day weather forecast.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "The city name"}
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
        city = args.get("city", "London")
        import requests

        if tool_name == "get_weather":
            try:
                response = requests.get(f"https://wttr.in/{city}?format=%C+Temp:%t+Wind:%w")
                weather_data = response.text.encode('ascii', 'ignore').decode('ascii').strip() if response.status_code == 200 else "Error"
            except: weather_data = "Connection Error"
            result = f"Current Weather in {city}: {weather_data}"
        
        elif tool_name == "get_forecast":
            # Simple mock forecast for demonstration
            result = f"3-Day Forecast for {city}: Day 1: Sunny, Day 2: Possible Rain, Day 3: Cloudy."
        
        else:
            return json.dumps({"isError": True, "error": {"message": "Tool not found"}})

        return json.dumps({
            "content": [{"type": "text", "text": result}],
            "isError": False
        })

    return json.dumps({"isError": True, "error": {"message": "Method not found"}})
