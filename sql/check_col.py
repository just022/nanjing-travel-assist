import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root',
                       password='Root1234', database='nanjing_travel', charset='utf8mb4')
cur = conn.cursor()

def ensure_column(table, column, ddl):
    cur.execute(f"SHOW COLUMNS FROM {table} LIKE '{column}'")
    if not cur.fetchone():
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")
        print(f"added {table}.{column}")
    else:
        print(f"exists {table}.{column}")

ensure_column("scenic_spot", "image", "image VARCHAR(200) COMMENT '主配图文件名' AFTER recommend_traffic")
ensure_column("scenic_spot", "images", "images VARCHAR(500) COMMENT '图集文件名，逗号分隔' AFTER image")
ensure_column("scenic_spot", "description", "description TEXT COMMENT '图文介绍' AFTER images")
ensure_column("scenic_spot", "open_time", "open_time VARCHAR(100) COMMENT '开放时间' AFTER description")
ensure_column("scenic_spot", "ticket", "ticket VARCHAR(100) COMMENT '门票信息' AFTER open_time")
ensure_column("scenic_spot", "duration", "duration VARCHAR(50) COMMENT '建议游玩时长' AFTER ticket")
ensure_column("scenic_spot", "tags", "tags VARCHAR(200) COMMENT '亮点标签，逗号分隔' AFTER duration")
ensure_column("bus_line", "stations", "stations TEXT COMMENT '途经站点，逗号分隔'")
ensure_column("bus_line", "first_time", "first_time VARCHAR(20) COMMENT '首班车时间'")
ensure_column("bus_line", "last_time", "last_time VARCHAR(20) COMMENT '末班车时间'")

conn.commit()
conn.close()
