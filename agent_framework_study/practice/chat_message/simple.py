"""
OpenAIChatClientを使って、チャットレスポンスを取得する例
"""

from agent_framework import ChatMessage, ChatResponse

from agent_framework.openai import OpenAIChatClient


async def main() -> None:
    client = OpenAIChatClient(model_id="gpt-5-nano")
    messages = [
        ChatMessage(role="user", text="私の名前は太郎です。"),
        ChatMessage(role="user", text="私の名前は何ですか？"),
    ]
    for msg in messages:
        print(f"User: {msg.text}")
    response: ChatResponse = await client.get_response(messages)
    print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
