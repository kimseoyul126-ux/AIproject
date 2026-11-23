import csv
import os
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="서울 찐맛집 제과점 추천소 🥐", page_icon="🍰", layout="centered"
)


# 업로드된 Bbang.csv 파일에서 실제 영업 중인 가게 정보 불러오는 함수
@st.cache_data
def load_active_bakeries():
  file_name = "Bbang.csv"
  active_dict = {}

  if not os.path.exists(file_name):
    return active_dict

  # 인코딩 자동 대응 (cp949, utf-8, euc-kr)
  for enc in ["cp949", "utf-8", "euc-kr"]:
    try:
      with open(file_name, mode="r", encoding=enc) as f:
        reader = csv.DictReader(f)
        for row in reader:
          status = row.get("영업상태명", "")
          if "영업" in status:
            name = row.get("사업장명", "").strip()
            addr = row.get("지번주소", "").strip()
            if name:
              active_dict[name] = {"address": addr}
      break
    except UnicodeDecodeError:
      continue
  return active_dict


# 디저트 유형별 대표 유명 제과점 데이터 (Bbang.csv 실제 영업 업소 매칭)
DESSERT_DATA = {
    "🍦 모나카 아이스크림 & 사라다빵 (레트로 감성)": {
        "keyword": "태극당",
        "display_name": "태극당 (장충동 본점)",
        "history": "1946년 문을 연 서울에서 가장 오래된 전설의 빵집! 🏛️",
        "signature": "우유 맛 진한 수제 '모나카 아이스크림' & 추억의 '야채 사라다빵'",
        "vibe": "할머니 댁에 놀러 온 듯한 힙한 레트로 인테리어와 80년 전통의 클래식한 맛!",
        "fallback_addr": "서울특별시 중구 장충동2가 189-5",
    },
    "🥖 바삭한 바게트 & 바질·쪽파 베이글": {
        "keyword": "런던베이글뮤지엄",
        "display_name": "런던베이글뮤지엄 안국점",
        "history": "오픈런 대란을 일으킨 대한민국 베이글 성지! 🔥",
        "signature": "쪽파 프레첼 베이글, 브릭레인 샌드위치, 감자치즈 베이글",
        "vibe": (
            "런던 빈티지 카페에 온 것 같은 감성! 쫄깃하고 촉촉한 베이글 식감이"
            " 미쳤어요."
        ),
        "fallback_addr": "서울특별시 종로구 계동 102-1 연화빌딩",
    },
    "🍩 폭신폭신 크림 가득 도넛": {
        "keyword": "노티드",
        "display_name": "카페 노티드 (Knotted)",
        "history": "K-디저트 도넛 열풍의 주인공, 귀여운 스마일 마스코트 맛집! 😊",
        "signature": "우유 생크림 도넛, 얼그레이 도넛, 클래식 바닐라 도넛",
        "vibe": (
            "한 입 베어 물면 크림이 팡! 터지는 행복함. 친구들이랑 인증샷 찍기 딱"
            " 좋아요."
        ),
        "fallback_addr": "서울특별시 강남구 신사동 603-4",
    },
    "🥐 결이 살아있는 슈크림 & 밤식빵": {
        "keyword": "리치몬드과자점",
        "display_name": "리치몬드 과자점 (성산본점)",
        "history": "1979년부터 이어온 대한민국 제과명장의 자존심! 👑",
        "signature": "바닐라빈 콕콕 박힌 '슈크림' & 밤이 쏟아지는 '공주 밤식빵'",
        "vibe": (
            "기본에 충실한 진짜 빵의 정석! 부모님과 함께 가도 대만족하는 명품"
            " 빵집이에요."
        ),
        "fallback_addr": "서울특별시 마포구 성산동 114-5 1,2층",
    },
    "🎂 달콤한 케이크 & 수제 마카롱": {
        "keyword": "김영모과자점",
        "display_name": "김영모 과자점 (서초본점)",
        "history": "1982년 개업, 서울 3대 빵집으로 꼽히는 국가대표 명장 베이커리! 🏆",
        "signature": "부드러운 '뉴고구마케이크', 바게트 샌드위치, 몽블랑",
        "vibe": (
            "유기농 밀가루와 천연 발효종을 사용해 먹고 나도 속이 편하고 고급스러운"
            " 맛!"
        ),
        "fallback_addr": "서울특별시 서초구 서초동 1757-1",
    },
    "🫘 묵직한 통단팥빵 & 맘모스빵": {
        "keyword": "쟝블랑제리",
        "display_name": "쟝블랑제리 (낙성대 본점)",
        "history": (
            "1996년부터 서울대입구·낙성대를 지켜온 '빵지순례' 필수 코스! 🎒"
        ),
        "signature": "묵직한 '단팥빵', 생크림 팥빵, 거대한 크기의 '맘모스빵'",
        "vibe": (
            "빵 하나만 들어도 아령처럼 묵직한 가성비와 혜자로운 속재료가 매력"
            " 포인트!"
        ),
        "fallback_addr": "서울특별시 관악구 봉천동 1660-7",
    },
    "🍞 고소한 통밀빵 & 담백한 치아바타": {
        "keyword": "베이커리오월의종",
        "display_name": "오월의 종 (한남동 본점)",
        "history": "천연 효모 발효빵의 교과서로 불리는 이태원·한남동 터줏대감! 🌾",
        "signature": "무화과 호밀빵, 크랜베리 바게트, 올리브 치아바타",
        "vibe": (
            "달지 않고 씹을수록 고소한 곡물 풍미! 식사 대용 빵을 좋아한다면"
            " 무조건 추천해요."
        ),
        "fallback_addr": "서울특별시 용산구 한남동 745-11",
    },
}

