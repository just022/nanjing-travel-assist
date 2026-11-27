# services/makeup_service.py
import urllib.request
import json
import time
import os

IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "images")

# 天气结果短时缓存：避免每次打开页面都同步请求外部接口造成卡顿
_WEATHER_CACHE = {"data": None, "ts": 0}
_GEO_CACHE = {"loc": None}  # 经纬度基本不变，缓存地理编码结果，省去每次首次的 geo 请求
CACHE_TTL = 300  # 秒，5 分钟内复用缓存天气
HTTP_TIMEOUT = 4  # 单次请求超时，超时即走兜底，避免长时间阻塞

# 免费天气接口（Open-Meteo，无需 key），默认南京
# 地理编码与天气预报分两个域名，个别网络下预报域名握手慢，做了降级处理
GEO_URL = "https://geocoding-api.open-meteo.com/v1/search?name=Nanjing&count=1&language=zh"
WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,"
    "weather_code,wind_speed_10m&timezone=Asia%2FShanghai"
)

# 接口不可用时的兜底天气（南京春秋常见值）
FALLBACK_WEATHER = {
    "temperature": 18,
    "humidity": 60,
    "wind_speed": 10,
    "weather_code": 2,
    "weather_text": "多云",
    "city": "南京",
    "fallback": True,
}

# 天气代码 -> 中文描述
WEATHER_MAP = {
    0: "晴", 1: "晴间多云", 2: "多云", 3: "阴",
    45: "雾", 48: "雾凇",
    51: "小毛毛雨", 53: "毛毛雨", 55: "浓毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨",
    71: "小雪", 73: "中雪", 75: "大雪",
    80: "阵雨", 81: "强阵雨", 82: "暴雨",
    95: "雷阵雨",
}

RAIN_CODES = (51, 53, 55, 61, 63, 65, 80, 81, 82, 95)
SNOW_CODES = (71, 73, 75)

# 肤质 / 肤色可选项（供页面下拉选择）
SKIN_TYPES = ["中性", "油性", "干性", "混合"]
SKIN_TONES = ["白皙", "自然偏白", "自然黄皮", "健康小麦"]

# 穿搭场景可选项
OUTFIT_SCENES = ["日常通勤", "出游逛街", "约会聚餐", "运动休闲", "正式商务", "校园青春"]

# 穿搭风格偏好可选项
OUTFIT_STYLES = ["随性休闲", "简约通勤", "精致约会", "运动机能"]

# 性别可选项
GENDERS = ["女", "男"]

# 妆容场景可选项（含自动/天气场景与细分风格）
MAKEUP_SCENES = [
    ("auto", "自动（按天气）"),
    ("commute", "通勤淡妆"),
    ("trip", "出游元气"),
    ("date", "约会甜美"),
    ("interview", "面试正式"),
    ("party", "派对精致"),
    ("sweet", "日系甜美"),
    ("retro", "复古港风"),
    ("rainy", "雨天防脱"),
    ("snowy", "雪景氛围"),
]


def _get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_nanjing_weather():
    """获取南京当前天气，返回 dict；5 分钟内复用缓存，失败时返回兜底天气并标注。"""
    now = time.time()
    if _WEATHER_CACHE["data"] and now - _WEATHER_CACHE["ts"] < CACHE_TTL:
        return dict(_WEATHER_CACHE["data"])

    try:
        loc = _GEO_CACHE["loc"]
        if loc is None:
            geo = _get_json(GEO_URL)
            loc = geo["results"][0]
            _GEO_CACHE["loc"] = loc
        lat, lon = loc["latitude"], loc["longitude"]
        data = _get_json(WEATHER_URL.format(lat=lat, lon=lon))
        cur = data["current"]
        code = cur.get("weather_code", 0)
        weather = {
            "temperature": round(cur["temperature_2m"]),
            "humidity": cur["relative_humidity_2m"],
            "wind_speed": round(cur["wind_speed_10m"]),
            "weather_code": code,
            "weather_text": WEATHER_MAP.get(code, "未知"),
            "city": loc.get("name", "南京"),
            "fallback": False,
        }
        _WEATHER_CACHE["data"] = weather
        _WEATHER_CACHE["ts"] = now
        return dict(weather)
    except Exception:
        weather = dict(FALLBACK_WEATHER)
        weather["fallback"] = True
        _WEATHER_CACHE["data"] = weather
        _WEATHER_CACHE["ts"] = now
        return weather


