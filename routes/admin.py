from flask import Blueprint, render_template, request, redirect, url_for
from utils.database import get_db_connection, get_dict_cursor_connection

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin.html')
def admin_page():
    conn, cursor = get_dict_cursor_connection()
    if not conn or not cursor:
        return "DB 연결 실패", 500

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

        return render_template(
            'admin.html',
            reported_boards=reported_boards,
            reported_comments=reported_comments,
            pending_farms=pending_farms
        )

    except Exception as e:
        print(f"쿼리 오류: {e}")
        return "DB 조회 실패", 500
    finally:
        cursor.close()
        conn.close()

# 댓글 하드 딜리트 라우트
@admin_bp.route('/admin/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    conn = get_db_connection()
    if not conn:
        return "DB 연결 실패", 500

    try:
        with conn.cursor() as cursor:
            # comments 테이블에서 해당 id의 댓글 레코드 삭제
            cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
            conn.commit()
            return redirect(url_for('admin.admin_page'))
    except Exception as e:
        print(f"댓글 삭제 오류: {e}")
        return "댓글 삭제 중 오류 발생", 500
    finally:
        conn.close()

@admin_bp.route('/admin/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = get_db_connection()
    if not conn:
        return "DB 연결 실패", 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM board WHERE id = %s", (post_id,))
            conn.commit()
            return redirect(url_for('admin.admin_page'))
    except Exception as e:
        print(f"게시글 삭제 오류: {e}")
        return "삭제 중 오류 발생", 500
    finally:
        conn.close()

#승인
@admin_bp.route('/admin/approve_farm/<int:farm_id>', methods=['POST'])
def approve_farm(farm_id):
    conn = get_db_connection()
    if not conn:
        return "DB 연결 실패", 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE farms SET is_approved = 1 WHERE id = %s", (farm_id,))
            conn.commit()
            return redirect(url_for('admin.admin_page'))
    except Exception as e:
        print(f"승인 오류: {e}")
        return "승인 실패", 500
    finally:
        conn.close()

#거부
@admin_bp.route('/admin/reject_farm/<int:farm_id>', methods=['POST'])
def reject_farm(farm_id):
    conn = get_db_connection()
    if not conn:
        return "DB 연결 실패", 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM farms WHERE id = %s", (farm_id,))
            conn.commit()
            return redirect(url_for('admin.admin_page'))
    except Exception as e:
        print(f"거부 오류: {e}")
        return "거부 실패", 500
    finally:
        conn.close()