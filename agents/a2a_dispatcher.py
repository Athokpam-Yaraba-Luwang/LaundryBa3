# agents/a2a_dispatcher.py
import logging
from typing import Any, Dict

logger = logging.getLogger("a2a")
logger.setLevel(logging.INFO)

class A2ADispatcher:
    """
    Simple in-process A2A dispatcher. Register agent callables by name.
    In production this becomes a real A2A client (ADK or Agent Engine).
    """
    def __init__(self):
        self._registry = {}

    def register(self, name: str, fn):
        self._registry[name] = fn
        logger.info("Registered agent %s", name)

    async def call_agent(self, agent_name, params):
        if agent_name not in self._registry:
            raise ValueError(f"Agent {agent_name} not found")
        
        handler = self._registry[agent_name]
        # Support both async ADK agents and legacy sync functions
        if hasattr(handler, 'handle'):
            # ADK Agent class
            from google.adk.tools import ToolContext
            ctx = ToolContext(params)
            return await handler.handle(ctx)
        else:
            # Legacy function or lambda
            import asyncio
            if asyncio.iscoroutinefunction(handler):
                return await handler(params)
            return handler(params)

    # Alias for ADK compatibility
    async def call(self, agent_name, params):
        return await self.call_agent(agent_name, params)
