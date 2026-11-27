# services/recommend_service.py
import re
from models.spot import ScenicSpot
from models.user import RouteFavorite
from services import route_service, makeup_service


# 偏好大类 -> 景点标签关键词映射（用于把用户选择的大类匹配到景点 tags）
PREFERENCE_MAP = {
    "历史古迹": ["历史", "古迹", "博物馆", "文物", "遗址", "民国", "明代", "近代史", "古刹", "古寺", "石窟", "世界遗产"],
    "自然风光": ["山", "湖", "江景", "赏枫", "赏荷", "秋景", "四季风光", "观景", "滨江", "园林", "水乡"],
    "美食小吃": ["美食", "小吃", "古街", "古巷", "商业街", "古镇"],
    "拍照打卡": ["拍照", "街拍", "打卡", "文创", "民国建筑", "洋房", "琉璃塔", "光影"],
    "亲子研学": ["亲子", "研学", "科普", "文物", "博物馆"],
    "休闲散步": ["休闲", "漫步", "骑行", "划船", "城市漫步", "城墙", "祈福"],
}

# 季节 -> 应季推荐标签（当前天气/季节加成）
SEASON_TAGS = {
    "春": ["赏樱", "梅花山", "四季风光"],
    "夏": ["赏荷", "湖景", "划船", "城市湖景"],
    "秋": ["秋景", "赏枫名山", "梧桐", "银杏"],
    "冬": ["四季风光", "古刹", "名楼"],
}

# 可接受时长档位（小时）-> 解析景点时长后比较
DURATION_BUCKETS = {
    "1小时内": 1.5,
    "半天": 3,
    "一整天": 5,
}


def _parse_duration(duration):
    """把 '2—3小时' / '1—1.5小时' 解析为 (最低小时, 最高小时)，失败返回 (1, 3)。"""
    if not duration:
        return 1, 3
    nums = re.findall(r"\d+(?:\.\d+)?", duration)
    if len(nums) >= 2:
        return float(nums[0]), float(nums[1])
    if len(nums) == 1:
        v = float(nums[0])
        return v, v
    return 1, 3


def _season_from_weather(weather):
    """根据天气温度粗略判断季节倾向，用于应季加成。"""
    if not weather:
        return None
    t = weather.get("temperature", 18)
    if t >= 25:
        return "夏"
    if t >= 15:
        return "春"
    if t >= 5:
        return "秋"
    return "冬"


def _favorite_tags(user_id):
    """从用户历史收藏路线关联的目的地景点中提取偏好标签。"""
    if not user_id:
        return set()
    favs = RouteFavorite.query.filter_by(user_id=user_id).all()
    names = {f.destination for f in favs}
    if not names:
        return set()
    spots = ScenicSpot.query.filter(ScenicSpot.spot_name.in_(list(names))).all()
    tags = set()
    for s in spots:
        if s.tags:
            tags.update(t.strip() for t in s.tags.split(","))
    return tags


