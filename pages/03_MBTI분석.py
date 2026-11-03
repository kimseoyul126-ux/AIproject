import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="국가별 MBTI 분석기", page_icon="🌍", layout="wide"
)

st.title("🌍 전 세계 국가별 MBTI 분석 대시보드")


# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
  return pd.read_csv("countriesMBTI_16types.csv")


df = load_data()

# MBTI 16가지 컬럼 목록
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

# 사이드바 기능 선택
st.sidebar.header("⚙️ 메뉴 선택")
menu = st.sidebar.radio(
    "원하는 분석 기능을 선택하세요:",
    ["국가별 MBTI 조회", "MBTI별 국가 순위 (1위부터)"],
)

# ----------------------------------------------------
# 1. 국가별 MBTI 조회 기능
# ----------------------------------------------------
if menu == "국가별 MBTI 조회":
  selected_country = st.sidebar.selectbox("국가를 선택하세요:", df["Country"].unique())

  # 선택한 국가의 MBTI 데이터 정리
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

  col1, col2 = st.columns([1, 2])

  with col1:
    st.subheader(f"📊 {selected_country} MBTI 순위표")
    display_df = country_data[["MBTI", "Ratio"]].copy()
    display_df["비율 (%)"] = (display_df["Ratio"] * 100).round(2)
    st.dataframe(
        display_df[["MBTI", "비율 (%)"]].set_index("MBTI"),
        use_container_width=True,
    )

  with col2:
    st.subheader(f"📈 {selected_country} MBTI 분포 그래프")

    # 막대 색상: 1등 빨간색, 2등부터 파란색 그라데이션
    n = len(country_data)
    colors = []
    for i in range(n):
      if i == 0:
        colors.append("#ff4d4d")  # 1등 빨간색
      else:
        intensity = 0.8 - (i / n) * 0.6
        colors.append((0.1, 0.4, 0.8, max(intensity, 0.2)))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(
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

# ----------------------------------------------------
# 2. MBTI별 국가 순위 기능 (신규 추가)
# ----------------------------------------------------
else:
  selected_mbti = st.sidebar.selectbox("MBTI 유형을 선택하세요:", mbti_columns)

  # 선택한 MBTI 비율이 높은 순(내림차순)으로 전체 국가 정렬
  ranked_df = (
      df[["Country", selected_mbti]]
      .sort_values(by=selected_mbti, ascending=False)
      .reset_index(drop=True)
  )

  # 순위(1위부터) 컬럼 생성
  ranked_df.index = ranked_df.index + 1
  ranked_df.rename(
      columns={"Country": "국가명", selected_mbti: "비율"}, inplace=True
  )
  ranked_df["비율 (%)"] = (ranked_df["비율"] * 100).round(2)

  st.header(f"🏆 {selected_mbti} 비율이 높은 국가 순위 (전체 {len(ranked_df)}개국)")

  col1, col2 = st.columns([2, 1])

  with col1:
    st.subheader(f"🔝 상위 10개국 시각화")

    top10 = ranked_df.head(10).reset_index()

    # 상위 10개국 막대그래프 색상 (1위 빨간색, 2위부터 파란색 그라데이션)
    top_colors = []
    for i in range(10):
      if i == 0:
        top_colors.append("#ff4d4d")
      else:
        intensity = 0.8 - (i / 10) * 0.6
        top_colors.append((0.1, 0.4, 0.8, max(intensity, 0.2)))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(
        top10["국가명"],
        top10["비율 (%)"],
        color=top_colors,
        edgecolor="black",
        linewidth=0.5,
    )
    ax.set_ylabel("비율 (%)", fontsize=12)
    ax.set_title(f"Top 10 Countries for {selected_mbti}", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    st.pyplot(fig)

  with col2:
    st.subheader("📋 전체 국가 순위표")
    st.dataframe(ranked_df[["국가명", "비율 (%)"]], use_container_width=True)
