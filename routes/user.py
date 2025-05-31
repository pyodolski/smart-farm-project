import pymysql
import random
import smtplib
from flask import Blueprint, Flask, render_template, request, redirect, session, url_for, flash, jsonify
from config import DB_CONFIG
from flask_cors import CORS
from email.mime.text import MIMEText
from email.header import Header

user_bp = Blueprint('user', __name__)

def get_db_conn():
    return pymysql.connect(**DB_CONFIG)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # JSON 요청 처리
        try:
            if request.is_json:
                data = request.get_json()
                user_id = data.get('id')
                password = data.get('password')
            else:
                # 폼 데이터도 처리 가능하도록 유지
                user_id = request.form.get('id')
                password = request.form.get('password')

            if not user_id or not password:
                return jsonify({"success": False, "message": "모든 필드를 입력해주세요."}), 400

            conn = get_db_conn()
            if conn:
                try:
                    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                        cursor.execute("SELECT * FROM users WHERE id = %s AND password = %s", (user_id, password))
                        user = cursor.fetchone()
                        if user:
                            session['user_id'] = user_id
                            nickname = user['nickname']
                            session['nickname']  = nickname
                            is_admin = user['is_admin']

                            response = {
                                "success": True,
                                "message": "로그인 성공!",
                                "user_id": user_id,
                                "nickname": nickname
                            }

                            if is_admin == 1:
                                response["admin"] = True

                            return jsonify(response), 200
                        else:
                            return jsonify({"success": False, "message": "아이디 또는 비밀번호가 일치하지 않습니다."}), 401
                finally:
                    conn.close()
            else:
                return jsonify({"success": False, "message": "DB 연결 실패"}), 500
        except Exception as e:
            return jsonify({"success": False, "message": f"오류가 발생했습니다: {str(e)}"}), 500

    # GET 요청 처리 - React는 API만 사용하므로 JSON 응답만 필요
    return jsonify({"success": True, "message": "로그인 API가 정상 작동 중입니다."}), 200

@user_bp.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    email = data.get('email')

    code = str(random.randint(100000, 999999))
    session['verify_email'] = email
    session['verify_code'] = code
    try:
        msg = MIMEText(f'인증번호는 {code} 입니다.', _charset='utf-8')
        msg['Subject'] = Header('이메일 인증번호', 'utf-8')
        msg['From'] = '4642joung@yu.ac.kr'
        msg['To'] = email

        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        s.login('4642joung@yu.ac.kr', 'pqvk hxur beny bapi')
        s.send_message(msg)
        s.quit()

        return jsonify({'status': 'ok', 'message': '인증번호 전송 완료'})
    except Exception as e:
        return jsonify({'message': f'메일 전송 실패: {str(e)}'}), 500

#이메일 코드 일치/불일치 확인
@user_bp.route('/check_code', methods=['POST'])
def check_code():
    data = request.get_json()
    input_code = data.get('code')

    if not input_code:
        return jsonify({'verified': False, 'message': '인증번호가 입력되지 않았습니다.'}), 400

    stored_code = session.get('verify_code')

    if input_code == stored_code:
        session['email_verified'] = True
        return jsonify({'verified': True, 'message': '인증 성공'})
    else:
        return jsonify({'verified': False, 'message': '인증번호가 일치하지 않습니다.'})

