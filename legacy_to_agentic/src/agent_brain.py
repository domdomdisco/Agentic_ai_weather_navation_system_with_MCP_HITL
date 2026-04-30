import json
import os
import weather_mcp_adapter
import nav_mcp_adapter
import google.generativeai as genai
from audit_logger import AuditLogger
from dotenv import load_dotenv

# Configuration
load_dotenv() # Load environment variables from .env
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

class DynamicAgentBrain:
    def __init__(self):
        self.weather_tools = []
        self.nav_tools = []
        self.sensitive_tools = ["update_navigation"] # Governance: These require HITL
        self._discover_tools()

    def _discover_tools(self):
        """Phase 2 Discovery: Automatically identify capabilities via MCP"""
        print("[DISCOVERY] Querying MCP Adapters...")
        
        # Discover Weather Tools
        weather_resp = json.loads(weather_mcp_adapter.handle_request(json.dumps({"method": "tools/list"})))
        self.weather_tools = weather_resp["tools"]
        
        # Discover Nav Tools
        nav_resp = json.loads(nav_mcp_adapter.handle_request(json.dumps({"method": "tools/list"})))
        self.nav_tools = nav_resp["tools"]
        
        print(f"  - Discovered {len(self.weather_tools) + len(self.nav_tools)} legacy tools via MCP Bridge.")

    def _execute_mcp_tool(self, tool_name, args):
        """Routing tool calls to the correct MCP Adapter"""
        print(f"  ACTION: Executing MCP Tool '{tool_name}' with {args}")
        
        request = json.dumps({
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": args}
        })
        
        # Route to correct adapter
        if any(t['name'] == tool_name for t in self.weather_tools):
            response = weather_mcp_adapter.handle_request(request)
        else:
            response = nav_mcp_adapter.handle_request(request)
            
        observation = json.loads(response)["content"][0]["text"]
        print(f"  OBSERVATION: {observation}")
        return observation

    def _hitl_gate(self, tool_name, args, thought):
        """Phase 2 Governance: Human-in-the-Loop Gate"""
        print(f"\n--- 🛡️ GOVERNANCE GATE: SENSITIVE ACTION DETECTED ---")
        print(f"Tool:      {tool_name}")
        print(f"Arguments: {args}")
        print(f"Reasoning: {thought}")
        print(f"---------------------------------------------------")
        
        choice = input("Approve this action? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            print("Action Approved.")
            return True
        else:
            print("Action REJECTED by Human.")
            return False


    def run(self, user_goal):
        print(f"\n=== STARTING DYNAMIC AGENTIC LOOP ===\nGoal: {user_goal}")
        
        if not API_KEY:
            print("\n[ERROR] No Google API Key found. Please set GOOGLE_API_KEY in your .env file.")
            return

        # Initialize Gemini Flash (Latest Stable)
        model = genai.GenerativeModel(model_name='gemini-flash-latest')
        chat = model.start_chat(history=[])
        
        current_prompt = user_goal
        max_turns = 10
        logger = AuditLogger()
        
        for turn in range(max_turns):
            print(f"\n[TURN {turn + 1}] Reasoning...")
            
            system_instruction = (
                "You are an autonomous Navigation Agent.\n"
                "CRITICAL: You must only output text. Do NOT use native function calling.\n"
                "Follow this exact ReAct pattern for every turn:\n"
                "THOUGHT: Reason about what to do next.\n"
                "ACTION: tool_name(city='name')\n"
                "OBSERVATION: (This will be provided to you)\n"
                "FINAL ANSWER: Provide the solution to the user.\n\n"
                f"Available Tools (Use ONLY these names):\n{json.dumps(self.weather_tools + self.nav_tools, indent=2)}"
            )
            
            try:
                response = chat.send_message(f"{system_instruction}\nUser Goal: {current_prompt}")
                text = response.text
                
                # Financial Audit via External Module
                logger.log_turn_usage(turn + 1, response.usage_metadata)
                
                print(f"BRAIN OUTPUT:\n{text}")
                
                if "FINAL ANSWER:" in text:
                    break

                if "ACTION:" in text:
                    # Parse tool and city using regex
                    import re
                    match = re.search(r"ACTION:\s*(\w+)\(city=['\"]([^'\"]+)['\"]\)", text)
                    if match:
                        tool_name, city = match.groups()
                        
                        # 🛡️ Governance Check (HITL)
                        approved = True
                        if tool_name in self.sensitive_tools:
                            # Extract thought for the gate
                            thought_match = re.search(r"THOUGHT:\s*(.*)", text)
                            thought = thought_match.group(1) if thought_match else "No reasoning provided."
                            approved = self._hitl_gate(tool_name, {"city": city}, thought)
                        
                        if approved:
                            observation = self._execute_mcp_tool(tool_name, {"city": city})
                        else:
                            observation = "Error: This action was REJECTED by the Human Supervisor. Please try a different approach or justify your reasoning."
                        
                        current_prompt = f"OBSERVATION: {observation}"
                    else:
                        print("  [ERROR] Malformed action. Retrying...")
                        current_prompt = "Error: Use format ACTION: tool_name(city='name')"
                else:
                    break
            except Exception as e:
                print(f"\n[CRITICAL ERROR] {e}")
                break

        print("\n=== AGENTIC LOOP COMPLETE ===\n")

if __name__ == "__main__":
    agent = DynamicAgentBrain()
    agent.run("Check safety for Tokyo and New York.")