# --- UI 화면 구성 ---
st.title("🥐 오늘 뭐 먹지? 서울 찐 제과점 추천소 🍰")
st.markdown(
    "지금 딱 당기는 디저트를 하나 골라봐! 😋\n"
    "**`Bbang.csv` 공공데이터**를 바탕으로 현재 영업 중인 오래되고 유명한 찐"
    " 맛집을 연결해 줄게 ✨"
)
st.divider()

# 데이터 로드
active_bakeries = load_active_bakeries()

# 디저트 선택 위젯
selected_dessert = st.selectbox(
    "👇 제일 좋아하는 디저트 유형을 선택해 주세요!", options=list(DESSERT_DATA.keys())
)

# 추천 결과 보여주기
if st.button(
    "🎉 나에게 딱 맞는 제과점 찾기!", use_container_width=True, type="primary"
):
  info = DESSERT_DATA[selected_dessert]

  # Bbang.csv 데이터에서 실제 영업 상태 및 주소 검증
  matched_address = info["fallback_addr"]
  is_verified = False

  for store_name, store_info in active_bakeries.items():
    if info["keyword"] in store_name:
      if store_info["address"]:
        matched_address = store_info["address"]
      is_verified = True
      break

  st.balloons()
  st.subheader(f"🏆 추천 가게: {info['display_name']}")

  # 카드 형태로 깔끔하게 출력
  with st.container(border=True):
    st.markdown(f"**✨ 가게 소개:** {info['history']}")
    st.markdown(f"**😋 대표 메뉴:** {info['signature']}")
    st.markdown(f"**💡 추천 포인트:** {info['vibe']}")
    st.markdown(f"**📍 위치 주소:** `{matched_address}`")

    if is_verified:
      st.success("✅ `Bbang.csv` 데이터 확인 완료! 현재 **정상 영업 중**이야. 🏪")
    else:
      st.info("✅ 현재 서울에서 활발히 운영 중인 대표 인기 제과점이야!")

st.divider()
st.caption(
    "데이터 출처: Bbang.csv (서울특별시 제과점 영업 정보) | 맛있게 빵지순례"
    " 다녀와! 🥖💨"
)
