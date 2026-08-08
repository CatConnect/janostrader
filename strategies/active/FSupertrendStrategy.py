import logging
from freqtrade.strategy import IStrategy, IntParameter
from freqtrade.enums import TradingMode, MarginMode
from pandas import DataFrame
import pandas as pd
import talib.abstract as ta
import numpy as np

import technical.indicators as ftt


class FSupertrendStrategy(IStrategy):
    """
    Estratégia baseada em consenso de 3 indicadores Supertrend.
    Fonte: freqtrade/freqtrade-strategies (oficial)
    Adaptada para: Binance Futures, alavancagem máx 3x, conta ~$20 USDT
    """

    INTERFACE_VERSION: int = 3

    # Futuros
    can_short = True
    trading_mode = TradingMode.FUTURES
    margin_mode = MarginMode.ISOLATED

    buy_params = {
        "buy_m1": 4,
        "buy_m2": 7,
        "buy_m3": 1,
        "buy_p1": 8,
        "buy_p2": 9,
        "buy_p3": 8,
    }

    sell_params = {
        "sell_m1": 1,
        "sell_m2": 3,
        "sell_m3": 6,
        "sell_p1": 16,
        "sell_p2": 18,
        "sell_p3": 18,
    }

    minimal_roi = {"0": 0.1, "30": 0.075, "60": 0.05, "120": 0.025}

    stoploss = -0.265

    trailing_stop = True
    trailing_stop_positive = 0.05
    trailing_stop_positive_offset = 0.1
    trailing_only_offset_is_reached = False

    timeframe = "1h"
    startup_candle_count = 18

    buy_m1 = IntParameter(1, 7, default=1)
    buy_m2 = IntParameter(1, 7, default=3)
    buy_m3 = IntParameter(1, 7, default=4)
    buy_p1 = IntParameter(7, 21, default=14)
    buy_p2 = IntParameter(7, 21, default=10)
    buy_p3 = IntParameter(7, 21, default=10)

    sell_m1 = IntParameter(1, 7, default=1)
    sell_m2 = IntParameter(1, 7, default=3)
    sell_m3 = IntParameter(1, 7, default=4)
    sell_p1 = IntParameter(7, 21, default=14)
    sell_p2 = IntParameter(7, 21, default=10)
    sell_p3 = IntParameter(7, 21, default=10)

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag,
                 side: str, **kwargs) -> float:
        return 3.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        new_cols = []

        for multiplier in self.buy_m1.range:
            for period in self.buy_p1.range:
                new_cols.append(
                    self.supertrend_direction(dataframe, multiplier, period,
                        f"supertrend_1_buy_{multiplier}_{period}"))

        for multiplier in self.buy_m2.range:
            for period in self.buy_p2.range:
                new_cols.append(
                    self.supertrend_direction(dataframe, multiplier, period,
                        f"supertrend_2_buy_{multiplier}_{period}"))

        for multiplier in self.buy_m3.range:
            for period in self.buy_p3.range:
                new_cols.append(
                    self.supertrend_direction(dataframe, multiplier, period,
                        f"supertrend_3_buy_{multiplier}_{period}"))

        for multiplier in self.sell_m1.range:
            for period in self.sell_p1.range:
                new_cols.append(
                    self.supertrend_direction(dataframe, multiplier, period,
                        f"supertrend_1_sell_{multiplier}_{period}"))

        for multiplier in self.sell_m2.range:
            for period in self.sell_p2.range:
                new_cols.append(
                    self.supertrend_direction(dataframe, multiplier, period,
                        f"supertrend_2_sell_{multiplier}_{period}"))

        for multiplier in self.sell_m3.range:
            for period in self.sell_p3.range:
                new_cols.append(
                    self.supertrend_direction(dataframe, multiplier, period,
                        f"supertrend_3_sell_{multiplier}_{period}"))

        if new_cols:
            dataframe = pd.concat([dataframe] + new_cols, axis=1)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe[f"supertrend_1_buy_{self.buy_m1.value}_{self.buy_p1.value}"] == "up")
            & (dataframe[f"supertrend_2_buy_{self.buy_m2.value}_{self.buy_p2.value}"] == "up")
            & (dataframe[f"supertrend_3_buy_{self.buy_m3.value}_{self.buy_p3.value}"] == "up")
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1

        dataframe.loc[
            (dataframe[f"supertrend_1_sell_{self.sell_m1.value}_{self.sell_p1.value}"] == "down")
            & (dataframe[f"supertrend_2_sell_{self.sell_m2.value}_{self.sell_p2.value}"] == "down")
            & (dataframe[f"supertrend_3_sell_{self.sell_m3.value}_{self.sell_p3.value}"] == "down")
            & (dataframe["volume"] > 0),
            "enter_short",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe[f"supertrend_2_sell_{self.sell_m2.value}_{self.sell_p2.value}"] == "down"),
            "exit_long",
        ] = 1

        dataframe.loc[
            (dataframe[f"supertrend_2_buy_{self.buy_m2.value}_{self.buy_p2.value}"] == "up"),
            "exit_short",
        ] = 1

        return dataframe

    def supertrend_direction(self, dataframe: DataFrame, multiplier: int,
                              period: int, name: str) -> pd.Series:
        _, stx = ftt.supertrend(dataframe, period=period, multiplier=multiplier)
        return pd.Series(stx, index=dataframe.index, name=name).fillna("")
