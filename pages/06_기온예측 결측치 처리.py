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
st.set_page_config(page_title="기온 예측 및 결측치/알고리즘 비교 대시보드", layout="wide")

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

st.title("🌡️ 기온 예측 및 결측치·알고리즘 비교 대시보드")
st.write("결측치 처리 방식(제거, 중앙값 대체, 선형보간법)과 머신러닝 알고리즘에 따른 미래 기온 예측 결과를 비교하고 시각화합니다.")

# 데이터 불러오기 함수 (상위 폴더의 temperature_utf8.csv 경로 지정)
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'temperature_utf8.csv')
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
st.sidebar.header("⚙️ 분석 및 예측 설정")

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

# 2. 결측치 처리 방식 선택 (요청사항 2번)
impute_option = st.sidebar.selectbox(
    "결측치 처리 방식 선택",
    options=["1. 제거 (Drop)", "2. 중앙값으로 대체 (Median)", "3. 선형보간법 (Interpolate)"]
)

# 3. 알고리즘 선택 (요청사항 3번: 복수 선택 또는 단일 선택 비교 가능)
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 머신러닝 알고리즘 선택")
use_lr = st.sidebar.checkbox("선형 회귀 (Linear Regression)", value=True)
use_ridge = st.sidebar.checkbox("릿지 회귀 (Ridge Regression)", value=True)
use_rf = st.sidebar.checkbox("랜덤 포레스트 (Random Forest)", value=True)

# 4. 미래 예측 연도 입력
max_year = int(df['Year'].max())
target_future_year = st.sidebar.number_input(
    "미래 예측 연도 입력", 
    min_value=max_year + 1, 
    max_value=max_year + 50, 
    value=max_year + 10, 
    step=1
)

# 선택한 개월 데이터 추출 및 연도순 정렬
month_df = df[df['Month'] == selected_month].sort_values('Year').copy()

# -------------------------------------------------------------
# 결측치 처리 로직 적용 (요청사항 1, 2번)
# -------------------------------------------------------------
original_missing_count = month_df['평균기온(℃)'].isnull().sum()

if "1. 제거" in impute_option:
    processed_df = month_df.dropna(subset=['평균기온(℃)'])
elif "2. 중앙값" in impute_option:
    median_val = month_df['평균기온(℃)'].median()
    month_df['평균기온(℃)'] = month_df['평균기온(℃)'].fillna(median_val)
    processed_df = month_df
else: # 선형보간법
    month_df['평균기온(℃)'] = month_df['평균기온(℃)'].interpolate(method='linear')
    processed_df = month_df.dropna(subset=['평균기온(℃)'])

st.subheader(f"📈 [{month_names[selected_month]}] 결측치 처리 방식 및 알고리즘별 예측 비교")
st.info(f"ℹ️ 선택한 개월의 전체 데이터 수: {len(month_df)}개 (기존 결측치: {original_missing_count}개) | 적용된 방식: **{impute_option}**")

if processed_df.empty:
    st.warning("처리할 데이터가 부족합니다.")
else:
    X = processed_df[['Year']].values
    y = processed_df['평균기온(℃)'].values
    
    # 모델 정의
    models = {}
    if use_lr:
        models["선형 회귀 (Linear Regression)"] = LinearRegression()
    if use_ridge:
        models["릿지 회귀 (Ridge Regression)"] = Ridge(alpha=1.0)
    if use_rf:
        models["랜덤 포레스트 (Random Forest)"] = RandomForestRegressor(n_estimators=100, random_state=42)
        
    if not models:
        st.warning("적어도 하나의 알고리즘을 사이드바에서 선택해주세요.")
    else:
        future_years = np.arange(max_year + 1, target_future_year + 1).reshape(-1, 1)
        predictions = {}
        
        for name, model in models.items():
            model.fit(X, y)
            pred = model.predict(future_years)
            predictions[name] = pred

        # 시각화 그래프 생성
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 실제 데이터 플롯
        ax.plot(processed_df['Year'], y, marker='o', color='#2E8B57', linewidth=2, label=f'전처리된 실제 기온 (1927~{max_year})')
        
        colors = {
            "선형 회귀 (Linear Regression)": '#FF4500', 
            "릿지 회귀 (Ridge Regression)": '#9932CC', 
            "랜덤 포레스트 (Random Forest)": '#1E90FF'
        }
        styles = {
            "선형 회귀 (Linear Regression)": '--', 
            "릿지 회귀 (Ridge Regression)": '-.', 
            "랜덤 포레스트 (Random Forest)": ':'
        }
        
        full_future_X = np.vstack([X[-1:], future_years])
        
        for name, pred in predictions.items():
            full_pred = np.hstack([[y[-1]], pred])
            ax.plot(full_future_X.flatten(), full_pred, linestyle=styles.get(name, '-'), color=colors.get(name, '#000000'), linewidth=2.5, label=f'{name} 예측')

        ax.set_title(f"{month_names[selected_month]} 기온 예측 ({impute_option})", fontsize=16, fontweight='bold', pad=15)
        ax.set_xlabel("연도", fontsize=12)
        ax.set_ylabel("평균기온 (℃)", fontsize=12)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        st.pyplot(fig)

        # 예측값 테이블 표시
        with st.expander("📊 선택된 알고리즘별 미래 예측값 상세 비교 표"):
            pred_df = pd.DataFrame({'연도': future_years.flatten()})
            for name, pred in predictions.items():
                pred_df[name] = np.round(pred, 2)
            st.dataframe(pred_df.set_index('연도'))

# -------------------------------------------------------------
# 알고리즘 작동 원리 설명
# -------------------------------------------------------------
st.markdown("---")
st.subheader("💡 머신러닝 알고리즘 및 결측치 처리 가이드")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 1. 선형 회귀\n(Linear Regression)")
    st.write("""
    * **작동 원리**: 데이터의 전체 흐름을 관통하는 **하나의 직선(최소제곱법)**을 찾아냅니다.
    * **특징**: 장기적인 기온 상승 또는 하강 추세가 미래에도 일정한 기울기로 이어진다고 가정합니다.
    """)

with col2:
    st.markdown("### 2. 릿지 회귀\n(Ridge Regression)")
    st.write("""
    * **작동 원리**: 선형 회귀에 **규제(Regularization)**를 추가하여 과도하게 급격한 기울기가 생기는 것을 방지합니다.
    * **특징**: 데이터의 이상치나 급격한 변동에 덜 흔들리고 안정적인 예측선을 만듭니다.
    """)

with col3:
    st.markdown("### 3. 랜덤 포레스트\n(Random Forest)")
    st.write("""
    * **작동 원리**: 여러 개의 의사결정 나무를 조합하여 복잡하고 비선형적인 패턴을 학습합니다.
    * **특징**: 최근 연도의 복잡한 기온 등락 패턴을 반영하지만, 먼 미래 예측 시 최근 평균값 부근으로 수렴합니다.
    """)
