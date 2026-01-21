from openai import OpenAI

#TODO: create_and_runが非推奨なので、新しいAPIに書き換える
# これはただ単に実行しただけで、結果を受け取れていないので、修正が必要

client = OpenAI()

run = client.beta.threads.create_and_run(
  assistant_id="asst_DlhSstODIeAZPUmjwzfSknzg",
  thread={
    "messages": [
      {"role": "user", "content": "木は何からできていますか？"}
    ]
  }
)

print(run)
