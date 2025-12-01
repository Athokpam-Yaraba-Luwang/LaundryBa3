# agents/analytics_orchestrator.py

from google.adk import Agent, AgentConfig
from google.adk.tools import ToolContext
import asyncio

class AnalyticsOrchestrator(Agent):
    def __init__(self, a2a):
        super().__init__(
            config=AgentConfig(
                name="analytics_orchestrator",
                model="gemini-2.0-flash-exp",
                description="Runs parallel revenue/logistics/feedback agents.",
                system_instruction="Aggregate all agent outputs.",
            )
        )
        self.a2a = a2a

    async def handle(self, ctx: ToolContext):
        timeframe = ctx.inputs.get("timeframe", "last_7_days")

        # Parallel execution using A2A
        revenue_task = self.a2a.call("revenue_agent", {"timeframe": timeframe})
        logistics_task = self.a2a.call("logistics_agent", {"timeframe": timeframe})
        feedback_task = self.a2a.call("feedback_agent", {"timeframe": timeframe})

        try:
            revenue, logistics, feedback = await asyncio.gather(
                revenue_task, logistics_task, feedback_task
            )
        except Exception as e:
            print(f"Analytics Error: {e}")
            revenue, logistics, feedback = {}, {}, {}

        # Format for frontend
        summary = {
            "timeframe": timeframe,
            "revenue_analysis": revenue.get("ai_summary") or f"Total Revenue: ${revenue.get('revenue_total', 0)}",
            "logistics_analysis": logistics.get("ai_summary") or f"Efficiency: {logistics.get('efficiency', 0)}% (Avg Turnaround: {logistics.get('avg_turnaround', 0)}h)",
            "feedback_analysis": feedback.get("ai_summary") or f"Avg Rating: {feedback.get('avg_rating', 0)} stars. Issues: {', '.join(feedback.get('issues', [])) or 'None'}"
        }
        return summary

    # Legacy method
    def run_all(self, timeframe="last_7_days"):
        import asyncio
        ctx = ToolContext({"timeframe": timeframe})
        return asyncio.run(self.handle(ctx))
