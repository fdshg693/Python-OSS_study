"""
openaiクライアントで、ツールを利用するサンプル
"""

from typing import Annotated
from pydantic import Field

from agent_framework.openai import OpenAIResponsesClient
from agent_framework import ChatResponse

openai_client = OpenAIResponsesClient(model_id="gpt-5-nano")


def get_square(
    number_string: Annotated[str, Field(description="number for square.")],
) -> str:
    """Get the square of a given number."""
    print(f"Calculating the square of {number_string}")
    try:
        number = int(number_string)
        return f"The square of {number} is {number * number}."
    except ValueError:
        return "Please provide a valid integer."


async def get_openai_response():
    """
    ツールを利用してレスポンスを取得する例
    """
    # get_responseメソッドにより、途中のツール呼び出しも含めた最終レスポンスを取得できる
    response: ChatResponse = await openai_client.get_response(
        messages="get square of 5", tools=[get_square]
    )
    print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(get_openai_response())
