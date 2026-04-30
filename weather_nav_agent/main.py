import os
from dotenv import load_dotenv
from real_mcp_agent import RealMCPAgent

def main():
    # 1. Setup environment
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("[ERROR] Please set GEMINI_API_KEY in .env")
        return

    # 2. Initialize the Unified Agent
    # This agent is MCP-compliant (discovers tools via protocol)
    # and LLM-enabled (uses Gemini for reasoning).
    agent = RealMCPAgent(api_key)
    
    # 3. Set the Goal
    # The agent will discover 'get_forecast' and 'set_speed_limit' automatically!
    goal = "Check the 3-day forecast for New York. If rain is expected, set the vehicle speed limit to 50 mph as a precaution."
    
    # 4. Run the autonomous loop
    agent.run(goal)

if __name__ == "__main__":
    main()
