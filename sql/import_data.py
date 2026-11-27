# 临时导入脚本：解析 init_db.sql，批量执行 INSERT（绕过注释与分号问题）
import re
import pymysql

conn = pymysql.connect(
    host="localhost", port=3306, user="root", password="Root1234",
    database="nanjing_travel", charset="utf8mb4",
)
cur = conn.cursor()

sql = open(r"E:\byys\sql\init_db.sql", encoding="utf-8").read()

# 去掉 -- 注释行
lines = [ln for ln in sql.splitlines() if not ln.strip().startswith("--")]
sql = "\n".join(lines)

# 按分号拆分语句
stmts = [s.strip() for s in sql.split(";") if s.strip()]

# 先关闭外键检查，清空旧数据
cur.execute("SET FOREIGN_KEY_CHECKS = 0")
for tbl in ("subway_station", "bus_line", "scenic_spot", "subway_line"):
    cur.execute(f"DELETE FROM {tbl}")
cur.execute("SET FOREIGN_KEY_CHECKS = 1")

for stmt in stmts:
    if stmt.upper().startswith("INSERT"):
        cur.execute(stmt)

conn.commit()

for tbl in ("subway_line", "subway_station", "bus_line", "scenic_spot"):
    cur.execute(f"SELECT COUNT(*) FROM {tbl}")
    print(tbl, cur.fetchone()[0])

conn.close()
print("import done")
