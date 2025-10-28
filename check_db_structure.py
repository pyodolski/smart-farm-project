#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def check_db_structure():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'pyodolski'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'smartfarm'),
            port=int(os.getenv('DB_PORT', 5432))
        )
        
        cur = conn.cursor()
        
        print("=== 테이블 목록 ===")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        for table in tables:
            print(f"테이블: {table[0]}")
        
        print("\n=== users 테이블 구조 ===")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """)
        columns = cur.fetchall()
        for col in columns:
            print(f"컬럼: {col[0]} ({col[1]})")
        
        print("\n=== farms 테이블 구조 ===")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'farms'
        """)
        columns = cur.fetchall()
        for col in columns:
            print(f"컬럼: {col[0]} ({col[1]})")
        
        print("\n=== users 테이블 데이터 (처음 5개) ===")
        cur.execute("SELECT * FROM users LIMIT 5")
        users = cur.fetchall()
        for user in users:
            print(f"사용자: {user}")
        
        conn.close()
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    check_db_structure()