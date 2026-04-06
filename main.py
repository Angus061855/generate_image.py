import json
import random
from generate_image import generate_quote_image
from post_instagram import upload_to_cloudinary, post_to_instagram

# 讀取文案庫
with open("images/quotes.json", "r", encoding="utf-8") as f:
    quotes = json.load(f)

# 隨機選一則（或按順序）
quote = random.choice(quotes)

# 生成圖片
generate_quote_image(quote["main"], quote["sub"], "output.png")

# 上傳 + 發佈
image_url = upload_to_cloudinary("output.png")
post_to_instagram(image_url, quote["caption"])
