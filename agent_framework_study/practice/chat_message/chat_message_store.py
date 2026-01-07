"""
ChatMessageStoreの使い方の例
"""

from agent_framework import ChatMessage, ChatMessageStore


async def main() -> None:
    message_store = ChatMessageStore()
    await message_store.add_messages(
        [ChatMessage(role="system", content="You are a helpful assistant.")]
    )
    await message_store.add_messages(
        [ChatMessage(role="user", content="Hello, who won the world series in 2020?")]
    )
    message_list: list[ChatMessage] = await message_store.list_messages()
    for msg in message_list:
        print(f"{msg.role}: {msg.additional_properties['content']}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
