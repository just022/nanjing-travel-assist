# 下载妆容推荐配图到 static/images
import os
import urllib.request

IMG_DIR = r"E:\byys\static\images"
os.makedirs(IMG_DIR, exist_ok=True)

IMAGES = {
    "makeup_summer.jpg":  "https://aka.doubaocdn.com/s/CwV5EgJxbb",
    "makeup_spring.jpg":  "https://aka.doubaocdn.com/s/oEdiKirwSB",
    "makeup_autumn.jpg":  "https://aka.doubaocdn.com/s/eNqfKsvgyK",
    "makeup_winter.jpg":  "https://aka.doubaocdn.com/s/jUXRsTVeuh",
    "makeup_default.jpg": "https://aka.doubaocdn.com/s/QBb7JkqqxQ",
}

headers = {"User-Agent": "Mozilla/5.0"}

for filename, url in IMAGES.items():
    path = os.path.join(IMG_DIR, filename)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        with open(path, "wb") as f:
            f.write(data)
        print(f"OK  {filename}  {len(data)} bytes")
    except Exception as e:
        print(f"FAIL {filename}  {e}")
