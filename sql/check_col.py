import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root',
                       password='Root1234', database='nanjing_travel', charset='utf8mb4')
cur = conn.cursor()
cur.execute("SHOW COLUMNS FROM scenic_spot LIKE 'image'")
row = cur.fetchone()
if not row:
    cur.execute("ALTER TABLE scenic_spot ADD COLUMN image VARCHAR(200) COMMENT '配图文件名' AFTER recommend_traffic")
    conn.commit()
    print('image column added')
else:
    print('image column exists')
conn.close()
