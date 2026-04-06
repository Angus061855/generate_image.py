import os
import google.generativeai as genai

def generate_caption(topic_text):
    """
    用 Gemma 4 31B 生成 Threads/IG 文案
    """
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

    model = genai.GenerativeModel("gemma-4-27b-it")
    # 如果 gemma-4-31b-it 可用就改成：
    # model = genai.GenerativeModel("gemma-4-31b-it")

    prompt = f"""你是一位專業的 Instagram/Threads 文案寫手。

根據以下主題文字，撰寫一篇強而有力的文案：

主題：{topic_text}

規則：
- 第一句必須能獨立成立，吸引滑手機的人停下來
- 不要在開場就給答案，保持神秘感
- 禁止用「——」
- 禁止用「他笑著搖搖頭」「我愣住了」等 AI 感用語
- 要有一句總結性金句
- 結尾拋出一個開放式問題引發討論
- 語言自然，像在跟朋友聊天
- 使用全形標點符號（，。？：）
- 不要加任何引用來源符號
- 不要加 hashtag
- 文案長度控制在 150-300 字

請直接輸出文案，不要加任何前綴說明。"""

    response = model.generate_content(prompt)
    caption = response.text.strip()
    return caption


if __name__ == "__main__":
    text = "我們總以為 來日方長"
    print(generate_caption(text))
