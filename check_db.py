import psycopg2
from config import DB_CONFIG

def get_db_connection():
    try:
        return psycopg2.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
    except psycopg2.Error as e:
        print(f"DB 연결 실패: {e}")
        return None

def check_database():
    try:
        print("데이터베이스 연결 시도 중...")
        print(f"연결 정보: {DB_CONFIG}")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
        print("데이터베이스 연결 성공!")

        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        print(f"테이블 목록: {[table[0] for table in tables]}")
        
        # board 테이블 구조 확인 (PostgreSQL 문법)
        try:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'board'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print(f"board 테이블 구조: {columns}")
            
            # 게시글 수 확인
            cursor.execute("SELECT COUNT(*) FROM board")
            count = cursor.fetchone()
            print(f"board 테이블 게시글 수: {count[0]}")
            
            # 샘플 게시글 확인
            cursor.execute("SELECT * FROM board LIMIT 1")
            post = cursor.fetchone()
            if post:
                print(f"샘플 게시글: {post}")
            else:
                print("게시글이 없습니다.")
        except Exception as e:
            print(f"board 테이블 조회 실패: {e}")
        
        # farms 테이블 구조 확인
        try:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'farms'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print(f"farms 테이블 구조: {columns}")
            
            # 농장 수 확인
            cursor.execute("SELECT COUNT(*) FROM farms")
            count = cursor.fetchone()
            print(f"farms 테이블 농장 수: {count[0]}")
        except Exception as e:
            print(f"farms 테이블 조회 실패: {e}")
        
        cursor.close()
        conn.close()
        print("데이터베이스 연결 종료")
        
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}")

if __name__ == "__main__":
    check_database() 