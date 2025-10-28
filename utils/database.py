import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

def get_db_connection():
    try:
        # PostgreSQL 연결 설정
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
        return conn
    except psycopg2.Error as e:
        print(f"DB 연결 실패: {e}")
        return None

def get_dict_cursor_connection():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        return conn, cursor
    except psycopg2.Error as e:
        print(f"DB 연결 실패: {e}")
        return None, None 