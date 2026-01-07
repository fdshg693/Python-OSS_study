"""
カスタムエグゼキュータを使用したワークフローエージェントの例
1が2倍され、最終的に16になって10を超えるまで繰り返されます。
"""

from agent_framework import (
    AgentRunResponse,
    WorkflowAgent,
    WorkflowBuilder,
    Executor,
    WorkflowContext,
    ChatMessage,
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
        self, user_messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]
    ):
        """
        user_messagesで受け取った数字を2倍にして返します。
        返すために、contextのsend_messageを使用しています。
        また、2倍にした数字が10未満の場合は、再度user_messagesとして送り返し、
        10以上の場合は、そのまま返却しています。
        """
        doubled_number = int(user_messages[-1].text) * 2
        print(f"Doubled number: {doubled_number}")
        if doubled_number < 10:
            await ctx.send_message([ChatMessage(role="user", text=str(doubled_number))])
        else:
            return


number_double_executor: Executor = NumberDoubleExecutor(id="number_double_executor")
number_double_executor2: Executor = NumberDoubleExecutor(id="number_double_executor2")

workflowagent: WorkflowAgent = (
    WorkflowBuilder()
    .add_edge(source=number_double_executor, target=number_double_executor2)
    .add_edge(source=number_double_executor2, target=number_double_executor)
    .set_start_executor(number_double_executor)
    .build()
    .as_agent()
)


async def main():
    _response: AgentRunResponse = await workflowagent.run(
        ChatMessage(role="user", text="1")
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
