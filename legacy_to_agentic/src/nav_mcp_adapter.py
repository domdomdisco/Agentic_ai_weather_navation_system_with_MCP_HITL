import json
import legacy_navigation_system
import legacy_weather_service # Used to feed the legacy nav system

def handle_request(request_json):
    """
    MCP Adapter for Legacy Navigation System.
    Bridges the gap between modern agentic calls and legacy blob-based logic.
    """
    request = json.loads(request_json)
    method = request.get("method")
    
    if method == "tools/list":
        return json.dumps({
            "tools": [
                {
                    "name": "update_navigation",
                    "description": "Calculate speed limits and safety alerts based on weather for a city.",
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

        if tool_name == "update_navigation":
            # 1. Fetch raw data (Legacy bridge)
            raw_weather = legacy_weather_service.get_weather_data(city)
            
            # 2. Process via legacy logic
            nav_data = legacy_navigation_system.process_weather_data(raw_weather)
            
            if isinstance(nav_data, str): # Error
                return json.dumps({"isError": True, "error": {"message": nav_data}})

            # 3. Sanitize: Convert into a clean text Observation for the LLM
            alerts = ", ".join(nav_data['alerts'])
            forecast = " | ".join(nav_data['forecast'])
            result = (f"NAV SYSTEM UPDATE for {city}:\n"
                      f"- Speed Limit: {nav_data['speed_limit']} km/h\n"
                      f"- Alerts: {alerts}\n"
                      f"- 3-Day Forecast: {forecast}")
            
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
    print("\n--- Tool Call: update_navigation ---")
    test_call = {
        "method": "tools/call",
        "params": {"name": "update_navigation", "arguments": {"city": "Reykjavik"}}
    }
    print(handle_request(json.dumps(test_call)))
