import requests
import xml.etree.ElementTree as ET

# 인증 정보
p_cert_key = 'test'  # 인증키
p_cert_id = 'test'  # 요청자 ID

# 요청 URL
url = 'http://www.kamis.or.kr/service/price/xml.do'

# 연도별로 데이터 요청
for year in range(2016, 2026):  # 2016년부터 2025년까지 반복
    p_regday = f'{year}-01-01'  # 연도별로 1월 1일로 설정

    # 요청 파라미터
    params = {
        'action': 'recentlyPriceTrendList',
        'p_productno': '321',  # 품목 코드
        'p_regday': p_regday,  # 검색일자 (1월 1일로 설정)
        'p_cert_key': p_cert_key,  # 인증키
        'p_cert_id': p_cert_id,  # 요청자 아이디
        'p_returntype': 'xml',  # 반환 데이터 형식 (xml)
    }

    # API 요청
    response = requests.get(url, params=params)

    if response.status_code == 200:
        try:
            # XML 파싱
            tree = ET.ElementTree(ET.fromstring(response.text))
            root = tree.getroot()

            # 응답 데이터에서 필요한 부분 추출 (예시: price, item 등)
            prices = root.findall('.//price/item')  # 'price' 태그 내의 'item' 찾기

            for price in prices:
                # 'yyyy' 태그 값 추출
                year_in_data = price.find('yyyy').text if price.find('yyyy') is not None else 'N/A'

                # "평년"은 건너뛰고, 요청된 연도와 일치하는 연도만 출력
                if year_in_data == str(year):
                    # 연도별 데이터 출력

                    mx = price.find('mx').text if price.find('mx') is not None else 'N/A'
                    mn = price.find('mn').text if price.find('mn') is not None else 'N/A'

                    # 결과 출력
                    print(f"Year: {year_in_data}, Max: {mx}, Min: {mn}")
        except Exception as e:
            print(f"XML 파싱 오류: {e}")
    else:
        print(f"Error: {response.status_code}")