def _skin_type_tip(skin_type):
    """按肤质给出底妆侧重建议。"""
    tips = {
        "油性": "油皮重点控油：妆前用控油乳，T区少量散粉定妆，随身备吸油纸。",
        "干性": "干皮重点保湿：妆前敷保湿面膜或涂保湿精华，选滋润型底妆，避免卡粉。",
        "混合": "混合肤质分区护理：T区控油定妆，两颊保湿滋润，底妆薄涂。",
        "中性": "肤质稳定，按季节与肤色选择底妆即可，注意日常护肤保湿。",
    }
    return tips.get(skin_type, "")


def _skin_tone_tip(skin_tone):
    """按肤色给出底妆色号与唇色建议。"""
    tips = {
        "白皙": "白皮可自由驾驭粉调与冷调粉底，唇色可选红棕、莓果、正红显白。",
        "自然偏白": "选自然一白/二白粉底，唇色豆沙、蜜桃、珊瑚都较稳妥。",
        "自然黄皮": "避免过白粉底发灰，选暖调自然色；唇色推荐番茄、橘红、红棕提气色。",
        "健康小麦": "选暖调健康色粉底，唇色用焦糖、土棕、橘红，避免过浅粉调。",
    }
    return tips.get(skin_tone, "")


def recommend_makeup(weather, skin_type="中性", skin_tone="自然偏白", scene="auto"):
    """
    根据天气（温度、湿度、天气状况）、肤质、肤色、场景推荐妆容。
    返回 dict: 风格、底妆、眼妆、唇妆、小贴士、图集 images（逗号分隔）、场景标签
    """
    if not weather:
        return {
            "style": "清爽通勤妆",
            "base": "根据自身肤质选择底妆产品",
            "eye": "大地色眼影 + 自然眼线",
            "lip": "日常豆沙色唇膏",
            "tips": "天气信息获取失败，以下为通用建议。",
            "images": ["makeup_default.jpg"],
            "scene": "通用",
        }

    temp = weather["temperature"]
    humidity = weather["humidity"]
    code = weather["weather_code"]
    rainy = code in RAIN_CODES
    snowy = code in SNOW_CODES

    # 1) 温度分档：基础风格 + 图集
    if temp >= 28:
        base = "高温易脱妆，选轻薄控油的持妆粉底液，局部遮瑕，避免厚粉"
        eye = "清透大地色，眼线轻薄，重点防晕染"
        lip = "水润哑光唇釉，选橘红、番茄色提气色"
        style = "清爽夏日裸妆"
        tips = "随身带吸油纸和定妆喷雾，出汗后及时补妆。"
        images = ["makeup_summer.jpg", "makeup_summer_2.jpg", "makeup_summer_3.jpg"]
        temp_key = "summer"
    elif temp >= 15:
        base = "肤质适中，可按肤色选自然光泽底妆"
        eye = "温柔奶茶色或淡粉眼影，眼线自然柔和"
        lip = "豆沙色、蜜桃色唇膏，日常百搭"
        style = "温柔日常妆"
        tips = "春秋温差较大，注意底妆与肤色衔接自然。"
        images = ["makeup_spring.jpg", "makeup_spring_2.jpg", "makeup_spring_3.jpg"]
        temp_key = "spring"
    elif temp >= 5:
        base = "偏干燥，选滋润型底妆，妆前做好保湿"
        eye = "暖棕、红棕眼影，增强气色与轮廓"
        lip = "红棕、枫叶色唇膏，显白有氛围感"
        style = "暖棕秋冬妆"
        tips = "唇部容易干裂，先涂润唇膏打底。"
        images = ["makeup_autumn.jpg", "makeup_autumn_2.jpg", "makeup_autumn_3.jpg"]
        temp_key = "autumn"
    else:
        base = "寒冷干燥，用高保湿底妆，避免卡粉起皮"
        eye = "大地色加深眼窝，睫毛卷翘提亮眼神"
        lip = "滋润正红或莓果色，提亮气色"
        style = "暖冬氛围感妆"
        tips = "室内外温差大，注意护肤保湿，避免底妆斑驳。"
        images = ["makeup_winter.jpg", "makeup_winter_2.jpg", "makeup_winter_3.jpg"]
        temp_key = "winter"

    # 2) 场景叠加（用户手动选择优先；auto 时按天气自动判断）
    scene_label = ""
    if scene == "commute":
        style = "干练通勤淡妆"
        eye = "大地色眼影 + 自然内眼线，睫毛卷翘即可"
        lip = "裸粉、豆沙等低饱和唇膏，持久不沾杯"
        base = "哑光持妆底妆，遮瑕均匀，整体干净利落"
        images = ["makeup_commute.jpg"]
        scene_label = "通勤"
    elif scene == "trip":
        style = "出游元气淡妆"
        eye = "橘粉、蜜桃眼影，卧蚕提亮，卷翘睫毛"
        lip = "亮泽唇蜜，蜜桃或珊瑚色，元气显气色"
        base = "水光肌底妆，轻薄通透，户外持妆定妆"
        images = ["makeup_trip.jpg"]
        scene_label = "出游"
    elif scene == "rainy" or (scene == "auto" and rainy):
        style = "雨天防脱妆"
        eye = "防水眼线 + 防水睫毛膏，眼影选低饱和大地色避免晕染"
        lip = "持久唇釉或染唇液，豆沙、红棕不易掉色"
        base = "高持妆防水底妆，妆前控油，定妆喷雾二次固妆"
        images = ["makeup_rainy.jpg"]
        scene_label = "雨天"
    elif scene == "snowy" or (scene == "auto" and snowy):
        style = "雪景氛围妆"
        eye = "冷调粉棕眼影，睫毛卷翘，眼头提亮"
        lip = "莓果、正红滋润唇膏，与冷白雪景呼应"
        base = "水润保湿底妆，腮红适当加重提升红润感"
        images = ["makeup_snowy.jpg"]
        scene_label = "雪景"
    elif scene == "date":
        style = "约会甜美妆"
        eye = "粉橘眼影 + 卧蚕提亮，睫毛纤长"
        lip = "蜜桃、玫瑰色水光唇，柔焦腮红"
        base = "清透光泽底妆，底妆轻薄有皮肤质感"
        images = ["makeup_spring_3.jpg"]
        scene_label = "约会"
    elif scene == "interview":
        style = "面试正式通勤妆"
        eye = "哑光大地色眼影，细窄内眼线，睫毛自然卷翘"
        lip = "裸粉、豆沙等低饱和唇膏，端庄不显夸张"
        base = "哑光持妆底妆，遮瑕均匀，眉形修整干净利落"
        images = ["makeup_commute.jpg"]
        scene_label = "面试"
    elif scene == "party":
        style = "派对精致妆"
        eye = "珠光/亮片眼影叠加，上扬眼线，睫毛浓密卷翘"
        lip = "正红、莓果或金属感唇釉，妆面有存在感"
        base = "高遮瑕底妆，轮廓修容立体，腮红偏气场色"
        images = ["makeup_winter.jpg"]
        scene_label = "派对"
    elif scene == "sweet":
        style = "日系甜美妆"
        eye = "粉棕眼影 + 卧蚕提亮，圆眼型，睫毛纤长根根分明"
        lip = "水润蜜桃、草莓色唇釉，团状腮红显嫩"
        base = "水光奶油肌底妆，轻薄通透，保留皮肤光泽"
        images = ["makeup_spring.jpg"]
        scene_label = "甜美"
    elif scene == "retro":
        style = "复古港风妆"
        eye = "红棕/橘棕眼影，上扬眼线勾勒眼尾，浓眉有型"
        lip = "哑光红棕、复古正红唇，轮廓清晰"
        base = "哑光底妆带瓷感，修容强调颧骨与下颌线"
        images = ["makeup_autumn.jpg"]
        scene_label = "复古"

    # 3) 天气状况叠加提示
    if rainy and scene_label != "雨天":
        tips += " 雨天湿度大，底妆优先防水防脱，眼妆用防水眼线和睫毛膏。"
        base += "；雨天潮湿，注意控油防水"
    elif snowy and scene_label != "雪景":
        tips += " 雪天光线偏冷，腮红可适当加重，提升面部红润感。"
    elif humidity >= 70:
        tips += " 湿度较高，定妆要到位，避免妆容黏腻。"
    elif humidity <= 30:
        tips += " 空气干燥，妆前加强补水，避免浮粉。"

    # 4) 肤质 / 肤色差异化建议
    skin_tip = _skin_type_tip(skin_type)
    tone_tip = _skin_tone_tip(skin_tone)
    if skin_tip:
        tips += f" 【肤质·{skin_type}】{skin_tip}"
    if tone_tip:
        tips += f" 【肤色·{skin_tone}】{tone_tip}"

    return {
        "style": style,
        "base": base,
        "eye": eye,
        "lip": lip,
        "tips": tips,
        "images": images,
        "scene": scene_label or "日常",
        "temp_key": temp_key,
    }


