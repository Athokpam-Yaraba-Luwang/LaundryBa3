# google/adk/tools/__init__.py
import asyncio

class Tool:
    pass

class ToolContext:
    def __init__(self, inputs, tool_runner=None, a2a_client=None):
        self.inputs = inputs
        self._tool_runner = tool_runner
        self._a2a_client = a2a_client

    async def call_tool(self, tool_name, args):
        if self._tool_runner:
            return await self._tool_runner(tool_name, args)
        return {}

    async def sleep(self, seconds):
        await asyncio.sleep(seconds)
