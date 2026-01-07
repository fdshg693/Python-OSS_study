"""
AgentThreadインスタンスに直接メッセージを追加する例
"""

from agent_framework import AgentThread, ChatMessage
from agent_framework.openai import OpenAIResponsesClient

# Create a client
client = OpenAIResponsesClient(model_id="gpt-5-nano")
thread = AgentThread()
agent = client.create_agent(name="Assistant")


async def run_agent_with_thread():
    # First turn
    await thread.on_new_messages(ChatMessage(role="user", text="X=2"))
    await thread.on_new_messages(ChatMessage(role="user", text="Y=4"))

    thread_serialize = await thread.serialize()
    print("Serialized thread:")
    print(thread_serialize)

    response = await agent.run("X+Y=?", thread=thread)
    print("Response:")
    print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_agent_with_thread())
