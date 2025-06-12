# routes/greenhouse.py

from flask import Blueprint, request, jsonify, session, render_template
import pymysql
import json
from utils.database import get_db_connection

greenhouse_bp = Blueprint('greenhouse', __name__)

# --------------------------
# 그룹 생성 관련 유틸 함수
# --------------------------
def find_contiguous_segments(line):
    segments = []
    start = 0
    val = line[0]
    for i in range(1, len(line)):
        if line[i] != val:
            segments.append((start, i - 1, val))
            start = i
            val = line[i]
    segments.append((start, len(line) - 1, val))
    return segments

def find_row_groups(grid):
    groups = []
    for row_idx, row in enumerate(grid):
        segments = find_contiguous_segments(row)
        for start, end, val in segments:
            if end > start:
                groups.append((row_idx, start, end, val))
    return groups

def find_col_groups(grid):
    groups = []
    for col_idx in range(len(grid[0])):
        col = [row[col_idx] for row in grid]
        segments = find_contiguous_segments(col)
        for start, end, val in segments:
            if end > start:
                groups.append((start, col_idx, end, val))
    return groups

# ✅ 자동으로 수평 vs 수직 그룹 수 비교하여 하나만 저장

def save_crop_groups(greenhouse_id, grid_data, conn):
    cur = conn.cursor()
    cur.execute("DELETE FROM crop_groups WHERE greenhouse_id = %s", (greenhouse_id,))

    row_groups = find_row_groups(grid_data)
    col_groups = find_col_groups(grid_data)

    # ✅ 첫 번째 행의 값이 모두 같으면 가로 병합, 아니면 세로 병합
    if all(x == grid_data[0][0] for x in grid_data[0]):
        selected_groups = row_groups
        is_horizontal = True
    else:
        selected_groups = col_groups
        is_horizontal = False

    for group in selected_groups:
        if is_horizontal:
            row_idx, start_col, end_col, value = group
            cells = [[row_idx, col] for col in range(start_col, end_col + 1)]
        else:
            start_row, col_idx, end_row, value = group
            cells = [[row, col_idx] for row in range(start_row, end_row + 1)]

        cur.execute("""
            INSERT INTO crop_groups (greenhouse_id, group_cells, crop_type, is_horizontal, is_read)
            VALUES (%s, %s, %s, %s, %s)
        """, (greenhouse_id, json.dumps(cells), value, is_horizontal, False))

# --------------------------
# 비닐하우스 생성
# --------------------------
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
        greenhouse_id = cur.lastrowid

        # ✅ 그룹 저장
        save_crop_groups(greenhouse_id, grid_data, conn)

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

        # ✅ 업데이트 시에도 그룹 재생성
        save_crop_groups(greenhouse_id, grid_data, conn)

        conn.commit()
        conn.close()

        return jsonify({"message": "✅ 하우스 업데이트 완료"}), 200
    except Exception as e:
        print("❌ 업데이트 오류:", e)
        return jsonify({"message": "서버 오류 발생"}), 500

@greenhouse_bp.route('/<int:greenhouse_id>', methods=['DELETE'])
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

@greenhouse_bp.route('/api/grid', methods=['GET'])
def get_grid_data():
    greenhouse_id = request.args.get('id')
    if not greenhouse_id:
        return jsonify({'error': 'greenhouse_id required'}), 400

    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT num_rows, num_cols, grid_data FROM greenhouses WHERE id = %s", (greenhouse_id,))
    greenhouse = cur.fetchone()
    conn.close()

    if not greenhouse:
        return jsonify({'error': '존재하지 않는 비닐하우스입니다.'}), 404

    return jsonify({
        'num_rows': greenhouse['num_rows'],
        'num_cols': greenhouse['num_cols'],
        'grid_data': json.loads(greenhouse['grid_data'])
    })

@greenhouse_bp.route('/<int:greenhouse_id>/groups', methods=['GET'])
def get_crop_groups(greenhouse_id):
    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT id, group_cells, crop_type, is_horizontal, harvest_amount, total_amount FROM crop_groups WHERE greenhouse_id = %s", (greenhouse_id,))
    groups = cur.fetchall()
    conn.close()
    axis = None
    if groups:
        axis = 'row' if groups[0]['is_horizontal'] else 'col'
    for g in groups:
        if isinstance(g['group_cells'], str):
            try:
                g['group_cells'] = json.loads(g['group_cells'])
            except Exception:
                g['group_cells'] = []
    groups = [g for g in groups if isinstance(g, dict) and 'group_cells' in g]
    return jsonify({'groups': groups, 'axis': axis})



# --------------------------
# 촬영 명령 전송
# --------------------------
@greenhouse_bp.route('/crop_groups/read', methods=['POST'])
def crop_groups_read():
    try:
        data = request.get_json()
        group_id = data.get('group_id')
        iot_id = data.get('iot_id')

        if not group_id or not iot_id:
            return jsonify({'message': '필수 정보가 누락되었습니다.'}), 400
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE crop_groups SET is_read = TRUE WHERE id = %s", (group_id,))

        # 2. 실제 IoT 명령 전송 (여기에 코드를 추가!)

        conn.commit()
        conn.close()
        return jsonify({'message': '촬영 명령이 전송되었습니다.'}), 200
    except Exception as e:
        print("❌ 촬영 명령 오류:", e)
        return jsonify({'message': '서버 오류 발생'}), 500

def send_iot_capture_command(iot_id, group_id):
    # 실제 IoT 명령 전송 로직 작성
    pass
