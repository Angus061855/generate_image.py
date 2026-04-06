import requests
import os
import cloudinary
import cloudinary.uploader

def upload_to_cloudinary(image_path):
    """上傳圖片到 Cloudinary 取得公開 URL（免費方案）"""
    cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"]
    )
    result = cloudinary.uploader.upload(image_path)
    return result["secure_url"]

def post_to_instagram(image_url, caption):
    user_id = os.environ["INSTAGRAM_USER_ID"]
    token = os.environ["ACCESS_TOKEN"]

    # Step 1: 建立媒體容器
    res = requests.post(
        f"https://graph.facebook.com/v18.0/{user_id}/media",
        params={
            "image_url": image_url,
            "caption": caption,
            "access_token": token
        }
    )
    creation_id = res.json().get("id")
    print(f"媒體容器 ID：{creation_id}")

    # Step 2: 正式發佈
    pub = requests.post(
        f"https://graph.facebook.com/v18.0/{user_id}/media_publish",
        params={
            "creation_id": creation_id,
            "access_token": token
        }
    )
    print(f"發佈結果：{pub.json()}")
