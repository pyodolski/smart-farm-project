import pymysql
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 필수 환경변수 확인
required_env_vars = ['DB_PASSWORD']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"필수 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'smartfarm'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
    'port': int(os.getenv('DB_PORT', 3306))
}