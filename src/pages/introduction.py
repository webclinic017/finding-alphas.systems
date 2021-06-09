import streamlit as st

def app():
    selected_lang = st.radio('Language', ("English", "한국어"))

    if (selected_lang == "English"):
        st.title("Introduction")
        st.write(
            "Project `Finding-alphas Systems` is a side project that I am working on while studying Quantitative Investment. I simply prototyped interesting topics and ideas into a web application. You can navigate and check the functions implemented so far through the navigation sidebar at the top left of the page.")


    elif (selected_lang == "한국어"):
        st.title("프로젝트 소개")
        st.write(
            "`Finding-alphas Systems` 프로젝트는 제가 Quantitative Investment 분야를 공부하며 진행하고 있는 사이드 프로젝트입니다. 흥미로운 주제와 아이디어들을 간단하게 웹 어플리케이션으로 프로토타이핑하여 구현하였습니다. 페이지의 왼쪽 상단 Navigation Sidebar를 통해 지금까지 구현된 기능들로 이동하여 확인할 수 있습니다.")
