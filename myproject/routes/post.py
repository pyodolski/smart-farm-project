from flask import Blueprint, render_template, request, redirect, url_for, session
import pymysql
from config import DB_CONFIG

post_bp = Blueprint('post', __name__)

# DB 연결 공통 함수
def get_db_conn():
    return pymysql.connect(**DB_CONFIG)

@post_bp.route('/post')
def post():
    username = session.get('user_id')
    sort = request.args.get('sort', 'new')  # 정렬 기준 (new 또는 popular)
    keyword = request.args.get('search', '')  # 검색 키워드

    # 정렬 조건 구성
    order_query = "ORDER BY likes DESC, b.id DESC" if sort == 'popular' else "ORDER BY b.id DESC"

    conn = get_db_conn()
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
@post_bp.route('/post/content/<id>')
def content(id):
    if 'user_id' not in session:
        return render_template('Error.html')

    username = session['user_id']

    # 조회수 증가
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE board SET view = view + 1 WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    # 게시글, 좋아요 수, 댓글 가져오기
    conn = get_db_conn()
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
@post_bp.route('/like/<id>')
def like(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    username = session['user_id']
    conn = get_db_conn()
    cursor = conn.cursor()

    # 중복 좋아요 확인 및 등록
    cursor.execute("SELECT * FROM likes WHERE board_id = %s AND user_name = %s", (id, username))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO likes (board_id, user_name) VALUES (%s, %s)", (id, username))
        conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for('post.content', id=id))

# 게시글 수정
@post_bp.route('/post/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return render_template('Error.html')

    username = session['user_id']

    if request.method == 'POST':
        edittitle = request.form['title']
        editcontent = request.form['content']

        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE board SET title = %s, content = %s WHERE id = %s", (edittitle, editcontent, id))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('editSuccess.html')

    else:
        conn = get_db_conn()
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
@post_bp.route('/post/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    if 'user_id' not in session:
        return render_template('Error.html')

    username = session['user_id']

    if request.method == 'POST':
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM board WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('deleteSuccess.html')
    else:
        conn = get_db_conn()
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
@post_bp.route('/post/delete/success/<id>')
def deletesuccess(id):
    if 'user_id' not in session:
        return render_template('Error.html')

    username = session['user_id']
    conn = get_db_conn()
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
@post_bp.route('/write', methods=['GET', 'POST'])
def write():
    if 'user_id' not in session:
        return render_template('Error.html')

    username = session['user_id']

    if request.method == 'POST':
        usertitle = request.form['title']
        usercontent = request.form['content']

        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO board (name, title, content) VALUES (%s, %s, %s)", (username, usertitle, usercontent))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('post.post'))

    return render_template('write.html', logininfo=username)

# 댓글 작성
@post_bp.route('/comment/<post_id>', methods=['POST'])
def comment(post_id):
    if 'user_id' not in session:
        return render_template('Error.html')

    commenter = session['user_id']
    content = request.form['content']

    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (board_id, commenter, content) VALUES (%s, %s, %s)", (post_id, commenter, content))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('post.content', id=post_id))

# 댓글 삭제
@post_bp.route('/comment/delete/<comment_id>/<post_id>')
def delete_comment(comment_id, post_id):
    if 'user_id' not in session:
        return render_template('Error.html')

    username = session['user_id']
    conn = get_db_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT commenter FROM comments WHERE id = %s", (comment_id,))
    result = cursor.fetchone()

    if result and result['commenter'] == username:
        cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for('post.content', id=post_id))

# 댓글 수정
@post_bp.route('/comment/edit/<int:comment_id>', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if 'user_id' not in session:
        return render_template('Error.html')

    username = session['user_id']
    conn = get_db_conn()
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
            return redirect(url_for('post.content', id=board_id))
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


# 게시물 신고 기능
from flask import jsonify

@post_bp.route('/report/post/<int:post_id>', methods=['POST'])
def report_post(post_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    user_id = session['user_id']
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        # 중복 신고 확인
        cursor.execute("""
            SELECT 1 FROM report_log
            WHERE user_id=%s AND target_type='post' AND target_id=%s
        """, (user_id, post_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '이미 신고한 게시글입니다.'}), 400

        # 신고 수 증가
        cursor.execute("UPDATE board SET report = report + 1 WHERE id = %s", (post_id,))
        # 신고 로그 기록
        cursor.execute("""
            INSERT INTO report_log (user_id, target_type, target_id)
            VALUES (%s, 'post', %s)
        """, (user_id, post_id))

        conn.commit()
        return jsonify({'success': True, 'message': '신고 완료'}), 200

    except Exception as e:
        conn.rollback()
        print("신고 실패:", e)
        return jsonify({'success': False, 'message': '서버 오류가 발생했습니다.'}), 500

    finally:
        cursor.close()
        conn.close()


# 댓글 신고 기능
@post_bp.route('/report/comment/<int:comment_id>', methods=['POST'])
def report_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    user_id = session['user_id']
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        # 중복 신고 확인
        cursor.execute("""
            SELECT 1 FROM report_log
            WHERE user_id=%s AND target_type='comment' AND target_id=%s
        """, (user_id, comment_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '이미 신고한 댓글입니다.'}), 400

        # 신고 수 증가
        cursor.execute("UPDATE comments SET report = report + 1 WHERE id = %s", (comment_id,))
        # 로그 기록
        cursor.execute("""
            INSERT INTO report_log (user_id, target_type, target_id)
            VALUES (%s, 'comment', %s)
        """, (user_id, comment_id))

        conn.commit()
        return jsonify({'success': True, 'message': '댓글 신고 완료'}), 200

    except Exception as e:
        conn.rollback()
        print("댓글 신고 실패:", e)
        return jsonify({'success': False, 'message': '댓글 신고 실패'}), 500

    finally:
        cursor.close()
        conn.close()