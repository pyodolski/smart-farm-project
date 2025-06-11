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
def delete_notification(notification_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "로그인이 필요합니다"}), 401

        notification_mgr = NotificationManager()
        success = notification_mgr.delete_notification(notification_id)
        if success:
            return jsonify({"message": "알림이 삭제되었습니다."})
        return jsonify({"error": "알림 삭제 실패"}), 400
    except Exception as e:
        print(f"알림 삭제 오류: {e}")
        return jsonify({"error": "알림 삭제 실패"}), 500 