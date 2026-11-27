# 下载补充妆容配图到 static/images（每温度档图集 + 场景专属妆）
import os
import urllib.request

IMG_DIR = r"E:\byys\static\images"
os.makedirs(IMG_DIR, exist_ok=True)

IMAGES = {
    # 夏日档补充
    "makeup_summer_2.jpg": "https://aka.doubaocdn.com/s/wsgzQGGBBw",
    "makeup_summer_3.jpg": "https://aka.doubaocdn.com/s/2Lj0MCqTnV",
    # 春秋日常档补充
    "makeup_spring_2.jpg": "https://aka.doubaocdn.com/s/uEx0aqdrMi",
    "makeup_spring_3.jpg": "https://aka.doubaocdn.com/s/yb5xEng6lF",
    # 秋冬档补充
    "makeup_autumn_2.jpg": "https://aka.doubaocdn.com/s/TOaipaEBBE",
    "makeup_autumn_3.jpg": "https://aka.doubaocdn.com/s/QczlFPR7qW",
    # 冬季档补充
    "makeup_winter_2.jpg": "https://aka.doubaocdn.com/s/aYAubZpR4Z",
    "makeup_winter_3.jpg": "https://aka.doubaocdn.com/s/QsggNOdB4b",
    # 场景专属
    "makeup_commute.jpg": "https://aka.doubaocdn.com/s/V848lLoU3i",
    "makeup_rainy.jpg":   "https://aka.doubaocdn.com/s/n6UyyqrF7r",
    "makeup_snowy.jpg":   "https://aka.doubaocdn.com/s/8htDW2WBtO",
    "makeup_trip.jpg":    "https://aka.doubaocdn.com/s/oaT9bAquBe",
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
