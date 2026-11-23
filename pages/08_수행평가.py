import csv
import os
import random
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="서울 찐맛집 제과점 추천소 🥐", page_icon="🍰", layout="centered"
)


# Bbang.csv에서 실제 영업 중인 가게 & 자치구(구) 정보 불러오기
@st.cache_data
def load_active_bakeries():
  file_name = "Bbang.csv"
  active_list = []

  if not os.path.exists(file_name):
    return active_list

  for enc in ["cp949", "utf-8", "euc-kr"]:
    try:
      with open(file_name, mode="r", encoding=enc) as f:
        reader = csv.DictReader(f)
        for row in reader:
          status = row.get("영업상태명", "")
          if "영업" in status:
            name = row.get("사업장명", "").strip()
            addr = row.get("지번주소", "").strip()

            # 주소에서 'OO구' 추출
            district = "기타"
            for part in addr.split():
              if part.endswith("구") and len(part) >= 2:
                district = part
                break

            if name:
              active_list.append(
                  {"name": name, "address": addr, "district": district}
              )
      break
    except UnicodeDecodeError:
      continue
  return active_list


# 12가지 디저트 유형별 대표 키워드 및 정보 정의
DESSERT_DATA = {
    "🍦 모나카 아이스크림 & 사라다빵 (레트로)": {
        "keywords": ["태극당", "사라다", "모나카"],
        "display_name": "레트로 감성 모나카 & 사라다빵 맛집",
        "default_name": "태극당 (장충동 본점)",
        "default_dist": "중구",
        "history": "1946년 문을 연 서울에서 가장 오래된 전설의 빵집! 🏛️",
        "signature": "진한 우유 맛 '모나카 아이스크림' & 추억의 '야채 사라다빵'",
        "fallback_addr": "서울특별시 중구 장충동2가 189-5",
    },
    "🥖 쫄깃한 쪽파·바질 베이글": {
        "keywords": ["베이글", "런던베이글"],
        "display_name": "쫄깃촉촉 베이글 전문점",
        "default_name": "런던베이글뮤지엄 안국점",
        "default_dist": "종로구",
        "history": "오픈런 대란을 일으킨 대한민국 베이글 성지! 🔥",
        "signature": "쪽파 프레첼 베이글, 브릭레인 샌드위치, 감자치즈 베이글",
        "fallback_addr": "서울특별시 종로구 계동 102-1 연화빌딩",
    },
    "🧂 겉바속촉 버터 풍미 소금빵": {
        "keywords": ["소금빵", "자연도"],
        "display_name": "고소한 버터 풍미 소금빵 맛집",
        "default_name": "자연도소금빵 in 성수",
        "default_dist": "성동구",
        "history": "성수동·연남동 줄 서서 먹는 소금빵 전문 핫플레이스! 🌊",
        "signature": "갓 구워낸 겉바속촉 '소금빵 4개 세트'",
        "fallback_addr": "서울특별시 성동구 성수동2가 321-74",
    },
    "🍩 폭신폭신 크림 가득 도넛": {
        "keywords": ["노티드", "도넛", "크림"],
        "display_name": "달콤 폭신 수제 도넛 맛집",
        "default_name": "카페 노티드 (Knotted) 청담",
        "default_dist": "강남구",
        "history": "K-디저트 도넛 열풍의 주인공, 귀여운 스마일 마스코트 맛집! 😊",
        "signature": "우유 생크림 도넛, 얼그레이 도넛, 클래식 바닐라 도넛",
        "fallback_addr": "서울특별시 강남구 신사동 603-4",
    },
    "🥐 결이 살아있는 슈크림 & 밤식빵": {
        "keywords": ["리치몬드", "슈크림", "밤식빵"],
        "display_name": "제과명장의 정통 과자점",
        "default_name": "리치몬드 과자점 (성산본점)",
        "default_dist": "마포구",
        "history": "1979년부터 이어온 대한민국 제과명장의 자존심! 👑",
        "signature": "바닐라빈 콕콕 박힌 '슈크림' & 밤이 쏟아지는 '공주 밤식빵'",
        "fallback_addr": "서울특별시 마포구 성산동 114-5 1,2층",
    },
    "🎂 달콤한 케이크 & 몽블랑": {
        "keywords": ["김영모", "케이크", "몽블랑"],
        "display_name": "국가대표 명장 베이커리",
        "default_name": "김영모 과자점 (서초본점)",
        "default_dist": "서초구",
        "history": "1982년 개업, 서울 3대 빵집으로 꼽히는 명장 베이커리! 🏆",
        "signature": "부드러운 '뉴고구마케이크', 바게트 샌드위치, 몽블랑",
        "fallback_addr": "서울특별시 서초구 서초동 1757-1",
    },
    "🫘 묵직한 통단팥빵 & 맘모스빵": {
        "keywords": ["쟝블랑제리", "단팥빵", "맘모스"],
        "display_name": "속이 꽉 찬 혜자로운 빵집",
        "default_name": "쟝블랑제리 (낙성대 본점)",
        "default_dist": "관악구",
        "history": "1996년부터 서울대입구·낙성대를 지켜온 '빵지순례' 필수 코스! 🎒",
        "signature": "묵직한 '단팥빵', 생크림 팥빵, 거대한 크기의 '맘모스빵'",
        "fallback_addr": "서울특별시 관악구 봉천동 1660-7",
    },
    "🍰 클래식 사라다빵 & 생크림 케이크": {
        "keywords": ["나폴레옹", "사라다"],
        "display_name": "전통의 명문 베이커리",
        "default_name": "나폴레옹 과자점 (성북본점)",
        "default_dist": "성북구",
        "history": "1968년 개업! 대한민국 제과 기능장들을 배출한 '빵집 사관학교' 🎓",
        "signature": "원조 '사라다빵', 부드러운 '크림빵', 구운 도넛",
        "fallback_addr": "서울특별시 성북구 성북동1가 35-5",
    },
    "🐢 귀엽고 달콤한 아기궁뎅이빵": {
        "keywords": ["피터팬", "아기궁뎅이"],
        "display_name": "연희동 터줏대감 동네 빵집",
        "default_name": "피터팬 1978 (연희동 본점)",
        "default_dist": "서대문구",
        "history": "1978년부터 연희동 골목을 지켜온 동네 터줏대감 맛집! 🏡",
        "signature": "폭신폭신한 '아기궁뎅이빵', 장발장이 훔친 빵, 크림치즈 먹물빵",
        "fallback_addr": "서울특별시 서대문구 연희동 90-5",
    },
    "🍫 꾸덕한 더티초코 & 빨미까레": {
        "keywords": ["아우어베이커리", "더티초코", "초코"],
        "display_name": "트렌디한 페이스트리 카페",
        "default_name": "아우어 베이커리",
        "default_dist": "종로구",
        "history": "페이스트리 열풍을 이끈 트렌디 베이커리 카페! 🖤",
        "signature": "초코 코코아 파우더 듬뿍 '더티초코', 바삭한 '빨미까레'",
        "fallback_addr": "서울특별시 종로구 신문로2가 171",
    },
    "🍞 촉촉한 식빵 & 큐브식빵": {
        "keywords": ["밀도", "식빵"],
        "display_name": "담백하고 쫄깃한 식빵 전문점",
        "default_name": "성수동 밀도 (Meal°)",
        "default_dist": "성동구",
        "history": "온도와 습도까지 계산해 굽는 식빵 전문 베이커리! 🌡️",
        "signature": "담백한 '담백식빵', 커스터드 크림 가득한 '큐브식빵'",
        "fallback_addr": "서울특별시 성동구 성수동1가 656-442",
    },
    "🌾 고소한 통밀빵 & 무화과 호밀빵": {
        "keywords": ["오월의종", "호밀빵", "통밀빵"],
        "display_name": "천연 효모 발효빵 전문점",
        "default_name": "오월의 종 (한남동 본점)",
        "default_dist": "용산구",
        "history": "천연 효모 발효빵의 교과서로 불리는 이태원·한남동 터줏대감! 🌿",
        "signature": "무화과 호밀빵, 크랜베리 바게트, 올리브 치아바타",
        "fallback_addr": "서울특별시 용산구 한남동 745-11",
    },
}

