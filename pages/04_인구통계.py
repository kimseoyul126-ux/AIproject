import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="서울시 연령별 인구 현황 대시보드",
    page_icon="📊",
    layout="wide"
)

# 2. 데이터 로드 및 전처리 (상위 폴더의 CSV 파일 참조)
@st.cache_data
def load_data():
    # 현재 파일(py) 위치의 상위 폴더에 있는 population.csv 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "population.csv")
    
    # CP949 인코딩으로 데이터 로드 (한글 깨짐 방지)
    df = pd.read_csv(file_path, encoding='cp949')
    
    # 행정구역 이름 정제 (예: "서울특별시 종로구 (1111000000)" -> "서울특별시 종로구")
    df['행정구역_정제'] = df['행정구역'].str.split('(').str[0].str.strip()
    
    # 숫자 데이터 쉼표(,) 제거 후 정수 변환
    for col in df.columns:
        if col not in ['행정구역', '행정구역_정제']:
            df[col] = df[col].astype(str).str.replace(',', '').astype(int)
            
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"상위 폴더에서 `population.csv` 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

# 3. 사이드바 - 사용자 선택 옵션 (행정구, 성별, 연도)
st.sidebar.header("⚙️ 옵션 선택")

# (1) 행정구 선택
region_list = df['행정구역_정제'].tolist()
selected_region = st.sidebar.selectbox("행정구 선택", region_list, index=0)

# (2) 연도 선택 (2020년 ~ 2025년)
years = [str(y) for y in range(2020, 2026)]
selected_year = st.sidebar.selectbox("연도 선택", years, index=len(years)-1)

# (3) 성별 선택
gender_options = ["전체", "남성", "여성"]
selected_gender = st.sidebar.radio("성별 선택", gender_options, index=0)

# 4. 데이터 추출
region_row = df[df['행정구역_정제'] == selected_region].iloc[0]

# 연령대 카테고리 정의
age_categories = [
    '0~9세', '10~19세', '20~29세', '30~39세', '40~49세',
    '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상'
]

# 성별 조건에 따른 컬럼 Prefix 설정
if selected_gender == "전체":
    prefix = f"{selected_year}년_거주자_"
elif selected_gender == "남성":
    prefix = f"{selected_year}년_남_거주자_"
else:
    prefix = f"{selected_year}년_여_거주자_"

# 연령대별 인구수 추출
y_values = [region_row[f"{prefix}{age}"] for age in age_categories]

# 5. Plotly 꺾은선 그래프 생성 (핫핑크 색상 & 축 단위 설정)
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=age_categories,
    y=y_values,
    mode='lines+markers',
    name=f'{selected_gender} 인구',
    line=dict(color='hotpink', width=3),
    marker=dict(size=8, color='hotpink')
))

# 그래프 레이아웃 설정 (가로축 10살 단위 / 세로축 1,000만 단위 구분선)
fig.update_layout(
    title=dict(
        text=f"<b>{selected_region} ({selected_year}년 - {selected_gender}) 연령별 인구수</b>",
        font=dict(size=20)
    ),
    xaxis=dict(
        title="나이 (연령대)",
        showgrid=True,
        gridcolor='lightgrey',
        gridwidth=1
    ),
    yaxis=dict(
        title="인구수 (명)",
        tickmode='linear',
        tick0=0,
        dtick=10000000,  # 1,000만 단위 구분선
        showgrid=True,
        gridcolor='lightgrey',
        gridwidth=1
    ),
    hovermode="x unified",
    template="plotly_white",
    height=550
)

# 6. 메인 화면 출력
st.title("📈 서울시 연령별 인구수 분석")
st.markdown("---")

# 주요 지표 표시
total_selected = region_row[f"{prefix}총인구수"]
st.metric(
    label=f"선택 조건 ({selected_region} / {selected_year}년 / {selected_gender}) 총인구수", 
    value=f"{total_selected:,} 명"
)

# 그래프 출력
st.plotly_chart(fig, use_container_width=True)

# 상세 데이터 데이터프레임 확인
with st.expander("📊 추출된 인구 데이터 확인"):
    summary_df = pd.DataFrame({
        '연령대': age_categories,
        '인구수(명)': y_values
    })
    st.dataframe(summary_df, use_container_width=True)
