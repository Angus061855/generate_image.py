import os
import requests
import cloudinary
import cloudinary.uploader
from PIL import Image, ImageDraw, ImageFont
from google import genai

# ===== 環境變數 =====
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.environ.get("IG_ACCOUNT_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


# ========== 圖片生成 ==========
def create_image(text, output_path="output.png"):
    bg = Image.open("back.png").convert("RGBA")
    width, height = bg.size
    draw = ImageDraw.Draw(bg)

    main_font_size = int(width * 0.08)
    watermark_font_size = int(width * 0.03)

    main_font = ImageFont.truetype("ChiKuSung.otf", main_font_size)
    watermark_font = ImageFont.truetype("ChiKuSung.otf", watermark_font_size)

    lines = text.strip().split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=main_font)
        line_heights.append(bbox[3] - bbox[1])

    line_spacing = int(main_font_size * 0.6)
    total_text_height = sum(line_heights) + line_spacing * (len(lines) - 1)

    start_y = (height - total_text_height) // 2 - int(height * 0.05)

    current_y = start_y
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=main_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, current_y), line, font=main_font, fill="white")
        current_y += line_heights[i] + line_spacing

    watermark = "@angus061855"
    wm_bbox = draw.textbbox((0, 0), watermark, font=watermark_font)
    wm_width = wm_bbox[2] - wm_bbox[0]
    wm_x = (width - wm_width) // 2
    wm_y = height - int(height * 0.08)
    draw.text((wm_x, wm_y), watermark, font=watermark_font, fill=(180, 180, 180))

    bg.convert("RGB").save(output_path, "PNG")
    print(f"圖片已生成：{output_path}")
    return output_path


# ========== 文案生成 ==========
def create_caption(topic_text):
    client = genai.Client(api_key=GEMINI_API_KEY)

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

    response = client.models.generate_content(
        model="gemma-4-31b-it",
        contents=prompt
    )
    caption = response.text.strip()
    return caption


# ========== Notion 操作 ==========
def get_pending_posts():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": "狀態",
            "status": {"equals": "待發"}
        },
        "page_size": 1
    }
    res = requests.post(url, headers=NOTION_HEADERS, json=payload)
    data = res.json()
    return data.get("results", [])


def get_text_from_page(page):
    text_prop = page["properties"].get("文字", {})
    rich_texts = text_prop.get("rich_text", [])
    return "".join([rt["plain_text"] for rt in rich_texts])


def upload_to_cloudinary(image_path):
    result = cloudinary.uploader.upload(image_path)
    return result["secure_url"]


def update_notion_page(page_id, image_url, caption):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "圖片網址": {
                "url": image_url
            },
            "文案": {
                "rich_text": [{"text": {"content": caption[:2000]}}]
            }
        }
    }
    requests.patch(url, headers=NOTION_HEADERS, json=payload)


def post_to_instagram(image_url, caption):
    create_url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media"
    create_payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": IG_ACCESS_TOKEN
    }
    res = requests.post(create_url, data=create_payload)
    creation_id = res.json().get("id")

    if not creation_id:
        print(f"IG 建立媒體失敗：{res.json()}")
        return False

    publish_url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": IG_ACCESS_TOKEN
    }
    pub_res = requests.post(publish_url, data=publish_payload)
    print(f"IG 發布結果：{pub_res.json()}")
    return pub_res.json().get("id") is not None


def update_status_published(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "狀態": {"status": {"name": "已發布"}}
        }
    }
    requests.patch(url, headers=NOTION_HEADERS, json=payload)


def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)


# ========== 主程式 ==========
def main():
    posts = get_pending_posts()
    if not posts:
        print("沒有待發文章")
        return

    page = posts[0]
    page_id = page["id"]
    text = get_text_from_page(page)

    if not text:
        print("文字欄位為空，跳過")
        return

    print(f"處理文章：{text[:30]}...")

    # Step 1: 檢查是否已有圖片
    existing_url = page["properties"].get("圖片網址", {}).get("url")

    if existing_url:
        image_url = existing_url
        print(f"已有圖片，跳過生成：{image_url}")
    else:
        image_path = create_image(text, "output.png")
        image_url = upload_to_cloudinary(image_path)
        print(f"圖片上傳成功：{image_url}")

    # Step 2: 檢查是否已有文案
    existing_caption_parts = page["properties"].get("文案", {}).get("rich_text", [])
    existing_caption = "".join([rt["plain_text"] for rt in existing_caption_parts])

    if existing_caption:
        caption = existing_caption
        print("已有文案，跳過生成")
    else:
        caption = create_caption(text)
        print(f"文案生成完成：{caption[:50]}...")

    # Step 3: 更新 Notion
    update_notion_page(page_id, image_url, caption)

    # Step 4: 發布 IG
    success = post_to_instagram(image_url, caption)

    if success:
        update_status_published(page_id)
        send_telegram_notification(f"✅ IG 發布成功！\n\n{text[:50]}...")
        print("發布成功！")
    else:
        send_telegram_notification(f"❌ IG 發布失敗\n\n{text[:50]}...")
        print("發布失敗")


if __name__ == "__main__":
    main()
