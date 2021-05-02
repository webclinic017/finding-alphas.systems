import streamlit as st
import src.pages.home
import src.pages.black_scholes_model
import src.pages.square_test

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

PAGES = {
    "Home": src.pages.home,
    "Black-Scholes Model": src.pages.black_scholes_model,
    "Square Calculation Test": src.pages.square_test

}

st.sidebar.title("Navigation")
selection = st.sidebar.selectbox('Select',list(PAGES.keys()))

page = PAGES[selection]

with st.spinner(f"Running {selection} ..."):
    page.app()




