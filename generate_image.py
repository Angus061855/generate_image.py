import os
import requests
import cloudinary
import cloudinary.uploader
from notion_client import Client
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io

# 初始化
notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = "33a11a316c9e80b793f3eeb04850b385"

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"]
)

def get_pending_pages():
    # ✅ 修正：改用 notion.databases.query 並傳入 database_id 作為位置參數
    response = notion.databases.query(
        **{
            "database_id": DATABASE_ID,
            "filter": {
                "property": "狀態",
                "select": {"equals": "待發"}
            }
        }
    )
    return response["results"]

def generate_image(text):
    bg = Image.open("back.png").convert("RGBA")
    draw = ImageDraw.Draw(bg)

    try:
        font = ImageFont.truetype("NotoSansTC-Bold.ttf", 60)
        small_font = ImageFont.truetype("NotoSansTC-Bold.ttf", 30)
    except:
        font = ImageFont.load_default()
        small_font = font

    W, H = bg.size

    lines = text.split("\n")
    line_height = 80
    total_height = len(lines) * line_height
    y = (H - total_height) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w) // 2
        draw.text((x, y), line, font=font, fill="white")
        y += line_height

    account = "@angus061855"
    bbox = draw.textbbox((0, 0), account, font=small_font)
    acc_w = bbox[2] - bbox[0]
    draw.text(((W - acc_w) // 2, H - 80), account, font=small_font, fill="white")

    img_byte_arr = io.BytesIO()
    bg.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr

def upload_to_cloudinary(image_bytes, public_id):
    result = cloudinary.uploader.upload(
        image_bytes,
        public_id=public_id,
        overwrite=True,
        resource_type="image"
    )
    return result["secure_url"]

def update_notion_image_url(page_id, image_url):
    notion.pages.update(
        page_id=page_id,
        properties={
            "圖片網址": {
                "url": image_url
            }
        }
    )

def main():
    pages = get_pending_pages()
    print(f"找到 {len(pages)} 筆待發文章")

    for page in pages:
        page_id = page["id"]
        props = page["properties"]

        title_list = props.get("主題", {}).get("title", [])
        topic = title_list[0]["plain_text"] if title_list else ""

        if not topic:
            print(f"跳過 {page_id}：主題為空")
            continue

        print(f"處理：{topic}")

        image_bytes = generate_image(topic)

        safe_id = page_id.replace("-", "")
        image_url = upload_to_cloudinary(image_bytes, f"ig_post_{safe_id}")

        update_notion_image_url(page_id, image_url)
        print(f"圖片已上傳：{image_url}")

if __name__ == "__main__":
    main()