@user_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({
        'success': True,
        'message': '로그아웃 되었습니다.'
    }), 200

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()  # JSON 데이터 받기
        user_id = data.get('id')
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        nickname = data.get('nickname')
        email = data.get('email')
        name = data.get('name')
        
        if not (user_id and password and password_confirm and nickname and email and name):
            return jsonify({'success': False, 'message': '모든 필드를 입력해주세요.'}), 400

        if password != password_confirm:
            return jsonify({'success': False, 'message': '비밀번호가 일치하지 않습니다.'}), 400

        conn = get_db_conn()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE id = %s OR nickname = %s OR email = %s", (user_id, nickname, email))
                    if cursor.fetchone():
                        return jsonify({'success': False, 'message': '이미 등록된 아이디, 닉네임 또는 이메일입니다.'}), 400

                    cursor.execute("""
                        INSERT INTO users (id, password, nickname, email, name, is_black)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, password, nickname, email, name, False))
                    conn.commit()
                    return jsonify({'success': True, 'message': '회원가입에 성공했습니다!'}), 200
            finally:
                conn.close()
        else:
            return jsonify({'success': False, 'message': 'DB 연결 실패'}), 500

    # GET 요청에 대한 응답 (React 앱을 제공하는 경우)
    return jsonify({'success': True, 'message': 'API is running'}), 200


#정보 수정
@user_bp.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    user_id = session['user_id']
    conn = get_db_conn()

    if request.method == 'POST':
        new_nickname = request.form.get('nickname')
        new_email = request.form.get('email')
        new_name = request.form.get('name')
        current_password = request.form.get('current_password')

        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
                    user = cursor.fetchone()
                    if not user or user[0] != current_password:
                        flash("현재 비밀번호가 일치하지 않습니다.")
                        return render_template('edit.html', nickname=new_nickname, email=new_email, name=new_name)

                    update_query = """
                        UPDATE users
                        SET nickname = %s, email = %s, name = %s
                        WHERE id = %s
                    """
                    cursor.execute(update_query, (new_nickname, new_email, new_name, user_id))
                    conn.commit()
                    flash("정보가 성공적으로 수정되었습니다.")
                    return redirect(url_for('edit_profile'))
            finally:
                conn.close()

    else:
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT nickname, email, name FROM users WHERE id = %s", (user_id,))
                    user = cursor.fetchone()
                    if user:
                        return render_template('edit.html', nickname=user[0], email=user[1], name=user[2])
                    else:
                        flash("사용자 정보를 찾을 수 없습니다.")
                        return redirect(url_for('index'))
            finally:
                conn.close()

# 사용자 정보 조회
@user_bp.route('/api/user/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    user_id = session['user_id']
    conn = get_db_conn()

    if conn:
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(
                    "SELECT id, nickname, email, name FROM users WHERE id = %s",
                    (user_id,)
                )
                user = cursor.fetchone()
                if user:
                    return jsonify({
                        'success': True,
                        'user': user
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': '사용자 정보를 찾을 수 없습니다.'
                    }), 404
        finally:
            conn.close()
    return jsonify({'success': False, 'message': 'DB 연결 실패'}), 500

# 사용자 정보 수정
@user_bp.route('/api/user/profile', methods=['PUT'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    user_id = session['user_id']
    data = request.get_json()
    
    new_nickname = data.get('nickname')
    new_email = data.get('email')
    new_name = data.get('name')
    current_password = data.get('current_password')

    if not all([new_nickname, new_email, new_name, current_password]):
        return jsonify({
            'success': False,
            'message': '모든 필드를 입력해주세요.'
        }), 400

    conn = get_db_conn()
    if conn:
        try:
            with conn.cursor() as cursor:
                # 현재 비밀번호 확인
                cursor.execute(
                    "SELECT password FROM users WHERE id = %s",
                    (user_id,)
                )
                user = cursor.fetchone()
                if not user or user[0] != current_password:
                    return jsonify({
                        'success': False,
                        'message': '현재 비밀번호가 일치하지 않습니다.'
                    }), 401

                # 닉네임과 이메일 중복 확인
                cursor.execute(
                    "SELECT id FROM users WHERE (nickname = %s OR email = %s) AND id != %s",
                    (new_nickname, new_email, user_id)
                )
                if cursor.fetchone():
                    return jsonify({
                        'success': False,
                        'message': '이미 사용 중인 닉네임 또는 이메일입니다.'
                    }), 400

                # 정보 업데이트
                update_query = """
                    UPDATE users
                    SET nickname = %s, email = %s, name = %s
                    WHERE id = %s
                """
                cursor.execute(update_query, (new_nickname, new_email, new_name, user_id))
                conn.commit()

                return jsonify({
                    'success': True,
                    'message': '정보가 성공적으로 수정되었습니다.'
                })
        finally:
            conn.close()
    return jsonify({'success': False, 'message': 'DB 연결 실패'}), 500

# 비밀번호 변경
@user_bp.route('/api/user/password', methods=['PUT'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    user_id = session['user_id']
    data = request.get_json()
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not all([current_password, new_password, confirm_password]):
        return jsonify({
            'success': False,
            'message': '모든 필드를 입력해주세요.'
        }), 400

    if new_password != confirm_password:
        return jsonify({
            'success': False,
            'message': '새 비밀번호가 일치하지 않습니다.'
        }), 400

    conn = get_db_conn()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT password FROM users WHERE id = %s",
                    (user_id,)
                )
                user = cursor.fetchone()
                if not user or user[0] != current_password:
                    return jsonify({
                        'success': False,
                        'message': '현재 비밀번호가 일치하지 않습니다.'
                    }), 401

                cursor.execute(
                    "UPDATE users SET password = %s WHERE id = %s",
                    (new_password, user_id)
                )
                conn.commit()

                return jsonify({
                    'success': True,
                    'message': '비밀번호가 성공적으로 변경되었습니다.'
                })
        finally:
            conn.close()
    return jsonify({'success': False, 'message': 'DB 연결 실패'}), 500

@user_bp.route('/check_login', methods=['GET'])
def check_login():
    user_id = session.get('user_id')
    if user_id:
        return jsonify({
            'logged_in': True,
            'user_id': user_id
        }), 200
    return jsonify({
        'logged_in': False
    }), 200
