import logging
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
from freqtrade.enums import TradingMode, MarginMode
from pandas import DataFrame
import talib.abstract as ta
from technical.qtpylib import crossed_above, crossed_below


class FOttStrategy(IStrategy):
    """
    OTT (Optimized Trend Tracker) + ADX para futuros.
    Fonte: freqtrade/freqtrade-strategies (oficial)
    Adaptada para: Binance Futures, alavancagem máx 3x

    Lógica: O OTT é uma média adaptativa que reage à velocidade do mercado
    via CMO (Chande Momentum Oscillator). Entra quando o preço (VAR) cruza
    o OTT. Diferente do Supertrend — usa momentum adaptativo, não ATR.
    """

    INTERFACE_VERSION: int = 3
    can_short = True
    trading_mode = TradingMode.FUTURES
    margin_mode = MarginMode.ISOLATED

    minimal_roi = {"0": 0.1, "30": 0.075, "60": 0.05, "120": 0.025}
    stoploss = -0.265
    trailing_stop = True
    trailing_stop_positive = 0.05
    trailing_stop_positive_offset = 0.1
    trailing_only_offset_is_reached = False

    timeframe = "1h"
    startup_candle_count = 18

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag,
                 side: str, **kwargs) -> float:
        return 3.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        ott_data = self._ott(dataframe)
        dataframe["ott"] = ott_data["OTT"]
        dataframe["var"] = ott_data["VAR"]
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            crossed_above(dataframe["var"], dataframe["ott"]),
            "enter_long",
        ] = 1
        dataframe.loc[
            crossed_below(dataframe["var"], dataframe["ott"]),
            "enter_short",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["adx"] > 60), "exit_long"] = 1
        dataframe.loc[(dataframe["adx"] > 60), "exit_short"] = 1
        return dataframe

    def _ott(self, dataframe: DataFrame):
        """
        OTT (Optimized Trend Tracker) implementado com loops iterativos corretos.
        longstop/shortstop e trend/dir dependem do valor anterior — requerem .iat[i].
        """
        df = dataframe.copy()
        pds = 2
        percent = 1.4
        alpha = 2 / (pds + 1)

        # CMO (Chande Momentum Oscillator) via rolling sums de up/down moves
        ud1 = np.where(df["close"] > df["close"].shift(1), df["close"] - df["close"].shift(1), 0.0)
        dd1 = np.where(df["close"] < df["close"].shift(1), df["close"].shift(1) - df["close"], 0.0)
        ud = pd.Series(ud1, index=df.index).rolling(9).sum()
        dd = pd.Series(dd1, index=df.index).rolling(9).sum()
        total = ud + dd
        cmo = ((ud - dd) / total.replace(0, np.nan)).abs().fillna(0)

        # VAR: média adaptativa ponderada pelo CMO — precisa de loop iterativo
        close = df["close"].values
        cmo_arr = cmo.values
        var_arr = np.zeros(len(df))
        for i in range(1, len(df)):
            var_arr[i] = (alpha * cmo_arr[i] * close[i]) + (1 - alpha * cmo_arr[i]) * var_arr[i - 1]

        var = pd.Series(var_arr, index=df.index)
        fark = var * percent * 0.01
        newlongstop = var - fark
        newshort_stop = var + fark

        # longstop / shortstop — dependem de valor anterior: loop iterativo
        longstop_arr = np.zeros(len(df))
        shortstop_arr = np.full(len(df), float(1e18))
        nls = newlongstop.values
        nss = newshort_stop.values
        var_vals = var.values

        for i in range(1, len(df)):
            prev_long = longstop_arr[i - 1]
            prev_short = shortstop_arr[i - 1]
            # longstop: máximo entre novo e anterior (se Var ainda acima do anterior)
            if var_vals[i] > prev_long:
                longstop_arr[i] = max(nls[i], prev_long)
            else:
                longstop_arr[i] = nls[i]
            # shortstop: mínimo entre novo e anterior (se Var ainda abaixo do anterior)
            if var_vals[i] < prev_short:
                shortstop_arr[i] = min(nss[i], prev_short)
            else:
                shortstop_arr[i] = nss[i]

        longstop = pd.Series(longstop_arr, index=df.index)
        shortstop = pd.Series(shortstop_arr, index=df.index)

        # Crossover signals
        xlongstop = ((var.shift(1) > longstop.shift(1)) & (var < longstop.shift(1))).astype(int)
        xshortstop = ((var.shift(1) < shortstop.shift(1)) & (var > shortstop.shift(1))).astype(int)

        # trend/dir — dependem do valor anterior: loop iterativo
        trend_arr = np.zeros(len(df))
        dir_arr = np.ones(len(df))
        xl = xlongstop.values
        xs = xshortstop.values
        for i in range(1, len(df)):
            if xs[i] == 1:
                trend_arr[i] = 1
                dir_arr[i] = 1
            elif xl[i] == 1:
                trend_arr[i] = -1
                dir_arr[i] = -1
            else:
                trend_arr[i] = trend_arr[i - 1]
                dir_arr[i] = dir_arr[i - 1]

        dir_s = pd.Series(dir_arr, index=df.index)

        mt = np.where(dir_arr == 1, longstop_arr, shortstop_arr)
        mt_s = pd.Series(mt, index=df.index)
        ott = np.where(
            var_vals > mt,
            mt * (200 + percent) / 200,
            mt * (200 - percent) / 200,
        )
        ott_s = pd.Series(ott, index=df.index).shift(2)

        return DataFrame(index=df.index, data={"OTT": ott_s, "VAR": var})
