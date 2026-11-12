import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# 페이지 기본 설정
st.set_page_config(page_title="Iris 품종 예측기", page_icon="🌸", layout="centered")

st.title("🌸 붓꽃(Iris) 품종 예측 및 분류 시각화")
st.markdown("꽃잎의 길이와 너비를 입력하면 **랜덤 포레스트(Random Forest)** 알고리즘이 품종을 예측하고 분류 영역을 시각화합니다.")

# 1. 데이터 로드 및 모델 학습 (캐싱을 통해 속도 최적화)
@st.cache_resource
def load_and_train():
    # 업로드된 Iris.csv의 cp949 인코딩 처리
    try:
        df = pd.read_csv("Iris.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("Iris.csv", encoding="utf-8")

    X = df[["꽃잎길이", "꽃잎너비"]]
    y_raw = df["품종"]

    # 결정 경계 시각화를 위한 라벨 인코딩
    le = LabelEncoder()
    y = le.fit_transform(y_raw)

    # 가장 널리 쓰이는 분류 알고리즘: Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    return df, X, y, le, model

df, X, y, le, model = load_and_train()

# 2. 사이드바: 사용자 입력 받기
st.sidebar.header("📏 꽃잎 크기 입력 (cm)")
petal_length = st.sidebar.slider(
    "꽃잎 길이 (Petal Length)",
    min_value=float(df["꽃잎길이"].min() - 0.5),
    max_value=float(df["꽃잎길이"].max() + 0.5),
    value=3.8,
    step=0.1
)
petal_width = st.sidebar.slider(
    "꽃잎 너비 (Petal Width)",
    min_value=float(df["꽃잎너비"].min() - 0.3),
    max_value=float(df["꽃잎너비"].max() + 0.5),
    value=1.2,
    step=0.1
)

# 3. 예측 수행
input_data = pd.DataFrame([[petal_length, petal_width]], columns=["꽃잎길이", "꽃잎너비"])
pred_idx = model.predict(input_data)[0]
pred_species = le.inverse_transform([pred_idx])[0]
pred_proba = model.predict_proba(input_data)[0]

# 예측 결과 출력
st.subheader("🔍 예측 결과")
col1, col2 = st.columns([1, 1])

with col1:
    st.metric(label="예측된 품종", value=pred_species)
    st.write(f"- 입력 꽃잎 길이: **{petal_length} cm**")
    st.write(f"- 입력 꽃잎 너비: **{petal_width} cm**")

with col2:
    st.write("**품종별 예측 확률:**")
    proba_df = pd.DataFrame({
        "품종": le.classes_,
        "확률 (%)": np.round(pred_proba * 100, 1)
    })
    st.dataframe(proba_df, hide_index=True, use_container_width=True)

# 4. 결정 경계(Decision Boundary) 및 사용자 위치 시각화
st.subheader("📊 분류 근거 시각화 (결정 경계)")
st.caption("배경 색상은 모델이 학습한 각 품종의 분류 영역을 나타냅니다. 금색 별(★)이 위치한 영역의 색상과 주변 데이터 분포를 통해 분류 근거를 확인할 수 있습니다.")

fig, ax = plt.subplots(figsize=(8, 5.5))

# 그리드 생성 (배경 영역 색칠용)
x_min, x_max = X["꽃잎길이"].min() - 0.6, X["꽃잎길이"].max() + 0.6
y_min, y_max = X["꽃잎너비"].min() - 0.4, X["꽃잎너비"].max() + 0.4
xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                     np.arange(y_min, y_max, 0.02))

grid_df = pd.DataFrame(np.c_[xx.ravel(), yy.ravel()], columns=["꽃잎길이", "꽃잎너비"])
Z = model.predict(grid_df)
Z = Z.reshape(xx.shape)

# 결정 경계 배경 그리기
colors_bg = ["#FFCCCC", "#CCFFCC", "#CCCCFF"]
colors_pt = ["#E63946", "#2A9D8F", "#3A86FF"]
from matplotlib.colors import ListedColormap
cmap_bg = ListedColormap(colors_bg)

ax.contourf(xx, yy, Z, alpha=0.45, cmap=cmap_bg)

# 기존 학습 데이터 산점도 그리기
for idx, species_name in enumerate(le.classes_):
    subset = df[df["품종"] == species_name]
    ax.scatter(
        subset["꽃잎길이"],
        subset["꽃잎너비"],
        c=colors_pt[idx],
        label=f"{species_name} (Data)",
        edgecolors="white",
        s=55,
        alpha=0.85
    )

# 사용자가 입력한 값을 금색 별(★)로 표시
ax.scatter(
    petal_length,
    petal_width,
    c="gold",
    edgecolors="black",
    linewidth=1.5,
    marker="*",
    s=450,
    zorder=10,
    label=f"Your Input ({pred_species})"
)

# Streamlit Cloud 리눅스 환경을 고려하여 그래프 라벨은 영문으로 표기
ax.set_xlabel("Petal Length (cm)", fontsize=11, fontweight="bold")
ax.set_ylabel("Petal Width (cm)", fontsize=11, fontweight="bold")
ax.set_title("Random Forest Decision Boundary & Your Input", fontsize=13, fontweight="bold")
ax.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.9)
ax.grid(True, linestyle="--", alpha=0.3)

st.pyplot(fig)
