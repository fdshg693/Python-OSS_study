"""
カスタムエグゼキュータのサンプルコードです。
"""

import asyncio

from agent_framework import (
    handler,
    Executor,
    WorkflowContext,
    SharedState,
    InProcRunnerContext,
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


number_double_executor = NumberDoubleExecutor(id="number_double_executor")


async def main():
    runner_context = InProcRunnerContext()
    if number_double_executor.can_handle("5"):
        await number_double_executor.execute(
            message="5",
            source_executor_ids="number_double_executor",
            shared_state=SharedState(),
            runner_context=runner_context,
        )
    else:
        print("Executor cannot handle the input.")

    messages = await runner_context.drain_messages()
    print("Messages exchanged during execution:", messages)


if __name__ == "__main__":
    asyncio.run(main())
