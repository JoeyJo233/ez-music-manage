#!/usr/bin/env python3
"""
更新 イキツクシ-DADARAY.m4a 的专辑封面为 DADASTATION
在 Music 目录下运行：python fix_dadastation_cover.py
"""
import io, sys, requests
from pathlib import Path
from mutagen.mp4 import MP4, MP4Cover
from PIL import Image

FILE = Path(__file__).parent / "my_music_aac" / "Done" / "イキツクシ-DADARAY.m4a"

if not FILE.exists():
    print(f"找不到文件：{FILE}")
    sys.exit(1)

print(f"目标文件：{FILE.name}")

# 通过 iTunes Lookup API 获取 DADASTATION 封面（album id: 1308461549）
print("正在从 iTunes 获取封面...")
resp = requests.get(
    "https://itunes.apple.com/lookup",
    params={"id": "1308461549", "entity": "album"},
    timeout=15
)
data = resp.json()

artwork_url = None
for result in data.get("results", []):
    url = result.get("artworkUrl100", "")
    if url:
        artwork_url = url.replace("100x100bb", "1200x1200bb")
        print(f"找到封面：{result.get('collectionName')} / {result.get('artistName')}")
        break

if not artwork_url:
    print("❌ 未找到封面，请手动检查")
    sys.exit(1)

# 下载并处理图片
print("正在下载封面图片...")
img_resp = requests.get(artwork_url, timeout=15)
img = Image.open(io.BytesIO(img_resp.content)).convert("RGB")

# 裁剪正方形 + 缩放到 800x800
w, h = img.size
m = min(w, h)
img = img.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m))
img = img.resize((800, 800), Image.LANCZOS)

buf = io.BytesIO()
img.save(buf, format="JPEG", quality=92)
cover_data = buf.getvalue()

# 写入封面
audio = MP4(str(FILE))
audio.tags["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
audio.save()

# 验证
audio2 = MP4(str(FILE))
covr = audio2.tags.get("covr")
if covr:
    verify_img = Image.open(io.BytesIO(bytes(covr[0])))
    print(f"✅ 封面已更新：{verify_img.size[0]}x{verify_img.size[1]}px")
    print(f"   album: {audio2.tags.get('©alb', [''])[0]}")
else:
    print("❌ 封面写入验证失败")
