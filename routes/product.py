from flask import Blueprint, request, session, jsonify
from check_db import get_db_connection
import pymysql

product_bp = Blueprint('product', __name__, url_prefix='/product')

#구독
@product_bp.route('/subscribe', methods=['POST'])
def subscribe_iot():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"message": "로그인이 필요합니다", "success": False}), 401

        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "DB 연결 실패", "success": False}), 500

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO iot (owner_id, start_date)
            VALUES (%s, NOW())
        """, (user_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "IOT 구독이 완료되었습니다", "success": True}), 200

    except Exception as e:
        print(f"[에러] IOT 구독 중 오류 발생: {e}")
        return jsonify({"message": "서버 내부 오류", "success": False}), 500

#내 구독 목록
@product_bp.route('/my_devices', methods=['GET'])
def my_devices():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "로그인이 필요합니다"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM iot WHERE owner_id = %s", (user_id,))
    devices = cursor.fetchall()
    conn.close()

    return jsonify({"devices": devices})
