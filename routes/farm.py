from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, abort
import os
from config import DB_CONFIG
from werkzeug.utils import secure_filename
from utils.database import get_db_connection, get_dict_cursor_connection
from routes.weather import fetch_weather

UPLOAD_FOLDER = 'static/uploads/farms'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
farm_bp = Blueprint('farm', __name__)

# API: 농장 목록 조회
@farm_bp.route('/api/farms', methods=['GET'])
def get_farms():
    owner = session.get('user_id')
    if not owner:
        return jsonify({'error': '로그인이 필요합니다.'}), 403

    conn, cursor = get_dict_cursor_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT * FROM farms WHERE is_approved = true AND owner_username = %s", (owner,))
            farms = cursor.fetchall()
            return jsonify({'farms': farms})
        finally:
            cursor.close()
            conn.close()
    return jsonify({'error': 'DB 연결 실패'}), 500

# API: 농장 추가
@farm_bp.route('/api/farms', methods=['POST'])
def create_farm():
    name = request.form.get('name')
    location = request.form.get('location')
    document = request.files.get('document')
    owner = session.get('user_id')

    if not owner:
        return jsonify({'error': '로그인이 필요합니다.'}), 403
    if not document:
        return jsonify({'error': '첨부파일이 필요합니다.'}), 400

    filename = secure_filename(document.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, filename).replace('\\', '/')
    document.save(upload_path)

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO farms (name, location, owner_username, document_path)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (name, location, owner, upload_path))
                conn.commit()
                return jsonify({'message': 'Farm created'}), 201
        finally:
            conn.close()
    return jsonify({'error': 'DB 연결 실패'}), 500

# API: 농장 상세 정보 조회
@farm_bp.route('/api/farms/<int:farm_id>', methods=['GET'])
def get_farm_detail(farm_id):
    user = session.get('user_id')
    if not user:
        return jsonify({'error': '로그인이 필요합니다.'}), 403

    conn, cursor = get_dict_cursor_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT * FROM farms WHERE id = %s AND is_approved = true", (farm_id,))
            farm = cursor.fetchone()
            
            if not farm:
                return jsonify({'error': '존재하지 않는 농장입니다.'}), 404
            if farm['owner_username'] != user:
                return jsonify({'error': '이 농장에 접근할 수 없습니다.'}), 403

            return jsonify(farm)
        finally:
            cursor.close()
            conn.close()
    return jsonify({'error': 'DB 연결 실패'}), 500

# API: 농장 수정
@farm_bp.route('/api/farms/<int:farm_id>', methods=['PUT'])
def update_farm(farm_id):
    username = session.get('user_id')
    if not username:
        return jsonify({'error': '로그인이 필요합니다.'}), 403

    conn, cursor = get_dict_cursor_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT * FROM farms WHERE id = %s", (farm_id,))
            farm = cursor.fetchone()

            if not farm:
                return jsonify({'error': '존재하지 않는 농장입니다.'}), 404
            if farm['owner_username'] != username:
                return jsonify({'error': '수정 권한이 없습니다.'}), 403

            data = request.get_json()
            name = data.get('name')
            location = data.get('location')

            cursor.execute(
                "UPDATE farms SET name = %s, location = %s WHERE id = %s",
                (name, location, farm_id)
            )
            conn.commit()
            return jsonify({'message': 'Farm updated successfully'})
        finally:
            cursor.close()
            conn.close()
    return jsonify({'error': 'DB 연결 실패'}), 500

# API: 농장 삭제
@farm_bp.route('/api/farms/<int:farm_id>', methods=['DELETE'])
def delete_farm(farm_id):
    username = session.get('user_id')
    if not username:
        return jsonify({'error': '로그인이 필요합니다.'}), 403

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT owner_username FROM farms WHERE id = %s", (farm_id,))
                result = cursor.fetchone()

                if not result or result[0] != username:
                    return jsonify({'error': '삭제 권한이 없습니다.'}), 403

                cursor.execute("DELETE FROM farms WHERE id = %s", (farm_id,))
                conn.commit()
                return jsonify({'message': '삭제 완료'}), 200
        finally:
            conn.close()
    return jsonify({'error': 'DB 연결 실패'}), 500

# API: 농장별 날씨 조회
@farm_bp.route('/api/farms/<int:farm_id>/weather', methods=['GET'])
def farm_weather(farm_id):
    conn, cursor = get_dict_cursor_connection()
    if not (conn and cursor):
        return jsonify({'error': 'DB 연결 실패'}), 500
    try:
        cursor.execute(
            "SELECT id, name, location FROM farms WHERE id = %s AND is_approved = true",
            (farm_id,)
        )
        farm = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not farm:
        return jsonify({'error': 'Farm not found'}), 404

    weather = fetch_weather(farm['location'])
    if 'error' in weather:
        return jsonify({'error': weather['error']}), 502

    return jsonify({
        'farmId': farm['id'],
        'farmName': farm['name'],
        'location': farm['location'],
        'temperature': weather['temperature'],
        'description': weather['description']
    })

#승인 대기 목록
@farm_bp.route('/api/farms/pending', methods=['GET'])
def get_user_pending_farms():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 403

    conn, cursor = get_dict_cursor_connection()
    if not (conn and cursor):
        return jsonify({'error': 'DB 연결 실패'}), 500

    try:
        cursor.execute(
            "SELECT * FROM farms WHERE owner_username = %s AND is_approved = false",
            (user_id,)
        )
        pending_farms = cursor.fetchall()
        return jsonify({'pending_farms': pending_farms})
    finally:
        cursor.close()
        conn.close()