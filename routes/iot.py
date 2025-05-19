import json
import os
from datetime import datetime
from flask import Blueprint,jsonify, request
from check_db import get_db_connection

iot_bp = Blueprint('iot', __name__)

# ✅ 설정 읽기용 GET API
@iot_bp.route('/api/iot/camera-config', methods=['GET'])
def get_camera_config():
    try:
        with open("camera_config.json", "r") as f:
            config = json.load(f)
        return jsonify(config), 200
    except Exception as e:
        return jsonify({"error": f"설정 파일을 읽을 수 없습니다: {str(e)}"}), 500

#iot 주기 설정 파일 전송
@iot_bp.route('/api/iot/camera-config', methods=['POST'])
def save_camera_config():
    config = request.get_json()
    with open("camera_config.json", "w") as f:
        json.dump(config, f)
    return jsonify({"message": "설정 저장 완료"}), 200

#파일 수신
@iot_bp.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "파일 없음", 400

    file = request.files['file']
    filename = file.filename
    save_path = os.path.join("static", "images", filename)
    file.save(save_path)

    return f"저장 완료: {filename}", 200

#센서 데이터 수신
@iot_bp.route('/upload-sensor', methods=['POST'])
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

