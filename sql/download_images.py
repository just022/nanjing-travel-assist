# 下载景点配图到 static/images
import os
import urllib.request

IMG_DIR = r"E:\byys\static\images"
os.makedirs(IMG_DIR, exist_ok=True)

IMAGES = {
    "fuzimiao.jpg":  "https://aka.doubaocdn.com/l/zUKPQOXQmR",
    "zhongshanling.jpg": "https://aka.doubaocdn.com/l/UPExXrEY4h",
    "mingxiaoling.jpg":  "https://aka.doubaocdn.com/l/0RVqfvQ9HT",
    "bowuyuan.jpg":      "https://aka.doubaocdn.com/l/XRLDQNCqXt",
    "zongtongfu.jpg":    "https://aka.doubaocdn.com/l/TbZ2UDfVpT",
    "xuanwuhu.jpg":       "https://aka.doubaocdn.com/l/aE6HhAwEJL",
    "jimingsi.jpg":       "https://aka.doubaocdn.com/l/Uh9B5tKQEU",
    "laomendong.jpg":     "https://aka.doubaocdn.com/l/CZb9PlSf46",
    "niushoushan.jpg":    "https://aka.doubaocdn.com/l/mFyNR9dcK5",
    "qixiashan.jpg":      "https://aka.doubaocdn.com/l/1Po7uSHSr0",
    "mochouhu.jpg":       "https://aka.doubaocdn.com/l/VZ0NKgZOnU",
    "dabaensi.jpg":       "https://aka.doubaocdn.com/l/hUOvAMTLZa",
    "yihelu.jpg":         "https://aka.doubaocdn.com/l/s1IZPTqIEk",
    "zijinshan.jpg":      "https://aka.doubaocdn.com/l/XYXTP4WPRu",
    "yuejianglou.jpg":    "https://aka.doubaocdn.com/l/5VJVQUDROw",
    "gaochun.jpg":        "https://aka.doubaocdn.com/l/q1NKUzRU8g",
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
