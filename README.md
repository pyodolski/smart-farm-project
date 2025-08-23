# 스마트팜 관리 시스템

농장 관리, 온실 모니터링, 병해충 탐지, 커뮤니티 기능을 제공하는 스마트팜 IoT 플랫폼입니다.

## 기술 스택

- **Backend**: Flask (Python)
- **Frontend**: React
- **Database**: MySQL
- **IoT**: 센서 데이터 수집 및 모니터링

## 개발 환경 설정

### 1. 저장소 클론

```bash
git clone <repository-url>
cd smartfarm
```

### 2. 환경 변수 설정

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 본인의 환경에 맞게 수정
# 특히 DB_PASSWORD, DB_NAME 등을 본인 환경에 맞게 변경
```

### 3. 의존성 설치

```bash
# Python 패키지 설치
pip install -r requirements.txt

# Node.js 패키지 설치
cd front && npm install
```

## 개발 서버 실행

### 백엔드 서버 실행

```bash
python app.py
```

### 프론트엔드 서버 실행 (새 터미널에서)

```bash
cd front
npm start
```

### 4. 데이터베이스 설정

MySQL에서 `smartfarm` 데이터베이스를 생성하고 필요한 테이블들을 설정해주세요.

## 환경 변수 설명

| 변수명           | 설명                  | 기본값               |
| ---------------- | --------------------- | -------------------- |
| DB_HOST          | 데이터베이스 호스트   | localhost            |
| DB_USER          | 데이터베이스 사용자명 | root                 |
| DB_PASSWORD      | 데이터베이스 비밀번호 | 1234                 |
| DB_NAME          | 데이터베이스 이름     | smartfarm            |
| DB_PORT          | 데이터베이스 포트     | 3306                 |
| FLASK_SECRET_KEY | Flask 세션 보안 키    | your_secret_key_here |
| FLASK_DEBUG      | Flask 디버그 모드     | True                 |
| FLASK_PORT       | Flask 서버 포트       | 5001                 |

## 주요 기능

- 🏡 **농장 관리**: 농장 등록, 수정, 삭제
- 🏠 **온실 모니터링**: IoT 센서를 통한 실시간 환경 데이터 수집
- 🐛 **병해충 탐지**: AI 기반 이미지 분석을 통한 자동 탐지
- 💬 **커뮤니티**: 농업인들 간의 정보 공유 게시판
- 📊 **데이터 시각화**: 농장 데이터 차트 및 통계
- 🛒 **상품 거래**: 농산물 판매 및 구매
- 🔔 **알림 시스템**: 실시간 상황 알림

## 개발 참고사항

- 백엔드 서버: http://localhost:5001
- 프론트엔드 서버: http://localhost:3000
- `.env` 파일은 절대 커밋하지 마세요
- 새로운 환경 변수 추가 시 `.env.example`도 함께 업데이트해주세요
