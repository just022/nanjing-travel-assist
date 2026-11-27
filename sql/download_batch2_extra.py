# 下载第二批新景点的辅图（_2.jpg / _3.jpg）到 static/images
import os
import urllib.request

IMG_DIR = r"E:\byys\static\images"
os.makedirs(IMG_DIR, exist_ok=True)

IMAGES = {
    "yuhuatai_2.jpg": "https://aka.doubaocdn.com/s/8S8YW1mxGj",  # 山林松柏步道
    "yuhuatai_3.jpg": "https://aka.doubaocdn.com/s/p4Uz5ib7gl",  # 园林水景古亭
    "hongshan_2.jpg": "https://aka.doubaocdn.com/s/DRYZ3kr3dS",  # 大熊猫展区
    "hongshan_3.jpg": "https://aka.doubaocdn.com/s/U7Kt7Pu5tu",  # 鹿群草地
    "nju_2.jpg": "https://aka.doubaocdn.com/s/uPGyZsU7fg",       # 梧桐林荫道
    "nju_3.jpg": "https://aka.doubaocdn.com/s/KGD1PEwc4i",      # 老建筑庭院
    "haidi_2.jpg": "https://aka.doubaocdn.com/s/nQ2xXg6tEY",     # 水母宫
    "haidi_3.jpg": "https://aka.doubaocdn.com/s/F6k0GozCfd",     # 企鹅展区
    "zhonghuamen_2.jpg": "https://aka.doubaocdn.com/s/WJVcGQ4GqC",  # 藏兵洞拱券
    "zhonghuamen_3.jpg": "https://aka.doubaocdn.com/s/5oeiLZBCz7",  # 城墙俯瞰老城
    "yuzui_2.jpg": "https://aka.doubaocdn.com/s/eZe9yJR0si",     # 芦苇栈道
    "yuzui_3.jpg": "https://aka.doubaocdn.com/s/hapgnByakj",     # 江滩大桥
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
