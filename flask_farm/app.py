import pymysql
from flask import Flask, render_template, request, redirect, session, url_for
from routes.farm import farm_bp
from config import DB_CONFIG

app = Flask(__name__)
app.register_blueprint(farm_bp)

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

@app.route('/')
def home():
    username = session.get('username')  #로그인한 유저 이름

    farms = []

    if username:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM farms WHERE owner_username = %s"
        cur.execute(sql, (username,))
        farms = cur.fetchall()
        conn.close()

    return render_template('my_farms.html', farms=farms)

#임시(로그인/회원가입) --------------------------------------------------------------------
app.secret_key = 'your_secret_key'  # 세션에 필요한 비밀키 (랜덤한 문자열)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        sql = 'SELECT * FROM users WHERE username=%s AND password=%s'
        cur.execute(sql, (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return '로그인 실패'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            sql = 'INSERT INTO users (username, password) VALUES (%s, %s)'
            cur.execute(sql, (username, password))
            conn.commit()
            conn.close()
            return '회원가입 성공!'
        except pymysql.err.IntegrityError:
            return '이미 존재하는 아이디입니다.'
        except Exception as e:
            return f'에러 발생: {str(e)}'

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
