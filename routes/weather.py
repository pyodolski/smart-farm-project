from flask import Blueprint, jsonify, request
from collections import defaultdict
from datetime import datetime, timedelta
import requests

weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')
API_KEY = '2c583720d6f7b0b19b9164ed79e28471'
cities = ['서울특별시',
    '부산광역시',
    '대구광역시',
    '인천광역시',
    '광주광역시',
    '대전광역시',
    '울산광역시',
    # 특별자치시
    '세종특별자치시',
    # 도
    '경기도',
    '강원특별자치도',
    '충청북도',
    '충청남도',
    '전라북도',
    '전라남도',
    '경상북도',
    '경상남도',
    # 특별자치도
    '제주특별자치도' ]

def normalize_kor_city(kor_name: str) -> str:
    mapping = {
        '서울': '서울특별시', '부산': '부산광역시', '대구': '대구광역시',
        '인천': '인천광역시', '광주': '광주광역시', '대전': '대전광역시',
        '울산': '울산광역시', '세종': '세종특별자치시',
        '경기': '경기도', '강원': '강원특별자치도', '충북': '충청북도',
        '충남': '충청남도', '전북': '전라북도', '전남': '전라남도',
        '경북': '경상북도', '경남': '경상남도', '제주': '제주특별자치도',
    }

    if kor_name in mapping.values():
        return kor_name

    if kor_name in mapping:
        return mapping[kor_name]

    key = kor_name.rstrip('도시')
    return mapping.get(key, kor_name)


def city_kor_to_eng(kor_name):
    mapping = {
        # 특별시·광역시
        '서울특별시':   'Seoul',
        '부산광역시':   'Busan',
        '대구광역시':   'Daegu',
        '인천광역시':   'Incheon',
        '광주광역시':   'Gwangju',
        '대전광역시':   'Daejeon',
        '울산광역시':   'Ulsan',
        # 특별자치시
        '세종특별자치시': 'Sejong',
        # 도
        '경기도':       'Gyeonggi-do',
        '강원특별자치도': 'Gangwon-do',
        '충청북도':     'Chungcheongbuk-do',
        '충청남도':     'Chungcheongnam-do',
        '전라북도':     'Jeollabuk-do',
        '전라남도':     'Jeollanam-do',
        '경상북도':     'Gyeongsangbuk-do',
        '경상남도':     'Gyeongsangnam-do',
        # 특별자치도
        '제주특별자치도': 'Jeju-do',
    }
    return mapping.get(kor_name,'Seoul')

#지금 해당 도시의 기온 날씨를 가져오는 함수
def fetch_weather(kor_city: str) -> dict:
    kor_city_full = normalize_kor_city(kor_city)
    city_eng = city_kor_to_eng(kor_city_full)
    url = (f"http://api.openweathermap.org/data/2.5/weather"
           f"?q={city_eng}&appid={API_KEY}&units=metric&lang=kr")
    print(f"[DEBUG] OpenWeatherMap 요청 URL: {url}")
    try:
        res = requests.get(url); res.raise_for_status()
        d = res.json()
        return {'city':kor_city,
                'temperature':d['main']['temp'],
                'description':d['weather'][0]['description']}
    except:
        return {'error':'날씨 정보를 가져올 수 없습니다.'}

#5일치 3시간 간격 예보를 가져오는 함수
def fetch_forecast(kor_city: str) -> list:
    city_eng = city_kor_to_eng(kor_city)
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_eng}&appid={API_KEY}&units=metric&lang=kr"
    try:
        res = requests.get(url); res.raise_for_status()
        data = res.json()
        out = []
        for it in data['list']:
            out.append({
                'dt_txt': it['dt_txt'],
                'temp':    it['main']['temp'],
                'description': it['weather'][0]['description']
            })
        return out
    except:
        return []

#3시간 단위 예보에서 내일과 모레 날짜만 골라 최고 최저 기온 계산
def fetch_two_day_minmax(kor_city: str) -> list:
    raw = fetch_forecast(kor_city)
    if not raw:
        return []
    today = datetime.utcnow() + timedelta(hours=9)
    d1 = (today + timedelta(days=1)).date().isoformat()
    d2 = (today + timedelta(days=2)).date().isoformat()

    temps = defaultdict(list)
    descs = defaultdict(list)
    for it in raw:
        date = it['dt_txt'].split(' ')[0]
        if date in (d1, d2):
            temps[date].append(it['temp'])
            descs[date].append(it['description'])

    summary = []
    for date in (d1, d2):
        tlist = temps.get(date, [])
        if tlist:
            summary.append({
                'date':        date,
                'min_temp':    round(min(tlist),1),
                'max_temp':    round(max(tlist),1),
                'description': max(set(descs[date]), key=descs[date].count)
            })
    return summary

@weather_bp.route('', methods=['GET'])
def get_weather():
    city = request.args.get('city', '서울특별시')
    weather = fetch_weather(city)
    two_day = fetch_two_day_minmax(city)
    return jsonify({
        'weather': weather,
        'two_day': two_day
    })