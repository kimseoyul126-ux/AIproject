import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="국가별 MBTI 분석기", page_icon="🌍", layout="wide"
)

st.title("🌍 국가별 MBTI 분포 시각화 대시보드")
st.write(
    "국가를 선택하면 16가지 MBTI 비율을 막대그래프로 확인할 수 있습니다. (1등: 빨간색, 나머지: 파란색 그라데이션)"
)


# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
  return pd.read_csv("countriesMBTI_16types.csv")


df = load_data()

# MBTI 컬럼 목록
mbti_columns = [
    "INFJ",
    "ISFJ",
    "INTP",
    "ISFP",
    "ENTP",
    "INFP",
    "ENTJ",
    "ISTP",
    "INTJ",
    "ESFP",
    "ESTJ",
    "ENFP",
    "ESTP",
    "ISTJ",
    "ENFJ",
    "ESFJ",
]

# 사이드바에서 국가 선택
st.sidebar.header("⚙️ 설정")
selected_country = st.sidebar.selectbox("국가를 선택하세요:", df["Country"].unique())

# 선택한 국가의 데이터 추출 및 정렬 (비율 높은 순)
country_row = df[df["Country"] == selected_country]
country_data = (
    country_row.melt(
        id_vars=["Country"],
        value_vars=mbti_columns,
        var_name="MBTI",
        value_name="Ratio",
    )
    .sort_values(by="Ratio", ascending=False)
    .reset_index(drop=True)
)

# 레이아웃 구성
col1, col2 = st.columns([1, 2])

with col1:
  st.subheader(f"📊 {selected_country} MBTI 순위표")
  # 보기 좋게 백분율(%)로 변환하여 표시
  display_df = country_data[["MBTI", "Ratio"]].copy()
  display_df["Ratio (%)"] = (display_df["Ratio"] * 100).round(2)
  st.dataframe(
      display_df[["MBTI", "Ratio (%)"]].set_index("MBTI"),
      use_container_width=True,
  )

with col2:
  st.subheader(f"📈 {selected_country} MBTI 분포 그래프")

  # 막대그래프 색상 지정 (1등: 빨간색, 나머지: 파란색 계열 그라데이션)
  n = len(country_data)
  colors = []
  for i in range(n):
    if i == 0:
      colors.append("#ff4d4d")  # 1등: 빨간색
    else:
      # 2등부터는 파란색 농도가 점차 옅어지는 그라데이션 효과
      intensity = 0.8 - (i / n) * 0.6  # 0.2 ~ 0.8 사이 조절
      colors.append((0.1, 0.4, 0.8, max(intensity, 0.2)))

  fig, ax = plt.subplots(figsize=(10, 5))
  bars = ax.bar(
      country_data["MBTI"],
      country_data["Ratio"] * 100,
      color=colors,
      edgecolor="black",
      linewidth=0.5,
  )

  ax.set_ylabel("비율 (%)", fontsize=12)
  ax.set_xlabel("MBTI 유형", fontsize=12)
  ax.set_title(f"[{selected_country}] MBTI Distribution", fontsize=14)
  plt.xticks(rotation=45, ha="right")
  plt.grid(axis="y", linestyle="--", alpha=0.7)

  st.pyplot(fig)
