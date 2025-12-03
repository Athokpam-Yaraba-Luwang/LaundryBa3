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
        
        # Initialize Gemini for message generation
        import google.generativeai as genai
        import os
        self.genai = genai
        if os.environ.get("GEMINI_API_KEY"):
            self.genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            self.model = self.genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None

    async def handle(self, ctx: ToolContext):
        phone = ctx.inputs.get("phone")
        msg = ctx.inputs.get("message") or ctx.inputs.get("msg")
        
        # If no explicit message, generate one based on context
        if not msg and ctx.inputs.get("type") == "order_update":
            status = ctx.inputs.get("status")
            order_id = ctx.inputs.get("order_id")
            
            if self.model:
                try:
                    prompt = f"""
                    You are a witty, friendly laundry assistant (like the Duolingo owl but for laundry).
                    Write a SHORT, FUN push notification for Order #{order_id} which is now '{status}'.
                    Use emojis. Be encouraging or slightly dramatic but cute.
                    Max 15 words.
                    """
                    response = self.model.generate_content(prompt)
                    msg = response.text.strip()
                except Exception as e:
                    print(f"[NotificationAgent] Generation failed: {e}")
                    msg = f"Your order {order_id} is {status}! 🧺"
            else:
                msg = f"Your order {order_id} is {status}! 🧺"

        # In real ADK: return await ctx.call_tool("push_notify_tool", {"phone":phone, "msg":msg})
        # For our shim/demo:
        print(f"[NotificationAgent] Sending to {phone}: {msg}")
        
        # Save to memory bank so it can be fetched by UI
        # We need access to memory bank. In this shim, we can import the global one or pass it in.
        # Ideally passed in init, but for quick fix we can import from app context or similar.
        # But since this is an Agent class, let's try to get it from the tool context or import.
        # Actually, let's just import the MemoryBank class and instantiate it (it handles singleton/connection logic)
        # OR better, pass it in constructor if possible.
        # Given the constraints, let's import the global 'mem' from business_app.app if running there, 
        # but this agent might run in isolation.
        # SAFEST: Re-instantiate MemoryBank (it connects to same DB/Firestore)
        try:
            from agents.memory_bank import MemoryBank
            mem = MemoryBank()
            mem.save_notification(phone, msg)
        except Exception as e:
            print(f"[NotificationAgent] Failed to save notification: {e}")

        return {"status": "sent", "recipient": phone, "message": msg}

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
