import streamlit as st
import scipy.stats as stat
import numpy as np
import plotly.graph_objs as go

def app():
    st.title('Black-Scholes Model')

    st.write('Theoretical estimate of the price of European-style options')

    option_type = st.radio("Option type", ('Call','Put'))
    S = st.number_input("Current underlying asset price", value=100)
    K = st.number_input("Strike price", value=100)
    r = st.number_input("Risk-free interest rate", value = 0.02)
    T = st.number_input("Time to maturity (Year)", value = 1.0)
    sigma = st.number_input("Standard deviation of the underlying asset's returns", value = 0.2)

    if (st.button('Estimate Option Price')):
        option_price = europian_option(S, K, T, r, sigma, option_type)
        st.write("The price of this option is ", option_price)

        with st.spinner(f"Plotting option price graph ..."):
            T_linspace = np.linspace(0, T, 100)
            S_linspace = np.linspace(0, S * 2, 100)
            T_grid, S_grid = np.meshgrid(T_linspace, S_linspace)
            option_price_list = europian_option(S_grid, K, T_grid, r, sigma, option_type)
            trace = go.Surface(x=T_grid, y=S_grid, z=option_price_list)
            data = [trace]

            layout = go.Layout(title='Option price graph',
                               scene={'xaxis': {'title': 'Maturity'},
                                      'yaxis': {'title': 'Spot Price'},
                                      'zaxis': {'title': 'Option Price'}})
            fig = go.Figure(data=data, layout=layout)
            st.plotly_chart(fig, use_container_width=True)

def europian_option(S, K, T, r, sigma, option_type):

    """
    :param S: 기초자산의 자격
    :param K: 행사 가격
    :param T: 잔존만기(3개월, 1년, ...)
    :param r: 무위험이자율
    :param sigma: 변동성
    :param option_type: 옵션 종류(call or put)
    :return: 옵션의 이론 가격
    """

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'Call':
        V = S * stat.norm.cdf(d1) - K * np.exp(-r * T) * stat.norm.cdf(d2)
    else:
        V = K * np.exp(-r * T) * stat.norm.cdf(-d2) - S * stat.norm.cdf(-d1)

    return V
