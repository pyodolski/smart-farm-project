import json
from flask import Blueprint, jsonify, abort
from utils.database import get_db_connection, get_dict_cursor_connection

group_bp = Blueprint('group', __name__, url_prefix='/api/greenhouses')

@group_bp.route('/<int:gh_id>/groups', methods=['GET'])
def get_greenhouse_groups(gh_id):
    # DB에서 grid_data 가져오기
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT grid_data FROM greenhouses WHERE id = %s",
                (gh_id,)
            )
            row = cursor.fetchone()
            if not row:
                abort(404, f"Greenhouse {gh_id} not found")
            grid = json.loads(row[0])
    finally:
        conn.close()

    # 첫 번째 행의 모든 요소가 같은지 확인
    first_row = grid[0]
    is_row_merge = all(x == first_row[0] for x in first_row)

    if is_row_merge:
        groups = find_row_groups(grid)
        axis = 'row'
    else:
        groups = find_col_groups(grid)
        axis = 'col'

    # JSON 형태로 반환
    return jsonify({
        'greenhouseId': gh_id,
        'axis': axis,
        'groups': groups
    })

def find_contiguous_segments(line):
    segments = []
    start = 0
    val = line[0]
    for i in range(1, len(line)):
        if line[i] != val:
            segments.append((start, i-1, val))  # (시작 인덱스, 끝 인덱스, 값)
            start = i
            val = line[i]
    segments.append((start, len(line)-1, val))  # 마지막 세그먼트
    return segments

def find_row_groups(grid):
    groups = []
    for row_idx, row in enumerate(grid):
        segments = find_contiguous_segments(row)
        for start, end, val in segments:
            groups.append((row_idx, start, end, val))  # (행 인덱스, 시작 열, 끝 열, 값)
    return groups

def find_col_groups(grid):
    groups = []
    for col_idx in range(len(grid[0])):
        col = [row[col_idx] for row in grid]
        segments = find_contiguous_segments(col)
        for start, end, val in segments:
            groups.append((start, col_idx, end, val))  # (시작 행, 열 인덱스, 끝 행, 값)
    return groups
