# User: ツールを使って1+1を計算して
# 1と1の合計を計算します
# Assistant: 1 + 1 の計算結果は 2 です。

import asyncio

from agent_framework.azure import AzureOpenAIChatClient

from typing import Annotated
from pydantic import Field


def add_nums(
    num1: Annotated[int, Field(description="1番目の数字")],
    num2: Annotated[int, Field(description="2番目の数字")],
) -> int:
    """2つの数字の合計を計算する"""
    print(f"{num1}と{num2}の合計を計算します")
    return num1 + num2


async def main() -> None:
    client = AzureOpenAIChatClient(env_file_path=".env")
    message = "1+1をツールを使って計算して"
    print(f"User: {message}")
    response = await client.get_response(message, tools=add_nums, tool_choice="auto")
    print(f"Assistant: {response}")


if __name__ == "__main__":
    asyncio.run(main())
