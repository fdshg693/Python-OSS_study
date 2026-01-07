from agent_framework import ChatMessage, ChatAgent
from agent_framework.openai import OpenAIResponsesClient
from typing import Annotated
from pydantic import Field


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


async def single_agent_example():
    prompt = "what is the square of 5?"
    client = OpenAIResponsesClient(model_id="gpt-5-nano")

    math_agent: ChatAgent = client.create_agent(
        instructions=("call the tool to compute the square of a number "),
        name="math_agent",
        tools=[get_square],
    )

    result = await math_agent.run(messages=[ChatMessage(role="user", text=prompt)])
    print(result.text)


if __name__ == "__main__":
    import asyncio

    asyncio.run(single_agent_example())
