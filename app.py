import streamlit as st
import src.pages.introduction
import src.pages.black_scholes_model
import src.pages.stock_screener
import src.pages.monte_carlo_simulation
import src.pages.backtesting
import src.pages.cross_asset_momentum
import src.pages.factor_correlation

IMG_SRC = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/279/magnifying-glass-tilted-left_1f50d.png"

st.set_page_config(
    page_title = "Finding Alphas",
    page_icon = IMG_SRC,
)

# Display header.
st.markdown("<br>", unsafe_allow_html=True)
st.image(IMG_SRC, width=80)

"""
# Finding-alphas Systems
&nbsp[![Blog](https://img.shields.io/badge/Blog-Q's%20Tech%20Blog-red)](https://karl6885.github.io/)
"""
# 링크드인 링크 잠시 삭제(블라인드 채용) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Yeongkyu%20Kim-blue)](https://linkedin.com/in/yeongkyu-kim)

st.markdown("<br>", unsafe_allow_html=True)

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

PAGES = {
    "Introduction": src.pages.introduction,
    "Black-Scholes Model": src.pages.black_scholes_model,
    "Stock Screener": src.pages.stock_screener,
    "Monte Carlo Simulation": src.pages.monte_carlo_simulation,
    "Simple Backtesting": src.pages.backtesting,
    "Cross-Asset Momentum Backtesting": src.pages.cross_asset_momentum,
    "Portfolio-Factor Correlation": src.pages.factor_correlation

}

st.sidebar.title("Navigation")
selection = st.sidebar.selectbox('Select',list(PAGES.keys()))

page = PAGES[selection]

with st.spinner(f"Running {selection} ..."):
    page.app()




