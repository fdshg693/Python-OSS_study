"""
openaiクライアントで、responseAPIを利用するサンプル
"""

from agent_framework.openai import OpenAIResponsesClient

openai_client = OpenAIResponsesClient(model_id="gpt-5-nano")


async def get_openai_response():
    """
    単純なレスポンスを取得する例
    """
    response = await openai_client.get_response("1+1")
    print(response)


def print_client_info():
    """
    クライアント情報を辞書形式で表示する例
    """
    client_info = openai_client.to_dict()
    print(client_info)


if __name__ == "__main__":
    print_client_info()
