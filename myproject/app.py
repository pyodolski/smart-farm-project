from flask import Flask, render_template, session, url_for, request, redirect
import pymysql

# render_template : HTML
# session : 로그인 상태 세션
# request : 클라이언트에서 보낸 데이터 접근
# redirect : URL 이동

app = Flask(__name__)
app.secret_key = 'sample_secret'
# 플라스크 앱 생성 세션이나, 쿠키 데이터를 암호화할 때 사용(로그인 시 사용)

def connectsql():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        passwd='comep1522w',
        db='smartfarm',
        charset='utf8'
    )
    return conn

@app.route('/')
# 세션유지를 통한 로그인 유무 확인
def index():
    if 'username' in session:
        username = session['username']

        return render_template('index.html', logininfo = username)
    else:
        username = None
        return render_template('index.html', logininfo = username )

@app.route('/post')
def post():
    username = session.get('username', None)
    sort = request.args.get('sort', 'new')  # 정렬
    keyword = request.args.get('search', '')  # 검색 키워드

    if sort == 'popular':
        order_query = "ORDER BY likes DESC, b.id DESC"
    else:
        order_query = "ORDER BY b.id DESC"

    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 🔍 검색 조건
    if keyword:
        search_condition = "WHERE b.title LIKE %s OR b.content LIKE %s"
        search_values = (f"%{keyword}%", f"%{keyword}%")
    else:
        search_condition = ""
        search_values = ()

    query = f"""
    SELECT 
        b.id, 
        b.name, 
        b.title, 
        b.wdate, 
        b.view,
        (SELECT COUNT(*) FROM likes WHERE board_id = b.id) AS likes
    FROM board AS b
    {search_condition}
    {order_query}
    """
    cursor.execute(query, search_values)
    post_list = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'post.html',
        postlist=post_list,
        logininfo=username,
        current_sort=sort,
        current_search=keyword
    )


@app.route('/post/content/<id>')  # 조회수 up + 좋아요 수 출력
def content(id):
    if 'username' in session:
        username = session['username']

        # 조회수 증가
        conn = connectsql()
        cursor = conn.cursor()
        cursor.execute("UPDATE board SET view = view + 1 WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()

        # 게시글 데이터 + 좋아요 수 불러오기
        conn = connectsql()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 게시글 내용
        cursor.execute("SELECT id, title, content FROM board WHERE id = %s", (id,))
        content = cursor.fetchone()

        # 좋아요 수
        cursor.execute("SELECT COUNT(*) AS cnt FROM likes WHERE board_id = %s", (id,))
        like_count = cursor.fetchone()['cnt']

        # 댓글
        cursor.execute("SELECT commenter, content, cdate FROM comments WHERE board_id = %s ORDER BY cdate DESC", (id,))
        comments = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            'content.html',
            data=content,
            username=username,
            like_count=like_count,
            comments=comments
        )
    else:
        return render_template('Error.html')


@app.route('/like/<id>') # 좋아요 수 증가
def like(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = connectsql()
    cursor = conn.cursor()

    # 중복 확인
    check_query = "SELECT * FROM likes WHERE board_id = %s AND user_name = %s"
    cursor.execute(check_query, (id, username))
    result = cursor.fetchone()

    if not result:
        # 좋아요 등록
        insert_query = "INSERT INTO likes (board_id, user_name) VALUES (%s, %s)"
        cursor.execute(insert_query, (id, username))
        conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('content', id=id))  # 다시 해당 게시글로 이동

