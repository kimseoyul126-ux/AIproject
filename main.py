import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
a=st.text_input('이름을 입력하거라!')
b=st.selectbox('좋아하는 음식을 선택하거라!',['치킨','공차','마라탕','피자','불닭','휘낭시에'])
if st.button('인사말 생성'):
  st.write('반갑습니다!')
