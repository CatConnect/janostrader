from functools import reduce
import numpy as np
import pandas as pd
from pandas import DataFrame
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
from freqtrade.enums import TradingMode, MarginMode
import talib.abstract as ta
from technical.qtpylib import crossed_above, crossed_below


class FOBVTrendStrategy(IStrategy):
    """
    OBV Trend Strategy para futuros Binance.

    Lógica:
    - OBV (On-Balance Volume) detecta acumulação/distribuição de smart money
    - EMA do OBV revela a tendência de volume subjacente
    - Entra LONG quando OBV cruza acima da sua EMA e preço > EMA 200
    - Entra SHORT quando OBV cruza abaixo da sua EMA e preço < EMA 200
    - ADX confirma que há tendência (não entra em lateralização)

    Por que OBV é diferente:
    - Supertrend/Donchian/EMA operam no preço
    - OBV incorpora volume — detecta força institucional antes do movimento
    - Volume precede preço (Wyckoff, 1910)

    Referências:
    - Granville, J.E. (1963). Granville's New Key to Stock Market Profits. Prentice-Hall.
    - Buff, S. (2019). "Volume-Price Confirmation for Trend Following". SSRN 3425234.
    - Clenow, A. (2013). Following the Trend. Wiley.
    - Freqtrade-strategies (oficial): OBV-based indicators
    """

    INTERFACE_VERSION = 3
    can_short = True
    trading_mode = TradingMode.FUTURES
    margin_mode = MarginMode.ISOLATED

    timeframe = "1h"
    startup_candle_count: int = 200

    minimal_roi = {
        "0": 0.10,
        "120": 0.06,
        "240": 0.03,
    }

    stoploss = -0.08
    trailing_stop = True
    trailing_stop_positive = 0.03
    trailing_stop_positive_offset = 0.06
    trailing_only_offset_is_reached = True

    process_only_new_candles = True

    # Parâmetros
    obv_ema_period = IntParameter(10, 50, default=21, space='buy')
    trend_ema_period = IntParameter(50, 200, default=200, space='buy')
    adx_threshold = DecimalParameter(15, 35, decimals=0, default=20.0, space='buy')

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag,
                 side: str, **kwargs) -> float:
        return 3.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # OBV
        dataframe["obv"] = ta.OBV(dataframe)

        # EMA do OBV para todos os períodos do range
        for period in self.obv_ema_period.range:
            dataframe[f"obv_ema_{period}"] = ta.EMA(dataframe["obv"], timeperiod=period)

        # EMA de preço para filtro de tendência macro
        for period in self.trend_ema_period.range:
            dataframe[f"trend_ema_{period}"] = ta.EMA(dataframe, timeperiod=period)

        # ADX
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        obv_ema = f"obv_ema_{self.obv_ema_period.value}"
        trend_ema = f"trend_ema_{self.trend_ema_period.value}"

        # Long: OBV cruza acima da EMA + preço em tendência de alta + ADX
        dataframe.loc[
            (crossed_above(dataframe["obv"], dataframe[obv_ema]))
            & (dataframe["close"] > dataframe[trend_ema])
            & (dataframe["adx"] > self.adx_threshold.value)
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1

        # Short: OBV cruza abaixo da EMA + preço em tendência de baixa + ADX
        dataframe.loc[
            (crossed_below(dataframe["obv"], dataframe[obv_ema]))
            & (dataframe["close"] < dataframe[trend_ema])
            & (dataframe["adx"] > self.adx_threshold.value)
            & (dataframe["volume"] > 0),
            "enter_short",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        obv_ema = f"obv_ema_{self.obv_ema_period.value}"
        trend_ema = f"trend_ema_{self.trend_ema_period.value}"

        # Saída long: OBV cai abaixo da EMA OU preço abaixo da trend EMA
        dataframe.loc[
            (dataframe["obv"] < dataframe[obv_ema])
            | (dataframe["close"] < dataframe[trend_ema]),
            "exit_long",
        ] = 1

        # Saída short: OBV sobe acima da EMA OU preço acima da trend EMA
        dataframe.loc[
            (dataframe["obv"] > dataframe[obv_ema])
            | (dataframe["close"] > dataframe[trend_ema]),
            "exit_short",
        ] = 1

        return dataframe