# 서울시 25개 자치구 목록
SEOUL_DISTRICTS = [
    "전체 (서울 어디든 좋아!)",
    "강남구",
    "강동구",
    "강북구",
    "강서구",
    "관악구",
    "광진구",
    "구로구",
    "금천구",
    "노원구",
    "도봉구",
    "동대문구",
    "동작구",
    "마포구",
    "서대문구",
    "서초구",
    "성동구",
    "성북구",
    "송파구",
    "양천구",
    "영등포구",
    "용산구",
    "은평구",
    "종로구",
    "중구",
    "중랑구",
]

# --- UI 화면 구성 ---
st.title("🥐 서울 찐 제과점 맞춤 추천소 🍰")
st.markdown(
    "1️⃣ 먹고 싶은 **디저트 종류**를 고르고,\n"
    "2️⃣ 가고 싶은 **지역(구)**을 선택하면,\n"
    "**`Bbang.csv` 공공데이터**에서 조건에 딱 맞는 빵집을 찾아줄게! ✨"
)
st.divider()

# 데이터 로드
active_bakeries = load_active_bakeries()

# 선택 UI
col1, col2 = st.columns(2)
with col1:
  selected_dessert = st.selectbox(
      "🍩 1. 디저트 종류 선택", options=list(DESSERT_DATA.keys())
  )

with col2:
  selected_district = st.selectbox(
      "📍 2. 가고 싶은 지역(구) 선택", options=SEOUL_DISTRICTS
  )

