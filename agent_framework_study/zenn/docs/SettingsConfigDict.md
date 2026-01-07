## SettingsConfigDictとは

`SettingsConfigDict`は、`pydantic-settings`ライブラリにおいて`BaseSettings`クラスの振る舞いを制御するための型付き辞書（TypedDict）です。環境変数の読み込み方法、`.env`ファイルの処理、バリデーションの挙動などを細かく設定できます。

Pydantic v2以降、設定は`model_config`クラス属性に`SettingsConfigDict`を渡す形式に統一されました。

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    debug: bool = False
    database_url: str
    api_key: str
```

## 主要なオプション

### 環境変数関連

```python
model_config = SettingsConfigDict(
    # 環境変数のプレフィックス（APP_DEBUG, APP_DATABASE_URLなど）
    env_prefix="APP_",
    
    # ネストしたモデルの区切り文字（デフォルト: "__"）
    env_nested_delimiter="__",
    
    # 環境変数名の大文字小文字を無視
    case_sensitive=False,  # デフォルト
)
```

`env_nested_delimiter`は階層構造を持つ設定で重要です：

```python
class DatabaseSettings(BaseModel):
    host: str
    port: int

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")
    db: DatabaseSettings

# 環境変数: DB__HOST=localhost, DB__PORT=5432
```

### .envファイル関連

```python
model_config = SettingsConfigDict(
    # 単一ファイルまたは複数ファイル（優先度順）
    env_file=(".env.local", ".env"),
    
    env_file_encoding="utf-8",
    
    # ファイルが存在しない場合のエラーを無視
    env_ignore_empty=True,
    
    # 追加の環境変数を無視せず読み込む
    extra="ignore",  # "allow", "forbid"も選択可
)
```

### シークレット管理

```python
model_config = SettingsConfigDict(
    # Docker Secretsなどのファイルベースシークレット
    secrets_dir="/run/secrets",
)

# /run/secrets/api_key ファイルの内容が api_key フィールドに読み込まれる
```

### バリデーション制御

```python
model_config = SettingsConfigDict(
    # 厳密な型検証
    strict=True,
    
    # バリデーションエラー時の挙動
    validate_default=True,
    
    # JSON文字列の自動パース（リストや辞書を環境変数で渡す場合）
    json_parse_env_vars=True,  # '["a","b"]' → ["a", "b"]
)
```

## 設定の読み込み優先順位

`BaseSettings`は複数のソースから値を読み込み、以下の優先順位で解決します（上が優先）：

```
1. コンストラクタに直接渡された引数
2. 環境変数
3. .envファイル
4. secrets_dirのファイル
5. フィールドのデフォルト値
```

この順序はカスタマイズ可能です：

```python
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # .envファイルを環境変数より優先させる
        return (init_settings, dotenv_settings, env_settings, file_secret_settings)
```

## ConfigDictとの関係

| 項目 | `ConfigDict` (pydantic) | `SettingsConfigDict` (pydantic-settings) |
|------|------------------------|------------------------------------------|
| **用途** | `BaseModel`の設定 | `BaseSettings`の設定 |
| **継承** | — | `ConfigDict`を継承・拡張 |
| **固有オプション** | `from_attributes`, `populate_by_name`など | `env_prefix`, `env_file`, `secrets_dir`など |
| **互換性** | 全`ConfigDict`オプションが使用可能 | `ConfigDict` + 環境変数関連オプション |

`SettingsConfigDict`は内部的に`ConfigDict`を継承しているため、`str_strip_whitespace`や`frozen`といった標準オプションもすべて利用できます。

## 実践的なパターン

```python
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MYAPP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",  # 未定義の環境変数でエラー
    )
    
    # SecretStrで機密情報をマスク
    api_key: SecretStr
    
    # バリデーション付き
    port: int = Field(default=8080, ge=1, le=65535)
    
    # エイリアスで環境変数名を明示
    db_url: str = Field(alias="DATABASE_URL")
```


## .envファイルの解決ルール

`env_file=".env"`のような**相対パス**を指定した場合、**カレントワーキングディレクトリ（CWD）**を基準に解決されます。プロジェクトのルートディレクトリやPythonファイルの位置ではありません。

```python
# 実行時の CWD が /home/user/myproject なら
# → /home/user/myproject/.env を探す

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
```

## CWD基準であることの影響

```
myproject/
├── src/
│   └── config.py      # ← Settingsクラスを定義
├── .env               # ← 読み込みたいファイル
└── scripts/
    └── run.py
```

```bash
# ケース1: プロジェクトルートから実行 → 成功
cd /home/user/myproject
python src/config.py   # CWD=/home/user/myproject → .env が見つかる

# ケース2: scriptsディレクトリから実行 → 失敗
cd /home/user/myproject/scripts
python ../src/config.py  # CWD=/home/user/myproject/scripts → .env が見つからない
```

## 解決策：絶対パスを使う

実行場所に依存しない堅牢な方法：

```python
from pathlib import Path

# 方法1: __file__基準（設定ファイルからの相対位置）
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env"  # 絶対パスになる
    )

# 方法2: 明示的な絶対パス
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="/etc/myapp/.env"
    )
```

## ファイルが見つからない場合の挙動

| 状況 | デフォルト動作 |
|------|---------------|
| ファイルが存在しない | **エラーなし**（静かに無視） |
| パーミッションエラー | 例外が発生 |
| エンコーディングエラー | 例外が発生 |

存在チェックを明示的に行いたい場合：

```python
from pathlib import Path

env_path = Path(".env")
if not env_path.exists():
    raise FileNotFoundError(f".env not found at {env_path.resolve()}")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path)
```

## 内部実装の概要

pydantic-settingsは内部で`python-dotenv`を使用しています：

```python
# pydantic_settings内部（簡略化）
from dotenv import dotenv_values

def _read_env_file(env_file: Path | str) -> dict[str, str]:
    # 相対パスはそのまま渡される → CWD基準で解決
    return dotenv_values(env_file, encoding=self.env_file_encoding)
```

`dotenv_values`がパスを受け取ると、Pythonの標準的なファイルオープン動作に従い、相対パスはCWD基準で解決されます。