"""
OpenAIChatClientを使って、チャットレスポンスを取得する例
"""

from agent_framework.openai import OpenAIChatClient


async def main() -> None:
    client = OpenAIChatClient(model_id="gpt-5-nano")
    message = "1+2"
    print(f"User: {message}")
    print("Assistant: ", end="")
    response = await client.get_response(message)
    print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
