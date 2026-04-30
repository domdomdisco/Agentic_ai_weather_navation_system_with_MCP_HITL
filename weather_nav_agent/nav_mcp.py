import json

def handle_request(request_json):
    """
    STRICT MCP COMPLIANT NAVIGATION SERVER
    """
    request = json.loads(request_json)
    method = request.get("method")
    
    print(f"[NAV SERVER] MCP INbound: {method}")

    if method == "tools/list":
        return json.dumps({
            "tools": [
                {
                    "name": "update_navigation",
                    "description": "Send a safety alert to the driver's dashboard.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
                            "message": {"type": "string"}
                        },
                        "required": ["priority", "message"]
                    }
                },
                {
                    "name": "set_speed_limit",
                    "description": "Adjust the vehicle's maximum speed limit.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "limit_mph": {"type": "integer", "description": "The new speed limit in mph"}
                        },
                        "required": ["limit_mph"]
                    }
                }
            ]
        })
    
    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "update_navigation":
            msg = args.get("message", "")
            print(f"\n[MCP DASHBOARD] ALERT: {msg}\n")
            result = "Navigation updated."
        
        elif tool_name == "set_speed_limit":
            limit = args.get("limit_mph", 60)
            print(f"\n[MCP VEHICLE CONTROL] Speed limit set to {limit} mph.\n")
            result = f"Speed limit updated to {limit} mph."
        
        else:
            return json.dumps({"isError": True, "error": {"message": "Unknown method"}})
        
        return json.dumps({
            "content": [{"type": "text", "text": result}],
            "isError": False
        })

    return json.dumps({"isError": True, "error": {"message": "Unknown method"}})
