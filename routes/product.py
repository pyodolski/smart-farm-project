from flask import Blueprint, request, session, jsonify
from check_db import get_db_connection
import pymysql
import os
import json
from datetime import datetime
from flask_cors import CORS

product_bp = Blueprint('product', __name__, url_prefix='/product')

# 구독하기 (IOT 설정)
@product_bp.route('/subscribe', methods=['POST'])
def subscribe_iot():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"message": "로그인이 필요합니다", "success": False}), 401

        data = request.get_json()
        iot_name = data.get('iot_name')
        gh_id = data.get('gh_id')
        capture_interval = data.get('capture_interval', '15')
        direction = data.get('direction', 'both')
        resolution = data.get('resolution', '1280x720')
        camera_on = data.get('camera_on', True)

        conn = get_db_connection()
        cur = conn.cursor()
        sql = """
            INSERT INTO iot (iot_name, owner_id, gh_id, capture_interval, direction, resolution, camera_on)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            iot_name, user_id, gh_id, capture_interval, direction, resolution, camera_on
        ))
        conn.commit()
        conn.close()

        return jsonify({"message": "IOT 구독이 완료되었습니다", "success": True}), 200

    except Exception as e:
        print(f"[에러] IOT 구독 중 오류 발생: {e}")
        return jsonify({"message": "서버 내부 오류", "success": False}), 500



# 내 구독 목록 조회
@product_bp.route('/my_devices', methods=['GET'])
def my_devices():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "로그인이 필요합니다"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT i.*, g.greenhouse_name
        FROM iot i
        LEFT JOIN greenhouses g ON i.gh_id = g.id
        WHERE i.owner_id = %s
    """, (user_id,))
    devices = cursor.fetchall()
    conn.close()

    return jsonify({"devices": devices})

# 내 비닐하우스 목록 조회
@product_bp.route('/my_greenhouses', methods=['GET'])
def my_greenhouses():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "로그인이 필요합니다"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = """
        SELECT g.id, g.greenhouse_name, g.farm_id
        FROM greenhouses g
        JOIN farms f ON g.farm_id = f.id
        WHERE f.owner_username = %s
    """
    cursor.execute(sql, (user_id,))
    greenhouses = cursor.fetchall()
    conn.close()

    return jsonify({"greenhouses": greenhouses})

# 설정 읽기용 get api
@product_bp.route('/camera-config', methods=['GET'])
def get_camera_config():
    try:
        with open("camera_config.json", "r") as f:
            config = json.load(f)
        return jsonify(config), 200
    except Exception as e:
        return jsonify({"error": f"설정 파일을 읽을 수 없습니다: {str(e)}"}), 500

# IOT 카메라 설정 저장
@product_bp.route('/camera-config', methods=['POST'])
def save_camera_config():
    config = request.get_json()
    with open("camera_config.json", "w") as f:
        json.dump(config, f)
    return jsonify({"message": "설정 저장 완료"}), 200
#이미지 파일 업로드
@product_bp.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "파일 없음", 400

    file = request.files['file']
    filename = file.filename
    save_path = os.path.join("static", "images", filename)
    file.save(save_path)

    return f"저장 완료: {filename}", 200

# 센서 데이터 수신
@product_bp.route('/upload-sensor', methods=['POST'])
def upload_sensor():
    data = request.get_json()
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    timestamp = data.get('timestamp', datetime.now().isoformat())

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO sensor_log (temperature, humidity, timestamp)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (temperature, humidity, timestamp))
            conn.commit()  
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 센서 데이터 값 띄우기 (실험용 코드입니다.)
@product_bp.route("/last-sensor", methods=["GET"])
def get_last_sensor():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT temperature, humidity, timestamp FROM sensor_log ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()

        # 아래 사진 데이터 형식 지정 필요
        if row:
            response = {
                "temperature": row[0],
                "humidity": row[1],
                "timestamp": row[2].isoformat(),  # JS에서 파싱 가능한 형태
                "image_url": "/static/images/last.jpg"
            }
        else:
            response = {
                "temperature": None,
                "humidity": None,
                "timestamp": None,
                "image_url": "/static/images/last.jpg"
            }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#구독 취소
@product_bp.route('/unsubscribe/<int:iot_id>', methods=['DELETE'])
def unsubscribe_iot(iot_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "로그인이 필요합니다"}), 401

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM iot WHERE id = %s AND owner_id = %s", (iot_id, user_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "구독이 취소되었습니다"}), 200

#iot 설정 수정
@product_bp.route('/update/<int:iot_id>', methods=['POST'])
def update_iot(iot_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "로그인이 필요합니다"}), 401

    data = request.get_json()
    iot_name = data.get('iot_name')
    gh_id = data.get('gh_id')
    capture_interval = data.get('capture_interval')
    direction = data.get('direction')
    resolution = data.get('resolution')
    camera_on = data.get('camera_on')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE iot
        SET iot_name = %s, gh_id = %s, capture_interval = %s,
            direction = %s, resolution = %s, camera_on = %s
        WHERE id = %s AND owner_id = %s
    """, (iot_name, gh_id, capture_interval, direction, resolution, camera_on, iot_id, user_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "IOT 정보가 수정되었습니다"}), 200