@app.route('/post/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if 'username' not in session:
        return render_template('Error.html')  # 로그인 안 된 경우

    username = session['username']

    if request.method == 'POST':
        # 폼 데이터 받아서 UPDATE
        edittitle = request.form['title']
        editcontent = request.form['content']

        conn = connectsql()
        cursor = conn.cursor()
        query = "UPDATE board SET title = %s, content = %s WHERE id = %s"
        cursor.execute(query, (edittitle, editcontent, id))
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('editSuccess.html')

    else:
        # 게시글 작성자와 로그인 유저가 같은지 확인
        conn = connectsql()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = "SELECT id, title, content, name FROM board WHERE id = %s"
        cursor.execute(query, (id,))
        postdata = cursor.fetchone()
        cursor.close()
        conn.close()

        if postdata and postdata['name'] == username:
            return render_template('edit.html', data=postdata, logininfo=username)
        else:
            return render_template('editError.html')

@app.route('/post/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    if 'username' not in session:
        return render_template('Error.html')

    username = session['username']

    if request.method == 'POST':
        # 삭제 요청 처리
        conn = connectsql()
        cursor = conn.cursor()
        query = "DELETE FROM board WHERE id = %s"
        cursor.execute(query, (id,))
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('deleteSuccess.html')

    else:
        # GET 요청: 삭제 권한 확인
        conn = connectsql()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = "SELECT name FROM board WHERE id = %s"
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result and result['name'] == username:
            return render_template('delete.html', id=id)
        else:
            return render_template('editError.html')

@app.route('/post/delete/success/<id>')
def deletesuccess(id):
    if 'username' not in session:
        return render_template('Error.html')

    username = session['username']

    # 삭제 권한 확인
    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT name FROM board WHERE id = %s", (id,))
    result = cursor.fetchone()

    if result and result['name'] == username:
        # 삭제 실행
        cursor.execute("DELETE FROM board WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('deleteSuccess.html')
    else:
        cursor.close()
        conn.close()
        return render_template('editError.html')

@app.route('/write', methods=['GET', 'POST'])
def write():
    if 'username' not in session:
        return render_template('Error.html')

    username = session['username']

    if request.method == 'POST':
        usertitle = request.form['title']
        usercontent = request.form['content']

        conn = connectsql()
        cursor = conn.cursor()
        query = "INSERT INTO board (name, title, content) VALUES (%s, %s, %s)"
        value = (username, usertitle, usercontent)
        cursor.execute(query, value)
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('post'))

    return render_template('write.html', logininfo=username)

@app.route('/comment/<post_id>', methods=['POST'])
def comment(post_id):
    if 'username' not in session:
        return render_template('Error.html')

    commenter = session['username']
    content = request.form['content']

    conn = connectsql()
    cursor = conn.cursor()
    query = "INSERT INTO comments (board_id, commenter, content) VALUES (%s, %s, %s)"
    cursor.execute(query, (post_id, commenter, content))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('content', id=post_id))  # 다시 게시글 보기로 이동

@app.route('/comment/delete/<comment_id>/<post_id>')
def delete_comment(comment_id, post_id):
    if 'username' not in session:
        return render_template('Error.html')

    username = session['username']

    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 댓글 작성자 확인
    cursor.execute("SELECT commenter FROM comments WHERE id = %s", (comment_id,))
    result = cursor.fetchone()

    if result and result['commenter'] == username:
        cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('content', id=post_id))

@app.route('/comment/edit/<comment_id>', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if 'username' not in session:
        return render_template('Error.html')

    username = session['username']
    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        new_content = request.form['content']
        cursor.execute("UPDATE comments SET content = %s WHERE id = %s AND commenter = %s", (new_content, comment_id, username))
        conn.commit()
        # 댓글의 게시글 ID 찾아서 redirect
        cursor.execute("SELECT board_id FROM comments WHERE id = %s", (comment_id,))
        post = cursor.fetchone()
        cursor.close()
        conn.close()
        return redirect(url_for('content', id=post['board_id']))

    else:
        # 수정 폼 보여주기
        cursor.execute("SELECT * FROM comments WHERE id = %s", (comment_id,))
        comment = cursor.fetchone()
        cursor.close()
        conn.close()

        if comment and comment['commenter'] == username:
            return render_template('editComment.html', comment=comment)
        else:
            return render_template('editError.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['id']
        userpw = request.form['pw']

        conn = connectsql()
        cursor = conn.cursor()
        query = "SELECT * FROM user WHERE user_name = %s AND user_password = %s"
        cursor.execute(query, (userid, userpw))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['username'] = userid
            return redirect(url_for('post'))  # 로그인 성공 시 메인으로 이동
        else:
            return render_template('loginError.html')
    else:
        return render_template('login.html')

@app.route('/regist', methods=['GET', 'POST'])
def regist():
    if request.method == 'POST':
        userid = request.form['id']
        userpw = request.form['pw']

        conn = connectsql()
        cursor = conn.cursor()

        # 이미 존재하는 사용자 체크
        cursor.execute("SELECT * FROM user WHERE user_name = %s", (userid,))
        existing = cursor.fetchone()

        if existing:
            cursor.close()
            conn.close()
            return render_template('registError.html')
        else:
            cursor.execute("INSERT INTO user (user_name, user_password) VALUES (%s, %s)", (userid, userpw))
            conn.commit()
            cursor.close()
            conn.close()
            return render_template('registSuccess.html')
    else:
        return render_template('regist.html')

if __name__ == '__main__':
    app.run(debug=True)
