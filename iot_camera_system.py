#!/usr/bin/env python3
"""
IoT 카메라 시스템 - 딸기 농장 모니터링
Raspberry Pi에서 실행되는 스크립트
"""

import os
import time
import requests
import glob
from datetime import datetime
from flask import Flask, request, jsonify
import threading
import json

# --- 설정 ---
IMAGE_DIR = "/home/pi/images"  # 촬영된 이미지 저장 디렉토리
SERVER_BASE_URL = "http://localhost:5001"  # 메인 서버 URL (실제 환경에서는 ngrok URL 사용)
IMAGE_UPLOAD_URL = f"{SERVER_BASE_URL}/api/greenhouses/iot-image-upload"
SENSOR_UPLOAD_URL = f"{SERVER_BASE_URL}/api/sensor/upload"

MAX_IMAGES_TO_UPLOAD_PER_CYCLE = 6
processed_files = set()

# Flask 앱 (명령 수신용)
app = Flask(__name__)

# --- 카메라 촬영 함수 ---
def capture_image(group_id, iot_id):
    """
    카메라로 이미지 촬영
    실제 환경에서는 Raspberry Pi 카메라 모듈 사용
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"iot_{iot_id}_group_{group_id}_{timestamp}.jpg"
        filepath = os.path.join(IMAGE_DIR, filename)
        
        # 실제 카메라 촬영 명령 (예시)
        # import picamera
        # with picamera.PiCamera() as camera:
        #     camera.capture(filepath)
        
        # 테스트용: 더미 이미지 생성
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (640, 480), color='green')
        draw = ImageDraw.Draw(img)
        
        # 딸기 모양 그리기 (테스트용)
        draw.ellipse([100, 100, 150, 150], fill='red')
        draw.ellipse([200, 150, 250, 200], fill='red')
        draw.ellipse([300, 120, 350, 170], fill='lightgreen')
        
        img.save(filepath)
        print(f"📸 이미지 촬영 완료: {filename}")
        return filepath
        
    except Exception as e:
        print(f"❌ 이미지 촬영 실패: {e}")
        return None

# --- 이미지 업로드 함수 ---
def upload_image(filepath, group_id, iot_id):
    """지정된 경로의 이미지를 서버로 업로드합니다."""
    filename = os.path.basename(filepath)
    
    # 파일이 완전히 기록될 때까지 대기
    time.sleep(0.1)
    
    try:
        # 파일 유효성 검사
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            print(f"⚠️ 파일이 준비되지 않았거나 비어 있습니다: {filename}")
            return False
        
        with open(filepath, "rb") as img_file:
            files = {"file": (filename, img_file, "image/jpeg")}
            data = {
                "group_id": group_id,
                "iot_id": iot_id
            }
            
            res = requests.post(
                IMAGE_UPLOAD_URL,
                files=files,
                data=data,
                timeout=30  # YOLO 분석 시간 고려
            )
            res.raise_for_status()
            
            result = res.json()
            print(f"✅ 이미지 업로드 및 분석 성공: {filename}")
            print(f"📊 분석 결과: {result.get('result', {})}")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 이미지 업로드 실패: {filename} - {e}")
        return False
    except Exception as e:
        print(f"❌ 알 수 없는 오류: {filename} - {e}")
        return False

# --- 센서 데이터 업로드 함수 ---
def upload_sensor_data(iot_id, gh_id):
    """온습도 센서 데이터를 서버로 전송"""
    try:
        # 실제 환경에서는 DHT22 센서 사용
        # import adafruit_dht
        # dht_device = adafruit_dht.DHT22(board.D4)
        # temperature = dht_device.temperature
        # humidity = dht_device.humidity
        
        # 테스트용 더미 데이터
        import random
        temperature = round(random.uniform(20.0, 30.0), 1)
        humidity = round(random.uniform(40.0, 80.0), 1)
        
        data = {
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": datetime.now().isoformat(),
            "iot_id": iot_id,
            "gh_id": gh_id
        }
        
        res = requests.post(SENSOR_UPLOAD_URL, json=data, timeout=10)
        res.raise_for_status()
        print(f"✅ 센서 데이터 업로드: 온도 {temperature}°C, 습도 {humidity}%")
        return True
        
    except Exception as e:
        print(f"❌ 센서 데이터 전송 실패: {e}")
        return False

# --- Flask 라우트: 촬영 명령 수신 ---
@app.route('/capture-command', methods=['POST'])
def receive_capture_command():
    """
    메인 서버로부터 촬영 명령을 수신하고 처리
    """
    try:
        data = request.get_json()
        group_id = data.get('group_id')
        iot_id = data.get('iot_id')
        action = data.get('action')
        
        if not all([group_id, iot_id, action]):
            return jsonify({'message': '필수 정보가 누락되었습니다.'}), 400
        
        if action == 'capture_and_upload':
            print(f"📸 촬영 명령 수신 - 그룹 ID: {group_id}, IoT ID: {iot_id}")
            
            # 비동기적으로 촬영 및 업로드 실행
            def capture_and_upload_async():
                # 1. 이미지 촬영
                image_path = capture_image(group_id, iot_id)
                if image_path:
                    # 2. 서버로 업로드 및 분석
                    success = upload_image(image_path, group_id, iot_id)
                    if success:
                        # 3. 업로드 성공 시 로컬 파일 삭제
                        try:
                            os.remove(image_path)
                            print(f"🗑️ 로컬 이미지 삭제: {os.path.basename(image_path)}")
                        except OSError as e:
                            print(f"❌ 파일 삭제 실패: {e}")
                    else:
                        print(f"⚠️ 업로드 실패, 로컬 파일 유지: {image_path}")
                else:
                    print("❌ 이미지 촬영 실패")
            
            # 백그라운드에서 실행
            threading.Thread(target=capture_and_upload_async, daemon=True).start()
            
            return jsonify({
                'message': '촬영 명령을 수신했습니다. 처리 중...',
                'status': 'processing'
            }), 200
        
        else:
            return jsonify({'message': '알 수 없는 액션입니다.'}), 400
            
    except Exception as e:
        print(f"❌ 명령 처리 오류: {e}")
        return jsonify({'message': '서버 오류 발생', 'error': str(e)}), 500

# --- 자동 이미지 업로드 시스템 ---
def auto_image_upload_system():
    """
    주기적으로 이미지 폴더를 스캔하여 새로운 이미지를 자동 업로드
    (기존 코드 기반)
    """
    print(f"🚀 자동 이미지 업로더 시작. {IMAGE_DIR} 폴더를 주기적으로 스캔합니다.")
    
    # 초기 스캔: 기존 이미지들을 processed_files에 추가
    initial_images = glob.glob(os.path.join(IMAGE_DIR, "*.jpg"))
    for img_path in initial_images:
        processed_files.add(os.path.abspath(img_path))
    print(f"💡 초기 스캔 완료: {len(initial_images)}개의 기존 이미지 제외")
    
    while True:
        try:
            all_current_images = glob.glob(os.path.join(IMAGE_DIR, "*.jpg"))
            
            # 새로운 이미지만 필터링
            unprocessed_new_images = []
            for img_path in all_current_images:
                abs_path = os.path.abspath(img_path)
                if abs_path not in processed_files:
                    unprocessed_new_images.append(abs_path)
            
            if unprocessed_new_images:
                # 최신 파일 우선 정렬
                unprocessed_new_images.sort(key=os.path.getmtime, reverse=True)
                images_to_process = unprocessed_new_images[:MAX_IMAGES_TO_UPLOAD_PER_CYCLE]
                
                print(f"📦 {len(unprocessed_new_images)}개의 미처리 이미지 발견. {len(images_to_process)}개 처리 시도")
                
                for image_path in images_to_process:
                    # 파일명에서 group_id, iot_id 추출 (파일명 규칙에 따라)
                    filename = os.path.basename(image_path)
                    try:
                        # 파일명 형식: iot_{iot_id}_group_{group_id}_{timestamp}.jpg
                        parts = filename.split('_')
                        if len(parts) >= 4 and parts[0] == 'iot':
                            iot_id = parts[1]
                            group_id = parts[3]
                        else:
                            # 기본값 사용
                            iot_id = "1"
                            group_id = "1"
                    except:
                        iot_id = "1"
                        group_id = "1"
                    
                    if upload_image(image_path, group_id, iot_id):
                        try:
                            os.remove(image_path)
                            print(f"🗑️ 업로드 완료된 이미지 삭제: {os.path.basename(image_path)}")
                            processed_files.add(image_path)
                        except OSError as e:
                            print(f"❌ 파일 삭제 실패: {e}")
                    else:
                        print(f"⚠️ 업로드 실패: {os.path.basename(image_path)}. 다음 주기에서 재시도")
            
            time.sleep(5)  # 5초마다 스캔
            
        except Exception as e:
            print(f"❌ 자동 업로드 시스템 오류: {e}")
            time.sleep(10)

# --- 센서 데이터 주기적 전송 ---
def auto_sensor_upload_system():
    """주기적으로 센서 데이터를 서버로 전송"""
    current_iot_id = 1
    current_gh_id = 1
    
    while True:
        try:
            upload_sensor_data(current_iot_id, current_gh_id)
            time.sleep(60)  # 1분마다 센서 데이터 전송
        except Exception as e:
            print(f"❌ 센서 업로드 시스템 오류: {e}")
            time.sleep(60)

# --- 메인 실행 ---
if __name__ == "__main__":
    # 이미지 디렉토리 생성
    os.makedirs(IMAGE_DIR, exist_ok=True)
    
    print("🤖 IoT 카메라 시스템 시작")
    print(f"📁 이미지 디렉토리: {IMAGE_DIR}")
    print(f"🌐 서버 URL: {SERVER_BASE_URL}")
    
    # 백그라운드 스레드 시작
    threading.Thread(target=auto_image_upload_system, daemon=True).start()
    threading.Thread(target=auto_sensor_upload_system, daemon=True).start()
    
    # Flask 서버 시작 (명령 수신용)
    print("🚀 Flask 서버 시작 (포트 5002)")
    app.run(host='0.0.0.0', port=5002, debug=False)