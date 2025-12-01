# agents/analytics_agents.py

from google.adk import Agent, AgentConfig
from google.adk.tools import ToolContext
import time

from google import genai

class RevenueAgent(Agent):
    def __init__(self, mem_bank):
        super().__init__(
            config=AgentConfig(
                name="revenue_agent",
                model="gemini-2.0-flash-exp",
                description="Analyzes revenue from orders",
            )
        )
        self.mem = mem_bank
        self.client = genai.Client()

    async def handle(self, ctx: ToolContext):
        timeframe = ctx.inputs.get("timeframe", "last_7_days")
        orders = self.mem.get_all_orders()
        
        total_revenue = sum(o.get('total', 0) for o in orders)
        
        # AI Analysis
        prompt = f"Analyze this revenue: ${total_revenue} for {timeframe}. Brief 1-sentence insight."
        try:
            response = self.client.models.generate_content(model="gemini-2.0-flash-exp", contents=prompt)
            ai_summary = response.text.strip()
        except Exception as e:
            print(f"Revenue Agent AI Error: {e}")
            ai_summary = f"Total Revenue is ${total_revenue}."

        return {"revenue_total": total_revenue, "timeframe": timeframe, "ai_summary": ai_summary}

class LogisticsAgent(Agent):
    def __init__(self, mem_bank):
        super().__init__(
            config=AgentConfig(
                name="logistics_agent",
                model="gemini-2.0-flash-exp",
                description="Analyzes logistics efficiency",
            )
        )
        self.mem = mem_bank
        self.client = genai.Client()

    async def handle(self, ctx: ToolContext):
        orders = self.mem.get_all_orders()
        if not orders:
            return {"efficiency": 100, "avg_turnaround": 0, "ai_summary": "No orders to analyze."}
            
        finished_count = sum(1 for o in orders if o['status'] in ['Finished', 'Delivered'])
        efficiency = int((finished_count / len(orders)) * 100) if orders else 100
        avg_turnaround = 24 
        
        # AI Analysis
        prompt = f"Analyze logistics: {efficiency}% efficiency, {avg_turnaround}h turnaround. Brief 1-sentence insight."
        try:
            response = self.client.models.generate_content(model="gemini-2.0-flash-exp", contents=prompt)
            ai_summary = response.text.strip()
        except Exception as e:
            print(f"Logistics Agent AI Error: {e}")
            ai_summary = f"Efficiency is {efficiency}%."

        return {"efficiency": efficiency, "avg_turnaround": avg_turnaround, "ai_summary": ai_summary}

class FeedbackAgent(Agent):
    def __init__(self, mem_bank):
        super().__init__(
            config=AgentConfig(
                name="feedback_agent",
                model="gemini-2.0-flash-exp",
                description="Analyzes customer feedback",
            )
        )
        self.mem = mem_bank
        self.client = genai.Client()

    async def handle(self, ctx: ToolContext):
        feedbacks = self.mem.get_all_feedback()
        if not feedbacks:
            return {"avg_rating": 0, "issues": [], "ai_summary": "No feedback yet."}
            
        ratings = [f['rating'] for f in feedbacks]
        avg_rating = sum(ratings) / len(ratings)
        issues = [f['comment'] for f in feedbacks if f['rating'] < 3 and f['comment']]
        
        # AI Analysis
        prompt = f"Analyze feedback. Avg Rating: {avg_rating:.1f}. Issues: {issues}. Summarize key pain points in 1 sentence."
        try:
            response = self.client.models.generate_content(model="gemini-2.0-flash-exp", contents=prompt)
            ai_summary = response.text.strip()
        except Exception as e:
            print(f"Feedback Agent AI Error: {e}")
            ai_summary = f"Avg Rating {avg_rating:.1f}. Issues: {len(issues)} found."
        
        return {"avg_rating": round(avg_rating, 1), "issues": issues, "ai_summary": ai_summary}
