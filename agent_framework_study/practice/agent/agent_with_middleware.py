"""
エージェントミドルウェアを使用するサンプルコードです。
"""

from agent_framework import ChatMessage, ChatAgent, AgentMiddleware, AgentRunContext
from agent_framework.openai import OpenAIResponsesClient


class LoggingMiddleware(AgentMiddleware):
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    async def process(self, context: AgentRunContext, next):
        print("Starting agent run with LoggingMiddleware")
        await next(context)


async def middleware_example():
    client = OpenAIResponsesClient(model_id="gpt-5-nano")

    logging_agent: ChatAgent = client.create_agent(
        instructions="you are helpful",
        name="logging_agent",
        middleware=LoggingMiddleware(max_retries=2),
    )

    result = await logging_agent.run(
        messages=[ChatMessage(role="user", text="What is the square of 4?")]
    )
    print(result.text)


if __name__ == "__main__":
    import asyncio

    asyncio.run(middleware_example())
