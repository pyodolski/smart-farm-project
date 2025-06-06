# routes/greenhouse.py

from flask import Blueprint, request, jsonify, session, render_template
import pymysql
import json
from utils.database import get_db_connection

greenhouse_bp = Blueprint('greenhouse', __name__)

@greenhouse_bp.route('/create', methods=['POST'])
def create_greenhouse():
    try:
        data = request.get_json()
        farm_id = data.get('farm_id')
        name = data.get('name')
        num_rows = data.get('num_rows')
        num_cols = data.get('num_cols')
        grid_data = data.get('grid_data')

        if not all([farm_id, name, num_rows, num_cols, grid_data]):
            return jsonify({"message": "필수 정보가 누락되었습니다."}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "DB 연결 실패"}), 500

        cur = conn.cursor()
        sql = """
            INSERT INTO greenhouses (farm_id, name, num_rows, num_cols, grid_data)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            farm_id,
            name,
            num_rows,
            num_cols,
            json.dumps(grid_data)
        ))
        conn.commit()
        conn.close()

        return jsonify({"message": "✅ 하우스 저장 완료"}), 200
    except Exception as e:
        print("❌ 저장 오류:", e)
        return jsonify({"message": "서버 오류 발생"}), 500

@greenhouse_bp.route('/update/<int:greenhouse_id>', methods=['POST'])
def update_greenhouse(greenhouse_id):
    try:
        data = request.get_json()
        name = data.get('name')
        num_rows = data.get('num_rows')
        num_cols = data.get('num_cols')
        grid_data = data.get('grid_data')

        if not all([name, num_rows, num_cols, grid_data]):
            return jsonify({"message": "필수 정보가 누락되었습니다."}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        sql = """
            UPDATE greenhouses
            SET name = %s, num_rows = %s, num_cols = %s, grid_data = %s
            WHERE id = %s
        """
        cur.execute(sql, (
            name,
            num_rows,
            num_cols,
            json.dumps(grid_data),
            greenhouse_id
        ))
        conn.commit()
        conn.close()

        return jsonify({"message": "✅ 하우스 업데이트 완료"}), 200
    except Exception as e:
        print("❌ 업데이트 오류:", e)
        return jsonify({"message": "서버 오류 발생"}), 500

@greenhouse_bp.route('/delete/<int:greenhouse_id>', methods=['DELETE'])
def delete_greenhouse(greenhouse_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM greenhouses WHERE id = %s", (greenhouse_id,))
        if not cur.fetchone():
            conn.close()
            return jsonify({"message": "해당 하우스가 존재하지 않습니다."}), 404

        cur.execute("DELETE FROM greenhouses WHERE id = %s", (greenhouse_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "✅ 하우스 삭제 완료"}), 200
    except Exception as e:
        print("❌ 삭제 오류:", e)
        return jsonify({"message": "서버 오류 발생"}), 500

@greenhouse_bp.route('/list/<int:farm_id>', methods=['GET'])
def list_greenhouses(farm_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT id, name FROM greenhouses WHERE farm_id = %s"
        cur.execute(sql, (farm_id,))
        greenhouses = cur.fetchall()
        conn.close()
        return jsonify({"greenhouses": greenhouses}), 200
    except Exception as e:
        print("❌ 목록 불러오기 오류:", e)
        return jsonify({"message": "서버 오류 발생"}), 500

@greenhouse_bp.route('/grid', methods=['GET'])
def grid_generator():
    greenhouse_id = request.args.get('id')
    farm_id = request.args.get('farm_id')
    house_name = ""
    num_rows = 10
    num_cols = 10
    grid_data = []

    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    if greenhouse_id:
        cur.execute("SELECT * FROM greenhouses WHERE id = %s", (greenhouse_id,))
        greenhouse = cur.fetchone()
        if greenhouse:
            farm_id = greenhouse['farm_id']
            house_name = greenhouse['name']
            num_rows = greenhouse['num_rows']
            num_cols = greenhouse['num_cols']
            grid_data = json.loads(greenhouse['grid_data'])
        else:
            conn.close()
            return "존재하지 않는 비닐하우스입니다.", 404
    else:
        if not farm_id:
            username = session.get('user_id')
            if not username:
                conn.close()
                return "로그인이 필요합니다.", 401
            cur.execute("SELECT id FROM farms WHERE owner_username = %s LIMIT 1", (username,))
            farm = cur.fetchone()
            if farm:
                farm_id = farm['id']
            else:
                conn.close()
                return "등록된 농장이 없습니다.", 404

    conn.close()

    return render_template('grid_generator.html',
                           farm_id=farm_id,
                           greenhouse_id=greenhouse_id or '',
                           house_name=house_name,
                           num_rows=num_rows,
                           num_cols=num_cols,
                           grid_data=json.dumps(grid_data))