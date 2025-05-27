import pymysql
import os
import json
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from datetime import datetime

from routes.user import user_bp
from routes.admin import admin_bp
from routes.farm import farm_bp
from routes.iot import iot_bp
from routes.weather import weather_bp
from config import DB_CONFIG
from routes.post import post_bp
from routes.product import product_bp
from routes.crop import crop_bp
from routes.chart import chart_bp
from flask_cors import CORS

def get_db_conn():
    return pymysql.connect(**DB_CONFIG)
conn = get_db_conn()
cur = conn.cursor()
UPLOAD_FOLDER = 'static/uploads/farms'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app, 
     resources={r"/*": {"origins": "http://localhost:3000"}},
     supports_credentials=True)
app.register_blueprint(user_bp)
app.register_blueprint(farm_bp, url_prefix='/api/farms')
app.register_blueprint(post_bp)
app.register_blueprint(crop_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(iot_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(product_bp)
app.register_blueprint(chart_bp)

def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.MySQLError as e:
        print(f"DB 연결 실패: {e}")
        return None

@app.route('/')
def home():
    username = session.get('user_id')  #로그인한 유저 이름
    usernickname = session.get('nickname')

    farms = []

    if username:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM farms WHERE owner_username = %s"
        cur.execute(sql, (username,))
        farms = cur.fetchall()
        conn.close()

    return render_template('my_farms.html',farms=farms)

app.secret_key = 'your_secret_key'  # 세션에 필요한 비밀키 (랜덤한 문자열)

# --------------------(개발 중)----------------------
@app.route('/grid')
def grid():
    return render_template('grid_generator.html')

@app.route('/api/greenhouses/create', methods=['POST'])
def create_greenhouse():
    try:
        data = request.get_json()

        farm_id = data.get('farm_id')
        name = data.get('name')
        num_rows = data.get('num_rows')
        num_cols = data.get('num_cols')
        grid_data = data.get('grid_data')  # 2차원 배열

        # 필수값 검사
        if not all([farm_id, name, num_rows, num_cols, grid_data]):
            return jsonify({"message": "필수 정보가 누락되었습니다."}), 400

        # DB 연결
        conn = get_db_connection()
        cur = conn.cursor()

        # INSERT 쿼리
        sql = """
            INSERT INTO greenhouses (farm_id, name, num_rows, num_cols, grid_data)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            farm_id,
            name,
            num_rows,
            num_cols,
            json.dumps(grid_data)  # 배열을 JSON 문자열로 저장
        ))
        conn.commit()
        conn.close()

        return jsonify({"message": "✅ 하우스 저장 완료"}), 200

    except Exception as e:
        print("❌ 저장 오류:", e)
        return jsonify({"message": "서버 오류 발생"}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)