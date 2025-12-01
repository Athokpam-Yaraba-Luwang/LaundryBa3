# agents/offer_agent.py
from google.adk import Agent, AgentConfig
from google.adk.tools import ToolContext
import random, string
from typing import Dict

def _code():
    return ''.join(random.choice("ABCDEFGH0123456789") for _ in range(6))

class OfferAgent(Agent):
    def __init__(self, memory_bank, a2a):
        super().__init__(
            config=AgentConfig(
                name="offer_agent",
                model="gemini-2.0-flash-exp",
                description="Generates personalized offers",
                system_instruction="""
                Use long-term memory to generate best possible offer.
                """,
            )
        )
        self.mem = memory_bank
        self.a2a = a2a

    async def handle(self, ctx: ToolContext):
        phone = ctx.inputs["phone"]
        profile = self.mem.get_customer(phone) or {}

        # Check if we already gave an offer recently (simple check: if any unused offer exists)
        existing_offers = self.mem.get_redeems_by_phone(phone)
        unused_offers = [o for o in existing_offers if not o.get('used', False)]
        
        if len(unused_offers) > 0:
            # User already has an active offer, don't spam
            return {"status": "skipped", "reason": "Active offer exists"}

        # Simple logic for demo
        avg_spend = profile.get("avg_spend", 0)
        # Only give offer if spend > 0 (returning customer) or random chance
        import random
        if avg_spend == 0 and random.random() > 0.3:
             return {"status": "skipped", "reason": "New user, no spend history"}

        discount = "20% OFF" if avg_spend > 500 else "10% OFF"
        code = _code()

        self.mem.save_redeem(code, phone, {"discount":discount, "used":False, "type": "personal"})

        # Call Notification Agent via A2A
        await self.a2a.call("notification_agent", {
            "phone": phone, "message": f"You earned {discount}! Use code {code}"
        })

        return {"code":code, "discount":discount}

    # Legacy method
    def generate_personalized_offer(self, phone):
        import asyncio
        ctx = ToolContext({"phone": phone})
        return asyncio.run(self.handle(ctx))

    def generate_first_time_code(self, phone: str) -> str:
        # Simple logic for first time code
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        code = f"WELCOME-{suffix}"
        self.mem.save_redeem(code, phone, {"type":"first_time", "used": False, "discount": "15% OFF"})
        return code
