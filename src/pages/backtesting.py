import streamlit as st
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, resample_apply
import FinanceDataReader as fdr

from backtesting.test import SMA

def app():
    st.title('Simple Backtesting')

    st.write('### Backtest simple strategies using `Backtesting.py` with daily historical price data')

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

    selected_stock_key = st.selectbox('Select price data to use in backtest', list(stock_dict.keys()))
    selected_stock_value = stock_dict[selected_stock_key]

    strategy_dict = {
        "Moving Average Crossover": SmaCross,
        "Relative Strength Index": RSIStrategy,
        "Bollinger Band": BBStrategy,
        "RSI based Modified Strategy": RSIModifiedStrategy,
        "Volume-Momentum based Modified Strategy": CustomMomentumStrategy
    }

    selected_strategy_key = st.selectbox('Select a strategy', list(strategy_dict.keys()))
    selected_strategy = strategy_dict[selected_strategy_key]

    if (st.button('Execute backtest')):
        # 데이터 로드
        price_df = fdr.DataReader(selected_stock_value, '2015-01-01')

        # 백테스트 진행
        bt = Backtest(price_df, selected_strategy,
                      cash=1000000, commission=.002,
                      exclusive_orders=True)

        output = bt.run()
        output_df = pd.DataFrame(output)
        st.dataframe(output_df[:-2], height=800)
        bt.plot(open_browser=False, filename="backtest_plot")
        with open("backtest_plot.html", "r", encoding='utf-8') as f:
            plot_html = f.read()
        st.components.v1.html(plot_html, height=1000)

class SmaCross(Strategy):

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, 10)
        self.sma2 = self.I(SMA, close, 20)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()

def RSI(array, n):
    """Relative strength index"""
    # Approximate; good enough
    gain = pd.Series(array).diff()
    loss = gain.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    rs = gain.ewm(n).mean() / loss.abs().ewm(n).mean()
    return 100 - 100 / (1 + rs)

class RSIStrategy(Strategy):

    def init(self):
        # Compute moving averages the strategy demands
        self.ma10 = self.I(SMA, self.data.Close, 10)
        self.ma20 = self.I(SMA, self.data.Close, 20)
        self.ma50 = self.I(SMA, self.data.Close, 50)
        self.ma100 = self.I(SMA, self.data.Close, 100)

        # Compute daily RSI
        self.daily_rsi = self.I(RSI, self.data.Close, 30)
        self.buy_level = 30
        self.sell_level = 70

    def next(self):
        price = self.data.Close[-1]

        # If we don't already have a position, and
        # if all conditions are satisfied, enter long.
        if self.daily_rsi[-1] < self.buy_level:
            self.buy()

        elif self.daily_rsi[-1] > self.sell_level:
            self.sell()


class RSIModifiedStrategy(Strategy):
    d_rsi = 30  # Daily RSI lookback periods
    w_rsi = 30  # Weekly
    level = 70

    def init(self):
        # Compute moving averages the strategy demands
        self.ma10 = self.I(SMA, self.data.Close, 10)
        self.ma20 = self.I(SMA, self.data.Close, 20)
        self.ma50 = self.I(SMA, self.data.Close, 50)
        self.ma100 = self.I(SMA, self.data.Close, 100)

        # Compute daily RSI(30)
        self.daily_rsi = self.I(RSI, self.data.Close, self.d_rsi)

        # To construct weekly RSI, we can use `resample_apply()`
        # helper function from the library
        self.weekly_rsi = resample_apply(
            'W-FRI', RSI, self.data.Close, self.w_rsi)

    def next(self):
        price = self.data.Close[-1]

        # If we don't already have a position, and
        # if all conditions are satisfied, enter long.
        if (not self.position and
                self.daily_rsi[-1] > self.level and
                self.weekly_rsi[-1] > self.level and
                self.weekly_rsi[-1] > self.daily_rsi[-1] and
                self.ma100[-1] < self.ma50[-1] < self.ma20[-1] < self.ma10[-1] < price) \
                and not self.position.is_long:

            # Buy at market price on next open, but do
            # set 8% fixed stop loss.
            self.buy(sl=.92 * price)

        # If the price closes 2% or more below 10-day MA
        # close the position, if any.
        elif price < .98 * self.ma10[-1]:
            self.position.close()

def BB(array, n, is_upper):
    sma = pd.Series(array).rolling(n).mean()
    std = pd.Series(array).rolling(n).std()
    upper_bb = sma + std * 2
    lower_bb = sma - std * 2
    if (is_upper == True):
        return upper_bb
    else:
        return lower_bb

class BBStrategy(Strategy):

    def init(self):

        # Compute daily Bollinger Band
        self.upper_bb = self.I(BB, self.data.Close, 20, True)
        self.lower_bb = self.I(BB, self.data.Close, 20, False)

    def next(self):
        price = self.data.Close[-1]

        if self.upper_bb[-1] < price:
            self.sell()

        elif self.lower_bb[-1] > price:
            self.buy()


def CustomMomentum(price: pd.Series, volume: pd.Series, n: int, adj: int) -> pd.Series:

    denominator = 1 / np.arange(1+adj, 1+n+adj)[::-1]

    log_return = np.log(pd.Series(price)).diff() * 100
    volume_mean = pd.Series(volume).rolling(n).mean()
    normalized_volume = volume / volume_mean
    custom_momentum = log_return * normalized_volume

    normalized_custom_momentum = custom_momentum.rolling(n).apply(lambda x: np.sum(denominator * x), raw=True)

    return normalized_custom_momentum

class CustomMomentumStrategy(Strategy):

    def init(self):
        # self.log_return = self.I(LogReturn, self.data.Close)
        # self.volume_mean = self.I(VolumeMean, self.data.Volume, 20)

        self.custom_momentum = self.I(CustomMomentum, self.data.Close, self.data.Volume, 20, 5)

    def next(self):
        # price = self.data.Close[-1]
        # volume = self.data.Volume[-1]
        # normalized_volume = volume / self.volume_mean
        # custom_momentum = self.log_return * normalized_volume

        if self.custom_momentum[-1] >= 2.0 and not self.position.is_long:
            self.buy()
        elif self.custom_momentum[-1] <= -2.0 and not self.position.is_short:
            self.sell()