def recommend_outfit(weather, scene="日常通勤", gender="女", style="随性休闲"):
    """
    根据天气（温度、晴雨、风、湿度）、场景、性别与风格偏好推荐穿搭。
    基础款按温度档×性别，再由风格偏好覆盖单品；返回上衣/下装/鞋履/配色/图集/提示。
    """
    if gender not in GENDERS:
        gender = "女"
    if style not in OUTFIT_STYLES:
        style = "随性休闲"

    if not weather:
        return {
            "temp_band": "未知",
            "top": "按当日气温选择薄外套或针织衫",
            "bottom": "长裤或半身裙，便于活动",
            "shoes": "舒适平底鞋或运动鞋",
            "colors": "基础黑、白、卡其百搭",
            "tips": "天气信息获取失败，以下为通用建议。",
            "weather_label": "通用",
            "images": ["outfit_default.jpg"],
            "gender": gender,
            "style": style,
        }

    temp = weather["temperature"]
    code = weather["weather_code"]
    windy = weather.get("wind_speed", 0) >= 20
    rainy = code in RAIN_CODES
    snowy = code in SNOW_CODES

    # 1) 温度档 × 性别：基础单品 / 配色 / 图集
    if temp >= 28:
        band, temp_key = "炎热", "summer"
        if gender == "女":
            base = {
                "top": "短袖 T 恤、吊带或薄衬衫，透气棉麻，可搭薄防晒衫",
                "bottom": "短裤、短裙、阔腿裤或薄款长裤",
                "shoes": "凉鞋、帆布鞋或透气运动鞋",
                "colors": "浅蓝、白色、浅粉、米色等清爽浅色系",
            }
        else:
            base = {
                "top": "短袖 T 恤、Polo 衫或薄款棉麻衬衫，透气宽松",
                "bottom": "休闲短裤、工装裤或薄款直筒长裤",
                "shoes": "板鞋、帆布鞋或透气运动鞋",
                "colors": "白、浅灰、卡其、藏蓝等清爽基础色",
            }
        tips = "高温注意防晒，出汗多选速干面料，随身补水。"
    elif temp >= 15:
        band, temp_key = "温和", "spring"
        if gender == "女":
            base = {
                "top": "长袖 T 恤、薄针织或衬衫，早晚加风衣/薄外套",
                "bottom": "牛仔裤、休闲长裤或过膝半裙",
                "shoes": "小白鞋、休闲鞋或短靴",
                "colors": "奶茶、卡其、豆绿、雾蓝等柔和大地色系",
            }
        else:
            base = {
                "top": "衬衫、薄针织或卫衣外搭夹克/风衣，叠穿方便",
                "bottom": "直筒牛仔裤、休闲西裤或工装长裤",
                "shoes": "板鞋、休闲皮鞋或低帮靴",
                "colors": "卡其、藏蓝、灰绿、米白等沉稳大地色",
            }
        tips = "昼夜温差较大，方便穿脱的叠穿最稳妥。"
    elif temp >= 5:
        band, temp_key = "凉爽", "autumn"
        if gender == "女":
            base = {
                "top": "毛衣、卫衣搭配风衣或薄棉服，内搭长袖打底",
                "bottom": "厚牛仔裤、灯芯绒裤或加绒半裙配打底袜",
                "shoes": "短靴、马丁靴或加绒休闲鞋",
                "colors": "焦糖、棕红、橄榄绿、灰色等暖调秋系",
            }
        else:
            base = {
                "top": "针织毛衣、卫衣外搭夹克、风衣或薄棉服",
                "bottom": "厚牛仔裤、休闲工装裤或灯芯绒长裤",
                "shoes": "马丁靴、工装靴或加绒休闲鞋",
                "colors": "棕褐、藏蓝、军绿、深灰等暖调秋系",
            }
        tips = "风大时注意颈部保暖，可选围巾叠穿。"
    else:
        band, temp_key = "寒冷", "winter"
        if gender == "女":
            base = {
                "top": "羽绒服/厚棉服 + 毛衣/针织打底，注意领口袖口防风",
                "bottom": "加绒长裤、羽绒裤或厚呢裙配保暖袜",
                "shoes": "保暖雪地靴或加绒皮鞋，防滑优先",
                "colors": "黑白灰、藏蓝、酒红等耐脏深色系，可用亮色围巾点缀",
            }
        else:
            base = {
                "top": "厚羽绒服/棉服 + 毛衣或抓绒打底，防风外套为主",
                "bottom": "加绒长裤、工装棉裤或厚牛仔裤",
                "shoes": "保暖雪地靴、加绒皮鞋或防滑运动鞋",
                "colors": "黑、灰、藏蓝、深棕等耐脏深色系，围巾帽子提亮",
            }
        tips = "室内外温差大，内层便于穿脱；出门注意护手护耳。"

    top, bottom, shoes, colors = base["top"], base["bottom"], base["shoes"], base["colors"]

    # 2) 风格偏好覆盖单品（在温度基础上换版型与搭配思路）
    style_override = _style_outfit(style, gender, temp_key)
    if style_override:
        top = style_override.get("top", top)
        bottom = style_override.get("bottom", bottom)
        shoes = style_override.get("shoes", shoes)
        colors = style_override.get("colors", colors)

    # 图集：优先「温度×性别×风格」专属图，缺图回退到温度性别通用图
    g_key = "f" if gender == "女" else "m"
    s_key = {"随性休闲": "casual", "简约通勤": "commute",
             "精致约会": "date", "运动机能": "sport"}.get(style, "casual")
    style_img = f"outfit_{temp_key}_{g_key}_{s_key}.jpg"
    generic = [f"outfit_{temp_key}_{g_key}.jpg", f"outfit_{temp_key}_{g_key}_2.jpg"]
    images = [style_img] if os.path.exists(os.path.join(IMG_DIR, style_img)) else generic

    # 3) 天气状况叠加
    weather_label = weather["weather_text"]
    if rainy:
        tips += " 雨天建议穿防水外套、备伞，鞋履选防滑不怕湿的款式，避免布鞋。"
        colors += "；雨天可选耐脏深色，避免浅色下装溅湿显脏"
    elif snowy:
        tips += " 雪天注意防滑保暖，裤脚避免拖地，鞋子优先防滑防水。"
    elif windy:
        tips += " 风力较大，外套选防风面料，长裙注意防吹翻。"

    # 4) 场景微调
    scene_tips = {
        "日常通勤": "版型利落简约，配色低调百搭，方便久坐与挤公共交通。",
        "出游逛街": "以舒适耐走为主，方便步行与拍照，可搭配亮色小配饰。",
        "约会聚餐": "可选有质感的单品，注重版型与配色协调，整体精致但不夸张。",
        "运动休闲": "速干运动面料为主，宽松透气，运动鞋最便于活动。",
        "正式商务": "选挺括面料与合身剪裁，配色沉稳，避免过于休闲的款式。",
        "校园青春": "单品宽松有活力，配色明快，便于长时间步行与课间走动。",
    }
    tips += f" 【{scene}】{scene_tips.get(scene, '')}"

    return {
        "temp_band": band,
        "top": top,
        "bottom": bottom,
        "shoes": shoes,
        "colors": colors,
        "tips": tips,
        "images": images,
        "weather_label": weather_label,
        "gender": gender,
        "style": style,
    }


