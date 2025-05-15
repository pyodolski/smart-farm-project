import pymysql
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify

from routes.user import user_bp
from routes.admin import admin_bp
from routes.farm import farm_bp
from config import DB_CONFIG
from routes.post import post_bp
from routes.crop import crop_bp, fetch_disease_detail, fetch_insect_detail, fetch_predator_detail
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

def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.MySQLError as e:
        print(f"DB 연결 실패: {e}")
        return None

@app.route('/')
def home():
    username = session.get('user_id')  #로그인한 유저 이름
    nickname = session.get('nickname')

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


if __name__ == '__main__':
    app.run(port=5001, debug=True)