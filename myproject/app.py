import pymysql
import os
import random
import smtplib
import requests
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from routes.farm import farm_bp
from config import DB_CONFIG
from routes.post import post_bp
from routes.crop import crop_bp, fetch_disease_detail, fetch_insect_detail, fetch_predator_detail
from flask_cors import CORS
from email.mime.text import MIMEText
from email.header import Header
from routes.weather import weather_bp
from routes.weather import cities, fetch_weather, fetch_two_day_minmax

def get_db_conn():
    return pymysql.connect(**DB_CONFIG)
conn = get_db_conn()
cur = conn.cursor()
UPLOAD_FOLDER = 'static/uploads/farms'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app, 
     resources={r"/*": {"origins": "http://localhost:3000"}},
     supports_credentials=True)
app.register_blueprint(farm_bp)
app.register_blueprint(post_bp)
app.register_blueprint(crop_bp)

def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.MySQLError as e:
        print(f"DB 연결 실패: {e}")
        return None

# 리액트 프론트엔드용 API 경로 추가
@app.route('/api/crops/detail/<crop>')
def api_crop_detail(crop):
    from routes.crop import get_crop_info, fetch_disease_data, fetch_insect_data, fetch_predator_data
    
    valid_crops = {
        "strawberry": "딸기",
        "tomato": "토마토"
    }

    if crop not in valid_crops:
        return jsonify({"error": "존재하지 않는 작물입니다."}), 404

    crop_name_kor = valid_crops[crop]
    info = get_crop_info(crop)
    items = fetch_disease_data(crop_name_kor)
    insects = fetch_insect_data(crop_name_kor)
    enemies = fetch_predator_data(crop_name_kor)

    return jsonify({
        "info": info,
        "items": items,
        "insects": insects,
        "enemies": enemies
    })

@app.route('/')
def home():
    username = session.get('user_id')  #로그인한 유저 이름

    farms = []

    if username:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM farms WHERE owner_username = %s"
        cur.execute(sql, (username,))
        farms = cur.fetchall()
        conn.close()
    
    selected_city = request.form.get('city','서울특별시')
    weather = fetch_weather(selected_city)
    two_day = fetch_two_day_minmax(selected_city)

    return render_template(
        'my_farms.html',
        farms=farms,
        cities=cities,
        selected_city=selected_city,
        weather=weather,
        two_day=two_day
        )

#임시(로그인/회원가입) --------------------------------------------------------------------
app.secret_key = 'your_secret_key'  # 세션에 필요한 비밀키 (랜덤한 문자열)


@app.route('/login', methods=['GET', 'POST'])
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

            conn = get_db_connection()
            if conn:
                try:
                    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                        cursor.execute("SELECT * FROM users WHERE id = %s AND password = %s", (user_id, password))
                        user = cursor.fetchone()
                        if user:
                            session['user_id'] = user_id
                            is_admin = user['is_admin']

                            response = {
                                "success": True,
                                "message": "로그인 성공!",
                                "user_id": user_id
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

@app.route('/admin.html')
def admin_page():
    return render_template('admin.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({
        'success': True,
        'message': '로그아웃 되었습니다.'
    }), 200

@app.route('/register', methods=['GET', 'POST'])
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

        conn = get_db_connection()
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

#이메일 전송
@app.route('/send_code', methods=['POST'])
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
@app.route('/check_code', methods=['POST'])
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

