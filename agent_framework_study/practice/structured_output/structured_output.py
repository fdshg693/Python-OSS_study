import asyncio

from agent_framework.openai import OpenAIResponsesClient
from pydantic import BaseModel


class Language(BaseModel):
    """A structured output for testing purposes."""

    language: str
    difficulty: str


async def simple_structure_example() -> None:
    language_detection_agent = OpenAIResponsesClient(
        model_id="gpt-5-nano"
    ).create_agent(
        name="LanguageDetectionAgent",
        instructions="Determine the language, and its difficulty level from the given text.",
    )

    input_text = "Ich bin in Paris."
    print(f"User: {input_text}")

    result = await language_detection_agent.run(input_text, response_format=Language)

    if result.value:
        detected_language: Language = result.value  # type: ignore
        print("Assistant Structured Output:")
        print(f"Language: {detected_language.language}")
        print(f"Difficulty: {detected_language.difficulty}")
    else:
        print("Error: No structured data found in result.value")


async def main() -> None:
    await simple_structure_example()


if __name__ == "__main__":
    asyncio.run(main())
