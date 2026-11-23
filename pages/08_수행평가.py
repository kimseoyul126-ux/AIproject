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


# 12가지 다양한 디저트 유형별 대표 유명 제과점 데이터
DESSERT_DATA = {
    "🍦 모나카 아이스크림 & 사라다빵 (레트로)": {
        "keyword": "태극당",
        "display_name": "태극당 (장충동 본점)",
        "district": "중구",
        "history": "1946년 문을 연 서울에서 가장 오래된 전설의 빵집! 🏛️",
        "signature": "진한 우유 맛 '모나카 아이스크림' & 추억의 '야채 사라다빵'",
        "vibe": "할머니 댁에 놀러 온 듯한 힙한 레트로 감성과 80년 전통의 클래식한 맛!",
        "fallback_addr": "서울특별시 중구 장충동2가 189-5",
    },
    "🥖 쫄깃한 쪽파·바질 베이글": {
        "keyword": "런던베이글뮤지엄",
        "display_name": "런던베이글뮤지엄 안국점",
        "district": "종로구",
        "history": "오픈런 대란을 일으킨 대한민국 베이글 성지! 🔥",
        "signature": "쪽파 프레첼 베이글, 브릭레인 샌드위치, 감자치즈 베이글",
        "vibe": "런던 빈티지 카페에 온 것 같은 감성! 쫄깃하고 촉촉한 베이글 식감이 최고야.",
        "fallback_addr": "서울특별시 종로구 계동 102-1 연화빌딩",
    },
    "🧂 겉바속촉 버터 풍미 소금빵": {
        "keyword": "자연도소금빵",
        "display_name": "자연도소금빵 in 성수",
        "district": "성동구",
        "history": "성수동·연남동 줄 서서 먹는 소금빵 전문 핫플레이스! 🌊",
        "signature": "갓 구워낸 겉바속촉 '소금빵 4개 세트'",
        "vibe": "빵 나오는 시간마다 고소한 버터 향기가 골목을 가득 채우는 찐 맛집이야.",
        "fallback_addr": "서울특별시 성동구 성수동2가 321-74",
    },
    "🍩 폭신폭신 크림 가득 도넛": {
        "keyword": "노티드",
        "display_name": "카페 노티드 (Knotted) 청담",
        "district": "강남구",
        "history": "K-디저트 도넛 열풍의 주인공, 귀여운 스마일 마스코트 맛집! 😊",
        "signature": "우유 생크림 도넛, 얼그레이 도넛, 클래식 바닐라 도넛",
        "vibe": "한 입 베어 물면 크림이 팡! 터지는 행복함. 친구들이랑 인증샷 찍기 딱 좋아.",
        "fallback_addr": "서울특별시 강남구 신사동 603-4",
    },
    "🥐 결이 살아있는 슈크림 & 밤식빵": {
        "keyword": "리치몬드과자점",
        "display_name": "리치몬드 과자점 (성산본점)",
        "district": "마포구",
        "history": "1979년부터 이어온 대한민국 제과명장의 자존심! 👑",
        "signature": "바닐라빈 콕콕 박힌 '슈크림' & 밤이 쏟아지는 '공주 밤식빵'",
        "vibe": "기본에 충실한 진짜 빵의 정석! 부모님과 함께 가도 대만족하는 명품 빵집.",
        "fallback_addr": "서울특별시 마포구 성산동 114-5 1,2층",
    },
    "🎂 달콤한 케이크 & 몽블랑": {
        "keyword": "김영모과자점",
        "display_name": "김영모 과자점 (서초본점)",
        "district": "서초구",
        "history": "1982년 개업, 서울 3대 빵집으로 꼽히는 국가대표 명장 베이커리! 🏆",
        "signature": "부드러운 '뉴고구마케이크', 바게트 샌드위치, 몽블랑",
        "vibe": "유기농 밀가루와 천연 발효종을 사용해 먹고 나도 속이 편한 고급스러운 맛!",
        "fallback_addr": "서울특별시 서초구 서초동 1757-1",
    },
    "🫘 묵직한 통단팥빵 & 맘모스빵": {
        "keyword": "쟝블랑제리",
        "display_name": "쟝블랑제리 (낙성대 본점)",
        "district": "관악구",
        "history": "1996년부터 서울대입구·낙성대를 지켜온 '빵지순례' 필수 코스! 🎒",
        "signature": "묵직한 '단팥빵', 생크림 팥빵, 거대한 크기의 '맘모스빵'",
        "vibe": "빵 하나만 들어도 아령처럼 묵직한 가성비와 혜자로운 속재료가 매력 포인트!",
        "fallback_addr": "서울특별시 관악구 봉천동 1660-7",
    },
    "🍰 클래식 사라다빵 & 생크림 케이크": {
        "keyword": "나폴레옹",
        "display_name": "나폴레옹 과자점 (성북본점)",
        "district": "성북구",
        "history": "1968년 개업! 대한민국 제과 기능장들을 배출한 '빵집 사관학교' 🎓",
        "signature": "원조 '사라다빵', 부드러운 '크림빵', 구운 도넛",
        "vibe": "50년 넘게 한자리를 지켜온 서울 3대 빵집! 실패 없는 클래식한 매력이 있어.",
        "fallback_addr": "서울특별시 성북구 성북동1가 35-5",
    },
    "🐢 귀엽고 달콤한 아기궁뎅이빵": {
        "keyword": "피터팬",
        "display_name": "피터팬 1978 (연희동 본점)",
        "district": "서대문구",
        "history": "1978년부터 연희동 골목을 지켜온 동네 터줏대감 맛집! 🏡",
        "signature": "폭신폭신한 '아기궁뎅이빵', 장발장이 훔친 빵, 크림치즈 먹물빵",
        "vibe": "이름부터 귀여운 시그니처 빵들이 가득! 연희동 산책하면서 들르기 딱 좋아.",
        "fallback_addr": "서울특별시 서대문구 연희동 90-5",
    },
    "🍫 꾸덕한 더티초코 & 빨미까레": {
        "keyword": "아우어베이커리",
        "display_name": "아우어 베이커리 (광화문·인사동)",
        "district": "종로구",
        "history": "페이스트리 열풍을 이끈 트렌디 베이커리 카페! 🖤",
        "signature": "초코 코코아 파우더 듬뿍 '더티초코', 바삭한 '빨미까레'",
        "vibe": "달달하고 꾸덕한 초코 충전을 원할 때 무조건 추천하는 힙한 공간이야.",
        "fallback_addr": "서울특별시 종로구 신문로2가 171",
    },
    "🍞 촉촉한 탕종 식빵 & 큐브식빵": {
        "keyword": "밀도",
        "display_name": "성수동 밀도 (Meal°)",
        "district": "성동구",
        "history": "온도와 습도까지 계산해 굽는 식빵 전문 베이커리! 🌡️",
        "signature": "담백한 '담백식빵', 커스터드 크림 가득한 '큐브식빵'",
        "vibe": "손으로 찢어 먹을 때 결대로 쭉쭉 늘어나는 쫄깃하고 촉촉한 식감이 예술이야.",
        "fallback_addr": "서울특별시 성동구 성수동1가 656-442",
    },
    "🌾 고소한 통밀빵 & 무화과 호밀빵": {
        "keyword": "베이커리오월의종",
        "display_name": "오월의 종 (한남동 본점)",
        "district": "용산구",
        "history": "천연 효모 발효빵의 교과서로 불리는 이태원·한남동 터줏대감! 🌿",
        "signature": "무화과 호밀빵, 크랜베리 바게트, 올리브 치아바타",
        "vibe": "달지 않고 씹을수록 고소한 곡물 풍미! 건강한 식사 빵을 좋아한다면 강추해.",
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
st.title("🥐 서울 찐 제과점 추천소 🍰")
st.markdown(
    "좋아하는 **디저트 취향**이랑 **가고 싶은 동네(구)**를 골라봐! 😋\n"
    "**`Bbang.csv` 실제 영업 데이터**를 뒤져서 찐 맛집을 매칭해 줄게 ✨"
)
st.divider()

# 데이터 로드
active_bakeries = load_active_bakeries()

# 2단 컬럼으로 디저트 + 지역 선택 배치
col1, col2 = st.columns(2)

with col1:
  selected_dessert = st.selectbox(
      "🍩 1. 좋아하는 디저트 고르기", options=list(DESSERT_DATA.keys())
  )

with col2:
  selected_district = st.selectbox(
      "📍 2. 가고 싶은 지역(구) 고르기", options=SEOUL_DISTRICTS
  )

# 추천 버튼
if st.button(
    "🎉 나만의 찐 제과점 추천받기!", use_container_width=True, type="primary"
):
  info = DESSERT_DATA[selected_dessert]

  # 1) 선택한 디저트의 대표 유명 제과점 검증
  matched_address = info["fallback_addr"]
  is_verified = False

  for store in active_bakeries:
    if info["keyword"] in store["name"]:
      if store["address"]:
        matched_address = store["address"]
      is_verified = True
      break

  st.balloons()
  st.subheader(f"🏆 오늘의 대표 추천: {info['display_name']}")

  with st.container(border=True):
    st.markdown(f"**✨ 가게 소개:** {info['history']}")
    st.markdown(f"**😋 대표 메뉴:** {info['signature']}")
    st.markdown(f"**💡 추천 포인트:** {info['vibe']}")
    st.markdown(
        f"**📍 위치 주소:** `{matched_address}` (지역: **{info['district']}**)"
    )

    if is_verified:
      st.success("✅ `Bbang.csv` 확인 완료! 현재 **정상 영업 중**인 가게야. 🏪")

  # 2) 사용자가 특정 지역(구)을 선택했을 때, 해당 구의 실제 영업 중인 제과점도 함께 추천!
  if selected_district != "전체 (서울 어디든 좋아!)":
    st.divider()
    st.subheader(f"🗺️ '{selected_district}'에서 지금 영업 중인 추천 빵집!")

    district_stores = [
        s for s in active_bakeries if s["district"] == selected_district
    ]

    if district_stores:
      # 유명 프랜차이즈 외에 개성 있는 로컬 빵집을 우선적으로 최대 5곳 랜덤 추천
      sample_count = min(5, len(district_stores))
      picked_stores = random.sample(district_stores, sample_count)

      st.caption(
          f"💡 `{selected_district}`에는 총 **{len(district_stores)}개**의"
          " 제과점이 영업 중이야! 그중 5곳을 뽑아봤어 👇"
      )
      for idx, store in enumerate(picked_stores, 1):
        with st.container(border=True):
          st.markdown(f"**{idx}. 🥖 {store['name']}**")
          st.markdown(f"📍 주소: `{store['address']}`")
    else:
      st.warning(
          f"😢 `{selected_district}` 데이터에서 일치하는 가게를 찾지 못했어."
          " 다른 구를 선택해 볼래?"
      )

st.divider()
st.caption(
    "데이터 출처: Bbang.csv (서울특별시 제과점 영업 정보) | 친구들이랑 맛있는"
    " 빵지순례 다녀와! 🥖💨"
)
