import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Streamlit 페이지 설정
st.set_page_config(page_title="월별 기온 분석", layout="wide")

st.title("🌡️ 월별 연도별 기온 분석 대시보드")
st.write("데이터 파일에서 특정 월을 선택하여 연도별 최고/최저기온 변화를 확인할 수 있습니다.")

# 데이터 불러오기 함수 (캐싱 적용)
@st.cache_data
def load_data():
    # 한글 깨짐 방지를 위해 cp949 인코딩 사용 (필요시 utf-8로 변경 가능)
    df = pd.read_csv("temperature.csv", encoding="cp949")
    
    # '일시' 컬럼(예: Oct-07)을 날짜 형식으로 변환
    df['parsed_date'] = pd.to_datetime(df['일시'], format='%b-%y')
    df['Year'] = df['parsed_date'].dt.year
    df['Month'] = df['parsed_date'].dt.month
    
    # 2000년대 이후 데이터로 올바르게 정렬 (YY 형식 파싱 보정)
    df.loc[df['Year'] > 2026, 'Year'] -= 100
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 파일을 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 사이드바: 월 선택
st.sidebar.header("🔍 조회 옵션")
month_names = {
    1: "1월", 2: "2월", 3: "3월", 4: "4월", 
    5: "5월", 6: "6월", 7: "7월", 8: "8월", 
    9: "9월", 10: "10월", 11: "11월", 12: "12월"
}

selected_month_num = st.sidebar.selectbox(
    "조회할 월을 선택하세요", 
    options=list(month_names.keys()), 
    format_func=lambda x: month_names[x]
)

# 데이터 필터링
filtered_df = df[df['Month'] == selected_month_num].sort_values('Year')

if filtered_df.empty:
    st.warning("선택한 월에 해당하는 데이터가 없습니다.")
else:
    st.subheader(f"📅 {month_names[selected_month_num]} 연도별 기온 변화")
    
    # 맷플롯립 그래프 설정 (한글 폰트 깨짐 방지용 기본 폰트 설정)
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # 최고기온: 핫핑크 (#FF1493), 최저기온: 하늘색 (#00BFFF)
    ax.plot(filtered_df['Year'], filtered_df['최고기온(℃)'], marker='o', color='#FF1493', linewidth=2, label='최고기온(℃)')
    ax.plot(filtered_df['Year'], filtered_df['최저기온(℃)'], marker='s', color='#00BFFF', linewidth=2, label='최저기온(℃)')
    
    # 그래프 제목 및 축 이름 설정
    ax.set_title("월별 기온분석", fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel("연도", fontsize=12)
    ax.set_ylabel("온도 (℃)", fontsize=12)
    
    # 범례 표시
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # 스트림릿에 그래프 출력
    st.pyplot(fig)
    
    # 하단 데이터 테이블 표시 (선택 사항)
    with st.expander("📊 상세 데이터 보기"):
        st.dataframe(filtered_df[['Year', '일시', '최고기온(℃)', '최저기온(℃)', '평균기온(℃)']].reset_index(drop=True))
