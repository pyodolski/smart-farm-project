import pymysql
from config import DB_CONFIG

def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.MySQLError as e:
        print(f"DB 연결 실패: {e}")
        return None

def get_dict_cursor_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        return conn, cursor
    except pymysql.MySQLError as e:
        print(f"DB 연결 실패: {e}")
        return None, None 