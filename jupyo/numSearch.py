# 품목 코드 조회용 api
import requests
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from io import BytesIO
import json
from flask import Flask, render_template, send_file

# Flask 앱 초기화
app = Flask(__name__)

# 인증 정보
p_cert_key = '2d4f611d-7307-4e9c-a61a-441d707dc833'  # 인증키
p_cert_id = '5428'  # 요청자 ID

# 요청 URL
url = 'https://www.kamis.or.kr/service/price/xml.do'

# # 요청 파라미터 (2021년부터 2025년까지 데이터 요청)
# params_323 = {
#     'action': 'dailySalesList',  # 액션
#     'p_productno': '321',  # 품목 코드
#     'p_regday': '2025-04-09',  # 검색일자
#     'p_cert_key': p_cert_key,  # 인증키
#     'p_cert_id': p_cert_id,  # 요청자 아이디
#     'p_returntype': 'xml',  # 반환 데이터 형식 (xml)
# }
#
# # 그래프 생성 함수
# def create_graph():
#     # API 요청
#     response = requests.get(url, params=params_323)
#
#     if response.status_code == 200:
#         try:
#             # XML 파싱
#             tree = ET.ElementTree(ET.fromstring(response.text))
#             root = tree.getroot()
#
#             # 데이터 가공 (2021년부터 2025년까지의 연도별 max와 min 값 추출)
#             years = []
#             max_values = []
#             min_values = []
#
#             # 필요한 데이터만 필터링
#             items = root.findall(".//item")
#             for item in items:
#                 # 태그가 존재하는지 확인하고 값 추출
#                 year = item.find('yyyy')
#                 max_value = item.find('max')
#                 min_value = item.find('min')
#
#                 # None 체크 후 값 추출
#                 if year is not None and max_value is not None and min_value is not None:
#                     year_text = year.text
#                     max_text = max_value.text
#                     min_text = min_value.text
#
#                     if year_text in ["2021", "2022", "2023", "2024", "2025"]:
#                         years.append(year_text)
#                         max_values.append(int(max_text))
#                         min_values.append(int(min_text))
#
#             # 그래프 그리기
#             fig, ax = plt.subplots(figsize=(10, 6))
#             ax.plot(years, max_values, color='green', label='최댓값', marker='o')  # 빨간색 선 (max)
#             ax.plot(years, min_values, color='blue', label='최솟값', marker='o')  # 파란색 선 (min)
#
#             # 그래프 꾸미기
#             ax.set_title('연도별 최댓값과 최솟값')
#             ax.set_xlabel('연도')
#             ax.set_ylabel('가격')
#             ax.legend()
#             ax.grid(True)
#
#             # y축 범위 설정 (4000에서 9000까지)
#             ax.set_ylim(4000, 9000)
#
#             # y축 눈금 간격 설정 (1000 단위)
#             ax.set_yticks(range(4000, 9001, 1000))
#
#             # 이미지를 BytesIO에 저장
#             img_stream = BytesIO()
#             plt.savefig(img_stream, format='png')
#             img_stream.seek(0)  # 이미지를 처음으로 되돌림
#
#             # 이미지를 base64로 인코딩
#             img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')
#
#             return img_base64
#
#         except Exception as e:
#             return f"XML 파싱 오류: {e}"
#     else:
#         return f"Error: {response.status_code}"
#
# # 웹 페이지 라우팅
# @app.route('/')
# def index():
#     img_base64 = create_graph()
#     return render_template('index.html', graph=img_base64)
#
# if __name__ == '__main__':
#     app.run(debug=True)


# # API 요청

# 요청 파라미터 (날짜 없이)
params = {
    'action': 'dailySalesList',         # 액션
    'p_cert_key': p_cert_key,           # 인증키
    'p_cert_id': p_cert_id,             # 요청자 아이디
    'p_returntype': 'xml'               # 반환 데이터 형식
}

# API 요청
response = requests.get(url, params=params)

if response.status_code == 200:
    try:
        # XML 응답 파싱
        root = ET.fromstring(response.text)
        result = []

        # 'item' 태그 순회
        for item in root.findall(".//item"):
            product_name = item.findtext('productName', default='정보 없음')

            # "딸기" 포함 품목만 필터링
            if "딸기" in product_name:
                item_data = {
                    '품목 코드': item.findtext('productno', default='정보 없음'),
                    '품목 이름': product_name,
                    '단위': item.findtext('unit', default='정보 없음'),
                    '당일 가격': item.findtext('dpr1', default='정보 없음'),
                    '1일 전 가격': item.findtext('dpr2', default='정보 없음'),
                    '1개월 전 가격': item.findtext('dpr3', default='정보 없음'),
                    '1년 전 가격': item.findtext('dpr4', default='정보 없음')
                }
                result.append(item_data)

        # 결과 출력 (JSON 포맷)
        print(json.dumps(result, ensure_ascii=False, indent=4))

    except ET.ParseError as e:
        print(f"XML 파싱 오류: {e}")
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
else:
    print(f"HTTP 요청 실패: 상태 코드 {response.status_code}")