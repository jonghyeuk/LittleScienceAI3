import streamlit as st

st.title("LittleScienceAI 도우미 - 테스트")
st.write("이것은 테스트 앱입니다.")

topic = st.text_input("연구 주제를 입력하세요:")
if topic:
    st.write(f"입력한 주제: {topic}")
    st.info("이 앱은 기본 테스트 버전입니다.")
