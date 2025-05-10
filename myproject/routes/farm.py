from flask import Blueprint, render_template, request, redirect, url_for, session
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

#농장 추가 버튼
@farm_bp.route('/add_farm', methods=['GET', 'POST'])
def add_farm():
    if request.method == 'POST':
        name = request.form['name']
        area = request.form['area']
        location = request.form['location']
        #owner = request.form['owner'] #추후 교체 필요 (직접입력 -> 로그인되어있는 유저로 자동 입력)
        owner = session.get('user_id')
        document = request.files.get('document') #농장주 증명 첨부 파일

        if not owner:
            return '로그인 후 이용해주세요.', 403
        if not document:
            return '첨부파일이 첨부하세요.', 400
        
        filename = secure_filename(document.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        document.save(filepath)

        conn = get_db_conn()
        cur = conn.cursor()

        sql = """
            INSERT INTO farms (name, area, location, owner_username, document_path)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(sql, (name, area, location, owner, filepath))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('add_farm.html')

#농장 페이지
@farm_bp.route('/farm/<int:farm_id>', endpoint='farm_detail')
def farm_detail(farm_id):
    #로그인 상태 확인
    user = session.get('user_id')
    if not user:
        return redirect(url_for('login'))

    conn = get_db_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT * FROM farms WHERE id = %s AND approved = 1", (farm_id,))
    farm = cur.fetchone()
    conn.close()
    
    if not farm:
        return '존재하지 않는 농장입니다.', 404
    if farm['owner_username'] != user:
        return '이 농장에 접근할 수 없습니다.', 403

    return render_template('farm_detail.html', farm=farm)

#농장 페이지 -> 농장 수정
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
        area = request.form['area']
        location = request.form['location']

        cur.execute(
            "UPDATE farms SET name = %s, area = %s, location = %s WHERE id = %s",
            (name, area, location, farm_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('farm.farm_detail', farm_id=farm_id))

    conn.close()
    return render_template('edit_farm.html', farm=farm)

#농장 페이지 -> 농장 삭제
@farm_bp.route('/farm/<int:farm_id>/delete', methods=['POST'])
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
    return redirect(url_for('home'))
