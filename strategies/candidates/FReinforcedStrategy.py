from functools import reduce
import numpy as np
import pandas as pd
from pandas import DataFrame
from freqtrade.strategy import DecimalParameter, IStrategy, IntParameter
from freqtrade.enums import TradingMode, MarginMode
from freqtrade.exchange import timeframe_to_minutes
import talib.abstract as ta
from technical.qtpylib import crossed_above, crossed_below
from technical.util import resample_to_interval, resampled_merge


class FReinforcedStrategy(IStrategy):
    """
    EMA crossover reforçado por SMA de timeframe maior (60min resample).
    Fonte: freqtrade/freqtrade-strategies (oficial)
    Adaptada para: Binance Futures, alavancagem máx 3x

    Diferencial: usa SMA 50 no timeframe 1h resampled para 5x (60min)
    como filtro macro de tendência. Só entra long se preço > SMA macro,
    só entra short se preço < SMA macro. Reduz entradas contra-tendência.
    """

    INTERFACE_VERSION = 3
    can_short = True
    trading_mode = TradingMode.FUTURES
    margin_mode = MarginMode.ISOLATED

    timeframe = "5m"
    minimal_roi = {"60": 0.075, "30": 0.1, "0": 0.05}
    stoploss = -0.05
    trailing_stop = False
    process_only_new_candles = True
    startup_candle_count: int = 14

    pos_entry_adx = DecimalParameter(15, 40, decimals=1, default=30.0, space="buy")
    pos_exit_adx = DecimalParameter(15, 40, decimals=1, default=30.0, space="sell")
    adx_period = IntParameter(4, 24, default=14, space='buy')
    ema_short_period = IntParameter(4, 24, default=8, space='buy')
    ema_long_period = IntParameter(12, 175, default=21, space='buy')

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag,
                 side: str, **kwargs) -> float:
        return 3.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        for val in self.adx_period.range:
            dataframe[f"adx_{val}"] = ta.ADX(dataframe, timeperiod=val)
        for val in self.ema_short_period.range:
            dataframe[f"ema_short_{val}"] = ta.EMA(dataframe, timeperiod=val)
        for val in self.ema_long_period.range:
            dataframe[f"ema_long_{val}"] = ta.EMA(dataframe, timeperiod=val)

        self.resample_interval = timeframe_to_minutes(self.timeframe) * 12
        dataframe_long = resample_to_interval(dataframe, self.resample_interval)
        dataframe_long["sma"] = ta.SMA(dataframe_long, timeperiod=50, price="close")
        dataframe = resampled_merge(dataframe, dataframe_long, fill_na=True)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions_long = [
            dataframe["close"] > dataframe[f"resample_{self.resample_interval}_sma"],
            crossed_above(
                dataframe[f"ema_short_{self.ema_short_period.value}"],
                dataframe[f"ema_long_{self.ema_long_period.value}"],
            ),
        ]
        conditions_short = [
            dataframe["close"] < dataframe[f"resample_{self.resample_interval}_sma"],
            crossed_below(
                dataframe[f"ema_short_{self.ema_short_period.value}"],
                dataframe[f"ema_long_{self.ema_long_period.value}"],
            ),
        ]
        dataframe.loc[reduce(lambda x, y: x & y, conditions_long), "enter_long"] = 1
        dataframe.loc[reduce(lambda x, y: x & y, conditions_short), "enter_short"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions_close = [
            dataframe[f"adx_{self.adx_period.value}"] < self.pos_exit_adx.value,
        ]
        dataframe.loc[reduce(lambda x, y: x & y, conditions_close), "exit_long"] = 1
        dataframe.loc[reduce(lambda x, y: x & y, conditions_close), "exit_short"] = 1
        return dataframe
