from flask import Blueprint, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
from utils.database import get_db_connection

sensor_bp = Blueprint('sensor', __name__)

@sensor_bp.route('/api/sensor/latest', methods=['GET'])
def get_latest_sensor():
    try:
        gh_id = request.args.get('gh_id')
        if not gh_id:
            return jsonify({'error': 'gh_id required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'DB 연결 실패'}), 500
            
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM sensor_log WHERE gh_id = %s ORDER BY logged_at DESC LIMIT 1", (gh_id,))
        row = cur.fetchone()
        
        if not row:
            return jsonify({
                'temperature': None,
                'humidity': None,
                'timestamp': None,
                'message': '온습도를 측정하기 위해 IoT를 작동시키세요.'
            })
            
        return jsonify({
            'temperature': row['temperature'],
            'humidity': row['humidity'],
            'timestamp': row['logged_at'],
            'message': None
        })
    except Exception as e:
        print(f"Sensor API 오류: {str(e)}")
        return jsonify({'error': f'센서 데이터 조회 실패: {str(e)}'}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close() 