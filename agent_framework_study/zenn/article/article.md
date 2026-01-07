---
title: "Agent Frameworkで始めるAzure OpenAI連携 - たった5行で動くチャットボットの裏側を理解する"
emoji: "🤖"
type: "tech"
topics: ["Python", "AzureOpenAI", "AgentFramework", "ChatBot"]
published: false
---

# はじめに

Agent FrameworkはMicrosoftが開発したPythonライブラリで、AIエージェントを簡単に構築できるフレームワークです。この記事では、わずか5行のコードで動作するAzure OpenAIチャットボットを題材に、その裏側で何が起きているのかを段階的に深掘りしていきます。

「動かせるけど仕組みが分からない」という初心者の方にこそ読んでいただきたい内容です。実際に動くコードから始めて、徐々に内部実装を理解していく構成になっています。

:::message
この記事で扱うAgent Frameworkのバージョン: 1.0.0b260106系
対象読者: Pythonの基本文法を理解している方、Azure OpenAIを使ってみたい方
:::

# 実際に動かしてみよう

まずは、実際に動くコードを見てみましょう。

```python
import asyncio
from agent_framework.azure import AzureOpenAIChatClient

async def main() -> None:
    # Azure OpenAIチャットクライアントの初期化
    # .envファイルからAPIキーやエンドポイントなどの設定を読み込む
    client = AzureOpenAIChatClient(env_file_path=".env")
    # AIに渡すメッセージ
    message = "1+1=?"
    print(f"User: {message}")
    # Azure OpenAIチャットクライアントを使って応答を取得
    response = await client.get_response(message)
    # AIの応答を表示
    print(f"Assistant: {response}")

if __name__ == "__main__":
    asyncio.run(main())
```

たったこれだけのコードで、Azure OpenAIとの対話が可能になります。
実行すると以下のような出力が得られます：

```
User: 1+1=?
Assistant: 2
```

## 必要な準備

このコードを動かすには、`.env`ファイルに以下の設定が必要です：

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_KEY=your-api-key-here
```

これで準備は完了です。しかし、このシンプルなコードの裏側では、実は複雑な処理が動いています。次のセクションから、その仕組みを紐解いていきましょう。

# コードの全体像を理解する

先ほどのコードは、実質的に3つのステップで構成されています：

## ステップ1: クライアントの初期化

```python
client = AzureOpenAIChatClient(env_file_path=".env")
```

この1行で、`.env`ファイルから設定を読み込み、Azure OpenAIと通信できる状態を作り出しています。

## ステップ2: 応答の取得

```python
response = await client.get_response(message)
```

この1行で、ユーザーのメッセージをAzure OpenAIに送信し、応答を受け取っています。

## ステップ3: 結果の表示

```python
print(f"Assistant: {response}")
```

取得した応答を表示しています。

一見シンプルですが、各ステップの裏側では、設定の読み込み、クライアントの構築、メッセージの変換、API呼び出しなど、多くの処理が隠蔽されています。

次のセクションから、これらの処理を1つずつ深掘りしていきます。

# 【深掘り①】env_file_pathで何が起きているのか

`env_file_path=".env"`という引数を渡すだけで、なぜ設定が読み込まれるのでしょうか？この仕組みを理解するには、Agent Frameworkの設定管理の階層構造を知る必要があります。

## 設定管理の階層構造

Agent Frameworkでは、以下のような階層で設定を管理しています：

```
Pydantic BaseSettings（基盤）
    ↑
AFBaseSettings（Agent Framework共通設定）
    ↑
AzureOpenAISettings（Azure OpenAI固有設定）
    ↑
AzureOpenAIChatClient（チャットクライアント）
```

### 各層の役割

1. **Pydantic BaseSettings**: 環境変数やファイルから設定を読み込む基本機能を提供
2. **AFBaseSettings**: Agent Framework全体で共通の設定管理を提供
3. **AzureOpenAISettings**: Azure OpenAI固有の設定項目を定義
4. **AzureOpenAIChatClient**: 実際に使用するクライアント

## 設定値の読み込み優先順位

Agent Frameworkでは、以下の優先順位で設定値が決定されます：

1. **コンストラクタ引数**: `AzureOpenAIChatClient(api_key="xxx")`で直接指定
2. **環境変数**: `os.environ`に設定された値
3. **.envファイル**: `env_file_path`で指定されたファイルから読み込み
4. **デフォルト値**: コード内で定義されたデフォルト値

このため、`.env`ファイルに設定があっても、環境変数が設定されていればそちらが優先されます。

## env_file_pathの伝播プロセス

`env_file_path`引数がどのように処理されるか、順を追って見ていきましょう。

### プロセス1: AzureOpenAIChatClientから設定オブジェクトへ

`AzureOpenAIChatClient`の`__init__`メソッドは、`env_file_path`を`AzureOpenAISettings`にそのまま渡します。

[azure\_chat_client.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/azure/_chat_client.py
```python
# 簡略化版
class AzureOpenAIChatClient(AzureOpenAIConfigMixin, OpenAIBaseChatClient):
    def __init__(self, env_file_path: str | None = None, ...):
        # azure_openai_settingsに.envから読み込まれた設定が格納される
        azure_openai_settings = AzureOpenAISettings(env_file_path=env_file_path, ...)
        ...
