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
    
    plt.rcParams['axes.unicode_minus'] = False

set_korean_font()

st.title("🌡️ 기온 예측 및 머신러닝 알고리즘 비교 대시보드")
st.write("1907년부터 현재까지의 기온 데이터를 기반으로 특정 개월의 과거 추이를 분석하고, 미래 연도의 평균기온을 다양한 머신러닝 모델로 예측합니다.")

# 데이터 불러오기 함수 (상위 폴더의 temperature_utf8.csv 경로 지정)
@st.cache_data
def load_data():
    # 현재 파일(pages/app.py) 기준 상위 폴더(..)에 있는 파일 경로 지정
    file_path = os.path.join(os.path.dirname(__file__), '..', 'temperature_utf8.csv')
    
    # 파일이 상위 폴더에 없거나 루트에 있는 경우 대비 예외 처리 경로 설정
    if not os.path.exists(file_path):
        file_path = 'temperature_utf8.csv'
        
    df = pd.read_csv(file_path, encoding="utf-8-sig")
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

# 개월 선택
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

# 미래 예측 연도 입력
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

# 과거 추이 및 3가지 알고리즘 미래 예측 그래프
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
    
    colors = {
        'Linear Regression (선형 회귀)': '#FF4500', 
        'Ridge Regression (릿지 회귀)': '#9932CC', 
        'Random Forest (랜덤 포레스트)': '#1E90FF'
    }
    styles = {
        'Linear Regression (선형 회귀)': '--', 
        'Ridge Regression (릿지 회귀)': '-.', 
        'Random Forest (랜덤 포레스트)': ':'
    }
    
    full_future_X = np.vstack([X[-1:], future_years])
    
    for name, model in models.items():
        full_pred = np.hstack([[y[-1]], predictions[name]])
        ax.plot(full_future_X.flatten(), full_pred, linestyle=styles[name], color=colors[name], linewidth=2.5, label=f'{name} 예측')

    ax.set_title(f"{month_names[selected_month]} 기온 분석 및 {target_future_year}년까지의 예측 비교", fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel("연도", fontsize=12)
    ax.set_ylabel("평균기온 (℃)", fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    st.pyplot(fig)

# 알고리즘 작동 원리 및 특징 설명
st.markdown("---")
st.subheader("💡 예측 알고리즘별 작동 원리 및 그래프 해석 가이드")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 1. 선형 회귀\n(Linear Regression)")
    st.write("""
    * **작동 원리**: 데이터들의 전체적인 경향을 관통하는 **하나의 직선(최소제곱법)**을 찾아냅니다. 과거의 기온 상승/하강 추세가 미래에도 일정한 기울기로 쭉 이어진다고 가정합니다.
    * **그래프 특징**: 연도가 지남에 따라 일정한 직선 형태로 온도가 계속 증가하거나 감소하는 예측선을 보여줍니다.
    """)

with col2:
    st.markdown("### 2. 릿지 회귀\n(Ridge Regression)")
    st.write("""
    * **작동 원리**: 선형 회귀와 비슷하지만, **규제(Regularization)**를 더해 과도하게 가파른 기울기가 만들어지는 것을 방지합니다. 데이터의 변동성에 영향을 덜 받도록 안정적인 직선을 그립니다.
    * **그래프 특징**: 선형 회귀와 유사한 직선 형태이지만, 과적합을 억제하여 조금 더 완만하거나 안정된 예측 추세를 나타냅니다.
    """)

with col3:
    st.markdown("### 3. 랜덤 포레스트\n(Random Forest)")
    st.write("""
    * **작동 원리**: 여러 개의 **의사결정 나무(Decision Tree)**를 숲처럼 모아서 다수결이나 평균으로 예측하는 앙상블 알고리즘입니다. 비선형적인 복잡한 패턴을 학습하는 데 강합니다.
    * **그래프 특징**: 직선이 아니라 최근 데이터의 패턴을 반영한 꺾은선 형태로 나타나며, 먼 미래 예측 시 최근 평균값 부근으로 수렴하는 특성이 있습니다.
    """)

# 미래 예측 요약 테이블
if not month_df.empty:
    with st.expander("📊 알고리즘별 미래 연도 예측값 상세 비교 표"):
        pred_df = pd.DataFrame({'연도': future_years.flatten()})
        for name, pred in predictions.items():
            pred_df[name] = np.round(pred, 2)
        st.dataframe(pred_df.set_index('연도'))
