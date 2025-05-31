from flask import Blueprint, jsonify
import requests

crop_bp = Blueprint('crop', __name__, url_prefix='/api')

API_KEY = "20253105e956e7f172ff09e237ed92508153"
BASE_URL = "http://ncpms.rda.go.kr/npmsAPI/service"

def fetch_disease_data(crop_name):
    params = {
        "apiKey": API_KEY,
        "serviceCode": "SVC01",
        "serviceType": "AA003",
        "cropName": crop_name,
        "displayCount": 100
    }
    res = requests.get(BASE_URL, params=params)
    data = res.json()
    return data["service"]["list"] if "list" in data["service"] else []

#병해 세부 정보 (sickKey를 이용)
def fetch_disease_detail(sick_key):
    params = {
        "apiKey": API_KEY,
        "serviceCode": "SVC05", #세부 병해 정보 코드
        "sickKey": sick_key
    }
    res = requests.get(BASE_URL, params=params)
    try:
        data = res.json()
        print("API Response:", data)
        if "service" in data and data["service"]:
            return data["service"]
        else:
            print(f"Error: {sick_key}에 대한 세부 데이터가 없습니다.")
            return None
    except Exception as e:
        print(f"에러 발생: {e}")
        return None
    
#해충 정보
def fetch_insect_detail(insect_key):
    params = {
        "apiKey": API_KEY,
        "serviceCode": "SVC07",  #세부 병해 정보 코드
        "insectKey": insect_key
    }
    res = requests.get(BASE_URL, params=params)
    try:
        data = res.json()
        print("API Response:", data)
        if "service" in data and data["service"]:
            return data["service"]
        else:
            print(f"Error: {insect_key}에 대한 세부 데이터가 없습니다.")
            return None
    except Exception as e:
        print(f"에러 발생: {e}")
        return None

#천적 곤충 세부 정보
def fetch_predator_detail(insect_key):
    params = {
        "apiKey": API_KEY,
        "serviceCode": "SVC15",  # 천적 곤충 상세 정보 코드
        "insectKey": insect_key
    }
    res = requests.get(BASE_URL, params=params)
    try:
        data = res.json()
        print("API Response (Predator):", data)
        if "service" in data and data["service"]:
            return data["service"]
        else:
            print(f"Error: {insect_key}에 대한 천적 곤충 세부 데이터가 없습니다.")
            return None
    except Exception as e:
        print(f"에러 발생: {e}")
        return None

def get_crop_info(crop):
    #딸기
    if crop == "strawberry":
        return {
            "season": "2월 ~ 6월",
            "temp": "15~20",
            "humidity": "60~70",
        }
    #토마토
    elif crop == "tomato":
        return {
            "season": "3월 ~ 7월",
            "temp": "18~25",
            "humidity": "60~70",
        }
    #이후 추가 시 생성
    return {}

def fetch_predator_data(crop_name):
    params = {
        "apiKey": API_KEY,
        "serviceCode": "SVC14",
        "serviceType": "AA003", 
        "cropName": crop_name,
        "displayCount": 100
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return data.get("service", {}).get("list", [])

def fetch_insect_data(crop_name):
    params = {
        "apiKey": API_KEY,
        "serviceCode": "SVC03",
        "serviceType": "AA003",
        "cropName": crop_name,
        "displayCount": 100
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return data.get("service", {}).get("list", [])

## 리액트 프론트엔드용 API 경로 추가
@crop_bp.route('crops/detail/<crop>')
def api_crop_detail(crop):
    from routes.crop import get_crop_info, fetch_disease_data, fetch_insect_data, fetch_predator_data
    
    valid_crops = {
        "strawberry": "딸기",
        "tomato": "토마토"
    }

    if crop not in valid_crops:
        return jsonify({"error": "존재하지 않는 작물입니다."}), 404

    crop_name_kor = valid_crops[crop]
    info = get_crop_info(crop)
    items = fetch_disease_data(crop_name_kor)
    insects = fetch_insect_data(crop_name_kor)
    enemies = fetch_predator_data(crop_name_kor)

    return jsonify({
        "info": info,
        "items": items,
        "insects": insects,
        "enemies": enemies
    })

#병해 정보
@crop_bp.route('/diseases/<disease_id>')
def api_disease_detail(disease_id):
    disease = fetch_disease_detail(disease_id)
    if not disease:
        return jsonify({'error': '병해 정보를 찾을 수 없습니다.'}), 404
    return jsonify(disease)

#해충 정보
@crop_bp.route('/insects/<insect_id>')
def api_insect_detail(insect_id):
    insect = fetch_insect_detail(insect_id)
    if not insect:
        return jsonify({'error': '해충 정보를 찾을 수 없습니다.'}), 404
    return jsonify(insect)

#천적 곤충 정보
@crop_bp.route('/enemies/<enemy_id>')
def api_enemy_detail(enemy_id):
    enemy = fetch_predator_detail(enemy_id)
    if not enemy:
        return jsonify({'error': '천적 곤충 정보를 찾을 수 없습니다.'}), 404
    return jsonify(enemy)