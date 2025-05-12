from flask import Blueprint, render_template, request, redirect,url_for
import pymysql
from config import DB_CONFIG

admin_bp = Blueprint('admin', __name__)

# 공통 DB 연결 함수 (post.py와 동일한 방식)
def get_db_conn():
    return pymysql.connect(**DB_CONFIG)

@admin_bp.route('/admin.html')
def admin_page():
    conn = get_db_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # 신고된 게시글 가져오기 (report >= 5)
        cursor.execute("""
            SELECT id, title, content, name AS author, report 
            FROM board 
            WHERE report >= 5 
            ORDER BY report DESC, id DESC
        """)
        reported_boards = cursor.fetchall()

        # 신고된 댓글 가져오기 (report >= 5)
        cursor.execute("""
            SELECT 
                c.id, 
                c.content, 
                c.commenter AS author, 
                c.report, 
                c.board_id,
                b.title AS board_title,
                b.name AS board_author
            FROM comments c
            JOIN board b ON c.board_id = b.id
            WHERE c.report >= 5
            ORDER BY c.report DESC, c.id DESC
        """)
        reported_comments = cursor.fetchall()

    except pymysql.MySQLError as e:
        print(f"쿼리 오류: {e}")
        return "DB 조회 실패", 500
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'admin.html',
        reported_boards=reported_boards,
        reported_comments=reported_comments
    )

@admin_bp.route('/admin/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM board WHERE id = %s", (post_id,))
        conn.commit()
    except Exception as e:
        print(f"게시글 삭제 오류: {e}")
        return "삭제 중 오류 발생", 500
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.admin_page'))

