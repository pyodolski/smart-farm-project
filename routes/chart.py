import matplotlib
matplotlib.use('Agg')  # 반드시 추가
import requests
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify, Blueprint
import pandas as pd
from flask_cors import CORS
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import base64
from io import BytesIO
import platform
import os

p_cert_key = '2d4f611d-7307-4e9c-a61a-441d707dc833'
p_cert_id = '5428'
url = 'https://www.kamis.or.kr/service/price/xml.do'
YEARS = list(range(2016, 2026))

chart_bp = Blueprint('chart', __name__)

# ✅ 운영체제별 한글 폰트 설정 후 반환
font_prop = None

def set_korean_font():
    global font_prop
    system = platform.system()
    font_candidates = []

    if system == 'Windows':
        font_candidates = ['C:/Windows/Fonts/malgun.ttf']
    elif system == 'Darwin':
        font_candidates = [
            '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
            '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
        ]
    else:
        font_candidates = [
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            '/usr/share/fonts/truetype/unfonts-core/UnDotum.ttf'
        ]

    for path in font_candidates:
        if os.path.exists(path):
            try:
                font_prop = fm.FontProperties(fname=path)
                font_name = font_prop.get_name()
                plt.rcParams['font.family'] = font_name
                plt.rcParams['axes.unicode_minus'] = False
                print(f"[INFO] 한글 폰트 설정 완료: {font_name}")
                return
            except Exception as e:
                print(f"[WARN] 폰트 설정 실패: {e}")

set_korean_font()
sns.set_theme(style="ticks")

def encode_plot_to_base64():
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode()}"

def fetch_annual_trend(productno, title, unit):
    years = []
    max_values = []
    min_values = []
    for year in YEARS:
        p_regday = f'{year}-01-01'
        params = {
            'action': 'recentlyPriceTrendList',
            'p_productno': productno,
            'p_regday': p_regday,
            'p_cert_key': p_cert_key,
            'p_cert_id': p_cert_id,
            'p_returntype': 'xml',
        }
        response = requests.get(url, params=params)
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
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=years, y=max_values, label='최고가', marker='o', color='#e74c3c', linewidth=2.5, markersize=8)
    sns.lineplot(x=years, y=min_values, label='최저가', marker='o', color='#3498db', linewidth=2.5, markersize=8)
    plt.title(title, fontsize=18, fontweight='bold', pad=20, fontproperties=font_prop)
    plt.xlabel('연도', fontsize=14, fontproperties=font_prop)
    plt.ylabel(f'가격 ({unit})', fontsize=14, fontproperties=font_prop)
    plt.xticks(fontsize=12, fontproperties=font_prop)
    plt.yticks(fontsize=12, fontproperties=font_prop)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(prop=font_prop)
    plt.tight_layout()
    return encode_plot_to_base64()

def fetch_monthly_price(year, itemcode, title, is_retail=False):
    params = {
        'action': 'monthlySalesList',
        'p_yyyy': str(year),
        'p_period': '12',
        'p_itemcategorycode': '200',
        'p_itemcode': str(itemcode),
        'p_kindcode': '00',
        'p_graderank': '1',
        'p_convert_kg_yn': 'N',
        'p_cert_key': p_cert_key,
        'p_cert_id': p_cert_id,
        'p_returntype': 'xml',
    }
    productclscode = '01' if is_retail else '02'
    months = []
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)
    for price in root.findall('.//price'):
        if price.find('productclscode') is not None and price.find('productclscode').text == productclscode:
            for item in price.findall('item'):
                for m in range(1, 13):
                    val = item.find(f'm{m}').text
                    if val == '-' or val is None:
                        months.append(0)
                    else:
                        months.append(int(val.replace(',', '')))
                break
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=list(range(1, 13)), y=months, marker='o', color='#2ecc71', linewidth=2.5, markersize=8)
    plt.title(f'{year}년 {title}', fontsize=18, fontweight='bold', pad=20, fontproperties=font_prop)
    plt.xlabel('월', fontsize=14, fontproperties=font_prop)
    plt.ylabel('가격 (원)', fontsize=14, fontproperties=font_prop)
    plt.xticks(fontsize=12, fontproperties=font_prop)
    plt.yticks(fontsize=12, fontproperties=font_prop)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(prop=font_prop)
    plt.tight_layout()
    return encode_plot_to_base64()

@chart_bp.route('/api/statistics', methods=['GET'])
def statistics_api():
    graph = request.args.get('graph', 'tomato_annual')
    tomato_selected_year = int(request.args.get('tomato_year', YEARS[-1]))
    strawberry_selected_year = int(request.args.get('strawberry_year', YEARS[-1]))
    tomato_selected_year_retail = int(request.args.get('tomato_year_retail', YEARS[-1]))
    strawberry_selected_year_retail = int(request.args.get('strawberry_year_retail', YEARS[-1]))

    plot_base64 = None
    if graph == 'tomato_annual':
        plot_base64 = fetch_annual_trend('321', '토마토 연간 시세 변동 그래프 (1kg)', '원')
        graph_title = "토마토 연간 시세 변동 그래프 (1kg)"
    elif graph == 'strawberry_annual':
        plot_base64 = fetch_annual_trend('323', '딸기 연간 시세 변동 그래프 (100g)', '원')
        graph_title = "딸기 연간 시세 변동 그래프 (100g)"
    elif graph == 'tomato_monthly_wholesale':
        plot_base64 = fetch_monthly_price(tomato_selected_year, 225, "토마토 월간 도매가(5kg 상자 기준)", is_retail=False)
        graph_title = f"{tomato_selected_year}년 토마토 월간 도매가 변동"
    elif graph == 'strawberry_monthly_wholesale':
        plot_base64 = fetch_monthly_price(strawberry_selected_year, 226, "딸기 월간 도매가(500g 상자 기준)", is_retail=False)
        graph_title = f"{strawberry_selected_year}년 딸기 월간 도매가 변동"
    elif graph == 'tomato_monthly_retail':
        plot_base64 = fetch_monthly_price(tomato_selected_year_retail, 225, "토마토 월간 소매가(1kg)", is_retail=True)
        graph_title = f"{tomato_selected_year_retail}년 토마토 월간 소매가 변동"
    elif graph == 'strawberry_monthly_retail':
        plot_base64 = fetch_monthly_price(strawberry_selected_year_retail, 226, "딸기 월간 소매가(100g)", is_retail=True)
        graph_title = f"{strawberry_selected_year_retail}년 딸기 월간 소매가 변동"
    else:
        plot_base64 = fetch_annual_trend('321', '토마토 연간 시세 변동 그래프 (1kg)', '원')
        graph_title = "토마토 연간 시세 변동 그래프 (1kg)"

    return jsonify({
        'plot_base64': plot_base64,
        'graph_title': graph_title
    })