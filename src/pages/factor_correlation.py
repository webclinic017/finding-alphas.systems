import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from urllib.request import urlopen
import json
from datetime import date
import FinanceDataReader as fdr
from sklearn.linear_model import LinearRegression
import plotly.express as px

def app():
    st.title('Portfolio-Factor Correlation Calculator')

    st.write('### Calculate the factor correlation of US ETFs using MSCI World index data')
    st.write('Below is [MSCI Index data](https://www.msci.com/end-of-day-data-search) used in calculating factor correlation')

    st.write('- `Market` : MSCI World Indexes\n- `Value` : MSCI World Enhanced Value Indexes\n- `Size` : MSCI World Small Cap Indexes\n- `Momentum` : MSCI World Momentum Indexes\n- `Quality` : MSCI World Quality Indexes\n- `Yield` : MSCI World High Dividend Yield Indexes\n- `Growth` : MSCI World Growth Indexes\n- `Volatility` : MSCI WORLD Minimum Volatility Indexes')

    # Type US ETF Ticker to Analysis
    etf_ticker = st.text_input('Type US ETF Ticker to Analysis', 'SOXX')

    # Set Start Date for Analysis
    start_date = st.date_input("Set Start Date for Analysis", date(2019, 1, 1))
    start_date = str(start_date).replace("-","")

    # Set End Date for Analysis
    end_date = st.date_input("Set End Date for Analysis", date.today())
    end_date = str(end_date).replace("-", "")

    # Select Correlation Analysis Method
    corr_dict = {'Pearson': 'pearson', 'Spearman': 'spearman', 'Kendall': 'kendall'}
    selected_method = st.radio("Correlation Analysis Method", list(corr_dict.keys()))
    corr_method = corr_dict[selected_method]

    if (st.button('Calculate correlation')):

        # ETF 데이터 다운로드
        etf_data = fdr.DataReader(etf_ticker.capitalize())
        # soxx = fdr.DataReader('SOXX')#,'2015-01-01')
        # start_date = str(soxx.index[0]).split(" ")[0].replace("-","")

        # 다음 자료들을 참고하여 MSCI Indexes 데이터 다운로드
        # https://www.msci.com/documents/1296102/15220828/Introducing-MSCI-Factor-Index.pdf/a2c494d1-56b8-726d-33ee-4fe4319b12c6
        # https://www.msci.com/end-of-day-data-search
        factor_MSCI_dict = {
            "Market" : 990100, # MSCI WORLD Indexes
            "Value" : 705130, # MSCI WORLD Enhanced Value Indexes
            "Size" : 106230, # MSCI WORLD SMALL CAP Indexes
            "Momentum" : 703755, # MSCI WORLD Momentum Indexes
            "Quality" : 702787, # MSCI WORLD Quality Indexes
            "Yield" : 136064, # MSCI WORLD High Dividend Yield Indexes
            "Growth" : 105867, # MSCI WORLD Growth Indexes
            "Volatility" : 129896, # MSCI WORLD Minimum Volatility Indexes
        }

        url = "https://app2.msci.com/products/service/index/indexmaster/getLevelDataForGraph?currency_symbol=USD&index_variant=STRD&data_frequency=DAILY"

        factor_MSCI_price_df = pd.DataFrame()
        for key, value in factor_MSCI_dict.items():
            url_request = url + "&start_date=" + start_date + "&end_date=" + end_date + "&index_codes=" + str(value)
            response = urlopen(url_request)

            json_data = response.read().decode('utf-8', 'replace')

            d = json.loads(json_data)
            df = pd.DataFrame(d['indexes']['INDEX_LEVELS'])
            df['calc_date'] = pd.to_datetime(df['calc_date'].astype(str))
            df.set_index('calc_date', inplace=True)

            factor_MSCI_price_df[key] = df['level_eod']

        # 존재하는 Date에 따라 inner join merge
        merge_df = factor_MSCI_price_df.merge(etf_data['Close'], how='inner', left_index=True, right_index=True)

        # Linear Regression 학습
        X = merge_df.loc[:, merge_df.columns[:-1]]
        y = merge_df.loc[:, merge_df.columns[-1]]
        model = LinearRegression()
        model.fit(X, y)

        for factor, value in zip(merge_df.columns, model.coef_):
            print(factor + ": " + str(value))

        merge_df_pnl = merge_df.diff().fillna(0)
        corr_df = pd.DataFrame(merge_df_pnl.corr(corr_method)['Close'][:-1])

        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
        col1.metric("Market", "."+str(round(merge_df_pnl.corr()['Close'][0]*100)))
        col2.metric("Value", "."+str(round(merge_df_pnl.corr()['Close'][1]*100)))
        col3.metric("Size", "."+str(round(merge_df_pnl.corr()['Close'][2]*100)))
        col4.metric("Momentum", "."+str(round(merge_df_pnl.corr()['Close'][3]*100)))
        col5.metric("Quality", "."+str(round(merge_df_pnl.corr()['Close'][4]*100)))
        col6.metric("Yield", "."+str(round(merge_df_pnl.corr()['Close'][5]*100)))
        col7.metric("Growth", "."+str(round(merge_df_pnl.corr()['Close'][6]*100)))
        col8.metric("Volatility", "."+str(round(merge_df_pnl.corr()['Close'][7]*100)))

        fig = px.bar(corr_df, orientation='h',
                     labels={
                         "value": "Correlation",
                         "index": "Factor",
                     }
            )
        fig.update_layout(
            xaxis_title="Correlation",
            yaxis_title="Factor",
            title={
                'text': etf_ticker + "-Factor Correlation",
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)