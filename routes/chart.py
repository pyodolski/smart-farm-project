import requests
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, jsonify, Blueprint
import plotly.graph_objs as go
import pandas as pd
from flask_cors import CORS
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
import ssl

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SSL 컨텍스트 설정 - 레거시 서버 지원
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.load_default_certs()
        context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# 세션 생성 및 SSL 어댑터 적용
session = requests.Session()
session.mount('https://', SSLAdapter())

# 연간 시세 :  https://www.kamis.or.kr/customer/reference/openapi_list.do?action=detail&boardno=9
# 월간 도소매 사새 :

p_cert_key = '2d4f611d-7307-4e9c-a61a-441d707dc833'
p_cert_id = '5428'
url = 'https://www.kamis.or.kr/service/price/xml.do'
YEARS = list(range(2016, 2026))

# API 호출 실패 시 더미 데이터 사용 여부
USE_DUMMY_DATA_ON_ERROR = True

chart_bp = Blueprint('chart', __name__)

def generate_dummy_annual_data(productno, title, unit):
    """API 호출 실패 시 더미 데이터 생성"""
    import random
    years = list(YEARS)
    # 토마토와 딸기에 따라 다른 가격 범위 설정
    if productno == '321':  # 토마토
        base_max = 3000
        base_min = 2000
    else:  # 딸기
        base_max = 15000
        base_min = 10000
    
    max_values = [base_max + random.randint(-500, 500) for _ in years]
    min_values = [base_min + random.randint(-500, 500) for _ in years]
    
    trace_max = go.Scatter(
        x=years,
        y=max_values,
        mode='lines+markers',
        name='최고가',
        line=dict(color='red', width=2),
        marker=dict(size=8)
    )
    trace_min = go.Scatter(
        x=years,
        y=min_values,
        mode='lines+markers',
        name='최저가',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    )
    layout = go.Layout(
        title=f'{title} (더미 데이터)',
        xaxis=dict(title='연도'),
        yaxis=dict(title=f'가격({unit})'),
        legend=dict(x=0.01, y=0.99),
        hovermode='closest',
        margin=dict(l=60, r=20, t=60, b=60)
    )
    fig = go.Figure(data=[trace_max, trace_min], layout=layout)
    return fig.to_json()

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
        try:
            # SSL 어댑터를 사용한 세션으로 요청 (verify 파라미터 제거)
            response = session.get(url, params=params, timeout=10)
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
        except Exception as e:
            print(f"❌ API 호출 실패 ({year}): {e}")
            continue
    
    # 데이터가 없으면 더미 데이터 사용
    if not years and USE_DUMMY_DATA_ON_ERROR:
        print(f"⚠️ API 데이터 없음. 더미 데이터 사용: {title}")
        return generate_dummy_annual_data(productno, title, unit)
    
    trace_max = go.Scatter(
        x=years,
        y=max_values,
        mode='lines+markers',
        name='최고가',
        line=dict(color='#e74c3c', width=3, shape='spline'),
        marker=dict(color='#e74c3c', size=10, line=dict(color='white', width=2)),
        hovertemplate='<b>연도: %{x}</b><br>최고가: %{y:,}원<extra></extra>',
        fill='tonexty',
        fillcolor='rgba(231, 76, 60, 0.1)'
    )
    trace_min = go.Scatter(
        x=years,
        y=min_values,
        mode='lines+markers',
        name='최저가',
        line=dict(color='#3498db', width=3, shape='spline'),
        marker=dict(color='#3498db', size=10, line=dict(color='white', width=2)),
        hovertemplate='<b>연도: %{x}</b><br>최저가: %{y:,}원<extra></extra>'
    )
    layout = go.Layout(
        title=dict(
            text=title,
            font=dict(size=24, color='#2c3e50', family='Arial, sans-serif'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='연도',
            dtick=1,
            gridcolor='#ecf0f1',
            showline=True,
            linecolor='#bdc3c7',
            linewidth=2
        ),
        yaxis=dict(
            title=f'가격 ({unit})',
            gridcolor='#ecf0f1',
            showline=True,
            linecolor='#bdc3c7',
            linewidth=2,
            tickformat=','
        ),
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#bdc3c7',
            borderwidth=1,
            font=dict(size=12)
        ),
        hovermode='x unified',
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        margin=dict(l=80, r=40, t=80, b=60)
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
    
    try:
        # SSL 어댑터를 사용한 세션으로 요청 (verify 파라미터 제거)
        response = session.get(url, params=params, timeout=10)
        root = ET.fromstring(response.content)
    except Exception as e:
        print(f"❌ 월간 가격 API 호출 실패: {e}")
        # 오류 발생 시 빈 데이터 반환
        months = [0] * 12
        root = None
    
    if root is not None:
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
    # pandas 대신 기본 Python 사용
    months_data = []
    for i, price in enumerate(months):
        months_data.append({
            'Month': i + 1,
            'Price': price
        })
    
    # MoM_Change 계산 (pandas 대신)
    mom_changes = []
    for i, price in enumerate(months):
        if i == 0:
            mom_changes.append(0)
        else:
            prev_price = months[i-1]
            if prev_price > 0:
                mom_change = ((price - prev_price) / prev_price) * 100
            else:
                mom_change = 0
            mom_changes.append(round(mom_change, 2))
    
    # DiffFromAvg 계산
    valid_months = [v for v in months if v > 0]
    if valid_months:
        yearavg = sum(valid_months) / len(valid_months)
    else:
        yearavg = 0
    
    diff_from_avg = []
    for price in months:
        if yearavg > 0:
            diff = ((price - yearavg) / yearavg) * 100
        else:
            diff = 0
        diff_from_avg.append(round(diff, 2))
    
    # hovertexts 생성
    hovertexts = []
    for i, price in enumerate(months):
        m = i + 1
        mom = mom_changes[i]
        diff = diff_from_avg[i]
        if price == 0:
            hovertexts.append(f"{m}월: 데이터 없음")
        else:
            hovertexts.append(
                f"{m}월: {price:,}원<br>"
                f"전월 대비: {mom:+.2f}%<br>"
                f"연평균 대비: {diff:+.2f}%"
            )
    
    x = [f"{m}월" for m in range(1, 13)]
    
    # 색상 그라데이션 생성 (가격에 따라)
    colors = []
    max_price = max(months) if months else 1
    for price in months:
        if price == 0:
            colors.append('#95a5a6')
        else:
            intensity = price / max_price
            colors.append(f'rgba(76, 175, 80, {0.3 + intensity * 0.7})')
    
    trace = go.Bar(
        x=x,
        y=months,
        marker=dict(
            color=colors,
            line=dict(color='#4CAF50', width=2)
        ),
        hovertext=hovertexts,
        hoverinfo='text',
        name='소매가' if is_retail else '도매가',
        text=[f'{p:,}원' if p > 0 else '-' for p in months],
        textposition='outside',
        textfont=dict(size=11, color='#2c3e50')
    )
    
    # 연평균 라인 추가
    if yearavg > 0:
        trace_avg = go.Scatter(
            x=x,
            y=[yearavg] * 12,
            mode='lines',
            name='연평균',
            line=dict(color='#e74c3c', width=2, dash='dash'),
            hovertemplate=f'<b>연평균</b><br>{yearavg:,.0f}원<extra></extra>'
        )
        data = [trace, trace_avg]
    else:
        data = [trace]
    
    layout = go.Layout(
        title=dict(
            text=f'{year}년 {title}',
            font=dict(size=24, color='#2c3e50', family='Arial, sans-serif'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='월',
            gridcolor='#ecf0f1',
            showline=True,
            linecolor='#bdc3c7',
            linewidth=2
        ),
        yaxis=dict(
            title='가격 (원)',
            gridcolor='#ecf0f1',
            showline=True,
            linecolor='#bdc3c7',
            linewidth=2,
            tickformat=','
        ),
        hovermode='x unified',
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        margin=dict(l=80, r=40, t=80, b=60),
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#bdc3c7',
            borderwidth=1,
            font=dict(size=12)
        )
    )
    fig = go.Figure(data=data, layout=layout)
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

@chart_bp.route('/api/charts', methods=['GET'])
def get_charts():
    # 임시로 기본 응답만 반환
    return jsonify({'message': 'Charts temporarily disabled'})

