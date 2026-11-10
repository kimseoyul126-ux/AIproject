import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import os
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor

# Streamlit 페이지 설정
st.set_page_config(page_title="기온 예측 및 알고리즘 비교 대시보드", layout="wide")

# -------------------------------------------------------------
# 🛠️ 폰트 깨짐 방지 및 나눔폰트 강제 적용 설정
# -------------------------------------------------------------
def set_korean_font():
    system_name = platform.system()
    
    # 리눅스(스트림릿 클라우드) 환경인 경우 나눔고딕 명시적 지정
    if system_name == 'Linux':
        font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
        if os.path.exists(font_path):
            font_name = fm.FontProperties(fname=font_path).get_name()
            plt.rc('font', family=font_name)
        else:
            plt.rcParams['font.family'] = 'NanumGothic'
    elif system_name == 'Windows':
        plt.rcParams['font.family'] = 'Malgun Gothic'
    elif system_name == 'Darwin':
        plt.rcParams['font.family'] = 'AppleGothic'
    else:
        plt.rcParams['font.family'] = 'sans-serif'
    
    # 마이너스 기호 깨짐 방지
    plt.rcParams['axes.unicode_minus'] = False
    
    # 맷플롯립 폰트 캐시 리셋
    plt.font_manager._rebuild = lambda: None

set_korean_font()

st.title("🌡️ 기온 예측 및 머신러닝 알고리즘 비교 대시보드")
st.write("1907년부터 현재까지의 기온 데이터를 기반으로 특정 개월의 과거 추이를 분석하고, 미래 연도의 평균기온을 다양한 머신러닝 모델로 예측합니다.")

# 데이터 불러오기 함수 (캐싱 적용)
@st.cache_data
def load_data():
    df = pd.read_csv("temperature.csv", encoding="cp949")
    df['parsed_date'] = pd.to_datetime(df['일시'], format='%b-%y')
    df['Year'] = df['parsed_date'].dt.year
    df['Month'] = df['parsed_date'].dt.month
    df.loc[df['Year'] > 2026, 'Year'] -= 100
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 파일을 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 사이드바 설정
st.sidebar.header("⚙️ 예측 및 분석 설정")

# 1. 개월 선택
month_names = {
    1: "1월", 2: "2월", 3: "3월", 4: "4월", 
    5: "5월", 6: "6월", 7: "7월", 8: "8월", 
    9: "9월", 10: "10월", 11: "11월", 12: "12월"
}
selected_month = st.sidebar.selectbox(
    "조회 및 예측할 개월 선택", 
    options=list(month_names.keys()), 
    format_func=lambda x: month_names[x]
)

# 2. 미래 예측 연도 입력
max_year = int(df['Year'].max())
target_future_year = st.sidebar.number_input(
    "미래 예측 연도 입력", 
    min_value=max_year + 1, 
    max_value=max_year + 50, 
    value=max_year + 10, 
    step=1
)

# 데이터 필터링 및 결측치 제거
month_df = df[df['Month'] == selected_month].dropna(subset=['평균기온(℃)']).sort_values('Year')

# -------------------------------------------------------------
# 과거 추이 및 3가지 알고리즘 미래 예측 그래프
# -------------------------------------------------------------
st.subheader(f"📈 [{month_names[selected_month]}] 연도별 평균기온 추이 및 미래 예측")

if month_df.empty:
    st.warning("선택한 개월에 해당하는 데이터가 없습니다.")
else:
    X = month_df[['Year']].values
    y = month_df['평균기온(℃)'].values
    
    models = {
        "Linear Regression (선형 회귀)": LinearRegression(),
        "Ridge Regression (릿지 회귀)": Ridge(alpha=1.0),
        "Random Forest (랜덤 포레스트)": RandomForestRegressor(n_estimators=100, random_state=42)
    }
    
    future_years = np.arange(max_year + 1, target_future_year + 1).reshape(-1, 1)
    predictions = {}
    
    for name, model in models.items():
        model.fit(X, y)
        pred = model.predict(future_years)
        predictions[name] = pred

    # 시각화
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(month_df['Year'], y, marker='o', color='#2E8B57', linewidth=2, label=f'실제 평균기온 (1927~{max_year})')
    
    colors =
