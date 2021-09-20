import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import FinanceDataReader as fdr

def app():
    st.title('Monte-Carlo Simulation for Price Prediction')

    st.write('### Simple Monte-Carlo simulation for price prediction with daily historical price data')

    stock_dict = {
        "(Stock) Apple": "AAPL",
        "(Stock) Microsoft": "MSFT",
        "(Stock) Alphabet": "GOOG",
        "(Stock) Facebook": "FB",
        "(Stock) Samsung Electronics": "005930",
        "(Stock) SK Hynics": "000660",
        "(Stock) Naver": "035420",
        "(Stock) Kakao": "035720",
        "(Crypto) BTC/USD": "BTC/USD",
        "(Crypto) ETH/USD": "ETH/USD",
        "(Crypto) XRP/USD": "XRP/USD",
        "(FX) USD/EUR": "USD/EUR",
        "(FX) USD/JPY": "USD/JPY",
        "(FX) USD/KRW": "USD/KRW",
    }

    selected_stock_key = st.selectbox('Select price data to use in simulation', list(stock_dict.keys()))
    selected_stock_value = stock_dict[selected_stock_key]

    num_simulation = st.number_input("Number of simulations", value=1000)
    num_days = st.number_input("Number of days to simulate", value=252)

    if (st.button('Execute simulation')):
        # 데이터 로드
        price_df = fdr.DataReader(selected_stock_value, '2015-01-01')
        last_price = price_df['Close'][-1]

        simulation_df = pd.DataFrame()
        # 몬테카를로 시뮬레이션 진행
        for x in range(num_simulation):
            count = 0
            daily_vol = price_df['Change'].std()

            price_series = []

            price = last_price * (1 + np.random.normal(0, daily_vol))
            price_series.append(price)

            for y in range(num_days):
                price = price_series[count] * (1 + np.random.normal(0, daily_vol))
                price_series.append(price)
                count += 1

            simulation_df[x] = price_series

        fig = plt.figure()
        plt.suptitle('Monte Carlo Simulation for Price Prediction')
        plt.title('Last price of '+selected_stock_key+' : '+str(last_price))
        plt.plot(simulation_df)
        plt.axhline(y=last_price, color='r', linestyle='-')
        plt.xlabel('Day')
        plt.ylabel('Price')
        st.pyplot(fig)