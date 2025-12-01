# agents/hitl_agent.py
import time, logging

logger = logging.getLogger("hitl_agent")

# agents/hitl_agent.py

from google.adk import Agent, AgentConfig
from google.adk.tools import ToolContext
import time

class HITLAgent(Agent):
    def __init__(self, session_service):
        super().__init__(
            config=AgentConfig(
                name="hitl_agent",
                model="gemini-2.0-flash-exp",
                description="Manages human-in-the-loop verification.",
                system_instruction="""
                Pause until human approves the detection overlay.
                """,
            )
        )
        self.session = session_service

    async def handle(self, ctx: ToolContext):
        order_id = ctx.inputs["order_id"]
        overlay_url = ctx.inputs.get("overlay", "")

        self.session.create_task(order_id, {"status": "waiting", "overlay": overlay_url})

        # Pause/resume pattern from ADK docs
        while True:
            task = self.session.get_task(order_id)
            if not task: return {"status": "error", "message": "Task lost"}
            
            if task.get("status") != "waiting":
                return task
        return self.session.get_task(order_id)
