# services/route_service.py
import heapq
from models.subway import SubwayLine, SubwayStation
from models.bus import BusLine, BusStation
from models.city import City

# 城市编码 -> 城市名称 的兜底映射（数据库 city 表未灌入时使用）
DEFAULT_CITY_NAME = {"nanjing": "南京"}


def get_cities():
    """返回可选城市列表（已收录的优先），供页面下拉。"""
    cities = City.query.order_by(City.id).all()
    if cities:
        return [c.to_dict() for c in cities]
    return [{"code": code, "name": name, "enabled": True}
            for code, name in DEFAULT_CITY_NAME.items()]


def get_city_name(code):
    """根据城市编码取城市名。"""
    if not code:
        code = "nanjing"
    city = City.query.filter_by(code=code).first()
    if city:
        return city.name
    return DEFAULT_CITY_NAME.get(code, code)


def city_available(code):
    """判断该城市是否已收录交通数据。"""
    if not code:
        code = "nanjing"
    city = City.query.filter_by(code=code).first()
    if city is None:
        # 表里没有记录时，默认南京可用
        return code in DEFAULT_CITY_NAME
    return bool(city.enabled)


# 边权重：地铁优先（站间代价低），公交作为接驳（站间代价高），引导算法优先走地铁
SUBWAY_WEIGHT = 1
BUS_WEIGHT = 3

# 出行耗时估算（分钟）：地铁/公交站间平均行驶 + 停站；换乘额外步行等待
SUBWAY_MIN_PER_STATION = 2.5
BUS_MIN_PER_STATION = 4
TRANSFER_PENALTY_MIN = 6  # 每次换乘步行 + 等待
WALK_MIN = 5  # 起点/终点到站点的步行预留

# 票价简化规则（南京公交/地铁起步价，毕设演示用）
BUS_FARE = 2  # 公交统一 2 元
SUBWAY_BASE_FARE = 2  # 地铁起步 2 元（含 4 站以内）
SUBWAY_FARE_PER = 1  # 超出起步后每 4 站加 1 元


def _estimate_duration(segments, total_stations):
    """按分段类型估算全程耗时（分钟），返回取整后的分钟数。"""
    minutes = WALK_MIN
    for seg in segments:
        n = max(len(seg["stations"]) - 1, 0)
        minutes += n * (SUBWAY_MIN_PER_STATION if seg["kind"] == "地铁" else BUS_MIN_PER_STATION)
    transfer_count = len(segments) - 1
    minutes += transfer_count * TRANSFER_PENALTY_MIN
    return max(round(minutes), total_stations + 2)


