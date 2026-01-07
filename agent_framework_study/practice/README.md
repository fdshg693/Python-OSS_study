# Practice Scripts

agent_frameworkの学習用スクリプト集です。

## フォルダ構成

### 📁 chat/
基本的なChatClientの使い方を学ぶサンプル
- `simple_chat.py` - カスタムChatClientの作成、OpenAIクライアントの基本使用

### 📁 agent/
エージェントの作成と活用を学ぶサンプル
- `chat_agent_instance.py` - ChatAgent、BaseAgentの作成と実行
- `agent_chat.py` - ミドルウェア、ツール付きエージェント
- `agent_as_tool.py` - エージェントをツールとして使用する方法

### 📁 workflow/
ワークフローの構築を学ぶサンプル
- `workflow_agent.py` - シンプルなワークフローの構築
- `review_workflow.py` - レビュープロセス付きワークフロー（Executor間の連携）

### 📁 structured_output/
構造化出力を学ぶサンプル
- `structured_output.py` - Pydanticモデルを使った構造化出力
