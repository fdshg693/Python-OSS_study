"""
カスタムエグゼキュータを使用したワークフローエージェントの例
"""

from agent_framework import (
    AgentRunResponse,
    Workflow,
    WorkflowBuilder,
    Executor,
    WorkflowContext,
    handler,
)


class NumberDoubleExecutor(Executor):
    """
    数字を受け取り、その数字を2倍にして返すエグゼキュータのサンプルコードです。
    """

    def __init__(self, id: str) -> None:
        super().__init__(id=id)

    @handler
    async def handle_user_messages(
        self, user_messages: str, ctx: WorkflowContext[str]
    ) -> None:
        """
        user_messagesで受け取った数字を2倍にして返します。
        返すために、contextのsend_messageを使用しています。
        """
        input_number = int(user_messages[-1])

        doubled_number = input_number * 2
        print(f"Doubled number: {doubled_number}")
        await ctx.send_message(str(doubled_number))
        return


number_double_executor: Executor = NumberDoubleExecutor(id="number_double_executor")

workflow: Workflow = (
    WorkflowBuilder().set_start_executor(number_double_executor).build()
)


async def main():
    response: AgentRunResponse = await workflow.run(message="5")

    print("Final Response:", response.text)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
