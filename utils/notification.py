import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG
from datetime import datetime

class NotificationManager:
    def __init__(self):
        self.db = psycopg2.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
        self.cursor = self.db.cursor(cursor_factory=RealDictCursor)

    #알림 생성
    def create_notification(self, receiver_id: str, message: str, type: str, target_id: int, image_url: str = None):
        try:
            sql = """
                INSERT INTO notification (receiver_id, message, type, target_id, image_url)
                VALUES (%s, %s, %s, %s, %s)
            """
            print(f"Creating notification: receiver={receiver_id}, message={message}, type={type}")  # 디버깅 로그
            self.cursor.execute(sql, (receiver_id, message, type, target_id, image_url))
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error creating notification: {e}")
            self.db.rollback()
            return False

    #알림 목록
    def get_notifications(self, receiver_id: str, limit: int = 10):
        try:
            sql = """
                SELECT * FROM notification 
                WHERE receiver_id = %s AND is_read = FALSE
                ORDER BY created_at DESC 
                LIMIT %s
            """
            self.cursor.execute(sql, (receiver_id, limit))
            notifications = self.cursor.fetchall()
            
            # 각 알림에 대한 URL 생성
            for notification in notifications:
                notification['url'] = self.get_notification_url(notification['type'], notification['target_id'])
            
            return notifications
        except Exception as e:
            print(f"Error fetching notifications: {e}")
            return []

    def mark_as_read(self, notification_id: int):
        try:
            sql = "UPDATE notification SET is_read = TRUE WHERE id = %s"
            self.cursor.execute(sql, (notification_id,))
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            self.db.rollback()
            return False

    #알림 삭제
    def delete_notification(self, notification_id: int):
        try:
            sql = "DELETE FROM notification WHERE id = %s"
            self.cursor.execute(sql, (notification_id,))
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error deleting notification: {e}")
            self.db.rollback()
            return False

    #알림 URL 생성
    def get_notification_url(self, type: str, target_id: int) -> str:
        """알림 타입에 따른 이동할 URL 생성"""
        url_mapping = {
            'iot 탐색 종료': f'/farm/{target_id}',
            '병해충 발생': f'/farm/{target_id}',
            '새 댓글': f'/community/post/{target_id}',
            '승인 허가': f'/farm/{target_id}'
        }
        return url_mapping.get(type, '/')

    #IoT 탐색 종료 알림 생성
    def create_iot_completion_notification(self, receiver_id: str, greenhouse_id: int, greenhouse_name: str):
        try:
            self.cursor.execute("SELECT farm_id FROM greenhouses WHERE id = %s", (greenhouse_id,))
            result = self.cursor.fetchone()
            if not result:
                print(f"Error: Greenhouse {greenhouse_id} not found")
                return False
            
            farm_id = result['farm_id']
            message = f"'{greenhouse_name}' 비닐하우스의 탐색이 완료되었습니다."
            return self.create_notification(
                receiver_id=receiver_id,
                message=message,
                type="iot 탐색 종료",
                target_id=farm_id
            )
        except Exception as e:
            print(f"Error creating IoT completion notification: {e}")
            return False

    #병해충 발생 알림 생성
    def create_pest_detection_notification(self, receiver_id: str, greenhouse_id: int, greenhouse_name: str, image_url: str):
        message = f"'{greenhouse_name}' 비닐하우스에서 병해충이 발견되었습니다. 확인이 필요합니다."
        return self.create_notification(
            receiver_id=receiver_id,
            message=message,
            type="병해충 발생",
            target_id=greenhouse_id,
            image_url=image_url
        )

    #새 댓글 알림 생성
    def create_new_comment_notification(self, receiver_id: str, post_id: int, post_title: str):
        try:
            message = f"'{post_title}' 게시글에 새로운 댓글이 작성되었습니다."
            print(f"Creating comment notification: receiver={receiver_id}, post={post_title}")  # 디버깅
            return self.create_notification(
                receiver_id=receiver_id,
                message=message,
                type="새 댓글",
                target_id=post_id
            )
        except Exception as e:
            print(f"Error creating comment notification: {e}")
            return False

    #승인 허가 알림 생성
    def create_approval_notification(self, receiver_id: str, farm_id: int, farm_name: str):
        message = f"'{farm_name}' 농장 가입 신청이 승인되었습니다."
        return self.create_notification(
            receiver_id=receiver_id,
            message=message,
            type="승인 허가",
            target_id=farm_id
        )

    def get_notification_by_id(self, notification_id: int):
        try:
            sql = "SELECT * FROM notification WHERE id = %s"
            self.cursor.execute(sql, (notification_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error fetching notification: {e}")
            return None

    def __del__(self):
        try:
            self.cursor.close()
            self.db.close()
        except:
            pass 