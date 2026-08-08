from functools import reduce
import numpy as np
import pandas as pd
from pandas import DataFrame
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
from freqtrade.enums import TradingMode, MarginMode
import talib.abstract as ta
from technical.qtpylib import crossed_above, crossed_below


class FDonchianStrategy(IStrategy):
    """
    Donchian Channel Breakout para futuros Binance.

    Lógica:
    - Entra LONG quando close cruza acima do canal superior (breakout de alta)
    - Entra SHORT quando close cruza abaixo do canal inferior (breakout de baixa)
    - Volume confirma o breakout (volume > SMA volume)
    - ADX filtra entradas: só entra em tendência (ADX > 20)
    - Saída: trailing stop baseado no canal médio (DC period/2)

    Diferencial vs Supertrend:
    - Supertrend usa ATR para bandas dinâmicas
    - Donchian usa max/min absolutos de N períodos — puro price action
    - Clássico em commodities/futuros (Turtle Trading)

    Referências:
    - Richard Dennis & William Eckhardt — Turtle Trading System (1983)
    - "Following the Trend" — Andreas Clenow (2013)
    - Chan, E. (2013). Algorithmic Trading. Wiley.
    """

    INTERFACE_VERSION = 3
    can_short = True
    trading_mode = TradingMode.FUTURES
    margin_mode = MarginMode.ISOLATED

    timeframe = "1h"
    startup_candle_count: int = 55

    # ROI conservador — breakout segura tendência longa
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

    # Parâmetros de pesquisa
    dc_period = IntParameter(10, 55, default=20, space='buy')
    adx_threshold = DecimalParameter(15, 35, decimals=0, default=20.0, space='buy')
    vol_ma_period = IntParameter(10, 30, default=20, space='buy')

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag,
                 side: str, **kwargs) -> float:
        return 3.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Donchian Channel para todos os valores do range
        for period in self.dc_period.range:
            dataframe[f"dc_upper_{period}"] = dataframe["high"].rolling(period).max()
            dataframe[f"dc_lower_{period}"] = dataframe["low"].rolling(period).min()
            dataframe[f"dc_mid_{period}"] = (
                dataframe[f"dc_upper_{period}"] + dataframe[f"dc_lower_{period}"]
            ) / 2

        # ADX para filtro de tendência
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)

        # Volume SMA para confirmação de breakout
        for period in self.vol_ma_period.range:
            dataframe[f"vol_ma_{period}"] = dataframe["volume"].rolling(period).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dc_upper = f"dc_upper_{self.dc_period.value}"
        dc_lower = f"dc_lower_{self.dc_period.value}"
        vol_ma = f"vol_ma_{self.vol_ma_period.value}"

        # Long: fecha acima do canal superior com volume e ADX
        dataframe.loc[
            (crossed_above(dataframe["close"], dataframe[dc_upper].shift(1)))
            & (dataframe["adx"] > self.adx_threshold.value)
            & (dataframe["volume"] > dataframe[vol_ma])
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1

        # Short: fecha abaixo do canal inferior com volume e ADX
        dataframe.loc[
            (crossed_below(dataframe["close"], dataframe[dc_lower].shift(1)))
            & (dataframe["adx"] > self.adx_threshold.value)
            & (dataframe["volume"] > dataframe[vol_ma])
            & (dataframe["volume"] > 0),
            "enter_short",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dc_mid = f"dc_mid_{self.dc_period.value}"

        # Saída quando preço retorna à linha média do canal
        dataframe.loc[
            dataframe["close"] < dataframe[dc_mid],
            "exit_long",
        ] = 1

        dataframe.loc[
            dataframe["close"] > dataframe[dc_mid],
            "exit_short",
        ] = 1

        return dataframe
