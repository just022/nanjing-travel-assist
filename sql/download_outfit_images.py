# 下载穿搭参考图到 static/images（按季节档 × 性别，每档 2 张）
import os
import urllib.request

IMG_DIR = r"E:\byys\static\images"
os.makedirs(IMG_DIR, exist_ok=True)

IMAGES = {
    # 女 · 夏
    "outfit_summer_f.jpg": "https://aka.doubaocdn.com/s/9eC7oZRCY8",
    "outfit_summer_f_2.jpg": "https://aka.doubaocdn.com/s/DJcHwKxQBx",
    # 女 · 春秋
    "outfit_spring_f.jpg": "https://aka.doubaocdn.com/s/dEFiJiWOmK",
    "outfit_spring_f_2.jpg": "https://aka.doubaocdn.com/s/ViYSoXT5sO",
    # 女 · 秋
    "outfit_autumn_f.jpg": "https://aka.doubaocdn.com/s/fsLWFY62o3",
    "outfit_autumn_f_2.jpg": "https://aka.doubaocdn.com/s/a3h7uBEkE4",
    # 女 · 冬
    "outfit_winter_f.jpg": "https://aka.doubaocdn.com/s/z1IQauo3wV",
    "outfit_winter_f_2.jpg": "https://aka.doubaocdn.com/s/rqZ0x58MHR",
    # 男 · 夏
    "outfit_summer_m.jpg": "https://aka.doubaocdn.com/s/KAKauAHUlD",
    "outfit_summer_m_2.jpg": "https://aka.doubaocdn.com/s/0mLMtPBRZw",
    # 男 · 春秋
    "outfit_spring_m.jpg": "https://aka.doubaocdn.com/s/FKjB8JmMkH",
    "outfit_spring_m_2.jpg": "https://aka.doubaocdn.com/s/eElznKiVSl",
    # 男 · 秋
    "outfit_autumn_m.jpg": "https://aka.doubaocdn.com/s/seVyPriVVt",
    "outfit_autumn_m_2.jpg": "https://aka.doubaocdn.com/s/odAVyTidkk",
    # 男 · 冬
    "outfit_winter_m.jpg": "https://aka.doubaocdn.com/s/GLRR2Yl28f",
    "outfit_winter_m_2.jpg": "https://aka.doubaocdn.com/s/7OubX0SZ4G",
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