def _estimate_fare(segments):
    """简化估算票价：公交 2 元/段；地铁按站数分段计价。返回 (票价区间文本, 估算金额)。"""
    subway_segs = [s for s in segments if s["kind"] == "地铁"]
    bus_segs = [s for s in segments if s["kind"] == "公交"]
    fare = 0
    for seg in subway_segs:
        n = max(len(seg["stations"]) - 1, 0)
        fare += SUBWAY_BASE_FARE + (n // 4) * SUBWAY_FARE_PER
    fare += len(bus_segs) * BUS_FARE
    if fare <= 0:
        return "-", 0
    return f"约 {fare} 元", fare


def _build_graph():
    """
    基于数据库构建「地铁 + 公交」混合出行图：
    - station_lines: 站点名 -> {线路标识: 线路名称}
    - adj: 邻接表，adj[a] = {b: 边权重}
    同一名称站点视为同一节点，地铁与公交在此自然换乘。
    """
    station_lines = {}
    adj = {}

    def _add_edge(a, b, weight):
        adj.setdefault(a, {})[b] = weight
        adj.setdefault(b, {})[a] = weight

    # 地铁
    subway = SubwayStation.query.order_by(SubwayStation.line_id, SubwayStation.sort).all()
    line_names = {ln.id: ln.line_name for ln in SubwayLine.query.all()}
    lines = {}
    for st in subway:
        key = f"地铁:{st.line_id}"
        lines.setdefault(st.line_id, []).append(st.station_name)
        station_lines.setdefault(st.station_name, {})[key] = line_names.get(st.line_id, "地铁")
        adj.setdefault(st.station_name, {})

    for line_id, names in lines.items():
        for i in range(len(names) - 1):
            _add_edge(names[i], names[i + 1], SUBWAY_WEIGHT)

    # 公交（按 line_id 取站点序列）
    bus_lines = BusLine.query.order_by(BusLine.id).all()
    bus_stations = BusStation.query.all()
    bus_map = {}
    for bs in bus_stations:
        bus_map.setdefault(bs.line_id, []).append(bs)
    for bl in bus_lines:
        seq = sorted(bus_map.get(bl.id, []), key=lambda x: x.sort)
        names = [s.station_name for s in seq]
        key = f"公交:{bl.id}"
        for name in names:
            station_lines.setdefault(name, {})[key] = bl.line_name
            adj.setdefault(name, {})
        for i in range(len(names) - 1):
            _add_edge(names[i], names[i + 1], BUS_WEIGHT)

    return station_lines, adj


def _line_label(line_key):
    """线路标识 -> 展示名（地铁/公交）。"""
    if not line_key:
        return "未知线路"
    kind, _ = line_key.split(":", 1)
    return "地铁" if kind == "地铁" else "公交"


def _build_segment(line_key, stations, station_lines, bus_times):
    """组装一个乘行分段，附带线路名、类型、站数与公交首末班。"""
    kind = _line_label(line_key)
    line_name = station_lines[stations[0]].get(line_key, "未知线路")
    seg = {
        "line_name": line_name,
        "kind": kind,
        "stations": stations,
        "station_count": max(len(stations) - 1, 0),
    }
    if kind == "公交" and line_key:
        _, bus_id = line_key.split(":", 1)
        times = bus_times.get(int(bus_id))
        if times:
            seg["first_time"], seg["last_time"] = times
    return seg


def find_station(name):
    """精确匹配站点，找不到返回 None。"""
    if not name:
        return None
    return SubwayStation.query.filter_by(station_name=name.strip()).first()


def plan_route(origin, destination, city_code="nanjing"):
    """
    BFS 求起点到终点的最短站点路径（地铁 + 公交混合）。
    返回 dict：found / origin / destination / path / segments /
              total_stations / transfer_count / message / city_name
    """
    origin = (origin or "").strip()
    destination = (destination or "").strip()
    city_name = get_city_name(city_code)

    if not city_available(city_code):
        return {
            "found": False,
            "message": f"「{city_name}」的交通数据暂未收录，敬请期待。",
            "city_name": city_name,
        }

    if not origin or not destination:
        return {"found": False, "message": "请选择起点和终点", "city_name": city_name}

    if origin == destination:
        return {"found": False, "message": "起点和终点不能相同", "city_name": city_name}

    station_lines, adj = _build_graph()

    if origin not in station_lines:
        return {"found": False, "message": f"未找到站点「{origin}」，请核对名称", "city_name": city_name}
    if destination not in station_lines:
        return {"found": False, "message": f"未找到站点「{destination}」，请核对名称", "city_name": city_name}

    # Dijkstra：按边权重求最优路径（地铁优先，减少公交接驳与换乘）
    dist = {origin: 0}
    prev = {origin: None}
    pq = [(0, origin)]

    while pq:
        cur_dist, cur = heapq.heappop(pq)
        if cur == destination:
            break
        if cur_dist > dist.get(cur, float("inf")):
            continue
        for nxt, w in adj[cur].items():
            nd = cur_dist + w
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                prev[nxt] = cur
                heapq.heappush(pq, (nd, nxt))

    if destination not in prev:
        return {"found": False, "message": "当前线路数据中暂无可达路线", "city_name": city_name}

    # 回溯路径
    path = []
    cur = destination
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    # 公交运营时间映射（供分段展示首末班提示）
    bus_times = {bl.id: (bl.first_time, bl.last_time) for bl in BusLine.query.all()}

    # 分段：按乘坐线路（地铁/公交 + 具体线路）切分
    segments = []
    current_line = None
    segment_stations = [path[0]]

    def _common_line(a, b):
        common = station_lines[a].keys() & station_lines[b].keys()
        if not common:
            return None
        # 优先取地铁线路，避免同名公交线干扰同线连续判断
        subway_keys = [k for k in common if k.startswith("地铁:")]
        return subway_keys[0] if subway_keys else next(iter(common))

    for i in range(1, len(path)):
        prev_st, curr_st = path[i - 1], path[i]
        line_key = _common_line(prev_st, curr_st)

        if current_line is None:
            current_line = line_key
        elif line_key != current_line and line_key is not None:
            segments.append(_build_segment(current_line, segment_stations, station_lines, bus_times))
            current_line = line_key
            segment_stations = [prev_st]

        segment_stations.append(curr_st)

    segments.append(_build_segment(current_line, segment_stations, station_lines, bus_times))

    transfer_count = len(segments) - 1
    total_stations = len(path) - 1
    duration_min = _estimate_duration(segments, total_stations)
    fare_text, fare_value = _estimate_fare(segments)

    # 换乘指引：逐段说明在哪站换乘哪条线
    guides = []
    for idx, seg in enumerate(segments):
        if idx == 0:
            guides.append(f"在 {path[0]} 站乘坐 {seg['line_name']}")
        else:
            prev_seg = segments[idx - 1]
            guides.append(f"在 {seg['stations'][0]} 站由 {prev_seg['line_name']} 换乘 {seg['line_name']}")
    guides.append(f"在 {path[-1]} 站下车后步行前往目的地")

    return {
        "found": True,
        "origin": origin,
        "destination": destination,
        "path": path,
        "segments": segments,
        "total_stations": total_stations,
        "transfer_count": transfer_count,
        "duration_min": duration_min,
        "fare_text": fare_text,
        "fare_value": fare_value,
        "guides": guides,
        "message": f"共 {total_stations} 站，换乘 {transfer_count} 次，约 {duration_min} 分钟，{fare_text}",
        "city_name": city_name,
    }


def all_station_names(city_code="nanjing"):
    """返回全部可选站点名（地铁 + 公交），供页面下拉。城市未收录时返回空。"""
    if not city_available(city_code):
        return []
    names = []
    seen = set()
    for st in SubwayStation.query.order_by(SubwayStation.station_name).all():
        if st.station_name not in seen:
            seen.add(st.station_name)
            names.append(st.station_name)
    for bs in BusStation.query.order_by(BusStation.station_name).all():
        if bs.station_name not in seen:
            seen.add(bs.station_name)
            names.append(bs.station_name)
    return sorted(names)
