import pymysql
import os
import json
from flask import Flask, request, session, jsonify, render_template
from flask_cors import CORS
from config import DB_CONFIG
from routes.user import user_bp
from routes.admin import admin_bp
from routes.farm import farm_bp
from routes.weather import weather_bp
from routes.post import post_bp
from routes.product import product_bp
from routes.crop import crop_bp
from routes.chart import chart_bp

def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.MySQLError as e:
        print(f"DB 연결 실패: {e}")
        return None

app = Flask(__name__)
CORS(app,
     resources={r"/*": {"origins": "http://localhost:3000"}},
     supports_credentials=True)

app.secret_key = 'your_secret_key'  # 세션에 필요한 비밀키

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(farm_bp, url_prefix='/api/farms')
app.register_blueprint(post_bp)
app.register_blueprint(crop_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(product_bp)
app.register_blueprint(chart_bp)

# -------------------- React 연동 ----------------------

@app.route('/grid')
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
        # 수정 모드: 해당 greenhouse 데이터 불러오기
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
        # 신규 추가 모드: farm_id로 진입
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


@app.route('/api/greenhouses/create', methods=['POST'])
def create_greenhouse():
    try:
        data = request.get_json()

        farm_id = data.get('farm_id')
        name = data.get('name')
        num_rows = data.get('num_rows')
        num_cols = data.get('num_cols')
        grid_data = data.get('grid_data')  # 2차원 배열

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


@app.route('/api/greenhouses/update/<int:greenhouse_id>', methods=['POST'])
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

@app.route('/api/greenhouses/delete/<int:greenhouse_id>', methods=['DELETE'])
def delete_greenhouse(greenhouse_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 먼저 존재하는지 확인
        cur.execute("SELECT id FROM greenhouses WHERE id = %s", (greenhouse_id,))
        if not cur.fetchone():
            conn.close()
            return jsonify({"message": "해당 하우스가 존재하지 않습니다."}), 404

        # 삭제 쿼리
        cur.execute("DELETE FROM greenhouses WHERE id = %s", (greenhouse_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "✅ 하우스 삭제 완료"}), 200

    except Exception as e:
        print("❌ 삭제 오류:", e)
        return jsonify({"message": "서버 오류 발생"}), 500



@app.route('/api/greenhouses/list/<int:farm_id>', methods=['GET'])
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


if __name__ == '__main__':
    app.run(port=5001, debug=True)
