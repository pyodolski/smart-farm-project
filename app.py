# app.py
import pymysql
from flask import Flask, request, session, jsonify, render_template
from flask_cors import CORS
from config import DB_CONFIG

# 블루프린트 임포트
from routes.user import user_bp
from routes.admin import admin_bp
from routes.farm import farm_bp
from routes.weather import weather_bp
from routes.post import post_bp
from routes.product import product_bp
from routes.crop import crop_bp
from routes.chart import chart_bp
from routes.greenhouse import greenhouse_bp  # 새로 분리한 블루프린트
from routes.group import group_bp

# DB 연결 함수
def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.MySQLError as e:
        print(f"DB 연결 실패: {e}")
        return None

# Flask 앱 설정
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 세션 보안 키

# CORS 허용 (React 연결)
CORS(app,
     resources={r"/*": {"origins": "http://localhost:3000"}},
     supports_credentials=True)

# 블루프린트 등록
app.register_blueprint(user_bp)
app.register_blueprint(farm_bp, url_prefix='/api/farms')
app.register_blueprint(post_bp)
app.register_blueprint(crop_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(product_bp)
app.register_blueprint(chart_bp)
app.register_blueprint(greenhouse_bp, url_prefix='/api/greenhouses')  # ✅ 추가
app.register_blueprint(group_bp)

# 서버 실행
if __name__ == '__main__':
    app.run(port=5001, debug=True)