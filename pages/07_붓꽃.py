import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from matplotlib.colors import ListedColormap

# 페이지 기본 설정
st.set_page_config(page_title="Iris 품종 예측기", page_icon="🌸", layout="centered")

st.title("🌸 붓꽃(Iris) 품종 예측 및 분류 알고리즘 비교")
st.markdown("꽃잎의 길이와 너비를 조절하면 선택한 **머신러닝 분류 알고리즘**이 품종을 예측하고, 분류 기준(결정 경계)을 시각화합니다.")

# 1. 데이터 로드 및 모델 학습용 함수 (캐싱 적용)
@st.cache_resource
def load_data():
    try:
        df = pd.read_csv("Iris.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("Iris.csv", encoding="utf-8")

    X = df[["꽃잎길이", "꽃잎너비"]]
    y_raw = df["품종"]

    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    return df, X, y, le

df, X, y, le = load_data()

# -------------------------------------------------------------
# 2. 본문 영역: 사용자 입력 (슬라이더를 사이드바가 아닌 본문에 배치)
# -------------------------------------------------------------
st.subheader("🎛️ 꽃잎 크기 입력")
col_input1, col_input2 = st.columns(2)

with col_input1:
    petal_length = st.slider(
        "꽃잎 길이 (Petal Length, cm)",
        min_value=float(df["꽃잎길이"].min() - 0.5),
        max_value=float(df["꽃잎길이"].max() + 0.5),
        value=3.8,
        step=0.1
    )

with col_input2:
    petal_width = st.slider(
        "꽃잎 너비 (Petal Width, cm)",
        min_value=float(df["꽃잎너비"].min() - 0.3),
        max_value=float(df["꽃잎너비"].max() + 0.5),
        value=1.2,
        step=0.1
    )

# -------------------------------------------------------------
# 3. 알고리즘 선택 및 설명
# -------------------------------------------------------------
st.subheader("🤖 분류 알고리즘 선택")
algo_option = st.selectbox(
    "사용할 머신러닝 알고리즘을 선택하세요:",
    ("랜덤 포레스트 (Random Forest)", "서포트 벡터 머신 (SVM)", "K-최근접 이웃 (KNN)")
)

# 알고리즘 객체 생성 및 설명 딕셔너리
descriptions = {
    "랜덤 포레스트 (Random Forest)": {
        "model": RandomForestClassifier(n_estimators=100, random_state=42),
        "desc": "**랜덤 포레스트(Random Forest)**는 여러 개의 의사결정 나무(Decision Tree)를 숲처럼 구성하여 다수결로 결과를 예측하는 앙상블 알고리즘입니다. 과적합에 강하고 정확도가 높아 분류 문제에 가장 널리 사용됩니다."
    },
    "서포트 벡터 머신 (SVM)": {
        "model": SVC(kernel='rbf', C=1.0, probability=True, random_state=42),
        "desc": "**서포트 벡터 머신(SVM)**은 데이터들 사이에 경계면(Hyperplane)을 찾아내어 각 클래스를 최적으로 분리하는 알고리즘입니다. 특히 비선형 경계를 그릴 때 강력한 성능(RBF 커널 등)을 발휘합니다."
    },
    "K-최근접 이웃 (KNN)": {
        "model": KNeighborsClassifier(n_neighbors=5),
        "desc": "**K-최근접 이웃(KNN)**은 새로운 데이터 주변의 가장 가까운 $K$개의 데이터(이웃)를 찾아, 그중 가장 많은 비중을 차지하는 품종으로 분류하는 직관적인 거리 기반 알고리즘입니다."
    }
}

selected_info = descriptions[algo_option]
model = selected_info["model"]
model.fit(X, y)

# 알고리즘 설명 출력
st.info(selected_info["desc"])

# 4. 예측 수행
input_data = pd.DataFrame([[petal_length, petal_width]], columns=["꽃잎길이", "꽃잎너비"])
pred_idx = model.predict(input_data)[0]
pred_species = le.inverse_transform([pred_idx])[0]
pred_proba = model.predict_proba(input_data)[0]

# 예측 결과 출력
st.subheader("🔍 예측 결과")
res_col1, res_col2 = st.columns([1, 1])

with res_col1:
    st.metric(label="예측된 품종", value=pred_species)
    st.write(f"- 입력된 꽃잎 길이: **{petal_length} cm**")
    st.write(f"- 입력된 꽃잎 너비: **{petal_width} cm**")

with res_col2:
    st.write("**품종별 예측 확률:**")
    proba_df = pd.DataFrame({
        "품종": le.classes_,
        "확률 (%)": np.round(pred_proba * 100, 1)
    })
    st.dataframe(proba_df, hide_index=True, use_container_width=True)

# 5. 결정 경계(Decision Boundary) 및 사용자 위치 시각화
st.subheader("📊 선택한 알고리즘의 분류 경계 시각화")
st.markdown("배경 색상은 선택한 모델이 학습한 분류 영역을 뜻하며, 금색 별(`★`)은 사용자가 입력한 위치입니다.")

fig, ax = plt.subplots(figsize=(8, 5))

# 그리드 생성
x_min, x_max = X["꽃잎길이"].min() - 0.6, X["꽃잎길이"].max() + 0.6
y_min, y_max = X["꽃잎너비"].min() - 0.4, X["꽃잎너비"].max() + 0.4
xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                     np.arange(y_min, y_max, 0.02))

grid_df = pd.DataFrame(np.c_[xx.ravel(), yy.ravel()], columns=["꽃잎길이", "꽃잎너비"])
Z = model.predict(grid_df)
Z = Z.reshape(xx.shape)

# 배경 색상 및 데이터 포인트 색상 설정
colors_bg = ["#FFCCCC", "#CCFFCC", "#CCCCFF"]
colors_pt = ["#E63946", "#2A9D8F", "#3A86FF"]
cmap_bg = ListedColormap(colors_bg)

ax.contourf(xx, yy, Z, alpha=0.45, cmap=cmap_bg)

# 실제 데이터 산점도 표시
for idx, species_name in enumerate(le.classes_):
    subset = df[df["품종"] == species_name]
    ax.scatter(
        subset["꽃잎길이"],
        subset["꽃잎너비"],
        c=colors_pt[idx],
        label=f"{species_name}",
        edgecolors="white",
        s=55,
        alpha=0.85
    )

# 사용자 입력 위치를 금색 별로 표시
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

ax.set_xlabel("Petal Length (cm)", fontsize=11, fontweight="bold")
ax.set_ylabel("Petal Width (cm)", fontsize=11, fontweight="bold")
ax.set_title(f"Decision Boundary: {algo_option.split('(')[0].strip()}", fontsize=13, fontweight="bold")
ax.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.9)
ax.grid(True, linestyle="--", alpha=0.3)

st.pyplot(fig)
