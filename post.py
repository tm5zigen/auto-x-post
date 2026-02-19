import os
import tweepy
from openai import OpenAI
from datetime import datetime

# ===== OpenAI設定 =====
client_ai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

HISTORY_FILE = "history.txt"
MAX_HISTORY = 50


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
    history_text = "\n".join(previous_posts[-5:])

    prompt = f"""
短く自然な日本語の独り言を1つ生成してください。

条件：
・20〜40文字
・人間っぽい
・説明口調にしない
・ポジティブすぎない
・SNS向け
・過去の文章と似た表現を使わない

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
    auth = tweepy.OAuth1UserHandler(
        os.environ["API_KEY"],
        os.environ["API_SECRET"],
        os.environ["ACCESS_TOKEN"],
        os.environ["ACCESS_TOKEN_SECRET"],
    )

    api = tweepy.API(auth)
    api.update_status(text)


def main():
    history = load_history()

    for _ in range(3):
        text = generate_text(history)
        if text not in history:
            break

    final_text = f"{text}\n\n🕒 {datetime.now().strftime('%H:%M')}"

    post_to_x(final_text)
    save_history(text)

    print("Posted:", final_text)


if __name__ == "__main__":
    main()
