# google/adk/a2a/__init__.py

class A2AClient:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    async def call(self, agent_name, inputs):
        return await self.dispatcher.call_agent(agent_name, inputs)
