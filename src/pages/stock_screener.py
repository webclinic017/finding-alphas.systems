import streamlit as st
import requests
import json
import pandas as pd

def app():
    st.title('Stock Screener')

    st.write('Find stocks with various criteria')

    features = {'Beta': [0.0, 2.0],
                'Average Volume (3 Months, $1K)': [0.0, 30000.0],
                'Dividend Yield (%)': [0.0, 1000.0],
                'Dividend Growth Rate (Annual)': [-100.0, 100.0]
                }
    feature_value = dict()

    for feature in features:
        min_value = features[feature][0]
        max_value = features[feature][1]
        unit = (max_value - min_value)/100
        feature_value[feature] = st.slider(feature, min_value, max_value, (min_value, max_value))

    if (st.button('Find Stocks')):
        with st.spinner(f"Finding and listing stocks ..."):

            params = {
                'country[]': '5',
                'sector': '7,5,21,12,3,16,8,17,13,9,19,1,6,18,15,20,14,23,2,4,10,11,22',
                'industry': '81,56,110,59,119,41,120,68,67,88,124,125,51,72,147,136,47,12,144,8,50,111,2,151,71,9,105,69,45,117,156,46,13,94,102,95,58,100,101,87,31,106,6,38,112,150,79,107,30,77,131,130,149,160,113,165,28,158,5,103,163,170,60,18,26,137,135,44,35,53,166,48,141,49,142,143,55,129,126,139,169,114,153,78,7,86,10,164,132,1,34,154,3,127,146,115,11,121,162,62,16,108,24,20,54,33,83,29,152,76,133,167,37,90,85,82,104,22,14,17,109,19,43,140,89,145,96,57,84,118,93,171,27,74,97,4,73,36,42,98,65,70,40,99,39,92,122,75,66,63,21,159,25,155,64,134,157,128,61,148,32,138,91,116,123,52,23,15,80,168,161',
                'equityType': 'ORD,DRC,Preferred,Unit,ClosedEnd,REIT,ELKS,OpenEnd,Right,ParticipationShare,CapitalSecurity,PerpetualCapitalSecurity,GuaranteeCertificate,IGC,Warrant,SeniorNote,Debenture,ETF,ADR,ETC,ETN',
                'exchange[]': '2,1,50,95',
                'eq_beta[min]': feature_value['Beta'][0],
                'eq_beta[max]': feature_value['Beta'][1],
                'avg_volume[min]': int(feature_value['Average Volume (3 Months, $1K)'][0]),
                'avg_volume[max]': int(feature_value['Average Volume (3 Months, $1K)'][1]),
                'yield_us[min]': feature_value['Dividend Yield (%)'][0],
                'yield_us[max]': feature_value['Dividend Yield (%)'][1],
                'divgrpct_us[min]': feature_value['Dividend Growth Rate (Annual)'][0],
                'divgrpct_us[max]': feature_value['Dividend Growth Rate (Annual)'][1],
                'pn': '1',
                'order[col]': 'eq_market_cap',
                'order[dir]': 'd'
            }

            url = "https://www.investing.com/stock-screener/Service/SearchStocks"

            headers = {'user-agent': 'Mozilla/5.0',
                       'accept': 'application/json, text/javascript, */*; q=0.01',
                       'x-requested-with': "XMLHttpRequest"}

            response = requests.post(url, data=params, headers=headers)
            response_dict = json.loads(response.content)
            stock_df = pd.DataFrame(response_dict['hits'])
            st.dataframe(stock_df)