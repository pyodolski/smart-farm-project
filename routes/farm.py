from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import pymysql
import os
from config import DB_CONFIG
from werkzeug.utils import secure_filename
from flask_cors import CORS

UPLOAD_FOLDER = 'static/uploads/farms'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
farm_bp = Blueprint('farm', __name__)
CORS(farm_bp, resources={r"/*": {"origins": [
    "http://localhost:3001",
    "http://localhost:3000",
    "https://mature-grub-climbing.ngrok-free.app"
]}}, supports_credentials=True)


# DB 연결 공통 함수
def get_db_conn():
    return pymysql.connect(**DB_CONFIG)


#농장 목록 조회 및 추가
@farm_bp.route('/', methods=['GET', 'POST'])
def farms_api():
    if request.method == 'GET':
        owner = session.get('user_id')
        if not owner:
            return jsonify({'error': '로그인이 필요합니다.'}), 403

        conn = get_db_conn()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM farms WHERE is_approved = 1 AND owner_username = %s", (owner,))
        farms = cur.fetchall()
        conn.close()
        return jsonify({'farms': farms})

    elif request.method == 'POST':
        name = request.form.get('name')
        #area = request.form.get('area')
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

        conn = get_db_conn()
        cur = conn.cursor()
        sql = """
            INSERT INTO farms (name, location, owner_username, document_path)
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(sql, (name, location, owner, upload_path))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Farm created'}), 201


#농장 추가 버튼 처리
@farm_bp.route('/add_farm', methods=['GET', 'POST'])
def add_farm():
    if request.method == 'POST':
        name = request.form['name']
        #area = request.form['area']
        location = request.form['location']
        owner = session.get('user_id')
        document = request.files.get('document')

        if not owner:
            return '로그인 후 이용해주세요.', 403
        if not document:
            return '첨부파일이 첨부하세요.', 400

        filename = secure_filename(document.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename).replace('\\', '/')
        document.save(filepath)

        conn = get_db_conn()
        cur = conn.cursor()
        sql = """
            INSERT INTO farms (name, location, owner_username, document_path)
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(sql, (name, location, owner, filepath))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('add_farm.html')


# 농장 상세
@farm_bp.route('/farm/<int:farm_id>', endpoint='farm_detail')
def farm_detail(farm_id):
    user = session.get('user_id')
    if not user:
        return redirect(url_for('login'))

    conn = get_db_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM farms WHERE id = %s AND is_approved = 1", (farm_id,))
    
    farm = cur.fetchone()
    conn.close()

    if not farm:
        return '존재하지 않는 농장입니다.', 404
    if farm['owner_username'] != user:
        return '이 농장에 접근할 수 없습니다.', 403

    return render_template('farm_detail.html', farm=farm)


#농장 수정
@farm_bp.route('/farm/<int:farm_id>/edit', methods=['GET', 'POST'])
def edit_farm(farm_id):
    username = session.get('user_id')
    if not username:
        return redirect(url_for('login'))

    conn = get_db_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM farms WHERE id = %s", (farm_id,))
    farm = cur.fetchone()

    if not farm:
        conn.close()
        return '존재하지 않는 농장입니다.', 404
    if farm['owner_username'] != username:
        conn.close()
        return '수정 권한이 없습니다.', 403

    if request.method == 'POST':
        name = request.form['name']
        #area = request.form['area']
        location = request.form['location']

        cur.execute(
            "UPDATE farms SET name = %s, location = %s WHERE id = %s",
            (name, location, farm_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('farm.farm_detail', farm_id=farm_id))

    conn.close()
    return render_template('edit_farm.html', farm=farm)


# 농장 삭제
@farm_bp.route('/<int:farm_id>', methods=['DELETE'])
def delete_farm(farm_id):
    username = session.get('user_id')
    if not username:
        return redirect(url_for('login'))

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT owner_username FROM farms WHERE id = %s", (farm_id,))
    result = cur.fetchone()

    if not result or result[0] != username:
        conn.close()
        return '삭제 권한이 없습니다.', 403

    cur.execute("DELETE FROM farms WHERE id = %s", (farm_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': '삭제 완료'}), 200

