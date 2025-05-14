from flask import Blueprint, render_template, request, redirect, url_for, session
import pymysql
from config import DB_CONFIG

post_bp = Blueprint('post', __name__)

# DB 연결 공통 함수
def get_db_conn():
    return pymysql.connect(**DB_CONFIG)


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

# 게시글 관련 API
@post_bp.route('/api/posts', methods=['GET'])
def get_posts():
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_conn()
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

@post_bp.route('/api/posts', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': '제목과 내용을 모두 입력해주세요.'}), 400

    conn = get_db_conn()
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

@post_bp.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_conn()
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

@post_bp.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_conn()
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

@post_bp.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_conn()
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

@post_bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
def toggle_like(post_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_conn()
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
@post_bp.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'message': '댓글 내용을 입력해주세요.'}), 400

    conn = get_db_conn()
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

@post_bp.route('/api/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_conn()
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

@post_bp.route('/api/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_conn()
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

@post_bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'message': '로그인이 필요합니다.'}), 401

    conn = get_db_conn()
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
