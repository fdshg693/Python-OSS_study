"""
明示的にAI用の関数を作成するサンプルコードです。
実際はこのような形をとらずとも、普通の関数をAIに渡すだけでAI用関数として扱うことができます。
"""

from typing import Annotated
from pydantic import BaseModel, Field
from agent_framework import AIFunction, ai_function


# ========================
# Example usage of AIFunction with decorator
# ========================
@ai_function
def add(
    a: Annotated[int, "First number"],
    b: Annotated[int, "Second number"],
) -> int:
    """Add two numbers."""
    return a + b


async def decorator_example():
    # Invoke the function
    result = await add.invoke(a=3, b=5)
    print(result)


# ========================
# Example usage of AIFunction with class-based input model
# ========================
class AddArgs(BaseModel):
    a: Annotated[int, Field(description="First number")]
    b: Annotated[int, Field(description="Second number")]


add_func = AIFunction(
    name="add",
    description="Add two numbers",
    func=lambda a, b: a + b,
    approval_mode="never_require",
    input_model=AddArgs,
)


async def class_example():
    # Invoke the function
    result = await add_func.invoke(arguments=AddArgs(a=3, b=5))
    print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(class_example())
