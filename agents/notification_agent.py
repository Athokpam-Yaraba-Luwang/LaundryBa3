# agents/notification_agent.py

from google.adk import Agent, AgentConfig
from google.adk.tools import ToolContext

class NotificationAgent(Agent):
    def __init__(self, notifier_tool=None):
        super().__init__(
            config=AgentConfig(
                name="notification_agent",
                model="gemini-2.0-flash-exp",
                description="Delivers push notifications",
                tools=["push_notify_tool"]
            )
        )
        # In a real ADK app, tools are registered with the runtime.
        # Here we pass the tool implementation directly for the shim.
        self.tool = notifier_tool

    async def handle(self, ctx: ToolContext):
        phone = ctx.inputs["phone"]
        msg = ctx.inputs["message"]
        
        # In real ADK: return await ctx.call_tool("push_notify_tool", {"phone":phone, "msg":msg})
        # For our shim/demo:
        print(f"[NotificationAgent] Sending to {phone}: {msg}")
        return {"status": "sent", "recipient": phone}

# Legacy wrapper
def send_notification(params):
    import asyncio
    agent = NotificationAgent()
    ctx = ToolContext(params)
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We are already in an async loop, so we should return a coroutine
        # But this function is defined as sync. 
        # If the caller is async (like OfferAgent -> A2A -> this), A2A should handle it.
        # However, A2A calls this as a sync function because it's a lambda/def.
        # We need to return the coroutine task if possible, or use a separate thread.
        # Since A2A supports async handlers, we should register the agent instance directly
        # in app.py instead of this wrapper, OR make this wrapper async.
        
        # For now, let's just return the coroutine and let A2A await it if it can,
        # or use a task. But A2A checks iscoroutinefunction.
        return agent.handle(ctx)
    else:
        return asyncio.run(agent.handle(ctx))
