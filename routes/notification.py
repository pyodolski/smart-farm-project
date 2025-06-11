from flask import Blueprint, jsonify, session
from utils.notification import NotificationManager

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "로그인이 필요합니다"}), 401

        notification_mgr = NotificationManager()
        notifications = notification_mgr.get_notifications(user_id)
        return jsonify(notifications)
    except Exception as e:
        print(f"알림 조회 오류: {e}")
        return jsonify({"error": "알림 조회 실패"}), 500

@notification_bp.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
def handle_notification(notification_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "로그인이 필요합니다"}), 401

        notification_mgr = NotificationManager()
        
        # 알림 정보 가져오기
        notification = notification_mgr.get_notification_by_id(notification_id)
        if not notification:
            return jsonify({"error": "알림을 찾을 수 없습니다"}), 404
            
        # URL 생성
        redirect_url = notification_mgr.get_notification_url(notification['type'], notification['target_id'])
        
        # 읽음 표시
        success = notification_mgr.mark_as_read(notification_id)
        if success:
            return jsonify({
                "message": "알림을 읽음 표시했습니다.",
                "redirect_url": redirect_url
            })
        return jsonify({"error": "알림 읽음 표시 실패"}), 400
    except Exception as e:
        print(f"알림 읽음 표시 오류: {e}")
        return jsonify({"error": "알림 읽음 표시 실패"}), 500 