```

### プロセス2: AFBaseSettingsでのmodel_config設定

`AzureOpenAISettings`自体には`__init__`メソッドがないため、親クラスの`AFBaseSettings`が呼び出されます。

ここがポイントです。`AFBaseSettings`は`__new__`メソッドをオーバーライドしており、インスタンス生成前に`model_config`の`env_file`に`env_file_path`の値を設定します：

[azure\_pydantic.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/_pydantic.py
```python
# 簡略化版
class AFBaseSettings(BaseSettings):
    def __new__(cls: type["TSettings"], *args: Any, **kwargs: Any)
        ...

        # env_file_pathがキーワード引数にあれば取得
        if "env_file_path" in kwargs and kwargs["env_file_path"] is not None:
            env_file_path = kwargs["env_file_path"]

        ...
        # env_file_pathが上で設定されていれば、model_configを更新
        cls.model_config.update(env_file=env_file_path, ...)     

        ...
        return super().__new__(cls) 
```

この設定により、Pydanticの`BaseSettings`がmodel_config経由で`.env`ファイルから設定を読み込めるようになります。

#### __new__と__init__の役割分担

Pythonでは、オブジェクトの生成は2段階で行われます：

1. **__new__**: オブジェクトのメモリ領域を確保し、インスタンスを作成
2. **__init__**: 作成されたインスタンスを初期化

`AFBaseSettings`が`__new__`をオーバーライドしているのは、Pydanticの`BaseSettings`が`__init__`内で`model_config`を参照するためです。`__init__`が実行される前に`model_config`を書き換える必要があるため、より早い段階で実行される`__new__`を使っています。

これにより、「引数で渡されたファイルパスから設定を読み込む」という動作が実現されています。

### プロセス3: Pydantic BaseSettingsでの設定読み込み

最終的に、Pydantic の`BaseSettings`（[pydantic_settings\main.py]https://github.com/pydantic/pydantic-settings/blob/main/pydantic_settings/main.py）が`model_config`の`env_file`設定を参照し、指定されたファイルから設定値を読み込みます。

この処理は`_settings_build_values`メソッド内で行われ、ファイルから読み込まれた値がインスタンスのプロパティとして設定されます。

## なぜこのような設計なのか

この階層構造により、以下のメリットが得られます：

- **柔軟性**: 環境変数、設定ファイル、直接指定など、複数の方法で設定可能
- **フォールバック**: 環境変数がなければファイルから読み込むという優先順位を自動で処理
- **型安全性**: Pydanticによる型チェックとバリデーション

初心者には複雑に見えますが、「1つの引数で全てが動く」という使いやすさの裏には、このような設計思想があるのです。

# 【深掘り②】クライアントインスタンスの初期化プロセス

`.env`ファイルから設定が読み込まれた後、Azure OpenAIと通信できるクライアントインスタンスがどのように作られるのかを見ていきましょう。

## 設定値のマッピング

`AzureOpenAISettings`（調査ファイル：[azure\_shared.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/azure/_shared.py）では、`env_prefix`に`AZURE_OPENAI_`が設定されています。

また、親クラスの`AFBaseSettings`で`model_config`に`case_sensitive=False`が設定されているため、`.env`ファイルの項目は以下のように自動的にマッピングされます：

```
.envの項目                         → AzureOpenAISettingsのプロパティ
AZURE_OPENAI_ENDPOINT              → endpoint
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME  → chat_deployment_name
AZURE_OPENAI_API_KEY               → api_key
```

大文字・小文字を区別しないため、`.env`で`azure_openai_endpoint`と書いても動作します。

## クラス継承の全体像

実は、`AzureOpenAIChatClient`の継承構造は以下のようになっています：

```
AzureOpenAIChatClient
├─ AzureOpenAIConfigMixin (Azure固有の設定・初期化)
└─ OpenAIBaseChatClient (OpenAI API呼び出しの実装)
    └─ OpenAIBase (クライアントの保持)
        └─ BaseChatClient (共通インターフェース)
