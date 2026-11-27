# 下载穿搭「温度×性别×风格」专属参考图（32 张）
import os
import urllib.request

IMG_DIR = r"E:\byys\static\images"
os.makedirs(IMG_DIR, exist_ok=True)

IMAGES = {
    # 炎热 summer · 女 f
    "outfit_summer_f_casual.jpg": "https://aka.doubaocdn.com/s/PqWipH5W2w",
    "outfit_summer_f_commute.jpg": "https://aka.doubaocdn.com/s/NybLvT4oVP",
    "outfit_summer_f_date.jpg": "https://aka.doubaocdn.com/s/67LiktNb0i",
    "outfit_summer_f_sport.jpg": "https://aka.doubaocdn.com/s/BrjJP9Xogk",
    # 炎热 summer · 男 m
    "outfit_summer_m_casual.jpg": "https://aka.doubaocdn.com/s/SQQJX9T5cB",
    "outfit_summer_m_commute.jpg": "https://aka.doubaocdn.com/s/M2uHDMj6CD",
    "outfit_summer_m_date.jpg": "https://aka.doubaocdn.com/s/0jodouUB4P",
    "outfit_summer_m_sport.jpg": "https://aka.doubaocdn.com/s/70bG2FWMR0",
    # 温和 spring · 女 f
    "outfit_spring_f_casual.jpg": "https://aka.doubaocdn.com/s/nnu8HEUPsF",
    "outfit_spring_f_commute.jpg": "https://aka.doubaocdn.com/s/XeJ9nntNZU",
    "outfit_spring_f_date.jpg": "https://aka.doubaocdn.com/s/L4BOiU3uMG",
    "outfit_spring_f_sport.jpg": "https://aka.doubaocdn.com/s/F9JExKPuXo",
    # 温和 spring · 男 m
    "outfit_spring_m_casual.jpg": "https://aka.doubaocdn.com/s/clabnOp0Vw",
    "outfit_spring_m_commute.jpg": "https://aka.doubaocdn.com/s/YV61kIa8bu",
    "outfit_spring_m_date.jpg": "https://aka.doubaocdn.com/s/MePuSngXSJ",
    "outfit_spring_m_sport.jpg": "https://aka.doubaocdn.com/s/lctfOZ6BJ3",
    # 凉爽 autumn · 女 f
    "outfit_autumn_f_casual.jpg": "https://aka.doubaocdn.com/s/Agg0eHwYRv",
    "outfit_autumn_f_commute.jpg": "https://aka.doubaocdn.com/s/y7W56yp0XB",
    "outfit_autumn_f_date.jpg": "https://aka.doubaocdn.com/s/h7Pu4wwgFH",
    "outfit_autumn_f_sport.jpg": "https://aka.doubaocdn.com/s/VigfnRgdbV",
    # 凉爽 autumn · 男 m
    "outfit_autumn_m_casual.jpg": "https://aka.doubaocdn.com/s/aSO4254spB",
    "outfit_autumn_m_commute.jpg": "https://aka.doubaocdn.com/s/VSeXzM93wd",
    "outfit_autumn_m_date.jpg": "https://aka.doubaocdn.com/s/H1FctUdVgL",
    "outfit_autumn_m_sport.jpg": "https://aka.doubaocdn.com/s/N7bk3Rm8JO",
    # 寒冷 winter · 女 f
    "outfit_winter_f_casual.jpg": "https://aka.doubaocdn.com/s/JUT1jiWMK5",
    "outfit_winter_f_commute.jpg": "https://aka.doubaocdn.com/s/NYZ9ne008n",
    "outfit_winter_f_date.jpg": "https://aka.doubaocdn.com/s/GRlb2s1p2J",
    "outfit_winter_f_sport.jpg": "https://aka.doubaocdn.com/s/EhUewvYJdu",
    # 寒冷 winter · 男 m
    "outfit_winter_m_casual.jpg": "https://aka.doubaocdn.com/s/5MG64dNHiv",
    "outfit_winter_m_commute.jpg": "https://aka.doubaocdn.com/s/LJ1lUUeixW",
    "outfit_winter_m_date.jpg": "https://aka.doubaocdn.com/s/Q99aqcWqwh",
    "outfit_winter_m_sport.jpg": "https://aka.doubaocdn.com/s/LNOzFvfHnB",
}

headers = {"User-Agent": "Mozilla/5.0"}
ok = fail = 0
for filename, url in IMAGES.items():
    path = os.path.join(IMG_DIR, filename)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        with open(path, "wb") as f:
            f.write(data)
        print(f"OK  {filename}  {len(data)} bytes")
        ok += 1
    except Exception as e:
        print(f"FAIL {filename}  {e}")
        fail += 1

print(f"\n完成：成功 {ok}，失败 {fail}")
