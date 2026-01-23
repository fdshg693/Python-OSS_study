from typing import Annotated
from pydantic import Field


def add_nums(
    num1: Annotated[int, Field(description="1番目の数字")],
    num2: Annotated[int, Field(description="2番目の数字")],
) -> int:
    """2つの数字の合計を計算する"""
    print(f"{num1}と{num2}の合計を計算します")
    return num1 + num2


if __name__ == "__main__":
    print(add_nums.__name__)