```

多重継承と継承チェーンの組み合わせにより、Azure固有の設定管理とOpenAI共通のAPI呼び出しロジックを両立しています。

## 初期化の連鎖

設定が読み込まれた後、以下の順序で初期化が進みます：

### ステップ1: AzureOpenAISettingsのインスタンス化

前述の通り、`.env`ファイルから必要な設定（endpoint、api_key、deployment_nameなど）が読み込まれ、`azure_openai_settings`インスタンスのプロパティとして格納されます。

[azure\_chat_client.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/azure/_chat_client.py
```python
# 簡略化版
class AzureOpenAIChatClient(AzureOpenAIConfigMixin, OpenAIBaseChatClient):
    def __init__(self, env_file_path: str | None = None, ...):
        
        # azure_openai_settingsに.envから読み込まれた設定が格納される
        azure_openai_settings = AzureOpenAISettings(env_file_path=env_file_path, ...)
        ...

        # 親クラスのAzureOpenAIConfigMixinの初期化を呼び出す
        # azure_openai_settingsに格納された.env設定の値を渡す
        super().__init__(
            deployment_name=azure_openai_settings.chat_deployment_name,
            endpoint=azure_openai_settings.endpoint,
            api_key=azure_openai_settings.api_key.get_secret_value() if azure_openai_settings.api_key else None,
            ...
        )
```

### ステップ2: AzureOpenAIConfigMixinの初期化

`AzureOpenAIChatClient`は`AzureOpenAIConfigMixin`を継承しています。この`Mixin`（ミックスイン：複数のクラスに共通の機能を提供するクラス）の`__init__`メソッドで、Azure OpenAI用のクライアントが生成されます：

[azure\_shared.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/azure/_shared.py
```python
# 簡略化版
class AzureOpenAIConfigMixin(OpenAIBase):
    def __init__(
        self,
        deployment_name: str,
        endpoint: HTTPsUrl | None = None,
        api_key: str | None = None,
        ...
    ):
        # clientが引数で渡されなければ、新規作成（今回のケース）
        if not client:
            ...            
            # argsに格納されたapi_keyやendpointを使ってクライアントを生成
            client = AsyncAzureOpenAI(**args)

        ...
        # 親クラスのOpenAIBaseの初期化を呼び出す
        super().__init__(client=client)
```

ここで作成される`AsyncAzureOpenAI`は、OpenAI公式SDKが提供する非同期クライアントです。

### ステップ3: OpenAIBaseでのクライアント登録

さらに`super().__init__(client=client)`によって、`OpenAIBase`クラスの初期化が呼び出されます：

[azure\openai\_shared.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/openai\_shared.py
```python
# 簡略化版
class OpenAIBase(SerializationMixin):
    def __init__(self, client: AsyncOpenAI | None = None, ...):
        self.client = client
    ...
```

この`self.client`に格納されたインスタンスが、後述する`get_response`メソッド内でAzure OpenAI APIの呼び出しに使用されます。

## 初期化フローのまとめ

全体の流れを図式化すると、以下のようになります：

```
1. AzureOpenAIChatClient.__init__(env_file_path=".env")
   ↓
2. AzureOpenAISettings(env_file_path=".env")
   ↓ (.envから設定を読み込み)
3. AzureOpenAIConfigMixin.__init__()
   ↓ (AsyncAzureOpenAIを生成)
4. OpenAIBase.__init__(client=client)
   ↓ (self.clientに登録)
5. 初期化完了 → get_response()で使用可能に
```

複数のクラスが連携して、「たった1行のコード」を実現しているのです。

# 【深掘り③】get_responseメソッドの処理フロー

実際にメッセージを送信し、応答を取得する`get_response`メソッドの内部処理を追っていきましょう。

## メソッドの引数の柔軟性

`get_response`メソッドは、様々な形式でメッセージを受け取れます：

```python
# 全て有効な呼び出し方
response = await client.get_response("こんにちは")  # str
response = await client.get_response(chat_message)  # ChatMessage
response = await client.get_response(["こんにちは", "元気？"])  # list[str]
response = await client.get_response([msg1, msg2])  # list[ChatMessage]
```

型定義を見ると、`messages: str | ChatMessage | list[str] | list[ChatMessage]`となっており、初心者には文字列で、上級者には詳細な制御が可能な設計になっています。

## 処理フローの全体像

`get_response`の処理は、以下の5つのステップで構成されています：

### ステップ1: BaseChatClientのget_responseが呼ばれる

`AzureOpenAIChatClient`は`get_response`メソッドを定義していません。そのため、親クラスの`BaseChatClient`のメソッドが呼び出されます。

[azure\_clients.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/_clients.py
```python
# 簡略化版
class BaseChatClient(SerializationMixin, ABC):
    async def get_response(
        self,
        messages: str | ChatMessage | list[str] | list[ChatMessage],
        ...
    ) -> ChatResponse:
        ...

        # メッセージの正規化
        # str, ChatMessage, list[str], list[ChatMessage] → list[ChatMessage]
        prepped_messages = prepare_messages(messages)

        # 実際の応答生成（サブクラスで実装、今回だとOpenAIBaseChatClientの実装が呼ばれる）
        return await self._inner_get_response(messages=prepped_messages, ...)
