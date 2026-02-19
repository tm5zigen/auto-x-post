import os
import tweepy
import random
from openai import OpenAI
from datetime import datetime

# ===== OpenAI設定 =====
client_ai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

HISTORY_FILE = "history.txt"
MAX_HISTORY = 50

# =========================
# ランダムテーマ
# =========================
themes = [
    "AI副業",
    "時間管理",
    "お金の知識",
    "自動化",
    "フリーランス",
    "ChatGPT活用術",
    "個人で稼ぐ方法"
]

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]


def save_history(text):
    history = load_history()
    history.append(text)
    history = history[-MAX_HISTORY:]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        for h in history:
            f.write(h + "\n")


def generate_text(previous_posts):
    theme = random.choice(themes)
    history_text = "\n".join(previous_posts[-5:])
    prompt = f"""
あなたはフォロワー1万人のX運用者です。
インプレッションが伸びやすい投稿を1つ作ってください。

【条件】
・140文字以内
・結論を最初に書く
・少し煽り要素を入れる
・保存したくなる内容
・改行を使う
・絵文字は2個まで

テーマ：{theme}

過去の投稿例：
{history_text}

出力は文章のみ。
"""

    response = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=1.1
    )

    return response.choices[0].message.content.strip()


def post_to_x(text):
    client = tweepy.Client(
        consumer_key=os.environ["API_KEY"],
        consumer_secret=os.environ["API_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"],
    )

    client.create_tweet(text=text)


def main():
    history = load_history()

    for _ in range(3):
        text = generate_text(history)
        if text not in history:
            break

    final_text = f"{text}"

    post_to_x(final_text)
    save_history(text)

    print("Posted:", final_text)


if __name__ == "__main__":
    main()
