# google/adk/__init__.py

class AgentConfig:
    def __init__(self, name, model, description, system_instruction=None, tools=None):
        self.name = name
        self.model = model
        self.description = description
        self.system_instruction = system_instruction
        self.tools = tools or []

class Agent:
    def __init__(self, config: AgentConfig):
        self.config = config

    async def handle(self, ctx):
        raise NotImplementedError
