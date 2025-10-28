#!/usr/bin/env python3
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

load_dotenv()

def check_greenhouses():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        
        print("=== 데이터베이스 연결 성공 ===")
        
        # 일반 커서로 테스트
        cur = conn.cursor()
        cur.execute("SELECT id, name, farm_id FROM greenhouses")
        greenhouses = cur.fetchall()
        
        print(f"\n=== 모든 비닐하우스 (일반 커서) ===")
        for gh in greenhouses:
            print(f"ID: {gh[0]}, 이름: {gh[1]}, 농장ID: {gh[2]}")
        
        # RealDictCursor로 테스트
        cur_dict = conn.cursor(psycopg2.extras.RealDictCursor)
        cur_dict.execute("SELECT id, name, farm_id FROM greenhouses WHERE farm_id = %s", (2,))
        greenhouses_dict = cur_dict.fetchall()
        
        print(f"\n=== farm_id=2인 비닐하우스 (RealDictCursor) ===")
        for gh in greenhouses_dict:
            print(f"ID: {gh['id']}, 이름: {gh['name']}, 농장ID: {gh['farm_id']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_greenhouses()