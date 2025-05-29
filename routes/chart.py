import requests
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, jsonify, Blueprint
import plotly.graph_objs as go
import pandas as pd
from flask_cors import CORS
# 연간 시세 :  https://www.kamis.or.kr/customer/reference/openapi_list.do?action=detail&boardno=9
# 월간 도소매 사새 :

p_cert_key = '2d4f611d-7307-4e9c-a61a-441d707dc833'
p_cert_id = '5428'
url = 'https://www.kamis.or.kr/service/price/xml.do'
YEARS = list(range(2016, 2026))

chart_bp = Blueprint('chart', __name__)
CORS(chart_bp, resources={r"/*": {"origins": [
    "http://localhost:3001",
    "https://mature-grub-climbing.ngrok-free.app"
]}}, supports_credentials=True)

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
    trace_max = go.Scatter(
        x=years,
        y=max_values,
        mode='lines+markers',
        name='최고가',
        marker=dict(color='red'),
        hovertemplate='연도: %{x}<br>최고가: %{y:,}원'
    )
    trace_min = go.Scatter(
        x=years,
        y=min_values,
        mode='lines+markers',
        name='최저가',
        marker=dict(color='blue'),
        hovertemplate='연도: %{x}<br>최저가: %{y:,}원'
    )
    layout = go.Layout(
        title=title,
        xaxis=dict(title='연도', dtick=1),
        yaxis=dict(title=f'가격({unit})'),
        legend=dict(x=0.01, y=0.99),
        hovermode='closest',
        margin=dict(l=60, r=20, t=60, b=60)
    )
    fig = go.Figure(data=[trace_max, trace_min], layout=layout)
    return fig.to_json()

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
    yearavg = None
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
                yearavg_text = item.find('yearavg').text if item.find('yearavg') is not None else None
                if yearavg_text and yearavg_text != '-':
                    yearavg = float(yearavg_text.replace(',', ''))
                break
    valid_months = [v for v in months if v > 0]
    if valid_months:
        yearavg = sum(valid_months) / len(valid_months)
    else:
        yearavg = 0
    df = pd.DataFrame({'Month': range(1, 13), 'Price': months})
    df['MoM_Change'] = df['Price'].pct_change().replace([float('inf'), float('-inf')], 0) * 100
    df['MoM_Change'] = df['MoM_Change'].fillna(0).round(2)
    if yearavg > 0:
        df['DiffFromAvg'] = ((df['Price'] - yearavg) / yearavg * 100).round(2)
    else:
        df['DiffFromAvg'] = 0
    hovertexts = []
    for i, row in df.iterrows():
        m = int(row['Month'])
        price = int(row['Price'])
        mom = row['MoM_Change']
        diff = row['DiffFromAvg']
        if price == 0:
            hovertexts.append(f"{m}월: 데이터 없음")
        else:
            hovertexts.append(
                f"{m}월: {price:,}원<br>"
                f"전월 대비: {mom:+.2f}%<br>"
                f"연평균 대비: {diff:+.2f}%"
            )
    x = [f"{m}월" for m in range(1, 13)]
    trace = go.Scatter(
        x=x,
        y=months,
        mode='lines+markers',
        marker=dict(size=10, color='royalblue'),
        line=dict(width=2),
        hovertext=hovertexts,
        hoverinfo='text',
        name='소매가' if is_retail else '도매가'
    )
    layout = dict(
        title=f'{year}년 {title}',
        xaxis=dict(title='월'),
        yaxis=dict(title='가격(원)'),
        hovermode='closest'
    )
    fig = go.Figure(data=[trace], layout=layout)
    return fig.to_json()

@chart_bp.route('/api/statistics', methods=['GET'])
def statistics_api():
    graph = request.args.get('graph', 'tomato_annual')
    tomato_selected_year = int(request.args.get('tomato_year', YEARS[-1]))
    strawberry_selected_year = int(request.args.get('strawberry_year', YEARS[-1]))
    tomato_selected_year_retail = int(request.args.get('tomato_year_retail', YEARS[-1]))
    strawberry_selected_year_retail = int(request.args.get('strawberry_year_retail', YEARS[-1]))

    plot_json = None
    extra = {}
    if graph == 'tomato_annual':
        plot_json = fetch_annual_trend('321', '토마토 연간 시세 변동 그래프 (1kg)', '원')
        graph_title = "토마토 연간 시세 변동 그래프 (1kg)"
    elif graph == 'strawberry_annual':
        plot_json = fetch_annual_trend('323', '딸기 연간 시세 변동 그래프 (100g)', '원')
        graph_title = "딸기 연간 시세 변동 그래프 (100g)"
    elif graph == 'tomato_monthly_wholesale':
        plot_json = fetch_monthly_price(tomato_selected_year, 225, "토마토 월간 도매가(5kg 상자 기준)", is_retail=False)
        graph_title = f"{tomato_selected_year}년 토마토 월간 도매가 변동"
        extra['year_select'] = {
            'name': 'tomato_year',
            'selected': tomato_selected_year,
            'other': strawberry_selected_year,
            'label': '토마토 월 선택 연도:'
        }
    elif graph == 'strawberry_monthly_wholesale':
        plot_json = fetch_monthly_price(strawberry_selected_year, 226, "딸기 월간 도매가(500g 상자 기준)", is_retail=False)
        graph_title = f"{strawberry_selected_year}년 딸기 월간 도매가 변동"
        extra['year_select'] = {
            'name': 'strawberry_year',
            'selected': strawberry_selected_year,
            'other': tomato_selected_year,
            'label': '딸기 월 선택 연도:'
        }
    elif graph == 'tomato_monthly_retail':
        plot_json = fetch_monthly_price(tomato_selected_year_retail, 225, "토마토 월간 소매가(1kg)", is_retail=True)
        graph_title = f"{tomato_selected_year_retail}년 토마토 월간 소매가 변동"
        extra['year_select'] = {
            'name': 'tomato_year_retail',
            'selected': tomato_selected_year_retail,
            'other': strawberry_selected_year_retail,
            'label': '토마토 월 선택 연도:'
        }
    elif graph == 'strawberry_monthly_retail':
        plot_json = fetch_monthly_price(strawberry_selected_year_retail, 226, "딸기 월간 소매가(100g)", is_retail=True)
        graph_title = f"{strawberry_selected_year_retail}년 딸기 월간 소매가 변동"
        extra['year_select'] = {
            'name': 'strawberry_year_retail',
            'selected': strawberry_selected_year_retail,
            'other': tomato_selected_year_retail,
            'label': '딸기 월 선택 연도:'
        }
    else:
        plot_json = fetch_annual_trend('321', '토마토 연간 시세 변동 그래프 (1kg)', '원')
        graph_title = "토마토 연간 시세 변동 그래프 (1kg)"

    return jsonify({
        'plot_json': plot_json,
        'graph_title': graph_title
    })

