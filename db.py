import pymysql

# MariaDB 연결
conn = pymysql.connect(
    host='18.182.31.2',
    user='herita',
    password='201030',
    database='HERITA_TEST',
    connect_timeout=10
)

cursor = conn.cursor()

# 데이터 삽입 테스트
cursor.execute("INSERT INTO test_table (name) VALUES ('Flower Test');")
conn.commit()

# 데이터 확인
cursor.execute("SELECT * FROM test_table;")
for row in cursor.fetchall():
    print(row)

# 연결 종료
cursor.close()
conn.close()
