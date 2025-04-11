import requests
import xml.etree.ElementTree as ET

# 인증 정보
p_cert_key = '2d4f611d-7307-4e9c-a61a-441d707dc833'
p_cert_id = '5428'
url = 'https://www.kamis.or.kr/service/price/xml.do'

params_321 = {
    'action': 'dailySalesList',
    'p_productno': '321',           # 토마토 품목 코드
    'p_regday': '2025-04-09',
    'p_cert_key': p_cert_key,
    'p_cert_id': p_cert_id,
    'p_returntype': 'xml',
}

# API 요청 및 값 출력
response = requests.get(url, params=params_321)

if response.status_code == 200:
    try:
        root = ET.fromstring(response.text)
        for item in root.findall(".//item"):
            year = item.findtext('yyyy')
            max_val = item.findtext('max')
            min_val = item.findtext('min')

            if year in ["2021", "2022", "2023", "2024", "2025"]:
                print(f"Year: {year}, Max: {max_val}, Min: {min_val}")
    except Exception as e:
        print(f"XML 파싱 오류: {e}")
else:
    print(f"HTTP 오류: {response.status_code}")
