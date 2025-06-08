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

    # 그룹화 기준 판단
    standard = find_standard(grid)  # 0: row, 1: col
    if standard == 0:
        groups = find_row_groups(grid)
        axis = 'row'
    else:
        groups = find_col_groups(grid)
        axis = 'col'

    # JSON 형태로 반환
    return jsonify({
        'greenhouseId': gh_id,
        'axis':        axis,
        'groups':      groups
    })

def find_contiguous_segments(line):
    segments = []
    start = 0
    val = line[0]
    for i in range(1, len(line)):
        if line[i] != val:
            segments.append(list(range(start, i)))
            start = i
            val = line[i]
    segments.append(list(range(start, len(line))))
    return segments

def find_row_groups(grid):
    rows_as_tuples = [tuple(row) for row in grid]
    return find_contiguous_segments(rows_as_tuples)

def find_col_groups(grid):
    # 모든 행이 서로 같아야 열 기준 그룹화
    if not all(tuple(row) == tuple(grid[0]) for row in grid):
        return None
    
    template = grid[0]
    return find_contiguous_segments(template)

def find_standard(grid):
    """
    0을 반환하면 행 기준
    1을 반환하면 열 기준
    """
    row_groups = find_row_groups(grid)
    row_count = len(row_groups)

    col_groups = find_col_groups(grid)
    col_count = len(col_groups) if col_groups is not None else 0

    return 0 if row_count >= col_count else 1
