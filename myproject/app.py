import pymysql
import random
import smtplib
import requests
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from routes.farm import farm_bp
from config import DB_CONFIG
from routes.post import post_bp
from routes.weather import weather_bp
from routes.weather import cities, fetch_weather, fetch_two_day_minmax
from email.mime.text import MIMEText
from email.header import Header

app = Flask(__name__)
app.register_blueprint(farm_bp)
app.register_blueprint(post_bp)
app.register_blueprint(weather_bp)


def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.MySQLError as e:
        print(f"DB 연결 실패: {e}")
        return None

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

#--------------------------------------------------------------------
app.secret_key = 'your_secret_key'  # 세션에 필요한 비밀키 (랜덤한 문자열)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('id')
        password = request.form.get('password')

        if not user_id or not password:
            flash("모든 필드를 입력해주세요.")
            return redirect(url_for('login'))

        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE id = %s AND password = %s", (user_id, password))
                    user = cursor.fetchone()
                    if user:
                        session['user_id'] = user_id
                        #session['name'] = 
                        
                        return redirect(url_for('home'))
                    else:
                        flash("아이디 또는 비밀번호가 일치하지 않습니다.")
                        return redirect(url_for('login'))
            finally:
                conn.close()
        else:
            flash("DB 연결 실패")
            return redirect(url_for('login'))
    return render_template('login.html')

#로그아웃
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    
    return redirect(url_for('home'))

#회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form.get('id')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        name = request.form.get('name')
        
        if not (user_id and password and password_confirm and nickname and email and name):
            flash("모든 필드를 입력해주세요.")
            return redirect(url_for('register'))

        if password != password_confirm:
            flash("비밀번호가 일치하지 않습니다.")
            return redirect(url_for('register'))
        
        if session.get('verify_email') != email or not session.get('email_verified'):
            flash("이메일 인증이 필요합니다.")
            return redirect(url_for('register'))

        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE id = %s OR nickname = %s", (user_id, nickname))
                    if cursor.fetchone():
                        flash("이미 등록된 아이디, 닉네임 또는 이메일입니다.")
                        return redirect(url_for('register'))
                    cursor.execute("""
                        INSERT INTO users (id, password, nickname, email, name, is_black)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, password, nickname, email, name, False))
                    conn.commit()
                    flash("회원가입에 성공했습니다!")
                    return redirect(url_for('login'))
            finally:
                conn.close()
        else:
            flash("DB 연결 실패")
            return redirect(url_for('register'))

    return render_template('register.html')


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

#카카토옥 로그인 정보 DB 저장
@app.route('/oauth/kakao/callback', methods=['GET'])
def kakao_callback():
    code = request.args.get('code')

    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id" : "", #REST_API_KEY
        "redirect_uri": "http://127.0.0.1:5000/oauth/kakao/callback",
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



if __name__ == '__main__':
    app.run(debug=True)
