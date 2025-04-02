from flask import Flask, render_template, session, url_for, request, redirect
import pymysql

app = Flask(__name__)
app.secret_key = 'sample_secret'  # 세션 암호화를 위한 시크릿 키

# MySQL 연결 함수
def connectsql():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        passwd='comep1522w',
        db='smartfarm',
        charset='utf8'
    )
    return conn

# 메인 페이지 - 로그인 여부에 따라 분기
@app.route('/')
def index():
    username = session.get('username')
    return render_template('index.html', logininfo=username)

# 게시판 목록 화면
@app.route('/post')
def post():
    username = session.get('username')
    sort = request.args.get('sort', 'new')  # 정렬 기준 (new 또는 popular)
    keyword = request.args.get('search', '')  # 검색 키워드

    # 정렬 조건 구성
    order_query = "ORDER BY likes DESC, b.id DESC" if sort == 'popular' else "ORDER BY b.id DESC"

    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 검색 조건 구성
    if keyword:
        search_condition = "WHERE b.title LIKE %s OR b.content LIKE %s"
        search_values = (f"%{keyword}%", f"%{keyword}%")
    else:
        search_condition = ""
        search_values = ()

    # 게시글 목록 쿼리
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

    return render_template('post.html', postlist=post_list, logininfo=username, current_sort=sort, current_search=keyword)

# 게시글 상세 페이지
@app.route('/post/content/<id>')
def content(id):
    if 'username' not in session:
        return render_template('Error.html')

    username = session['username']

    # 조회수 증가
    conn = connectsql()
    cursor = conn.cursor()
    cursor.execute("UPDATE board SET view = view + 1 WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    # 게시글, 좋아요 수, 댓글 가져오기
    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, title, content, name FROM board WHERE id = %s", (id,))
    content = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS cnt FROM likes WHERE board_id = %s", (id,))
    like_count = cursor.fetchone()['cnt']
    cursor.execute("SELECT id, commenter, content, cdate FROM comments WHERE board_id = %s ORDER BY cdate DESC", (id,))
    comments = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('content.html', data=content, username=username, like_count=like_count, comments=comments)

# 게시글 좋아요 기능
@app.route('/like/<id>')
def like(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = connectsql()
    cursor = conn.cursor()

    # 중복 좋아요 확인 및 등록
    cursor.execute("SELECT * FROM likes WHERE board_id = %s AND user_name = %s", (id, username))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO likes (board_id, user_name) VALUES (%s, %s)", (id, username))
        conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for('content', id=id))

# 게시글 수정
@app.route('/post/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if 'username' not in session:
        return render_template('Error.html')

    username = session['username']

    if request.method == 'POST':
        edittitle = request.form['title']
        editcontent = request.form['content']

        conn = connectsql()
        cursor = conn.cursor()
        cursor.execute("UPDATE board SET title = %s, content = %s WHERE id = %s", (edittitle, editcontent, id))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('editSuccess.html')

    else:
        conn = connectsql()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, title, content, name FROM board WHERE id = %s", (id,))
        postdata = cursor.fetchone()
        cursor.close()
        conn.close()

        if postdata and postdata['name'] == username:
            return render_template('edit.html', data=postdata, logininfo=username)
        else:
            return render_template('editError.html')

# 게시글 삭제
@app.route('/post/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    if 'username' not in session:
        return render_template('Error.html')

    username = session['username']

    if request.method == 'POST':
        conn = connectsql()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM board WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('deleteSuccess.html')
    else:
        conn = connectsql()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT name FROM board WHERE id = %s", (id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result and result['name'] == username:
            return render_template('delete.html', id=id)
        else:
            return render_template('editError.html')

# 게시글 삭제 성공 처리
@app.route('/post/delete/success/<id>')
def deletesuccess(id):
    if 'username' not in session:
        return render_template('Error.html')

    username = session['username']
    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT name FROM board WHERE id = %s", (id,))
    result = cursor.fetchone()

    if result and result['name'] == username:
        cursor.execute("DELETE FROM board WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('deleteSuccess.html')
    else:
        cursor.close()
        conn.close()
        return render_template('editError.html')

# 게시글 작성
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
        cursor.execute("INSERT INTO board (name, title, content) VALUES (%s, %s, %s)", (username, usertitle, usercontent))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('post'))

    return render_template('write.html', logininfo=username)

# 댓글 작성
@app.route('/comment/<post_id>', methods=['POST'])
def comment(post_id):
    if 'username' not in session:
        return render_template('Error.html')

    commenter = session['username']
    content = request.form['content']

    conn = connectsql()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (board_id, commenter, content) VALUES (%s, %s, %s)", (post_id, commenter, content))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('content', id=post_id))

# 댓글 삭제
@app.route('/comment/delete/<comment_id>/<post_id>')
def delete_comment(comment_id, post_id):
    if 'username' not in session:
        return render_template('Error.html')

    username = session['username']
    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT commenter FROM comments WHERE id = %s", (comment_id,))
    result = cursor.fetchone()

    if result and result['commenter'] == username:
        cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for('content', id=post_id))

# 댓글 수정
@app.route('/comment/edit/<int:comment_id>', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if 'username' not in session:
        return render_template('Error.html')

    username = session['username']
    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        new_content = request.form['content']
        cursor.execute("SELECT board_id FROM comments WHERE id = %s AND commenter = %s", (comment_id, username))
        result = cursor.fetchone()

        if result:
            cursor.execute("UPDATE comments SET content = %s WHERE id = %s AND commenter = %s", (new_content, comment_id, username))
            conn.commit()
            board_id = result['board_id']
            cursor.close()
            conn.close()
            return redirect(url_for('content', id=board_id))
        else:
            cursor.close()
            conn.close()
            return render_template('editError.html')

    else:
        cursor.execute("SELECT * FROM comments WHERE id = %s", (comment_id,))
        comment = cursor.fetchone()
        cursor.close()
        conn.close()

        if comment and comment['commenter'] == username:
            return render_template('editComment.html', comment=comment)
        else:
            return render_template('editError.html')

# # 로그아웃
# @app.route('/logout')
# def logout():
#     session.pop('username', None)
#     return redirect(url_for('index'))

# # 로그인
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         userid = request.form['id']
#         userpw = request.form['pw']

#         conn = connectsql()
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM user WHERE user_name = %s AND user_password = %s", (userid, userpw))
#         user = cursor.fetchone()
#         cursor.close()
#         conn.close()

#         if user:
#             session['username'] = userid
#             return redirect(url_for('post'))
#         else:
#             return render_template('loginError.html')
#     else:
#         return render_template('login.html')

# # 회원가입
# @app.route('/regist', methods=['GET', 'POST'])
# def regist():
#     if request.method == 'POST':
#         userid = request.form['id']
#         userpw = request.form['pw']

#         conn = connectsql()
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM user WHERE user_name = %s", (userid,))
#         existing = cursor.fetchone()

#         if existing:
#             cursor.close()
#             conn.close()
#             return render_template('registError.html')
#         else:
#             cursor.execute("INSERT INTO user (user_name, user_password) VALUES (%s, %s)", (userid, userpw))
#             conn.commit()
#             cursor.close()
#             conn.close()
#             return render_template('registSuccess.html')
#     else:
#         return render_template('regist.html')

if __name__ == '__main__':
    app.run(debug=True)