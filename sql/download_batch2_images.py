# 下载第二批新景点主图到 static/images
import os
import urllib.request

IMG_DIR = r"E:\byys\static\images"
os.makedirs(IMG_DIR, exist_ok=True)

IMAGES = {
    "yuhuatai.jpg": "https://aka.doubaocdn.com/s/LgDBqPVgKS",   # 雨花台山林纪念碑
    "hongshan.jpg": "https://aka.doubaocdn.com/s/PhFgJODdtO",   # 红山动物园山地步道
    "nju.jpg": "https://aka.doubaocdn.com/s/usQrNPMUGh",        # 南大鼓楼校区塔楼
    "haidi.jpg": "https://aka.doubaocdn.com/s/Vy7ORvLWOe",      # 海底世界隧道
    "zhonghuamen.jpg": "https://aka.doubaocdn.com/s/QCHsDpUTVw", # 中华门瓮城城墙
    "yuzui.jpg": "https://aka.doubaocdn.com/s/pDrRjVDHUW",      # 鱼嘴湿地日落
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
