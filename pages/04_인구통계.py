import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="서울시 연령대별/성별 인구 비교 대시보드",
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
    # 전체 서울특별시(합계) 행은 제외하고 자치구들만 분석하기 위해 필터링할 수도 있습니다.
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

# 3. 사이드바 - 사용자 선택 옵션 (연도, 연령대)
st.sidebar.header("⚙️ 분석 조건 선택")

# (1) 연도 선택 (2020년 ~ 2025년)
years = [str(y) for y in range(2020, 2026)]
selected_year = st.sidebar.selectbox("연도 선택", years, index=len(years)-1)

# (2) 연령대 선택
age_categories = [
    '0~9세', '10~19세', '20~29세', '30~39세', '40~49세',
    '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상'
]
selected_age = st.sidebar.selectbox("연령대 선택 (10살 단위)", age_categories, index=2)

# 4. 데이터 가공 (서울시 전체 제외, 25개 자치구 대상)
# '서울특별시  (1100000000)' 같은 전체 합계 행은 제외하고 자치구만 추출
sub_df = df[df['행정구역_정제'] != '서울특별시'].copy()

# 선택된 연도와 연령대에 따른 남성, 여성 컬럼명 정의
male_col = f"{selected_year}년_남_거주자_{selected_age}"
female_col = f"{selected_year}년_여_거주자_{selected_age}"

# 데이터프레임에 남성, 여성 데이터 정리
chart_data = pd.DataFrame({
    '행정구': sub_df['행정구역_정제'],
    '남성': sub_df[male_col],
    '여성': sub_df[female_col]
})

# 인구수가 높은 순으로 정렬 (보기 쉽게 상위 25개 구 전체 또는 정렬)
chart_data = chart_data.sort_values(by='남성', ascending=True) # 가로 막대나 세로 막대 정렬용

# 5. Plotly 막대 그래프 생성 (남성: 핫핑크, 여성: 초록색)
fig = go.Figure()

# 남성 바 (핫핑크)
fig.add_trace(go.Bar(
    x=chart_data['행정구'],
    y=chart_data['남성'],
    name='남성',
    marker_color='hotpink'
))

# 여성 바 (초록색 - 예: ForestGreen 또는 MediumSeaGreen 등)
fig.add_trace(go.Bar(
    x=chart_data['행정구'],
    y=chart_data['여성'],
    name='여성',
    marker_color='mediumseagreen'
))

# 그래프 레이아웃 설정
fig.update_layout(
    title=dict(
        text=f"<b>{selected_year}년 [{selected_age}] 자치구별 남녀 인구 비교</b>",
        font=dict(size=20)
    ),
    xaxis=dict(
        title="행정구",
        tickangle=-45,
        showgrid=False
    ),
    yaxis=dict(
        title="인구수 (명)",
        showgrid=True,
        gridcolor='lightgrey',
        gridwidth=1
    ),
    barmode='group',  # 남녀 막대를 나란히 배치
    template="plotly_white",
    height=600,
    legend=dict(title="성별")
)

# 6. 메인 화면 출력
st.title("🏙️ 서울시 자치구별 연령·성별 인구 분석")
st.markdown("---")
st.markdown(f"현재 **{selected_year}년** 기준 **{selected_age}** 인구가 많은 서울시 자치구별 분포를 남녀(남성: 핑크, 여성: 초록)로 비교합니다.")

# 그래프 출력
st.plotly_chart(fig, use_container_width=True)

# 상세 데이터 표 제공
with st.expander("📊 상세 데이터 테이블 확인"):
    display_df = chart_data.sort_values(by='남성', ascending=False).reset_index(drop=True)
    display_df.columns = ['행정구', f'남성 ({selected_age})', f'여성 ({selected_age})']
    st.dataframe(display_df, use_container_width=True)
