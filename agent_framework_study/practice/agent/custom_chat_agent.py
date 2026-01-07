"""
カスタムチャットクライアントからエージェント作成して、レスポンスを取得する例
"""

from typing import AsyncIterable
from agent_framework import (
    BaseChatClient,
    ChatResponse,
    ChatResponseUpdate,
    ChatMessage,
)
import asyncio

### ============== CustomChatClientの実装 ============== ###


class CustomChatClient(BaseChatClient):
    """
    BaseChatClientの継承のために、abstractメソッド_inner_get_responseと_inner_get_streaming_responseメソッドを実装する必要があります。
    この2つのメソッドを実装すると、get_responseおよびget_streaming_responseメソッドが利用可能になります。
    """

    async def _inner_get_response(
        self, *, messages, chat_options, **kwargs
    ) -> ChatResponse:
        """
        どんなプロンプトが来ても、常に"2"と返すカスタム実装の例
        """
        return ChatResponse(
            messages=[ChatMessage(role="assistant", text="2")],
            response_id="custom-response",
        )

    async def _inner_get_streaming_response(
        self, *, messages, chat_options, **kwargs
    ) -> AsyncIterable[ChatResponseUpdate]:
        """
        どんなプロンプトが来ても、常に"2"・"And that is 1+1."と順番に返すカスタム実装の例
        """
        from agent_framework import ChatResponseUpdate

        yield ChatResponseUpdate(
            role="assistant", contents=[{"type": "text", "text": "2"}]
        )
        print("Simulating delay before sending the next chunk...")
        await asyncio.sleep(5)  # Simulate some delay
        yield ChatResponseUpdate(
            role="assistant", contents=[{"type": "text", "text": "And that is 1+1."}]
        )


client = CustomChatClient(model_id="gpt-4o-mini")  # モデルIDは任意のものを指定可能

agent = client.create_agent(
    name="assistant", instructions="custom instructions", temperature=0.7
)


async def get_custom_response():
    # Run the agent
    response = await agent.run("Hello!")
    print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(get_custom_response())
