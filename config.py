import pymysql
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def get_db_config():
    """환경변수에서 DB 설정을 가져옵니다."""
    
    # 필수 환경변수 확인
    db_password = os.getenv('DB_PASSWORD')
    if not db_password:
        raise ValueError(
            "DB_PASSWORD 환경변수가 설정되지 않았습니다. "
            ".env 파일을 확인하거나 .env.example을 복사해서 설정해주세요."
        )
    
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': db_password,
        'database': os.getenv('DB_NAME', 'smartfarm'),
        'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
        'port': int(os.getenv('DB_PORT', 3306))
    }

# DB 설정 로드
try:
    DB_CONFIG = get_db_config()
    print(f"✅ DB 설정 로드 완료: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
except ValueError as e:
    print(f"❌ DB 설정 오류: {e}")
    raise