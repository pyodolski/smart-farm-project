import pymysql
from flask import Flask, render_template, request, redirect, session, url_for, flash
from routes.farm import farm_bp
from config import DB_CONFIG

app = Flask(__name__)
app.register_blueprint(farm_bp)

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

    return render_template('my_farms.html', farms=farms)

#임시(로그인/회원가입) --------------------------------------------------------------------
app.secret_key = 'your_secret_key'  # 세션에 필요한 비밀키 (랜덤한 문자열)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # username = request.form['username']
        # password = request.form['password']
        user_id = request.form.get('id')
        password = request.form.get('password')

        if not user_id or not password:
            flash("모든 필드를 입력해주세요.")
            return redirect(url_for('login'))

        # conn = get_db_connection()
        # cur = conn.cursor()
        # sql = 'SELECT * FROM users WHERE username=%s AND password=%s'
        # cur.execute(sql, (username, password))
        # user = cur.fetchone()
        # conn.close()
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE id = %s AND password = %s", (user_id, password))
                    user = cursor.fetchone()
                    if user:
                        session['user_id'] = user_id
                        #session['name'] = 
                        flash("로그인 성공!")
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

    #     if user:
    #         session['username'] = username
    #         return redirect(url_for('home'))
    #     else:
    #         return '로그인 실패'
    # return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("로그아웃 되었습니다.")
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # username = request.form['username']
        # password = request.form['password']
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

        # try:
        #     conn = get_db_connection()
        #     cur = conn.cursor()
        #     sql = 'INSERT INTO users (username, password) VALUES (%s, %s)'
        #     cur.execute(sql, (username, password))
        #     conn.commit()
        #     conn.close()
        #     return '회원가입 성공!'
        # except pymysql.err.IntegrityError:
        #     return '이미 존재하는 아이디입니다.'
        # except Exception as e:
        #     return f'에러 발생: {str(e)}'
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE id = %s OR nickname = %s OR email = %s", (user_id, nickname, email))
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




if __name__ == '__main__':
    app.run(debug=True)
