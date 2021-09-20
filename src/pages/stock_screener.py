import streamlit as st
import requests
import json
import pandas as pd

def app():
    st.title('Stock Screener')

    st.write('### Find stocks with various criteria')
    default_criteria = ['PER','PBR','EPS','Beta']
    criteria_dict = load_criteria_dict()

    criteria_list = sorted(criteria_dict.keys())

    control_criteria = st.multiselect('Select criteria to use', criteria_list, default_criteria)

    criteria_value = dict()

    for criterion in control_criteria:
        min_value = criteria_dict[criterion]['min_value']
        max_value = criteria_dict[criterion]['max_value']
        criteria_value[criterion] = st.slider(criterion, min_value, max_value, (min_value, max_value))

    if (st.button('Find Stocks')):
        with st.spinner(f"Finding and listing stocks ..."):

            params = {
                'country[]': '5',
                'sector': '7,5,21,12,3,16,8,17,13,9,19,1,6,18,15,20,14,23,2,4,10,11,22',
                'industry': '81,56,110,59,119,41,120,68,67,88,124,125,51,72,147,136,47,12,144,8,50,111,2,151,71,9,105,69,45,117,156,46,13,94,102,95,58,100,101,87,31,106,6,38,112,150,79,107,30,77,131,130,149,160,113,165,28,158,5,103,163,170,60,18,26,137,135,44,35,53,166,48,141,49,142,143,55,129,126,139,169,114,153,78,7,86,10,164,132,1,34,154,3,127,146,115,11,121,162,62,16,108,24,20,54,33,83,29,152,76,133,167,37,90,85,82,104,22,14,17,109,19,43,140,89,145,96,57,84,118,93,171,27,74,97,4,73,36,42,98,65,70,40,99,39,92,122,75,66,63,21,159,25,155,64,134,157,128,61,148,32,138,91,116,123,52,23,15,80,168,161',
                'equityType': 'ORD,DRC,Preferred,Unit,ClosedEnd,REIT,ELKS,OpenEnd,Right,ParticipationShare,CapitalSecurity,PerpetualCapitalSecurity,GuaranteeCertificate,IGC,Warrant,SeniorNote,Debenture,ETF,ADR,ETC,ETN',
                'exchange[]': '2,1,50,95',
                'order[col]': 'eq_market_cap',
                'order[dir]': 'd'
            }

            for criterion in control_criteria:
                params[criteria_dict[criterion]['min_key']] = criteria_value[criterion][0]
                params[criteria_dict[criterion]['max_key']] = criteria_value[criterion][1]

            url = "https://www.investing.com/stock-screener/Service/SearchStocks"

            headers = {'user-agent': 'Mozilla/5.0',
                       'accept': 'application/json, text/javascript, */*; q=0.01',
                       'x-requested-with': "XMLHttpRequest"}

            response = requests.post(url, data=params, headers=headers)
            response_dict = json.loads(response.content)
            stock_df = pd.DataFrame(response_dict['hits'])

            # 한 번 요청할 때마다 최대 50개(1페이지당)만 보여주기 때문에 여러번 크롤링 진행
            totalCount = response_dict['totalCount']
            st.write('Number of stocks found:', totalCount)
            # 만약 주식 개수가 300개를 넘으면 300개만 보여준다.
            if (totalCount > 300):
                st.write('If the number of stocks found is more than 300, then only 300 stocks will be displayed.')
            crawling_try = min(totalCount // 50 + 1, 5)

            for i in range(crawling_try):
                params['pn'] = i+2
                response = requests.post(url, data=params, headers=headers)
                response_dict_temp = json.loads(response.content)
                stock_df_temp = pd.DataFrame(response_dict_temp['hits'])
                stock_df = stock_df.append(stock_df_temp, ignore_index=True)

            stock_df_display = stock_df[['name_trans','stock_symbol','exchange_trans','industry_trans','last','eq_market_cap','turnover_volume','avg_volume','a52_week_high','a52_week_low','eq_pe_ratio','eq_dividend','eq_eps','eq_beta','eq_revenue','RSI','STOCH','CCI','MACD','WilliamsR','STOCHRSI','ATR','HL','UO','ROC']]
            st.dataframe(stock_df_display)

def load_criteria_dict():

    criteria = {'Beta':
                    {'min_key': 'eq_beta[min]',
                     'max_key': 'eq_beta[max]',
                     'min_value': 0.0,
                     'max_value': 2.0},
                'Average Volume (3 Months, $1K)':
                    {'min_key': 'avg_volume[min]',
                     'max_key': 'avg_volume[max]',
                     'min_value': 0.0,
                     'max_value': 30000.0},
                'Dividend Yield (%)':
                    {'min_key': 'avg_volume[min]',
                     'max_key': 'avg_volume[max]',
                     'min_value': 0.0,
                     'max_value': 1000.0},
                'Dividend Growth Rate (Annual)':
                    {'min_key': 'divgrpct_us[min]',
                     'max_key': 'divgrpct_us[max]',
                     'min_value': -100.0,
                     'max_value': 100.0},
                'PER':
                    {'min_key': 'eq_pe_ratio[min]',
                     'max_key': 'eq_pe_ratio[max]',
                     'min_value': 0.0,
                     'max_value': 150.0},
                'EPS':
                    {'min_key': 'eq_eps[min]',
                     'max_key': 'eq_eps[max]',
                     'min_value': -1000.0,
                     'max_value': 1000.0},
                'PBR':
                    {'min_key': 'price2bk_us[min]',
                     'max_key': 'price2bk_us[max]',
                     'min_value': 0.0,
                     'max_value': 150.0},
                'Revenue ($1M)':
                    {'min_key': 'eq_revenue[min]',
                     'max_key': 'eq_revenue[max]',
                     'min_value': 1.0,
                     'max_value': 100000.0},
                'Gross Margin':
                    {'min_key': 'ttmgrosmgn_us[min]',
                     'max_key': 'ttmgrosmgn_us[max]',
                     'min_value': 0.0,
                     'max_value': 100.0},
                'Operating Margin':
                    {'min_key': 'ttmopmgn_us[min]',
                     'max_key': 'ttmopmgn_us[max]',
                     'min_value': -500.0,
                     'max_value': 200.0},
                'Net Profit Margin':
                    {'min_key': 'ttmnpmgn_us[min]',
                     'max_key': 'ttmnpmgn_us[max]',
                     'min_value': -500.0,
                     'max_value': 200.0},
                'Total Dept to Equity':
                    {'min_key': 'qtotd2eq_us[min]',
                     'max_key': 'qtotd2eq_us[max]',
                     'min_value': 0.0,
                     'max_value': 1000.0},
                'MACD':
                    {'min_key': 'MACD[min]',
                     'max_key': 'MACD[max]',
                     'min_value': -70.0,
                     'max_value': 70.0},
                'RSI':
                    {'min_key': 'RSI[min]',
                     'max_key': 'RSI[max]',
                     'min_value': 0.0,
                     'max_value': 100.0},
                'Stochastic Oscillator':
                    {'min_key': 'STOCH[min]',
                     'max_key': 'STOCH[max]',
                     'min_value': 0.0,
                     'max_value': 100.0},
                'Ultimate Oscillator':
                    {'min_key': 'UO[min]',
                     'max_key': 'UO[max]',
                     'min_value': 0.0,
                     'max_value': 100.0},
                'Williams %R (1D)':
                    {'min_key': 'WilliamsR[min]',
                     'max_key': 'WilliamsR[max]',
                     'min_value': -100.0,
                     'max_value': 0.0},
                }

    return criteria