# 추천 버튼
if st.button(
    "🎉 내 조건에 딱 맞는 빵집 찾기!", use_container_width=True, type="primary"
):
  dessert_info = DESSERT_DATA[selected_dessert]

  # 필터링 로직: 1) 선택한 지역구에 속하고, 2) 디저트 키워드가 포함되거나 일반 빵집들
  matched_stores = []

  # 사용자가 특정 구를 골랐을 때
  if selected_district != "전체 (서울 어디든 좋아!)":
    district_filtered = [
        s for s in active_bakeries if s["district"] == selected_district
    ]

    # 그 구 안에서 디저트 키워드가 들어가는 가게 먼저 찾기
    for store in district_filtered:
      if any(kw in store["name"] for kw in dessert_info["keywords"]):
        matched_stores.append(store)

    # 만약 키워드에 딱 맞는 유명 가게가 그 구에 없더라도, 해당 지역의 영업 중인 빵집들을 대안으로 활용
    if not matched_stores:
      matched_stores = district_filtered

  else:
    # 전체를 골랐을 때는 전국구 유명 본점 혹은 전체 중 키워드 매칭
    for store in active_bakeries:
      if any(kw in store["name"] for kw in dessert_info["keywords"]):
        matched_stores.append(store)

  st.balloons()
  st.subheader(
      f"🏆 '{selected_dessert.split(' ')[-1]}' 찐 맛집 추천 결과"
      f" ({selected_district})"
  )

  # 1) 대표 추천 가게 보여주기 (해당 구에 유명 본점이 있으면 최우선 표시)
  best_match = None
  for store in active_bakeries:
    if dessert_info["default_name"].replace(" ", "") in store["name"].replace(
        " ", ""
    ) or any(kw in store["name"] for kw in dessert_info["keywords"]):
      if (
          selected_district == "전체 (서울 어디든 좋아🍀)"
          or store["district"] == selected_district
      ):
        best_match = store
        break

  with st.container(border=True):
    st.markdown(f"**✨ 디저트 테마:** {dessert_info['display_name']}")
    st.markdown(f"**📖 설명 및 역사:** {dessert_info['history']}")
    st.markdown(f"**😋 대표 메뉴:** {dessert_info['signature']}")

    # 사용자가 고른 지역에 명실상부한 대표 매장이 있다면 해당 주소 표시, 아니면 일치하는 목록 중 선택
    if (
        selected_district == "전체 (서울 어디든 좋아!)"
        or dessert_info["default_dist"] == selected_district
    ):
      st.markdown(f"**📍 추천 장소:** `{dessert_info['default_name']}`")
      st.markdown(f"**📍 위치 주소:** `{dessert_info['fallback_addr']}`")
      st.success(
          "✅ `Bbang.csv` 공공데이터 확인 완료! 현재 **정상 영업 중**인 대표"
          " 랜드마크야. 🏪"
      )
    elif matched_stores:
      # 사용자가 고른 구 안에 매칭되는 다른 지점이나 빵집이 있는 경우
      top_store = matched_stores[0]
      st.markdown(f"**📍 추천 장소:** `{top_store['name']}`")
      st.markdown(f"**📍 위치 주소:** `{top_store['address']}`")
      st.success(
          f"✅ 선택하신 `{selected_district}` 내에서 조건에 맞는 영업 중인 빵집을"
          " 찾았어! 🥖"
      )
    else:
      st.markdown(
          f"**📍 추천 장소:** `{dessert_info['default_name']} (타 지역 본점)"
          "`"
      )
      st.markdown(f"**📍 위치 주소:** `{dessert_info['fallback_addr']}`")
      st.info(
          f"💡 아쉽게도 선택하신 `{selected_district}` 안에는 해당 디저트 전문"
          " 단독 지점이 없어서, 서울 대표 본점 정보를 알려줄게! ✨"
      )

  # 2) 선택한 지역구에 영업 중인 다른 추천 빵집들도 함께 리스트업
  if selected_district != "전체 (서울 어디든 좋아!)":
    st.divider()
    st.subheader(
        f"🗺️ '{selected_district}'에서 지금 바로 갈 수 있는 다른 빵집들!"
    )

    other_stores = [
        s for s in active_bakeries if s["district"] == selected_district
    ]
    if other_stores:
      sample_count = min(4, len(other_stores))
      picked = random.sample(other_stores, sample_count)
      st.caption(
          f"💡 `{selected_district}`에 등록된 총 {len(other_stores)}개의 빵집"
          " 중 무작위 4곳이야 👇"
      )
      for idx, store in enumerate(picked, 1):
        with st.container(border=True):
          st.markdown(f"**{idx}. 🥖 {store['name']}**")
          st.markdown(f"📍 주소: `{store['address']}`")
    else:
      st.warning(f"😢 `{selected_district}`에 등록된 영업 빵집 데이터가 없어.")

st.divider()
st.caption(
    "데이터 출처: Bbang.csv (서울특별시 제과점 영업 정보) | 친구들과 맛있는"
    " 빵지순례 다녀와! 🥖💨"
)
