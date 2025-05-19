import pymysql
from config import DB_CONFIG

def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.MySQLError as e:
        print(f"DB 연결 실패: {e}")
        return None

def check_database():
    try:
        print("데이터베이스 연결 시도 중...")
        print(f"연결 정보: {DB_CONFIG}")
        conn = pymysql.connect(**DB_CONFIG)
        print("데이터베이스 연결 성공!")

        cursor = conn.cursor()
        
        # 테이블 목록 조회
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"테이블 목록: {tables}")
        
        # board 테이블 구조 확인
        try:
            cursor.execute("DESCRIBE board")
            columns = cursor.fetchall()
            print(f"board 테이블 구조: {columns}")
            
            # 게시글 수 확인
            cursor.execute("SELECT COUNT(*) FROM board")
            count = cursor.fetchone()
            print(f"board 테이블 게시글 수: {count}")
            
            # 샘플 게시글 확인
            cursor.execute("SELECT * FROM board LIMIT 1")
            post = cursor.fetchone()
            if post:
                print(f"샘플 게시글: {post}")
            else:
                print("게시글이 없습니다.")
        except Exception as e:
            print(f"board 테이블 조회 실패: {e}")
        
        # likes 테이블 구조 확인
        try:
            cursor.execute("DESCRIBE likes")
            columns = cursor.fetchall()
            print(f"likes 테이블 구조: {columns}")
        except Exception as e:
            print(f"likes 테이블 조회 실패: {e}")
        
        # comments 테이블 구조 확인
        try:
            cursor.execute("DESCRIBE comments")
            columns = cursor.fetchall()
            print(f"comments 테이블 구조: {columns}")
        except Exception as e:
            print(f"comments 테이블 조회 실패: {e}")
        
        cursor.close()
        conn.close()
        print("데이터베이스 연결 종료")
        
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}")

if __name__ == "__main__":
    check_database() 