#카카오톡 로그인 정보 DB 저장
@app.route('/oauth/kakao/callback', methods=['GET'])
def kakao_callback():
    code = request.args.get('code')

    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id" : "", #REST_API_KEY
        "redirect_uri": "http://127.0.0.1:5000/oauth/kakao/callback", #포트번호 확인하기
        "code" : code
    }

    #토큰 받아오는 코드
    token_res = requests.post(token_url, data=data)
    token_json = token_res.json()
    access_token = token_json.get("access_token")

    if not access_token:
        flash("카카오 로그인 실패: access_token 없음")
        return redirect(url_for('login'))

    profile_url = "https://kapi.kakao.com/v2/user/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    profile_res = requests.get(profile_url, headers=headers)
    profile_json = profile_res.json()

    #사용자 정보 가져오기
    kakao_id = profile_json.get("id")
    nickname = profile_json["kakao_account"]["profile"].get("nickname")

    #사용자 DB 확인 (없으면 회원가입)
    user_id = f'kakao_{kakao_id}'

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            dummy_password = 'kakao_login'
            cursor.execute("""
                INSERT INTO users (id, password, nickname, email, name, is_black)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, dummy_password, nickname, '', nickname, False))
            conn.commit()
    conn.close()

    session['user_id'] = user_id
    print("user_id 저장됨:", session.get('user_id'))


    return redirect(url_for('home'))


#정보 수정
@app.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    user_id = session['user_id']
    conn = get_db_connection()

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

@app.route('/api/farms', methods=['GET'])
def get_farms():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cur.execute("SELECT * FROM farms WHERE id = %s AND approved = 1", (farm_id,))
                farms = cursor.fetchall()
                return jsonify({'success': True, 'farms': farms}), 200
        finally:
            conn.close()
    return jsonify({'success': False, 'message': 'DB 연결 실패'}), 500

@app.route('/api/farms', methods=['POST'])
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

@app.route('/api/farms/<int:farm_id>', methods=['PUT'])
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

    conn = get_db_connection()
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

@app.route('/api/farms/<int:farm_id>', methods=['DELETE'])
def delete_farm(farm_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    conn = get_db_connection()
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

# 게시글 관련 API
@app.route('/api/posts', methods=['GET'])
def get_posts():
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'DB 연결 실패'}), 500
    
    # URL 파라미터 가져오기
    sort_by = request.args.get('sort', 'new')  # 기본값은 'new'
    search_term = request.args.get('search', '')
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 기본 쿼리
    query = '''
        SELECT b.*, 
               (SELECT COUNT(*) FROM likes WHERE board_id = b.id) as like_count,
               (SELECT COUNT(*) FROM comments WHERE board_id = b.id) as comment_count
        FROM board b
    '''
    
    # 검색어가 있는 경우 WHERE 절 추가
    params = []
    if search_term:
        query += " WHERE b.title LIKE %s OR b.content LIKE %s "
        params.extend([f'%{search_term}%', f'%{search_term}%'])
    
    # 정렬 기준 적용
    if sort_by == 'popular':
        query += " ORDER BY like_count DESC, b.wdate DESC"
    else:  # 'new'
        query += " ORDER BY b.wdate DESC"
    
    cursor.execute(query, params)
    posts = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({'posts': posts})

@app.route('/api/posts', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': '제목과 내용을 모두 입력해주세요.'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'DB 연결 실패'}), 500
        
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO board (name, title, content) VALUES (%s, %s, %s)',
        (session['user_id'], title, content)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '게시글이 작성되었습니다.'})

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'DB 연결 실패'}), 500
        
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 게시글 정보 조회
    cursor.execute('''
        SELECT b.*, 
               (SELECT COUNT(*) FROM likes WHERE board_id = b.id) as like_count,
               b.name = %s as is_author
        FROM board b
        WHERE b.id = %s
    ''', (session['user_id'], post_id))
    post = cursor.fetchone()

    if not post:
        cursor.close()
        conn.close()
        return jsonify({'message': '게시글을 찾을 수 없습니다.'}), 404

    # 조회수 증가
    cursor.execute('UPDATE board SET view = view + 1 WHERE id = %s', (post_id,))
    
    # 댓글 조회 - cdate 기준으로 최신순 정렬
    cursor.execute('''
        SELECT c.*, 
               c.commenter = %s as is_author,
               DATE_FORMAT(c.cdate, '%%Y-%%m-%%d %%H:%%i:%%s') as formatted_date
        FROM comments c
        WHERE c.board_id = %s
        ORDER BY c.cdate DESC
    ''', (session['user_id'], post_id))
    comments = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        'post': post,
        'comments': comments
    })

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'DB 연결 실패'}), 500
        
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT name FROM board WHERE id = %s', (post_id,))
    post = cursor.fetchone()

    if not post:
        cursor.close()
        conn.close()
        return jsonify({'message': '게시글을 찾을 수 없습니다.'}), 404

    if post['name'] != session['user_id']:
        cursor.close()
        conn.close()
        return jsonify({'message': '수정 권한이 없습니다.'}), 403

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        cursor.close()
        conn.close()
        return jsonify({'message': '제목과 내용을 모두 입력해주세요.'}), 400

    cursor.execute(
        'UPDATE board SET title = %s, content = %s WHERE id = %s',
        (title, content, post_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '게시글이 수정되었습니다.'})

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'DB 연결 실패'}), 500
        
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT name FROM board WHERE id = %s', (post_id,))
    post = cursor.fetchone()

    if not post:
        cursor.close()
        conn.close()
        return jsonify({'message': '게시글을 찾을 수 없습니다.'}), 404

    if post['name'] != session['user_id']:
        cursor.close()
        conn.close()
        return jsonify({'message': '삭제 권한이 없습니다.'}), 403

    cursor.execute('DELETE FROM board WHERE id = %s', (post_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '게시글이 삭제되었습니다.'})

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def toggle_like(post_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'DB 연결 실패'}), 500
        
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 이미 좋아요를 눌렀는지 확인
    cursor.execute(
        'SELECT * FROM likes WHERE board_id = %s AND user_name = %s',
        (post_id, session['user_id'])
    )
    existing_like = cursor.fetchone()

    if existing_like:
        # 좋아요 취소
        cursor.execute(
            'DELETE FROM likes WHERE board_id = %s AND user_name = %s',
            (post_id, session['user_id'])
        )
    else:
        # 좋아요 추가
        cursor.execute(
            'INSERT INTO likes (board_id, user_name) VALUES (%s, %s)',
            (post_id, session['user_id'])
        )

    # 좋아요 수 조회
    cursor.execute('SELECT COUNT(*) as count FROM likes WHERE board_id = %s', (post_id,))
    like_count = cursor.fetchone()['count']

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        'message': '좋아요가 처리되었습니다.',
        'like_count': like_count
    })

# 댓글 관련 API
@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'message': '댓글 내용을 입력해주세요.'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'DB 연결 실패'}), 500
        
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO comments (board_id, commenter, content) VALUES (%s, %s, %s)',
        (post_id, session['user_id'], content)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '댓글이 작성되었습니다.'})

@app.route('/api/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'DB 연결 실패'}), 500
        
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT c.*
        FROM comments c
        WHERE c.id = %s
    ''', (comment_id,))
    comment = cursor.fetchone()
    cursor.close()
    conn.close()

    if not comment:
        return jsonify({'message': '댓글을 찾을 수 없습니다.'}), 404

    return jsonify(comment)

@app.route('/api/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'DB 연결 실패'}), 500
        
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT commenter FROM comments WHERE id = %s', (comment_id,))
    comment = cursor.fetchone()

    if not comment:
        cursor.close()
        conn.close()
        return jsonify({'message': '댓글을 찾을 수 없습니다.'}), 404

    if comment['commenter'] != session['user_id']:
        cursor.close()
        conn.close()
        return jsonify({'message': '수정 권한이 없습니다.'}), 403

    data = request.get_json()
    content = data.get('content')

    if not content:
        cursor.close()
        conn.close()
        return jsonify({'message': '댓글 내용을 입력해주세요.'}), 400

    cursor.execute(
        'UPDATE comments SET content = %s WHERE id = %s',
        (content, comment_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '댓글이 수정되었습니다.'})

@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'DB 연결 실패'}), 500
        
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT commenter FROM comments WHERE id = %s', (comment_id,))
    comment = cursor.fetchone()

    if not comment:
        cursor.close()
        conn.close()
        return jsonify({'message': '댓글을 찾을 수 없습니다.'}), 404

    if comment['commenter'] != session['user_id']:
        cursor.close()
        conn.close()
        return jsonify({'message': '삭제 권한이 없습니다.'}), 403

    cursor.execute('DELETE FROM comments WHERE id = %s', (comment_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '댓글이 삭제되었습니다.'})

# 사용자 정보 조회
@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    user_id = session['user_id']
    conn = get_db_connection()

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
@app.route('/api/user/profile', methods=['PUT'])
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

    conn = get_db_connection()
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
@app.route('/api/user/password', methods=['PUT'])
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

    conn = get_db_connection()
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

@app.route('/api/diseases/<disease_id>')
def api_disease_detail(disease_id):
    disease = fetch_disease_detail(disease_id)
    if not disease:
        return jsonify({'error': '병해 정보를 찾을 수 없습니다.'}), 404
    return jsonify(disease)

@app.route('/api/insects/<insect_id>')
def api_insect_detail(insect_id):
    insect = fetch_insect_detail(insect_id)
    if not insect:
        return jsonify({'error': '해충 정보를 찾을 수 없습니다.'}), 404
    return jsonify(insect)

@app.route('/api/enemies/<enemy_id>')
def api_enemy_detail(enemy_id):
    enemy = fetch_predator_detail(enemy_id)
    if not enemy:
        return jsonify({'error': '천적 곤충 정보를 찾을 수 없습니다.'}), 404
    return jsonify(enemy)

if __name__ == '__main__':
    app.run(port=5001, debug=True)