```

### ステップ2: prepare_messagesでメッセージを正規化

`prepare_messages`メソッドは、様々な形式の入力を`list[ChatMessage]`型に統一します：

```python
# prepare_messagesの処理イメージ
"こんにちは" 
  → [ChatMessage(role="user", content="こんにちは")]
  
["こんにちは", "元気？"]
  → [ChatMessage(role="user", content="こんにちは"),
     ChatMessage(role="user", content="元気？")]
```

この正規化により、後続の処理を統一的に扱えるようになります。

#### prepare_messagesの詳細な役割

`prepare_messages`は単なる型変換だけでなく、以下の重要な処理も行います：

1. **デフォルトroleの設定**: 文字列だけ渡された場合、自動的に`role="user"`を設定
2. **メッセージチェーンの検証**: システムメッセージが適切な位置にあるかチェック
3. **シリアライゼーション**: `ChatMessage`オブジェクトをAPIが受け付ける辞書形式に変換

これにより、開発者は細かい形式を気にせず、メッセージを柔軟に渡せるようになっています。

### ステップ3: _inner_get_responseで実装クラスへ委譲

`_inner_get_response`は`BaseChatClient`で抽象メソッド（必ずサブクラスで実装しなければならないメソッド）として定義されています。

`AzureOpenAIChatClient`自体は`_inner_get_response`を定義していませんが、`OpenAIBaseChatClient`を継承しているため、その実装が使われます。

### ステップ4: OpenAIBaseChatClientでAPI呼び出し

`OpenAIBaseChatClient`の`_inner_get_response`で、実際のAPI呼び出しが行われます：

[azure\openai\_chat_client.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/openai\_chat_client.py
```python
# 簡略化版
# 一部分かりやすさのため、変更（completionという中間変数は本来なら存在しないが、ここでは説明のために使用）
class OpenAIBaseChatClient(OpenAIBase, BaseChatClient):
    async def _inner_get_response(
        self,
        messages: MutableSequence[ChatMessage],
        ...
    ) -> ChatResponse:
        # messagesを含むAIへのリクエストのオプションを準備
        options_dict = self._prepare_options(messages, ...)
        ...
        
        # Azure OpenAI APIを呼び出し
        # AzureOpenAIChatClient初期化時に登録されたself.clientを使用
        completion = await self.client.chat.completions.create(
            stream=False,
            **options_dict
        )
        ...
        
        # 結果をChatResponse型に変換
        return self._create_chat_response(completion, ...)
```

ここで使われる`self.client`は、前述の初期化プロセスで作成された`AsyncAzureOpenAI`インスタンスです。

### ステップ5: _create_chat_responseで結果を整形

APIから返された生の応答（`ChatCompletion`オブジェクト）を、Agent Frameworkの`ChatResponse`型にラップします：
この`ChatResponse`オブジェクトは、そのまま文字列として扱うこともできるため、`print(response)`で簡単に内容を表示できます。

#### SerializationMixinの役割

`ChatResponse`は`SerializationMixin`を継承しており、以下の機能を持ちます：

- **to_dict()**: 辞書形式に変換（JSONシリアライゼーション用）
- **to_json()**: JSON文字列に変換
- **__str__()**: 文字列表現（`content`フィールドを返す）

これにより、開発者は必要に応じて詳細な情報にアクセスしたり、簡単に文字列として扱ったりできます。`print(response)`が直感的に動作するのは、この`__str__()`実装のおかげです。

## 処理フローの図解

全体の流れをまとめると：

```
1. client.get_response("1+1=?")
   ↓
2. BaseChatClient.get_response()
   ↓ prepare_messages()
3. messages正規化: "1+1=?" → [ChatMessage(role="user", content="1+1=?")]
   ↓ _inner_get_response()
4. OpenAIBaseChatClient._inner_get_response()
   ↓ _prepare_options()
5. options準備: {"messages": [{"role": "user", "content": "1+1=?"}], ...}
   ↓ client.chat.completions.create()