def recommend_spots(preferences=None, duration_bucket="半天", weather=None,
                    user_id=None, limit=6, origin=None, city_code="nanjing"):
    """
    综合打分预测推荐景点。
    打分维度：标签偏好匹配、时长适配、应季加成、历史收藏偏好、起点就近。
    返回 list[dict]：景点对象 + 得分明细 + 配套路线。
    """
    preferences = preferences or []
    season = _season_from_weather(weather)
    fav_tags = _favorite_tags(user_id)
    max_hours = DURATION_BUCKETS.get(duration_bucket, 3)

    # 偏好大类对应的关键词集合
    pref_keywords = set()
    for p in preferences:
        pref_keywords.update(PREFERENCE_MAP.get(p, []))

    spots = ScenicSpot.query.order_by(ScenicSpot.id).all()
    scored = []

    for spot in spots:
        tags = [t.strip() for t in (spot.tags or "").split(",") if t.strip()]
        tag_set = set(tags)
        low, high = _parse_duration(spot.duration)
        score = 0
        reasons = []

        # 1) 标签偏好匹配（权重最高）
        if pref_keywords:
            hit = tag_set & pref_keywords
            if hit:
                score += 30 * len(hit)
                reasons.append(f"契合你偏好的「{ '、'.join(list(hit)[:2]) }」")
            else:
                score -= 5

        # 2) 时长适配
        if high <= max_hours:
            score += 12
            reasons.append(f"约 {spot.duration}，符合时长安排")
        elif low <= max_hours:
            score += 6
        else:
            score -= 10

        # 3) 应季加成
        if season:
            season_hit = tag_set & set(SEASON_TAGS.get(season, []))
            if season_hit:
                score += 10
                reasons.append(f"{season}季应景（{ '、'.join(list(season_hit)[:2]) }）")

        # 4) 历史收藏偏好加成
        if fav_tags:
            fav_hit = tag_set & fav_tags
            if fav_hit:
                score += 15
                reasons.append("与你之前收藏的喜好相近")

        # 免费景点轻微加分（预算友好）
        if spot.ticket and "免费" in spot.ticket:
            score += 4

        # 5) 起点就近加成：有起点时，按到最近站点的站数折算，越近加分越多
        if origin and spot.nearest_station:
            near = route_service.plan_route(origin, spot.nearest_station, city_code=city_code)
            if near.get("found"):
                stations = near.get("total_stations", 0)
                near_score = max(0, 10 - stations)  # 10 站内线性递减，10 站以上不加分
                score += near_score
                if near_score >= 6:
                    reasons.append(f"离你较近（约 {stations} 站）")

        scored.append({
            "spot": spot,
            "score": score,
            "reasons": reasons,
            "tags": tags,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


def plan_to_spot(spot_name, origin, city_code="nanjing"):
    """为推荐景点生成从起点到景点最近站点的配套路线；不可达时回退交通建议文本。"""
    spot = ScenicSpot.query.filter_by(spot_name=spot_name).first()
    nearest = spot.nearest_station if spot else None
    traffic = spot.recommend_traffic if spot else "请结合当地公共交通前往"

    destination = nearest or spot_name
    if origin and nearest:
        result = route_service.plan_route(origin, nearest, city_code=city_code)
        if result.get("found"):
            # 终点显示为景点名，路线终点为最近站点
            result["destination"] = spot_name
            result["message"] = f"到「{nearest}」站后步行前往；{result['message']}"
            return result

    return {
        "found": False,
        "origin": origin or "未指定起点",
        "destination": spot_name,
        "message": traffic,
        "segments": [],
        "path": [],
        "total_stations": 0,
        "transfer_count": 0,
        "traffic_hint": traffic,
    }


# 时长档位 -> 一条动线上串联的景点数量
ITINERARY_SIZE = {"1小时内": 1, "半天": 2, "一整天": 3}


def _spot_nearest(spot):
    return spot.nearest_station if spot else None


def _segment_route(from_name, from_station, to_spot, city_code):
    """起点（站点或景点名）到下一景点最近站点的一段路线。"""
    if from_station and to_spot.nearest_station:
        result = route_service.plan_route(from_station, to_spot.nearest_station, city_code=city_code)
        if result.get("found"):
            result["destination"] = to_spot.spot_name
            result["message"] = f"到「{to_spot.nearest_station}」站后步行前往；{result['message']}"
            return result
    return None


def build_itinerary(scored_items, origin, city_code="nanjing", duration_bucket="半天"):
    """
    把打分靠前的景点串成一条有序一日游动线。
    按时长取 1~3 个景点，依次求 起点→A、A→B、B→C 的分段路线，
    返回 {spots, legs, summary}；legs[i] 为第 i 段（到第 i 个景点）的路线。
    """
    size = ITINERARY_SIZE.get(duration_bucket, 2)
    chosen = scored_items[:size]
    legs = []
    prev_station = None

    for idx, item in enumerate(chosen):
        spot = item["spot"]
        if idx == 0:
            leg = plan_to_spot(spot.spot_name, origin, city_code=city_code) if origin \
                else {"found": False, "origin": origin or "未指定起点",
                      "destination": spot.spot_name, "message": spot.recommend_traffic,
                      "segments": [], "path": [], "total_stations": 0, "transfer_count": 0}
        else:
            prev_spot = chosen[idx - 1]["spot"]
            leg = _segment_route(prev_spot.spot_name, prev_station, spot, city_code)
            if leg is None:
                leg = {"found": False, "origin": prev_spot.spot_name,
                       "destination": spot.spot_name, "message": spot.recommend_traffic,
                       "segments": [], "path": [], "total_stations": 0, "transfer_count": 0}
        legs.append(leg)
        prev_station = _spot_nearest(spot) or spot.spot_name

    # 汇总全程站数/换乘/耗时
    total_stations = sum(l.get("total_stations", 0) for l in legs)
    total_transfer = sum(l.get("transfer_count", 0) for l in legs)
    total_min = sum(l.get("duration_min", 0) for l in legs)
    found_legs = sum(1 for l in legs if l.get("found"))

    summary = {
        "spot_count": len(chosen),
        "total_stations": total_stations,
        "total_transfer": total_transfer,
        "total_min": total_min,
        "found_count": found_legs,
        "text": f"串联 {len(chosen)} 个景点，共 {total_stations} 站，换乘 {total_transfer} 次，约 {total_min} 分钟"
        if found_legs else "部分景点公共交通暂不可达，已附交通建议",
    }
    return {"spots": chosen, "legs": legs, "summary": summary}


def preference_options():
    """返回可选偏好大类。"""
    return list(PREFERENCE_MAP.keys())
