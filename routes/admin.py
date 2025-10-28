from flask import Blueprint, render_template, request, redirect, url_for
from utils.database import get_db_connection, get_dict_cursor_connection
from utils.notification import NotificationManager

admin_bp = Blueprint('admin', __name__)

# 관리자 메인 페이지
@admin_bp.route('/admin.html')
def admin_page():
    conn, cursor = get_dict_cursor_connection()
    if not conn or not cursor:
        return "DB 연결 실패", 500

    try:
        # 1. 신고된 게시글 (5회 이상)
        cursor.execute("""
            SELECT id, title, content, nickname AS author, report 
            FROM board 
            WHERE report >= 5 
            ORDER BY report DESC, id DESC
        """)
        reported_boards = cursor.fetchall()

        # 2. 신고된 댓글 (5회 이상)
        cursor.execute("""
            SELECT 
                c.id, 
                c.content, 
                u.nickname AS author, 
                c.report, 
                c.board_id,
                b.title AS board_title,
                b.nickname AS board_author
            FROM comments c
            JOIN board b ON c.board_id = b.id
            JOIN users u ON c.commenter = u.id
            WHERE c.report >= 5
            ORDER BY c.report DESC, c.id DESC
        """)
        reported_comments = cursor.fetchall()

        # 3. 승인 대기 농장
        cursor.execute("""
            SELECT id, name, location, owner_username, document_path 
            FROM farms 
            WHERE is_approved = false 
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


# 게시글 삭제
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


# 댓글 삭제
@admin_bp.route('/admin/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    conn = get_db_connection()
    if not conn:
        return "DB 연결 실패", 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
            conn.commit()
            return redirect(url_for('admin.admin_page'))
    except Exception as e:
        print(f"댓글 삭제 오류: {e}")
        return "댓글 삭제 중 오류 발생", 500
    finally:
        conn.close()


# 농장 승인
@admin_bp.route('/admin/approve_farm/<int:farm_id>', methods=['POST'])
def approve_farm(farm_id):
    conn = get_db_connection()
    if not conn:
        return "DB 연결 실패", 500

    try:
        with conn.cursor() as cursor:
            # 농장 정보 조회
            cursor.execute("""
                SELECT name, owner_username 
                FROM farms 
                WHERE id = %s
            """, (farm_id,))
            farm = cursor.fetchone()
            
            if not farm:
                return "농장을 찾을 수 없습니다", 404

            # 농장 승인 상태 업데이트
            cursor.execute("UPDATE farms SET is_approved = true WHERE id = %s", (farm_id,))
            
            # 알림 생성
            notification_mgr = NotificationManager()
            notification_mgr.create_approval_notification(
                receiver_id=farm[1],  # owner_username
                farm_id=farm_id,
                farm_name=farm[0]  # farm name
            )
            
            conn.commit()
            return redirect(url_for('admin.admin_page'))
    except Exception as e:
        print(f"승인 오류: {e}")
        conn.rollback()
        return "승인 실패", 500
    finally:
        conn.close()


# 농장 거부 (삭제)
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
