"""
スレッドを使ってコンテキストを保持するエージェントの例
"""

from agent_framework import AgentThread
from agent_framework.openai import OpenAIResponsesClient

# Create a client
client = OpenAIResponsesClient(model_id="gpt-5-nano")
thread = AgentThread()
agent = client.create_agent(name="Assistant")


async def run_agent_with_thread():
    # First turn
    response1 = await agent.run("My name is Alice. Just answer OK", thread=thread)
    print("First turn response:")
    print(response1)

    # Second turn (agent remembers context)
    response2 = await agent.run("What's my name?", thread=thread)
    print("Second turn response:")
    print(response2)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_agent_with_thread())
