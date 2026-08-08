from functools import reduce
import pandas as pd
from pandas import DataFrame
from freqtrade.strategy import DecimalParameter, IStrategy, IntParameter
from freqtrade.enums import TradingMode, MarginMode
import talib.abstract as ta
from technical.qtpylib import crossed_above, crossed_below


class FAdxSmaStrategy(IStrategy):
    """
    Estratégia ADX + SMA crossover para futuros.
    v2 — ajustada após backtest v1:
      - sma_long_period default: 48 → 30 (entrada mais rápida na tendência)
      - pos_entry_adx default: 30 → 35 (só entra em tendências mais fortes)
      - ROI mais conservador (saída mais rápida nos winners)
    """

    INTERFACE_VERSION = 3
    can_short = True
    trading_mode = TradingMode.FUTURES
    margin_mode = MarginMode.ISOLATED

    timeframe = "1h"
    minimal_roi = {"0": 0.04, "30": 0.07, "60": 0.05}

    stoploss = -0.05
    trailing_stop = False
    process_only_new_candles = True
    startup_candle_count: int = 50

    pos_entry_adx = DecimalParameter(25, 45, decimals=1, default=35.0, space="buy")
    pos_exit_adx = DecimalParameter(20, 40, decimals=1, default=25.0, space="sell")
    adx_period = IntParameter(4, 24, default=14, space='buy')
    sma_short_period = IntParameter(4, 24, default=12, space='buy')
    sma_long_period = IntParameter(12, 100, default=30, space='buy')

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag,
                 side: str, **kwargs) -> float:
        return 3.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        for val in self.adx_period.range:
            dataframe[f"adx_{val}"] = ta.ADX(dataframe, timeperiod=val)
        for val in self.sma_short_period.range:
            dataframe[f"sma_short_{val}"] = ta.SMA(dataframe, timeperiod=val)
        for val in self.sma_long_period.range:
            dataframe[f"sma_long_{val}"] = ta.SMA(dataframe, timeperiod=val)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions_long = [
            dataframe[f"adx_{self.adx_period.value}"] > self.pos_entry_adx.value,
            crossed_above(
                dataframe[f"sma_short_{self.sma_short_period.value}"],
                dataframe[f"sma_long_{self.sma_long_period.value}"],
            ),
        ]
        conditions_short = [
            dataframe[f"adx_{self.adx_period.value}"] > self.pos_entry_adx.value,
            crossed_below(
                dataframe[f"sma_short_{self.sma_short_period.value}"],
                dataframe[f"sma_long_{self.sma_long_period.value}"],
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
