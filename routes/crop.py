from flask import Blueprint, render_template
import requests

crop_bp = Blueprint('crop', __name__, url_prefix='/crops')

API_KEY = "20253105e956e7f172ff09e237ed92508153"
BASE_URL = "http://ncpms.rda.go.kr/npmsAPI/service"

@crop_bp.route('/')
def select_crop():
    return render_template("crops.html")

def fetch_disease_data(crop_name):
    params = {
        "apiKey": API_KEY,
        "serviceCode": "SVC01",
        "serviceType": "AA003",
        "cropName": crop_name
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
        "cropName": crop_name
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return data.get("service", {}).get("list", [])

def fetch_insect_data(crop_name):
    params = {
        "apiKey": API_KEY,
        "serviceCode": "SVC03",
        "serviceType": "AA003",
        "cropName": crop_name
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return data.get("service", {}).get("list", [])

#작물 상세 페이지
@crop_bp.route('/detail/<crop>')
def show_crop_detail(crop):
    valid_crops = {
        "strawberry": "딸기",
        "tomato": "토마토"
    }

    if crop not in valid_crops:
        return "존재하지 않는 작물입니다.", 404

    crop_name_kor = valid_crops[crop]
    info = get_crop_info(crop)
    items = fetch_disease_data(crop_name_kor)

    insects = fetch_insect_data(crop_name_kor)
    enemies = fetch_predator_data(crop_name_kor)

    return render_template("crop_detail.html", crop_name=crop_name_kor, info=info, items=items, insects=insects, enemies=enemies)

#병해 페이지
@crop_bp.route('/disease/<disease_id>')
def show_disease_detail(disease_id):
    # 병해 세부 정보
    disease_details = fetch_disease_detail(disease_id)
    
    if not disease_details:
        return f"{disease_id}에 대한 세부 정보가 없습니다.", 404
    
    #오류
    disease = disease_details if disease_details else {}

    return render_template("disease_detail.html", disease=disease)

#해충 피해 페이지
@crop_bp.route('/insect/<insect_id>')
def show_insect_detail(insect_id):
    # 해충 세부 정보
    insect_details = fetch_insect_detail(insect_id)
    
    if not insect_details:
        return f"{insect_id}에 대한 세부 정보가 없습니다.", 404
    
    #오류
    insect = insect_details if insect_details else {}

    return render_template("insect_detail.html", insect=insect)

#천적 곤충 페이지
@crop_bp.route('/enemy/<enemy_id>')
def show_enemy_detail(enemy_id):
    #천적 곤충 정보
    predator_details = fetch_predator_detail(enemy_id)
    
    if not predator_details:
        return f"{enemy_id}에 대한 천적 곤충 세부 정보가 없습니다.", 404
    
    #오류
    predator = predator_details if predator_details else {}

    return render_template("predator_detail.html", predator=predator)

