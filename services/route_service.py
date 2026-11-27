# services/route_service.py
from collections import deque
from models.subway import SubwayLine, SubwayStation


def _build_graph():
    """
    基于数据库构建地铁图：
    - station_lines: 站点名 -> 经过的线路列表
    - adj: 相邻站点邻接表（同一线路内按 sort 相邻连边）
    """
    stations = SubwayStation.query.order_by(SubwayStation.line_id, SubwayStation.sort).all()

    station_lines = {}
    adj = {}
    lines = {}

    for st in stations:
        lines.setdefault(st.line_id, []).append(st.station_name)
        station_lines.setdefault(st.station_name, set()).add(st.line_id)
        adj.setdefault(st.station_name, set())

    # 同一线路内相邻站点连边
    for line_id, names in lines.items():
        for i in range(len(names) - 1):
            a, b = names[i], names[i + 1]
            adj[a].add(b)
            adj[b].add(a)

    return station_lines, adj


def _line_name_map():
    return {ln.id: ln.line_name for ln in SubwayLine.query.all()}


def find_station(name):
    """精确匹配站点，找不到返回 None。"""
    if not name:
        return None
    return SubwayStation.query.filter_by(station_name=name.strip()).first()


def plan_route(origin, destination):
    """
    BFS 求起点到终点的最短站点路径。
    返回 dict：
      found: 是否找到
      origin / destination: 站点名
      path: 途经站点列表
      transfers: 换乘段说明 [{line_name, stations}]
      total_stations: 乘坐站数
      transfer_count: 换乘次数
      message: 提示信息
    """
    origin = (origin or "").strip()
    destination = (destination or "").strip()

    if not origin or not destination:
        return {"found": False, "message": "请输入起点和终点"}

    if origin == destination:
        return {"found": False, "message": "起点和终点不能相同"}

    station_lines, adj = _build_graph()
    line_names = _line_name_map()

    if origin not in station_lines:
        return {"found": False, "message": f"未找到站点「{origin}」，请核对名称"}
    if destination not in station_lines:
        return {"found": False, "message": f"未找到站点「{destination}」，请核对名称"}

    # BFS 记录前驱
    prev = {origin: None}
    queue = deque([origin])

    while queue:
        cur = queue.popleft()
        if cur == destination:
            break
        for nxt in adj[cur]:
            if nxt not in prev:
                prev[nxt] = cur
                queue.append(nxt)

    if destination not in prev:
        return {"found": False, "message": "当前线路数据中暂无可达路线"}

    # 回溯路径
    path = []
    cur = destination
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    # 分段：按乘坐线路切分路径
    segments = []
    current_line = None
    segment_stations = [path[0]]

    for i in range(1, len(path)):
        prev_st, curr_st = path[i - 1], path[i]
        common = station_lines[prev_st] & station_lines[curr_st]
        line_id = next(iter(common)) if common else None

        if current_line is None:
            current_line = line_id
        elif line_id != current_line and line_id is not None:
            segments.append({
                "line_name": line_names.get(current_line, "未知线路"),
                "stations": segment_stations,
            })
            current_line = line_id
            segment_stations = [prev_st]

        segment_stations.append(curr_st)

    segments.append({
        "line_name": line_names.get(current_line, "未知线路"),
        "stations": segment_stations,
    })

    transfer_count = len(segments) - 1
    total_stations = len(path) - 1

    return {
        "found": True,
        "origin": origin,
        "destination": destination,
        "path": path,
        "segments": segments,
        "total_stations": total_stations,
        "transfer_count": transfer_count,
        "message": f"共 {total_stations} 站，换乘 {transfer_count} 次",
    }


def all_station_names():
    """返回全部站点名，供页面下拉/自动补全使用。"""
    rows = SubwayStation.query.order_by(SubwayStation.station_name).all()
    seen = []
    for r in rows:
        if r.station_name not in seen:
            seen.append(r.station_name)
    return seen
