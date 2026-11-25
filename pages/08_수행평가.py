import csv
import os
import random
import urllib.parse
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


# 네이버 지도 검색 링크 생성 함수
def make_naver_map_url(store_name, district=""):
  query = f"서울 {district} {store_name}".strip()
  encoded = urllib.parse.quote(query)
  return f"https://map.naver.com/p/search/{encoded}"


# 12가지 기본 추천 디저트 유형
DESSERT_DATA = {
    "✍️ 직접 입력할래요! (원하는 빵·디저트 검색)": {
        "keywords": [],
        "display_name": "나만의 맞춤형 디저트 찾기",
        "default_name": "",
        "default_dist": "",
        "history": "내가 지금 딱 먹고 싶은 그 빵을 찾아보자! 🔍",
        "signature": "직접 입력한 최애 디저트",
        "fallback_addr": "",
    },
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
    "먹고 싶은 **디저트 종류**를 고르거나 **직접 입력**해 봐! ✍️\n"
    "선택한 **지역(구)** 안에서 실제 영업 중인 빵집을 찾아줄게 ✨"
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

# 직접 입력 옵션 선택 시 텍스트 입력창 표시
custom_bread = ""
if "직접 입력" in selected_dessert:
  custom_bread = st.text_input(
      "✍️ 찾고 싶은 빵이나 디저트 이름을 적어줘!",
      placeholder="예: 에그타르트, 크루아상, 마카롱, 꽈배기, 카스테라, 바게트...",
  ).strip()

# 버튼 클릭 후 실행 결과 저장용 변수 (그래프 연동을 위해 활용)
active_keywords_for_chart = []
search_performed = False

# 추천 버튼
if st.button(
    "🎉 내 조건에 딱 맞는 빵집 찾기!", use_container_width=True, type="primary"
):
  search_performed = True
  is_custom = "직접 입력" in selected_dessert

  if is_custom and not custom_bread:
    st.warning("👀 찾고 싶은 빵 이름을 먼저 입력해 줘!")
  else:
    if selected_district == "전체 (서울 어디든 좋아!)":
      pool = active_bakeries
    else:
      pool = [s for s in active_bakeries if s["district"] == selected_district]

    if is_custom:
      active_keywords_for_chart = [custom_bread]
      clean_kw = custom_bread.replace(" ", "")
      exact_matches = [
          s for s in pool if clean_kw in s["name"].replace(" ", "")
      ]

      st.balloons()
      st.subheader(f"🔍 '{custom_bread}' 검색 결과 ({selected_district})")

      if exact_matches:
        st.success(
            f"🎉 `{selected_district}`에서 **'{custom_bread}'** 관련 영업 중인"
            f" 가게 **{len(exact_matches)}곳**을 찾았어!"
        )
        for idx, store in enumerate(exact_matches[:6], 1):
          with st.container(border=True):
            # 🔥 가게 이름을 크고 굵게 강조!
            st.markdown(f"### {idx}. 🥖 {store['name']}")
            st.markdown(
                f"📍 위치 주소: `{store['address']}` ({store['district']})"
            )
            st.link_button(
                "🗺️ 네이버 지도로 위치·후기 보기",
                make_naver_map_url(store["name"], store["district"]),
            )
      else:
        st.info(
            f"💡 상호명에 직접 '{custom_bread}'가 들어간 곳은 없지만, 지금"
            f" **`{selected_district}`에서 영업 중인 인기 제과점**을 골라봤어!"
        )
        if pool:
          picked = random.sample(pool, min(4, len(pool)))
          for idx, store in enumerate(picked, 1):
            with st.container(border=True):
              # 🔥 가게 이름을 크고 굵게 강조!
              st.markdown(f"### {idx}. 🥐 {store['name']}")
              st.markdown(f"📍 위치 주소: `{store['address']}`")
              st.link_button(
                  f"🗺️ '{store['name']}' 메뉴 확인하기",
                  make_naver_map_url(store["name"], store["district"]),
              )
        else:
          st.warning(
              f"😢 `{selected_district}` 데이터에 등록된 가게가 없어. 다른"
              " 지역을 골라볼래?"
          )

    else:
      dessert_info = DESSERT_DATA[selected_dessert]
      active_keywords_for_chart = dessert_info["keywords"]
      matched_stores = [
          s
          for s in pool
          if any(kw in s["name"] for kw in dessert_info["keywords"])
      ]

      st.balloons()
      st.subheader(
          f"🏆 '{selected_dessert.split(' ')[-1]}' 찐 맛집 추천"
          f" ({selected_district})"
      )

      with st.container(border=True):
        st.markdown(f"**✨ 디저트 테마:** {dessert_info['display_name']}")
        st.markdown(f"**📖 설명 및 역사:** {dessert_info['history']}")
        st.markdown(f"**😋 대표 메뉴:** {dessert_info['signature']}")

        if (
            selected_district == "전체 (서울 어디든 좋아!)"
            or dessert_info["default_dist"] == selected_district
        ):
          # 🔥 대표 가게 이름을 크고 굵게 강조!
          st.markdown(f"### 🏆 {dessert_info['default_name']}")
          st.markdown(f"**📍 위치 주소:** `{dessert_info['fallback_addr']}`")
          st.success(
              "✅ `Bbang.csv` 공공데이터 확인 완료! 현재 **정상 영업 중**인"
              " 대표 랜드마크야. 🏪"
          )
          st.link_button(
              "🗺️ 네이버 지도로 길찾기",
              make_naver_map_url(
                  dessert_info["default_name"], dessert_info["default_dist"]
              ),
          )
        elif matched_stores:
          top_store = matched_stores[0]
          # 🔥 찾은 가게 이름을 크고 굵게 강조!
          st.markdown(f"### 🏆 {top_store['name']}")
          st.markdown(f"**📍 위치 주소:** `{top_store['address']}`")
          st.success(
              f"✅ `{selected_district}` 내에서 조건에 맞는 영업 중인 빵집을"
              " 찾았어! 🥖"
          )
          st.link_button(
              "🗺️ 네이버 지도로 길찾기",
              make_naver_map_url(top_store["name"], top_store["district"]),
          )
        else:
          st.markdown(
              f"**📍 추천 장소:** `{dessert_info['default_name']} (타 지역"
              " 본점)`"
          )
          st.markdown(f"**📍 위치 주소:** `{dessert_info['fallback_addr']}`")
          st.info(
              f"💡 선택하신 `{selected_district}` 안에는 해당 테마의 대표 본점이"
              " 없어서 서울 랜드마크 본점을 먼저 소개해 줄게! ✨"
          )
          st.link_button(
              "🗺️ 네이버 지도로 길찾기",
              make_naver_map_url(
                  dessert_info["default_name"], dessert_info["default_dist"]
              ),
          )

      if selected_district != "전체 (서울 어디든 좋아!)" and pool:
        st.divider()
        st.subheader(
            f"🗺️ '{selected_district}'에서 지금 갈 수 있는 다른 빵집들!"
        )
        picked = random.sample(pool, min(4, len(pool)))
        for idx, store in enumerate(picked, 1):
          with st.container(border=True):
            # 🔥 리스트 가게 이름을 크고 굵게 강조!
            st.markdown(f"### {idx}. 🥖 {store['name']}")
            st.markdown(f"📍 주소: `{store['address']}`")
            st.link_button(
                "🗺️ 네이버 지도 보기",
                make_naver_map_url(store["name"], store["district"]),
            )

# --- 📊 입력한 디저트에 따라 실시간으로 변하는 그래프 섹션 ---
st.divider()

# 사용자가 어떤 디저트를 골랐거나 입력했느냐에 따라 그래프 제목과 데이터를 동적으로 변경!
current_selection_name = (
    selected_dessert.split(" ")[-1]
    if "직접 입력" not in selected_dessert
    else (custom_bread if custom_bread else "선택한 디저트")
)

st.subheader(
    f"📊 '{current_selection_name}' 관련 빵집이 가장 많은 서울 핫플 TOP 10!"
)

if active_bakeries:
  # 만약 사용자가 특정 디저트를 골랐다면, 해당 키워드가 포함된 가게들만 필터링하여 구별 집계!
  filtered_for_chart = active_bakeries
  if "직접 입력" not in selected_dessert and DESSERT_DATA[selected_dessert][
      "keywords"
  ]:
    kws = DESSERT_DATA[selected_dessert]["keywords"]
    filtered_for_chart = [
        s for s in active_bakeries if any(kw in s["name"] for kw in kws)
    ]
  elif "직접 입력" in selected_dessert and custom_bread:
    clean_kws = custom_bread.replace(" ", "")
    filtered_for_chart = [
        s for s in active_bakeries if clean_kws in s["name"].replace(" ", "")
    ]

  # 필터링된 결과가 너무 적으면 전체 서울 기준으로 보여주되 안내 문구 출력
  is_fallback_to_all = False
  if len(filtered_for_chart) < 3:
    filtered_for_chart = active_bakeries
    is_fallback_to_all = True

  # 자치구별 집계
  district_counts = {}
  for store in filtered_for_chart:
    d = store["district"]
    if d != "기타":
      district_counts[d] = district_counts.get(d, 0) + 1

  top10 = sorted(district_counts.items(), key=lambda x: x[1], reverse=True)[:10]
  chart_data = {gu: count for gu, count in top10}

  if is_fallback_to_all:
    st.markdown(
        f"💡 '{current_selection_name}' 키워드와 정확히 일치하는 매장 데이터가"
        " 적어서, 전체 제과점 기준 자치구별 분포를 보여줄게! 📈"
    )
  else:
    st.markdown(
        f"✨ 서울 전체에서 **'{current_selection_name}'** 관련 빵집이 가장 많이"
        " 포진해 있는 지역 순위야 🏆"
    )

  # 스트림릿 막대그래프 출력 (디저트에 따라 막대 색상이나 데이터가 실시간으로 바뀜!)
  st.bar_chart(chart_data, color="#FF6B6B")

  if top10:
    top_gu, top_cnt = top10[0]
    st.info(
        f"🔥 **인사이트:** '{current_selection_name}' 관련 빵집은"
        f" **{top_gu}**({top_cnt개})에 가장 많이 모여있어! 이쪽으로 빵지순례"
        " 계획을 짜보면 어떨까? 😎"
    )

st.divider()
st.caption(
    "데이터 출처: Bbang.csv (서울특별시 제과점 영업 정보) | 친구들과 맛있는"
    " 빵지순례 다녀와! 🥖💨"
)