def _style_outfit(style, gender, temp_key):
    """风格偏好 -> 单品覆盖（按性别给不同版型）；未覆盖字段沿用基础款。"""
    F = {
        "随性休闲": {
            "top": "宽松卫衣/针织开衫叠穿，版型舒适无束缚",
            "bottom": "直筒牛仔裤、休闲阔腿裤或随性半裙",
            "shoes": "帆布鞋、小白鞋或休闲板鞋",
            "colors": "牛仔蓝、米白、浅灰、卡其等松弛基础色",
        },
        "简约通勤": {
            "top": "衬衫/薄针织塞衣角，外搭西装外套或挺括风衣",
            "bottom": "烟管裤、直筒西裤或过膝半裙，线条利落",
            "shoes": "乐福鞋、低跟踝靴或简约通勤鞋",
            "colors": "黑、白、藏蓝、驼色等低饱和干练配色",
        },
        "精致约会": {
            "top": "针织衫、雪纺衫或蕾丝上衣，可选有设计感的外套",
            "bottom": "碎花裙、A 字半裙或垂感长裤",
            "shoes": "细带凉鞋、小高跟或精致短靴",
            "colors": "柔粉、奶白、酒红、香槟等温柔显气色配色",
        },
        "运动机能": {
            "top": "速干 T 恤、运动卫衣或防风冲锋衣",
            "bottom": "束脚运动裤、工装束脚裤或瑜伽leggings外搭短裤",
            "shoes": "专业运动鞋、跑鞋或户外徒步鞋",
            "colors": "黑、灰、藏蓝、荧光点缀等功能运动配色",
        },
    }
    M = {
        "随性休闲": {
            "top": "宽松卫衣、连帽衫或休闲衬衫，落肩版型",
            "bottom": "直筒牛仔裤、工装裤或宽松休闲裤",
            "shoes": "板鞋、帆布鞋或复古慢跑鞋",
            "colors": "牛仔蓝、灰、卡其、军绿等松弛基础色",
        },
        "简约通勤": {
            "top": "衬衫或薄针织，外搭西装夹克或针织开衫",
            "bottom": "修身直筒西裤或弹力牛仔裤，裤线整齐",
            "shoes": "德比鞋、休闲皮鞋或干净板鞋",
            "colors": "藏蓝、灰、棕、米白等沉稳干练配色",
        },
        "精致约会": {
            "top": "质感针织衫、衬衫或西装外套，注重面料与剪裁",
            "bottom": "垂感西裤或合身休闲裤，避免过于宽松",
            "shoes": "皮质休闲鞋、切尔西靴或利落短靴",
            "colors": "深棕、墨绿、酒红、藏蓝等有质感配色",
        },
        "运动机能": {
            "top": "速干运动 T 恤、抓绒卫衣或防风冲锋衣",
            "bottom": "束脚运动裤、工装裤或户外长裤",
            "shoes": "跑鞋、户外徒步鞋或复古运动鞋",
            "colors": "黑、灰、深蓝、橙绿点缀等功能运动配色",
        },
    }
    table = F if gender == "女" else M
    return table.get(style)
