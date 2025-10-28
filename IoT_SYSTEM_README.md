# 🍓 IoT 딸기 농장 모니터링 시스템

## 시스템 구조

### 1. 메인 서버 (Flask)

- **포트**: 5001
- **역할**: 웹 인터페이스, 데이터베이스 관리, YOLO 모델 추론
- **주요 엔드포인트**:
  - `/api/greenhouses/crop_groups/read` - IoT 촬영 명령 전송
  - `/api/greenhouses/iot-image-upload` - IoT에서 이미지 업로드 및 분석

### 2. IoT 디바이스 (Raspberry Pi)

- **포트**: 5002
- **역할**: 카메라 촬영, 센서 데이터 수집, 이미지 업로드
- **스크립트**: `iot_camera_system.py`

## 🚀 시스템 실행 방법

### 1. 메인 서버 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 메인 서버 실행
python app.py
```

### 2. IoT 디바이스 실행 (Raspberry Pi)

```bash
# IoT 시스템 실행
python iot_camera_system.py
```

## 📸 촬영 워크플로우

### 1. 사용자 액션 (웹 인터페이스)

1. 농장 상세 페이지 접속
2. 비닐하우스 선택
3. "📷 촬영" 버튼 클릭
4. IoT 디바이스 선택
5. 촬영할 작물 영역 선택
6. "확인" 버튼 클릭

### 2. 시스템 처리 과정

```
[웹 브라우저]
    ↓ 촬영 요청
[메인 서버]
    ↓ 촬영 명령 전송 (HTTP POST)
[IoT 디바이스]
    ↓ 카메라 촬영
[IoT 디바이스]
    ↓ 이미지 업로드 (HTTP POST)
[메인 서버]
    ↓ YOLO 모델 추론
[메인 서버]
    ↓ 데이터베이스 업데이트
[웹 브라우저]
    ↓ 결과 확인 (자동 새로고침)
```

## 🔧 설정 변경

### IoT 디바이스 설정 (`iot_camera_system.py`)

```python
# 서버 URL 설정 (실제 환경에서는 ngrok URL 사용)
SERVER_BASE_URL = "http://localhost:5001"

# 이미지 저장 디렉토리
IMAGE_DIR = "/home/pi/images"

# 업로드 주기 설정
MAX_IMAGES_TO_UPLOAD_PER_CYCLE = 6
```

### 메인 서버 설정 (`routes/greenhouse.py`)

```python
# IoT 디바이스 IP 설정
RASPBERRY_PI_IP = "http://192.168.137.9:5002"

# YOLO 모델 경로
MODEL_RIPE = YOLO("model/ripe_straw.pt")
MODEL_ROTTEN = YOLO("model/rotten_straw.pt")
```

## 📊 분석 결과

### YOLO 모델 출력

- **익은 딸기**: `straw-ripe` 클래스 감지 개수
- **안익은 딸기**: `straw-unripe` 클래스 감지 개수
- **썩은 딸기**: `starw_rotten` 클래스 감지 여부

### 데이터베이스 업데이트

```sql
UPDATE crop_groups
SET harvest_amount = {익은_딸기_개수},
    total_amount = {전체_딸기_개수},
    is_read = {썩은_딸기_발견_여부}
WHERE id = {그룹_ID}
```

## 🛠️ 실제 하드웨어 연동

### Raspberry Pi 카메라 모듈

```python
# iot_camera_system.py의 capture_image() 함수에서
import picamera
with picamera.PiCamera() as camera:
    camera.capture(filepath)
```

### DHT22 온습도 센서

```python
# iot_camera_system.py의 upload_sensor_data() 함수에서
import adafruit_dht
import board
dht_device = adafruit_dht.DHT22(board.D4)
temperature = dht_device.temperature
humidity = dht_device.humidity
```

## 🔍 테스트 방법

### 1. 로컬 테스트

```bash
# 터미널 1: 메인 서버 실행
python app.py

# 터미널 2: IoT 시스템 실행
python iot_camera_system.py

# 웹 브라우저에서 http://localhost:3000 접속
```

### 2. 수동 촬영 명령 테스트

```bash
curl -X POST http://localhost:5002/capture-command \
  -H "Content-Type: application/json" \
  -d '{"group_id": "1", "iot_id": "1", "action": "capture_and_upload"}'
```

## 📝 로그 확인

### 메인 서버 로그

- YOLO 모델 로드 상태
- 이미지 분석 결과
- 데이터베이스 업데이트 상태

### IoT 디바이스 로그

- 촬영 명령 수신
- 이미지 촬영 완료
- 서버 업로드 결과
- 센서 데이터 전송 상태

## 🚨 문제 해결

### 1. YOLO 모델 로드 실패

```bash
# ultralytics 패키지 설치 확인
pip install ultralytics

# 모델 파일 존재 확인
ls -la model/
```

### 2. IoT 연결 실패

- 네트워크 연결 확인
- 방화벽 설정 확인
- IP 주소 및 포트 확인

### 3. 이미지 업로드 실패

- 파일 권한 확인
- 디스크 용량 확인
- 네트워크 대역폭 확인

## 🔄 업그레이드 계획

1. **실시간 스트리밍**: WebRTC를 통한 실시간 카메라 피드
2. **AI 개선**: 더 정확한 딸기 감지 모델 훈련
3. **알림 시스템**: 썩은 딸기 발견 시 즉시 알림
4. **데이터 분석**: 시간별/일별 수확량 통계
5. **모바일 앱**: 스마트폰에서 농장 모니터링
