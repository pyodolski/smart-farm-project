from flask import Blueprint, render_template, request, redirect,url_for
import pymysql
from config import DB_CONFIG
from flask_cors import CORS

admin_bp = Blueprint('admin', __name__)
CORS(admin_bp, resources={r"/*": {"origins": [
    "http://localhost:3001",
    "http://localhost:3000",
    "https://mature-grub-climbing.ngrok-free.app"
]}}, supports_credentials=True)

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

        # 승인 대기 농장 조회
        cursor.execute("""
            SELECT id, name, location, owner_username, document_path 
            FROM farms 
            WHERE is_approved = 0 
            ORDER BY id DESC
        """)
        pending_farms = cursor.fetchall()

        for farm in pending_farms:
            if farm['document_path']:
                farm['document_url'] = farm['document_path'].replace('\\', '/').split('static/')[-1]

    except pymysql.MySQLError as e:
        print(f"쿼리 오류: {e}")
        return "DB 조회 실패", 500
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'admin.html',
        reported_boards=reported_boards,
        reported_comments=reported_comments,
        pending_farms=pending_farms
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


#### -> 추가

#승인
@admin_bp.route('/admin/approve_farm/<int:farm_id>', methods=['POST'])
def approve_farm(farm_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE farms SET is_approved = 1 WHERE id = %s", (farm_id,))
        conn.commit()
    except Exception as e:
        print(f"승인 오류: {e}")
        return "승인 실패", 500
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.admin_page'))

#거부
@admin_bp.route('/admin/reject_farm/<int:farm_id>', methods=['POST'])
def reject_farm(farm_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM farms WHERE id = %s", (farm_id,))
        conn.commit()
    except Exception as e:
        print(f"거부 오류: {e}")
        return "거부 실패", 500
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin.admin_page'))
