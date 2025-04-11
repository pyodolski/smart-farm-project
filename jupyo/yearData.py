# 연간 시세 그래프 html 포함
from flask import Flask, render_template_string
import matplotlib.pyplot as plt
import requests
import xml.etree.ElementTree as ET
import base64
from io import BytesIO

app = Flask(__name__)

def fetch_price_trend(productno, title):
    years = []
    max_values = []
    min_values = []

    for year in range(2016, 2026):
        p_regday = f'{year}-01-01'
        params = {
            'action': 'recentlyPriceTrendList',
            'p_productno': productno,
            'p_regday': p_regday,
            'p_cert_key': '2d4f611d-7307-4e9c-a61a-441d707dc833',
            'p_cert_id': '5428',
            'p_returntype': 'xml',
        }

        response = requests.get('http://www.kamis.or.kr/service/price/xml.do', params=params)

        if response.status_code == 200:
            try:
                root = ET.fromstring(response.text)
                prices = root.findall('.//price/item')
                for price in prices:
                    year_in_data = price.findtext('yyyy')
                    if year_in_data == str(year):
                        mx = price.findtext('mx', default='0')
                        mn = price.findtext('mn', default='0')
                        years.append(int(year))
                        max_values.append(int(mx))
                        min_values.append(int(mn))
            except:
                continue

    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(years, max_values, color='red', marker='o', label='Max Price')
    ax.plot(years, min_values, color='blue', marker='o', label='Min Price')
    ax.set_title(title)
    ax.set_xlabel('Year')
    ax.set_ylabel('Price')
    ax.set_xticks(years)
    ax.grid(True)
    ax.legend()
    plt.tight_layout()

    # 그래프를 base64 이미지로 변환
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return image_base64

@app.route('/')
def index():
    tomato_graph = fetch_price_trend('321', '토마토 연간 시세 변동 그래프 (1kg)')
    strawberry_graph = fetch_price_trend('323', '딸기 연간 시세 변동 그래프 (100g)')

    html_content = """
    <!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>농산물 연간 시세 통계</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            display: flex;
        }
        .sidebar {
            width: 250px;
            background-color: #f4f4f4;
            height: 100vh;
            padding: 20px;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
        }
        .sidebar h2 {
            font-size: 18px;
            color: #333;
        }
        .sidebar ul {
            list-style: none;
            padding: 0;
        }
        .sidebar ul li {
            margin: 10px 0;
        }
        .sidebar ul li a {
            text-decoration: none;
            color: #4CAF50;
            font-weight: bold;
            cursor: pointer;
        }
        .content {
            flex: 1;
            padding: 20px;
            text-align: center;
        }
        .graph {
            display: none;
        }
        .graph.active {
            display: block;
        }
        img {
            width: 80%;
            max-width: 800px;
            margin-top: 20px;
            border: 1px solid #ccc;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>그래프 선택</h2>
        <ul>
            <li><a onclick="showGraph('tomato')">토마토 연간 시세 변동 그래프(최근 10년)</a></li>
            <li><a onclick="showGraph('strawberry')">딸기 연간 시세 변동 그래프(최근 10년)</a></li>
        </ul>
    </div>
    <div class="content">
        <div id="tomato" class="graph active">
            <h2>토마토 연간 시세 변동 그래프 (1kg)</h2>
            <img src="data:image/png;base64,{{ tomato }}">
        </div>
        <div id="strawberry" class="graph">
            <h2>딸기 연간 시세 변동 그래프 (100g)</h2>
            <img src="data:image/png;base64,{{ strawberry }}">
        </div>
    </div>

    <script>
        function showGraph(id) {
            document.querySelectorAll('.graph').forEach(function(el) {
                el.classList.remove('active');
            });
            document.getElementById(id).classList.add('active');
        }
    </script>
</body>
</html>

    """
    return render_template_string(html_content, tomato=tomato_graph, strawberry=strawberry_graph)

app.run(debug=True)
