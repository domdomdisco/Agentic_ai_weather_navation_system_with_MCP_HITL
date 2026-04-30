import json
import os
import re
from dotenv import load_dotenv
import weather_mcp
import nav_mcp

# ---------------------------------------------------------
# THE UNIFIED MCP SYSTEM PROMPT
# ---------------------------------------------------------
SYSTEM_PROMPT = """
You are an autonomous Weather-Navigation Agent operating via the Model Context Protocol (MCP).
Your goal is to ensure driver safety by checking weather and updating navigation.

RESOURCES:
The following tools have been discovered via MCP servers:
{tools_description}

INSTRUCTIONS:
1. THINK: Write a 'Thought' about what you need to do based on the Goal and History.
2. ACT: Write an 'Action' using an MCP tool if you need information or need to take an action.
3. OBSERVE: You will receive an 'Observation' from the MCP server.
4. REPEAT until you can provide a 'Final Answer:'.

CRITICAL RULES:
- You MUST check weather before updating navigation.
- Do NOT hallucinate data. Only use what is provided in 'Observation:'.
- FORMAT:
Thought: <reasoning>
Action: <tool_name>(<arg_name>='<value>')
<STOP>
"""

class RealMCPAgent:
    def __init__(self, api_key):
        # 1. Setup LLM
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
        except ImportError:
            print("[ERROR] Please install google-generativeai")

        # 2. Setup MCP Servers
        self.servers = {
            "weather": weather_mcp,
            "navigation": nav_mcp
        }
        self.tools_catalog = []
        self.history = []

    def discover_tools(self):
        """Official MCP Discovery Phase"""
        print("\n--- MCP DISCOVERY PHASE ---")
        for name, server in self.servers.items():
            request = json.dumps({"method": "tools/list", "params": {}})
            response = json.loads(server.handle_request(request))
            if "tools" in response:
                for tool in response["tools"]:
                    tool["server_id"] = name
                    self.tools_catalog.append(tool)
                    print(f"[CLIENT] Discovered: {tool['name']} from {name}")
        print("--- DISCOVERY COMPLETE ---\n")

    def call_mcp_tool(self, action_call, thought):
        """Translates LLM action into MCP 'tools/call'"""
        try:
            # Parse: tool_name(arg='val')
            match = re.match(r"(\w+)\((.*)\)", action_call)
            if not match: return "Error: Invalid format."
            
            tool_name = match.group(1)
            args_str = match.group(2)
            # Enhanced argument parser for key=value (supports strings and integers)
            args = {}
            for pair in re.findall(r"(\w+)=(['\"](.*?)['\"]|(\d+))", args_str):
                key = pair[0]
                val = pair[2] if pair[2] else int(pair[3])
                args[key] = val

            # Find tool in catalog
            tool = next((t for t in self.tools_catalog if t["name"] == tool_name), None)
            if not tool: return f"Error: Tool {tool_name} not found."

            # HITL Safety Gate for sensitive actions
            if tool_name in ["update_navigation", "set_speed_limit"]:
                print(f"\n[!!!] HITL SECURITY CHECK: Agent wants to call {tool_name}.")
                print(f"[!] REASON: {thought}")
                approval = input(f">>> Approve this {tool_name} action? (yes/no): ").strip().lower()
                if approval != 'yes':
                    return "ACTION DENIED BY HUMAN."

            # Execute via MCP Protocol
            server = self.servers[tool["server_id"]]
            request = {
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": args}
            }
            
            print(f"[CLIENT] >>> MCP REQUEST: {tool_name}({args})")
            response = json.loads(server.handle_request(json.dumps(request)))
            
            if "content" in response and len(response["content"]) > 0:
                return response["content"][0].get("text", "Success.")
            return "Error: Malformed MCP response."
            
        except Exception as e:
            return f"Error: {str(e)}"

    def run(self, goal, max_steps=5):
        print(f"=== STARTING MCP+LLM SESSION ===\nGOAL: {goal}")
        self.discover_tools()
        tools_str = json.dumps(self.tools_catalog, indent=2)
        
        for i in range(max_steps):
            # Construct Prompt
            prompt = SYSTEM_PROMPT.format(tools_description=tools_str)
            history_str = "\n".join(self.history)
            full_prompt = f"{prompt}\nGoal: {goal}\n{history_str}"
            
            print(f"\n[Step {i+1}] Thinking...")
            response = self.model.generate_content(full_prompt).text
            
            # Parse
            thought, action, final = "", None, None
            for line in response.split("\n"):
                if line.startswith("Thought:"): thought = line.replace("Thought:", "").strip()
                elif line.startswith("Action:"): action = line.replace("Action:", "").strip()
                elif "Final Answer:" in line: final = line.split("Final Answer:")[1].strip()

            if final:
                print(f"\n=== FINAL ANSWER ===\n{final}")
                break
            
            print(f"Thought: {thought}")
            self.history.append(f"Thought: {thought}")
            
            if action:
                print(f"Action: {action}")
                self.history.append(f"Action: {action}")
                obs = self.call_mcp_tool(action, thought)
                print(f"Observation: {obs}")
                self.history.append(f"Observation: {obs}")
            else:
                print("No action taken. Ending.")
                break
        print("\n=== SESSION COMPLETE ===")

if __name__ == "__main__":
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY")
    agent = RealMCPAgent(key)
    agent.run("Check weather in New York and update navigation if hazardous.")
