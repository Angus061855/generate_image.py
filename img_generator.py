import os
from PIL import Image, ImageDraw, ImageFont


def create_image(text, output_path="output.png"):
    """
    用 back.png + ChiKuSung.otf 生成圖片
    文字全部白色大字，置中排列
    底部加上 @angus061855
    """
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
    line_widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=main_font)
        line_widths.append(bbox[2] - bbox[0])
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
