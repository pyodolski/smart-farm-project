from flask import Blueprint, jsonify, request
import pymysql
from utils.database import get_db_connection

sensor_bp = Blueprint('sensor', __name__)

@sensor_bp.route('/api/sensor/latest', methods=['GET'])
def get_latest_sensor():
    gh_id = request.args.get('gh_id')
    if not gh_id:
        return jsonify({'error': 'gh_id required'}), 400
    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM sensor_log WHERE gh_id = %s ORDER BY timestamp DESC LIMIT 1", (gh_id,))
    row = cur.fetchone()
    conn.close()
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
        'timestamp': row['timestamp'],
        'message': None
    }) 