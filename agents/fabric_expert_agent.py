# agents/fabric_expert_agent.py

from google.adk import Agent, AgentConfig
from google.adk.tools import Tool, ToolContext
from google import genai
import hashlib
import json

class FabricExpertAgent(Agent):
    def __init__(self, fabric_db):
        super().__init__(
            config=AgentConfig(
                name="fabric_expert",
                model="gemini-2.0-flash-exp",
                description="Determines fabric type + care instructions",
                system_instruction="""
                You are the Fabric Expert Agent.
                If you do not recognize a fabric, use the google_search tool
                to learn instructions and store them in the Fabric DB.
                """,
                tools=["google_search"]      # <-- Comes from MCP allowlist
            )
        )

        self.db = fabric_db
        self.client = genai.Client()

    async def handle(self, ctx: ToolContext):
        hints = ctx.inputs.get("hints", {})         # {"type": "...", "color": "..."}
        img_b64 = ctx.inputs.get("image_b64")

        # Create a key based on hints (since we don't process image deeply here yet)
        key_str = json.dumps(hints, sort_keys=True)
        key = hashlib.sha1(key_str.encode()).hexdigest()

        # If known, retrieve
        existing = self.db.get_fabric(key)
        if existing:
            return existing.get("fabric_type"), existing.get("care_instructions")

        # If unknown, use Google Search tool (Simulated via shim/mock if tool not present)
        # In real ADK, this calls the tool. Here we simulate or call if available.
        try:
            result = await ctx.call_tool("google_search", {
                "query": f"how to wash {hints.get('type', 'cloth')} {hints.get('color', '')} fabric"
            })
            care = result.get("answer", "Wash cold, tumble dry low.")
        except:
            care = "Wash cold, tumble dry low (Default)."

        fabric_type = hints.get("type", "unknown")
        
        self.db.save_fabric(key, {
            "fabric_type": fabric_type,
            "care_instructions": care
        })

        return fabric_type, care

    # Legacy method
    def analyze(self, image_b64, hints):
        import asyncio
        ctx = ToolContext({"image_b64": image_b64, "hints": hints})
        return asyncio.run(self.handle(ctx))
