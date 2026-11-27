# 下载每个景点的补充视角配图到 static/images（主图保留原名，辅图 *_2.jpg / *_3.jpg）
import os
import urllib.request

IMG_DIR = r"E:\byys\static\images"
os.makedirs(IMG_DIR, exist_ok=True)

# key: 辅图文件名; value: 图片地址
IMAGES = {
    # 夫子庙·秦淮河
    "fuzimiao_2.jpg": "https://aka.doubaocdn.com/l/1BZbkjFKUT",   # 乌衣巷白墙黛瓦
    "fuzimiao_3.jpg": "https://aka.doubaocdn.com/l/ocZ0QawUnc",   # 秦淮河航拍白天
    # 中山陵
    "zhongshanling_2.jpg": "https://aka.doubaocdn.com/l/Wr3Waxmh1J",  # 祭堂台阶鸟瞰
    "zhongshanling_3.jpg": "https://aka.doubaocdn.com/l/Xjson0BCyV",  # 中轴秋林航拍
    # 明孝陵
    "mingxiaoling_2.jpg": "https://aka.doubaocdn.com/l/bAVi2c8sl1",   # 石象路石象
    "mingxiaoling_3.jpg": "https://aka.doubaocdn.com/l/qiU59kuIhx",   # 翁仲路武将神道
    # 南京博物院
    "bowuyuan_2.jpg": "https://aka.doubaocdn.com/l/rc2sK0ibU8",      # 民国馆街景老爷车
    "bowuyuan_3.jpg": "https://aka.doubaocdn.com/l/EeVpnVRx0p",      # 民国馆红砖街巷
    # 总统府
    "zongtongfu_2.jpg": "https://aka.doubaocdn.com/l/QJwy2le7CI",     # 煦园水榭倒影
    "zongtongfu_3.jpg": "https://aka.doubaocdn.com/l/VpKAdreH5l",     # 子超楼与喷泉
    # 玄武湖公园
    "xuanwuhu_2.jpg": "https://aka.doubaocdn.com/l/T4BDFtFBc1",       # 玄武门湖景紫金山
    "xuanwuhu_3.jpg": "https://aka.doubaocdn.com/l/LrKnIGmE6p",       # 樱洲樱花城墙
    # 鸡鸣寺
    "jimingsi_2.jpg": "https://aka.doubaocdn.com/l/Y5wELoLfXa",      # 樱花枝框药师塔
    "jimingsi_3.jpg": "https://aka.doubaocdn.com/l/wUF2sqcdEQ",      # 秋景城墙佛塔
    # 老门东
    "laomendong_2.jpg": "https://aka.doubaocdn.com/l/HwffbPelvO",     # 夜景马头墙灯笼
    "laomendong_3.jpg": "https://aka.doubaocdn.com/l/S7QUJbXWyZ",     # 青石板小巷
    # 牛首山
    "niushoushan_2.jpg": "https://aka.doubaocdn.com/l/lFQARlBbpy",    # 佛顶塔与双穹顶
    "niushoushan_3.jpg": "https://aka.doubaocdn.com/l/LuElCTHqpr",    # 山林航拍全景
    # 栖霞山
    "qixiashan_2.jpg": "https://aka.doubaocdn.com/l/020XAJSNy9",      # 舍利塔红叶
    "qixiashan_3.jpg": "https://aka.doubaocdn.com/l/6sIQ9GntlS",      # 栖霞寺航拍秋景
    # 莫愁湖公园
    "mochouhu_2.jpg": "https://aka.doubaocdn.com/l/1J8aCZXlGu",       # 莫愁女雕像海棠
    "mochouhu_3.jpg": "https://aka.doubaocdn.com/l/mTqPRGpBU8",       # 胜棋楼木楼
    # 大报恩寺遗址公园
    "dabaensi_2.jpg": "https://aka.doubaocdn.com/l/OXfyZaV6R5",       # 琉璃塔夜景灯光
    "dabaensi_3.jpg": "https://aka.doubaocdn.com/l/hYhoTtmsz6",       # 塔与博物馆立面
    # 颐和路民国公馆区
    "yihelu_2.jpg": "https://aka.doubaocdn.com/l/VvnM9ROliS",         # 黄墙梧桐街景
    "yihelu_3.jpg": "https://aka.doubaocdn.com/l/GWhBHWUCbB",         # 洋房群秋景航拍
    # 紫金山天文台
    "zijinshan_2.jpg": "https://aka.doubaocdn.com/l/2LPcyrPpJc",      # 圆顶与天球仪
    "zijinshan_3.jpg": "https://aka.doubaocdn.com/l/pzR3ZEupRc",      # 明制浑仪
    # 阅江楼
    "yuejianglou_2.jpg": "https://aka.doubaocdn.com/l/e0GZpN6bSe",    # 楼与长江大桥同框夜景
    "yuejianglou_3.jpg": "https://aka.doubaocdn.com/l/l9POcST9wV",    # 黄昏楼阁江景
    # 高淳老街
    "gaochun_2.jpg": "https://aka.doubaocdn.com/l/ERwZ9OrHzb",        # 石板老街商铺
    "gaochun_3.jpg": "https://aka.doubaocdn.com/l/ywcOiu7KKQ",        # 老街夜景灯光
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