6. Azure OpenAI API呼び出し
   ↓ (ネットワーク通信)
7. API応答: ChatCompletion(choices=[...])
   ↓ _create_chat_response()
8. ChatResponse(content="2", ...)
   ↓
9. return response
```

## 重要なポイント

この設計で注目すべきは、**責務の分離**です：

- `BaseChatClient`: 入力の正規化や共通処理
- `OpenAIBaseChatClient`: OpenAI/Azure OpenAI固有の処理
- `AzureOpenAIChatClient`: Azure固有の設定と初期化

各クラスが明確な役割を持つことで、コードの保守性と拡張性が高まっています。

# Agent Frameworkの設計思想

ここまで見てきた内部実装から、Agent Frameworkの設計思想が見えてきます。

## 1. 階層的な抽象化

Agent Frameworkは、以下のような階層構造で抽象化されています：

```
レイヤー          役割                     例
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
使用者レイヤー    シンプルなAPI           get_response("こんにちは")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
抽象レイヤー      共通インターフェース    BaseChatClient
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
プロバイダー層    プロバイダー固有処理    OpenAIBaseChatClient
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
実装レイヤー      具体的な実装           AzureOpenAIChatClient
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SDKレイヤー       外部SDKの呼び出し      AsyncAzureOpenAI
```

この階層化により、「使う時はシンプル、拡張する時は柔軟」という両立が実現されています。

## 2. Mixin パターンの活用

`AzureOpenAIConfigMixin`のように、Mixinパターン（複数のクラスに共通機能を追加する手法）を活用することで、コードの再利用性を高めています。

Azure OpenAIの設定管理は、チャットだけでなく、エージェントや他の機能でも共通して使えます。

## 3. 型安全性とバリデーション

Pydanticを基盤とすることで、以下のメリットを享受しています：

- **型チェック**: 設定値の型が間違っていれば実行時にエラー
- **バリデーション**: 必須項目が欠けていれば明確なエラーメッセージ
- **自動変換**: 文字列→数値などの変換を自動で実行

## 4. 非同期処理の標準化

全てのAPIが`async/await`を前提としており、現代的な非同期プログラミングに対応しています。これにより、複数のAI呼び出しを並行実行するなど、高度な処理も書きやすくなっています。

## 5. 柔軟な入力と一貫した出力

`get_response`が`str | ChatMessage | list[str] | list[ChatMessage]`を受け取れる設計は、**Progressive Disclosure**（段階的な情報開示）という設計原則に基づいています。

初心者は文字列だけで使い始め、慣れてきたら詳細な制御（会話履歴の管理、システムプロンプトの設定など）に進めます。

一方、出力は常に`ChatResponse`型で統一されており、予測可能な動作を保証しています。

# まとめ

この記事では、わずか5行のコードから始めて、Agent Frameworkの内部実装を深掘りしてきました。

## 学んだこと

1. **env_file_pathの仕組み**: Pydanticの`BaseSettings`を基盤とした階層的な設定管理
2. **初期化プロセス**: 設定の読み込みからクライアントインスタンスの生成まで
3. **get_responseの処理フロー**: メッセージの正規化、API呼び出し、結果の整形
4. **設計思想**: 階層的な抽象化、Mixinパターン、型安全性、非同期処理

## シンプルなAPIの裏側

たった5行のコードの裏側では、以下のような処理が動いていました：

- 設定ファイルのパース
- 環境変数とのマッピング
- クライアントインスタンスの生成
- メッセージ型の正規化
- API呼び出し
- 結果の型変換

これら全てが隠蔽されているからこそ、初心者でもすぐに使い始められるのです。

## 参考リソース

### 調査で参照したファイル

- [azure\_chat_client.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/azure/_chat_client.py
- [azure\_shared.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/azure/_shared.py
- [azure\_pydantic.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/_pydantic.py
- [azure\_clients.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/_clients.py
- [azure\openai\_chat_client.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/openai\_chat_client.py
- [azure\openai\_shared.py]https://github.com/microsoft/agent-framework/blob/main/python/packages/core/agent_framework/openai\_shared.py
- [pydantic_settings\main.py]https://github.com/pydantic/pydantic-settings/blob/main/pydantic_settings/main.py

### 公式ドキュメント

- [Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [Pydantic Settings GitHub](https://github.com/pydantic/pydantic-settings)

---

最後まで読んでいただき、ありがとうございました！
Agent Frameworkは、シンプルさと柔軟性を両立した優れた設計になっています。この記事が、フレームワークへの理解を深めるきっかけになれば幸いです。
質問やフィードバックがあれば、コメント欄でお気軽にどうぞ。
