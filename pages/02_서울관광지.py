import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# 페이지 기본 설정
st.set_page_config(
    page_title="외국인이 사랑하는 서울 관광지 TOP 10 (1박 2일 코스)",
    page_icon="🗽",
    layout="wide"
)

# 서울 주요 관광지 TOP 10 데이터셋
tourist_spots = [
    {
        "name": "경복궁",
        "lat": 37.579617,
        "lon": 126.977041,
        "desc": "조선 시대의 대표적인 궁궐로, 한국의 역사와 전통 건축 미학을 체험할 수 있는 으뜸 명소입니다.",
        "category": "역사/문화"
    },
    {
        "name": "N서울타워 (남산타워)",
        "lat": 37.551169,
        "lon": 126.988227,
        "desc": "서울 도심 전경과 멋진 야경을 한눈에 담을 수 있는 서울의 상징적인 랜드마크입니다.",
        "category": "랜드마크/전망대"
    },
    {
        "name": "북촌한옥마을",
        "lat": 37.582604,
        "lon": 126.983055,
        "desc": "경복궁과 창덕궁 사이에 위치하여 고즈넉한 전통 기와지붕 골목길 감성을 즐길 수 있는 대표 한옥 마을입니다.",
        "category": "전통/골목"
    },
    {
        "name": "명동 쇼핑거리",
        "lat": 37.563692,
        "lon": 126.982226,
        "desc": "K-뷰티, 패션 브랜드 매장과 함께 길거리 음식을 마음껏 맛볼 수 있는 쇼핑 메카입니다.",
        "category": "쇼핑/먹거리"
    },
    {
        "name": "홍대 거리",
        "lat": 37.556488,
        "lon": 126.924294,
        "desc": "젊음과 인디 문화의 중심지로 버스킹 공연, 독특한 카페, 클럽, 스트리트 패션을 경험할 수 있습니다.",
        "category": "쇼핑/문화"
    },
    {
        "name": "동대문디자인플라자 (DDP)",
        "lat": 37.566535,
        "lon": 127.009230,
        "desc": "세계적인 곡선 건축물로 다양한 디자인 전시, 패션쇼, 야시장이 열리는 복합문화공간입니다.",
        "category": "건축/디자인"
    },
    {
        "name": "인사동",
        "lat": 37.574348,
        "lon": 126.989710,
        "desc": "한국 전통 공예품, 골동품, 찻집 등이 즐비해 한국의 고전 문화 감성을 가장 잘 엿볼 수 있습니다.",
        "category": "전통/쇼핑"
    },
    {
        "name": "이태원",
        "lat": 37.534538,
        "lon": 126.994644,
        "desc": "세계 각국의 요리를 맛볼 수 있는 이국적인 글로벌 타운으로 다채로운 문화를 자랑합니다.",
        "category": "글로벌/음식"
    },
    {
        "name": "롯데월드타워 & 석촌호수",
        "lat": 37.512586,
        "lon": 127.102559,
        "desc": "123층의 웅장한 서울스카이 전망대, 초대형 쇼핑몰, 석촌호수 산책로를 즐기는 명소입니다.",
        "category": "쇼핑/엔터테인먼트"
    },
    {
        "name": "청계천",
        "lat": 37.569068,
        "lon": 126.978086,
        "desc": "서울 도심 한복판을 흐르는 휴식 산책로로, 밤에는 화려한 조명이 아름다운 힐링 장소입니다.",
        "category": "자연/산책"
    }
]

# 1박 2일 일정 데이터 (09:00 ~ 20:00)
schedule_day1 = [
    {"시간": "09:00 - 11:30", "장소": "경복궁", "주요 일정": "조선 궁궐 관람 및 한복 체험"},
    {"시간": "11:30 - 13:00", "장소": "북촌한옥마을", "주요 일정": "한옥 골목길 산책 및 점심 식사"},
    {"시간": "13:00 - 15:00", "장소": "인사동", "주요 일정": "전통 차 시음, 공예품 구경 및 쌈지길 탐방"},
    {"시간": "15:00 - 17:30", "장소": "청계천 & 명동", "주요 일정": "청계천 도심 산책 후 명동 쇼핑 및 스트리트 푸드 탐방"},
    {"시간": "17:30 - 20:00", "장소": "N서울타워 (남산타워)", "주요 일정": "케이블카 탑승, 도심 전경 감상 및 남산 야경/저녁 식사"}
]

schedule_day2 = [
    {"시간": "09:00 - 12:00", "장소": "홍대 거리", "주요 일정": "아침 브런치, 감성 카페 탐방 및 거리 구경"},
    {"시간": "12:00 - 14:30", "장소": "이태원", "주요 일정": "경리단길 탐방 및 이국적인 글로벌 맛집 점심 식사"},
    {"시간": "14:30 - 17:00", "장소": "동대문디자인플라자 (DDP)", "주요 일정": "DDP D-숲 및 현대적 미래 건축 디자인 전시 관람"},
    {"시간": "17:00 - 20:00", "장소": "롯데월드타워 & 석촌호수", "주요 일정": "석촌호수 산책, 서울스카이 전망대 야경 감상 및 저녁 식사"}
]

# 1. 상단 타이틀
st.title("🗽 서울 TOP 10 명소 1박 2일 여행 코스 (09:00 ~ 20:00)")
st.caption("서울 지도에서 위치를 확인하고 하단의 1박 2일 일정표와 상세 설명을 참고해보세요.")

# 2. Folium 지도 생성
m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 지도에 마커 추가
for spot in tourist_spots:
    popup_text = f"<b>{spot['name']}</b><br>{spot['category']}"
    folium.Marker(
        location=[spot['lat'], spot['lon']],
        popup=folium.Popup(popup_text, max_width=200),
        tooltip=spot['name'],
        icon=folium.Icon(color="red", icon="star")
    ).add_to(m)

# Streamlit 지도 렌더링
st_folium(m, width=900, height=500)

st.markdown("---")

# 3. 지도 밑 1박 2일 추천 일정표 (표 형식)
st.subheader("🗓️ 1박 2일 알짜배기 일정표 (09:00 - 20:00)")

tab1, tab2 = st.tabs(["DAY 1 (강북 대표 코스)", "DAY 2 (트렌디 & 강남 코스)"])

with tab1:
    st.dataframe(pd.DataFrame(schedule_day1), use_container_width=True, hide_index=True)

with tab2:
    st.dataframe(pd.DataFrame(schedule_day2), use_container_width=True, hide_index=True)

st.markdown("---")

# 4. 관광지 상세 설명
st.subheader("📌 서울 주요 관광지 10선 상세 설명")

col1, col2 = st.columns(2)

for idx, spot in enumerate(tourist_spots):
    target_col = col1 if idx % 2 == 0 else col2
    with target_col:
        with st.expander(f"{idx+1}. {spot['name']} ({spot['category']})", expanded=True):
            st.write(spot['desc'])
