"""
BaseAgentを継承してカスタムエージェントを作成するサンプルコードです。
"""

from agent_framework import (
    ChatMessage,
    BaseAgent,
    AgentRunResponse,
    AgentRunResponseUpdate,
)


class SimpleAgent(BaseAgent):
    async def run(self, messages=None, *, thread=None, **kwargs):
        # Custom implementation
        msg = ChatMessage(role="assistant", text="This is a simple agent.")
        return AgentRunResponse(messages=[msg], response_id="simple-response")

    def run_stream(self, messages=None, *, thread=None, **kwargs):
        async def _stream():
            # Custom streaming implementation
            yield AgentRunResponseUpdate()

        return _stream()


async def run_simple_agent_example():
    # Create a simple agent
    agent = SimpleAgent(name="my-agent", description="A simple agent implementation")

    # Run the simple agent with a message
    response = await agent.run("Hello, simple agent!")
    print(response.text)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_simple_agent_example())
