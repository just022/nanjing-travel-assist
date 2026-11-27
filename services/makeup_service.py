# services/makeup_service.py
import urllib.request
import json

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


def _get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_nanjing_weather():
    """获取南京当前天气，返回 dict；接口失败时返回兜底天气并标注。"""
    try:
        geo = _get_json(GEO_URL)
        loc = geo["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        data = _get_json(WEATHER_URL.format(lat=lat, lon=lon))
        cur = data["current"]
        code = cur.get("weather_code", 0)
        return {
            "temperature": round(cur["temperature_2m"]),
            "humidity": cur["relative_humidity_2m"],
            "wind_speed": round(cur["wind_speed_10m"]),
            "weather_code": code,
            "weather_text": WEATHER_MAP.get(code, "未知"),
            "city": loc.get("name", "南京"),
            "fallback": False,
        }
    except Exception:
        return dict(FALLBACK_WEATHER)


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
