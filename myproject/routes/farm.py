from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import pymysql
import os
from config import DB_CONFIG
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads/farms'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
farm_bp = Blueprint('farm', __name__)

# DB 연결 공통 함수
def get_db_conn():
    return pymysql.connect(**DB_CONFIG)

@farm_bp.route('', methods=['GET'])
def get_farms():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    conn = get_db_conn()
    if conn:
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM farms WHERE id = %s AND is_approved = 1", (user_id,))
                farms = cursor.fetchall()
                return jsonify({'success': True, 'farms': farms}), 200
        finally:
            conn.close()
    return jsonify({'success': False, 'message': 'DB 연결 실패'}), 500

@farm_bp.route('/<int:farm_id>', methods=['PUT'])
def update_farm(farm_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    data = request.get_json()
    name = data.get('name')
    location = data.get('location')
    area = data.get('area')

    if not all([name, location, area]):
        return jsonify({'success': False, 'message': '모든 필드를 입력해주세요.'}), 400

    conn = get_db_conn()
    cur = conn.cursor()
    if conn:
        try:
            with conn.cursor() as cursor:
                # 농장 소유자 확인
                cursor.execute("SELECT owner_username FROM farms WHERE id = %s", (farm_id,))
                farm = cursor.fetchone()
                if not farm or farm[0] != user_id:
                    return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403

                sql = """
                    UPDATE farms
                    SET name = %s, location = %s, area = %s
                    WHERE id = %s AND owner_username = %s
                """
                cursor.execute(sql, (name, location, area, farm_id, user_id))
                conn.commit()
                return jsonify({'success': True, 'message': '농장 정보가 수정되었습니다.'}), 200
        finally:
            conn.close()
    return jsonify({'success': False, 'message': 'DB 연결 실패'}), 500

@farm_bp.route('/<int:farm_id>', methods=['DELETE'])
def delete_farm(farm_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    conn = get_db_conn()
    cur = conn.cursor()
    if conn:
        try:
            with conn.cursor() as cursor:
                # 농장 소유자 확인
                cursor.execute("SELECT owner_username FROM farms WHERE id = %s", (farm_id,))
                farm = cursor.fetchone()
                if not farm or farm[0] != user_id:
                    return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403

                cursor.execute("DELETE FROM farms WHERE id = %s AND owner_username = %s", (farm_id, user_id))
                conn.commit()
                return jsonify({'success': True, 'message': '농장이 삭제되었습니다.'}), 200
        finally:
            conn.close()
    return jsonify({'success': False, 'message': 'DB 연결 실패'}), 500