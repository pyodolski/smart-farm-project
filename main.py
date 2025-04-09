import requests
import xml.etree.ElementTree as ET
import json

# 인증 정보
p_cert_key = '2d4f611d-7307-4e9c-a61a-441d707dc833'  # 인증키
p_cert_id = '5428'  # 요청자 ID

# 요청 URL
url = 'https://www.kamis.or.kr/service/price/xml.do'

# 요청 파라미터 (날짜 없이)
params = {
    'action': 'dailySalesList',  # 액션
    'p_cert_key': p_cert_key,  # 인증키
    'p_cert_id': p_cert_id,  # 요청자 아이디
    'p_returntype': 'xml',  # 반환 데이터 형식 (xml)
}

# API 요청
response = requests.get(url, params=params)

if response.status_code == 200:
    try:
        # 반환된 XML 응답을 출력하여 확인
        print(response.text)  # 응답 XML을 출력해 봅니다.

        # XML 응답을 파싱
        tree = ET.ElementTree(ET.fromstring(response.text))
        root = tree.getroot()

        # 딸기 품목만 필터링하여 JSON 형태로 변환
        result = []

        # 'item' 데이터를 순회
        items = root.findall(".//item")
        for item in items:
            product_name = item.find('productName').text if item.find('productName') is not None else '정보 없음'
            if "딸기" in product_name:  # 딸기 품목만 필터링
                item_data = {
                    '품목 코드': item.find('productno').text if item.find('productno') is not None else '정보 없음',
                    '품목 이름': product_name,
                    '단위': item.find('unit').text if item.find('unit') is not None else '정보 없음',
                    '당일 가격': item.find('dpr1').text if item.find('dpr1') is not None else '정보 없음',
                    '1일 전 가격': item.find('dpr2').text if item.find('dpr2') is not None else '정보 없음',
                    '1개월 전 가격': item.find('dpr3').text if item.find('dpr3') is not None else '정보 없음',
                    '1년 전 가격': item.find('dpr4').text if item.find('dpr4') is not None else '정보 없음'
                }
                result.append(item_data)

        # JSON 형식으로 출력
        print(json.dumps(result, ensure_ascii=False, indent=4))

    except Exception as e:
        print(f"XML 파싱 오류: {e}")
else:
    print(f"Error: {response.status_code}")
