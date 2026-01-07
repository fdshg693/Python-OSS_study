from agent_framework import (
    BaseChatClient,
    ChatResponse,
    ChatMessage,
    ChatAgent,
    AIFunction,
    ChatResponseUpdate,
)

from pydantic import BaseModel


class CustomChatClient(BaseChatClient):
    async def _inner_get_response(self, *, messages, chat_options, **kwargs):
        # as_toolでstream_callbackが指定されなかった場合に呼ばれます
        return ChatResponse(
            messages=[ChatMessage(role="assistant", text="2")],
            response_id="custom-response",
        )

    async def _inner_get_streaming_response(self, *, messages, chat_options, **kwargs):
        # as_toolの際に、stream_callbackが指定された場合に呼ばれます
        yield ChatResponseUpdate(
            role="assistant", contents=[{"type": "text", "text": "2"}]
        )
        yield ChatResponseUpdate(
            role="assistant", contents=[{"type": "text", "text": "And that is 1+1."}]
        )


# Create an instance of your custom client
custom_client = CustomChatClient()

# Create an agent
agent = ChatAgent(
    chat_client=custom_client,
    name="custom_agent",
    description="A custom agent that answers simple math questions",
)

# Convert the agent to a tool
custom_agent_tool: AIFunction[BaseModel, str] = agent.as_tool(
    # stream_callbackでコールバックを指定すると、ストリーミングモードで動作します
    stream_callback=None,
)


async def main():
    result = await custom_agent_tool.invoke(query="What is 1+1?")
    print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
