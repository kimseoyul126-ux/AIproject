import streamlit as st
import folium
from streamlit_folium import st_folium

# 페이지 기본 설정 (타이틀, 아이콘, 레이아웃)
st.set_page_config(
    page_title="외국인이 사랑하는 서울 관광지 TOP 10",
    page_icon="🗽",
    layout="wide"
)

# 서울 주요 관광지 TOP 10 데이터셋 (이름, 위도, 경도, 설명, 카테고리)
tourist_spots = [
    {
        "name": "경복궁",
        "lat": 37.579617,
        "lon": 126.977041,
        "desc": "조선 시대의 대표적인 궁궐로, 한국의 역사와 전통 건축 미학을 체험할 수 있는 으뜸 명소입니다. 한복 체험이 대단히 인기 있습니다.",
        "category": "역사/문화"
    },
    {
        "name": "N서울타워 (남산타워)",
        "lat": 37.551169,
        "lon": 126.988227,
        "desc": "서울 도심 전경과 멋진 야경을 한눈에 담을 수 있는 서울의 상징적인 랜드마크이자 연인들의 대표 데이트 코스입니다.",
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
        "desc": "K-뷰티, 패션 브랜드 매장과 함께 길거리 음식을 마음껏 맛볼 수 있어 외국인 관광객 만족도가 매우 높은 쇼핑 메카입니다.",
        "category": "쇼핑/먹거리"
    },
    {
        "name": "홍대 거리",
        "lat": 37.556488,
        "lon": 126.924294,
        "desc": "젊음과 인디 문화의 중심지로 버스킹 공연, 독특한 카페, 클럽, 스트리트 패션을 모두 경험할 수 있는 트렌디 핫플입니다.",
        "category": "쇼핑/문화"
    },
    {
        "name": "동대문디자인플라자 (DDP)",
        "lat": 37.566535,
        "lon": 127.009230,
        "desc": "우주선을 연상시키는 세계적인 곡선 건축물로 다양한 디자인 전시, 패션쇼, 밤 도깨비 야시장이 열리는 복합문화공간입니다.",
        "category": "건축/디자인"
    },
    {
        "name": "인사동",
        "lat": 37.574348,
        "lon": 126.989710,
        "desc": "한국 전통 공예품, 골동품, 서예 용품, 찻집 등이 즐비해 한국의 고전 문화 감성을 가장 잘 엿볼 수 있는 거리입니다.",
        "category": "전통/쇼핑"
    },
    {
        "name": "이태원",
        "lat": 37.534538,
        "lon": 126.994644,
        "desc": "세계 각국의 요리를 맛볼 수 있는 이국적인 글로벌 타운으로 다채로운 문화와 활기찬 밤문화를 자랑합니다.",
        "category": "글로벌/음식"
    },
    {
        "name": "롯데월드타워 & 석촌호수",
        "lat": 37.512586,
        "lon": 127.102559,
        "desc": "123층의 웅장한 서울스카이 전망대, 초대형 쇼핑몰, 실내 테마파크, 아름다운 석촌호수 산책로를 한 번에 즐기는 콤보 명소입니다.",
        "category": "쇼핑/엔터테인먼트"
    },
    {
        "name": "청계천",
        "lat": 37.569068,
        "lon": 126.978086,
        "desc": "서울 도심 한복판을 흐르는 휴식 산책로로, 밤에는 화려한 조명과 등불 축제가 열려 걷기에 아주 좋은 힐링 장소입니다.",
        "category": "자연/산책"
    }
]

# 1. 상단 제목 및 설명
st.title("🗽 외국인이 사랑하는 서울 명소 TOP 10")
st.caption("서울 지도 위의 마커를 클릭하거나 아래 개별 설명을 확인해보세요.")

# 2. Folium 지도 객체 생성 (서울 시청 중심 기준 설정)
m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 3. 지도 위에 10개 관광지 마커 찍기
for spot in tourist_spots:
    popup_text = f"<b>{spot['name']}</b><br>{spot['category']}"
    folium.Marker(
        location=[spot['lat'], spot['lon']],
        popup=folium.Popup(popup_text, max_width=200),
        tooltip=spot['name'],
        icon=folium.Icon(color="red", icon="star")
    ).add_to(m)

# 4. Streamlit 화면에 지도 렌더링
st_folium(m, width=900, height=500)

st.markdown("---")

# 5. 하단 관광지 상세 설명 섹션 (2열 배치)
st.subheader("📌 서울 주요 관광지 10선 상세 설명")

col1, col2 = st.columns(2)

for idx, spot in enumerate(tourist_spots):
    # 홀수/짝수 인덱스에 따라 좌우 칼럼 나눠 넣기
    target_col = col1 if idx % 2 == 0 else col2
    with target_col:
        with st.expander(f"{idx+1}. {spot['name']} ({spot['category']})", expanded=True):
            st.write(spot['desc'])
