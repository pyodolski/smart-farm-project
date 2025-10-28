# app.py
import os
import psycopg2 # pymysql 대신 psycopg2 사용
from flask import Flask, request, session, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta
import json # 추가된 임포트

# .env 파일 로드
load_dotenv()

# 블루프린트 임포트
from routes.user import user_bp
from routes.admin import admin_bp
from routes.farm import farm_bp
from routes.post import post_bp
from routes.product import product_bp
from routes.greenhouse import greenhouse_bp
from routes.crop import crop_bp
from routes.chart import chart_bp
from routes.weather import weather_bp
from routes.notification import notification_bp
from routes.sensor import sensor_bp

# PostgreSQL 연결 함수
def get_db_connection():
    try:
        # 환경 변수에서 데이터베이스 접속 정보 가져오기
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"DB 연결 실패: {e}")
        return None

# Flask 앱 설정
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# 세션 설정 (CORS와 쿠키를 위한)
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS에서만 쿠키 전송
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # CORS 요청에서 쿠키 허용

CORS(app, 
     origins=[
         "http://localhost:3000",
         "https://smart-farm-hub.app",
         "https://smart-farm-ignore.vercel.app",
         "https://smart-farm-ignore-git-main-pocketopis-projects.vercel.app",
         "https://smart-farm-ignore-c4z23edds-pocketopis-projects.vercel.app"
     ],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
     expose_headers=["Content-Range", "X-Content-Range"],
     vary_header=True)

# 세션 타임아웃 설정
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# 루트 경로 추가
@app.route('/')
def home():
    return jsonify({
        'message': 'Smart Farm API is running!',
        'status': 'success',
        'endpoints': {
            'users': '/login',
            'posts': '/api/posts',
            'farms': '/api/farms',
            'products': '/product/subscribe'
        }
    })

# 블루프린트 등록
app.register_blueprint(user_bp)
app.register_blueprint(farm_bp)
app.register_blueprint(post_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(product_bp)
app.register_blueprint(greenhouse_bp, url_prefix='/api/greenhouses')
app.register_blueprint(crop_bp)
app.register_blueprint(chart_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(sensor_bp)

# 전역 오류 처리기 추가
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"전역 오류: {str(e)}")
    return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

# 서버 실행
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)