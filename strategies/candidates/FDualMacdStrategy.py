from functools import reduce
import numpy as np
from pandas import DataFrame
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
from freqtrade.enums import TradingMode, MarginMode
import talib.abstract as ta


class FDualMacdStrategy(IStrategy):
    """
    Dual MACD Consensus Strategy para futuros Binance.

    Hipótese:
    A FSupertrendStrategy funciona porque exige consenso de 3 indicadores.
    Esta estratégia testa a mesma hipótese com MACD duplo:
    - MACD rápido (12,26,9) — sensível a movimentos de curto prazo
    - MACD lento (21,55,9) — filtra tendência de médio prazo

    Entra somente quando AMBOS apontam a mesma direção.
    Isso reduz drasticamente o número de falsos sinais.

    Referências:
    - Appel, G. (2005). Technical Analysis: Power Tools for Active Investors. FT Press.
    - Murphy, J.J. (1999). Technical Analysis of the Financial Markets. NYIF.
    - Li, Y. et al. (2015). "MACD-Based Trading Rule". Journal of Financial Research.
    - GitHub: freqtrade-strategies / MACD examples
    """

    INTERFACE_VERSION = 3
    can_short = True
    trading_mode = TradingMode.FUTURES
    margin_mode = MarginMode.ISOLATED

    timeframe = "1h"
    startup_candle_count: int = 100

    # ROI similar ao FSupertrendStrategy — deixar o lucro correr
    minimal_roi = {
        "0": 0.025,
        "60": 0.05,
        "120": 0.075,
        "240": 0.10,
    }

    stoploss = -0.265
    trailing_stop = True
    trailing_stop_positive = 0.05
    trailing_stop_positive_offset = 0.10
    trailing_only_offset_is_reached = False

    process_only_new_candles = True

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag,
                 side: str, **kwargs) -> float:
        return 3.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # MACD rápido (padrão)
        macd_fast, signal_fast, hist_fast = ta.MACD(
            dataframe["close"], fastperiod=12, slowperiod=26, signalperiod=9
        )
        dataframe["macd_fast"] = macd_fast
        dataframe["signal_fast"] = signal_fast
        dataframe["hist_fast"] = hist_fast

        # MACD lento (filtra tendência de médio prazo)
        macd_slow, signal_slow, hist_slow = ta.MACD(
            dataframe["close"], fastperiod=21, slowperiod=55, signalperiod=9
        )
        dataframe["macd_slow"] = macd_slow
        dataframe["signal_slow"] = signal_slow
        dataframe["hist_slow"] = hist_slow

        # EMA 200 para filtro macro de tendência
        dataframe["ema200"] = ta.EMA(dataframe, timeperiod=200)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Long: AMBOS MACDs acima da linha de sinal + preço acima EMA 200
        dataframe.loc[
            (dataframe["macd_fast"] > dataframe["signal_fast"])
            & (dataframe["macd_slow"] > dataframe["signal_slow"])
            & (dataframe["hist_fast"] > 0)
            & (dataframe["hist_slow"] > 0)
            & (dataframe["close"] > dataframe["ema200"])
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1

        # Short: AMBOS MACDs abaixo da linha de sinal + preço abaixo EMA 200
        dataframe.loc[
            (dataframe["macd_fast"] < dataframe["signal_fast"])
            & (dataframe["macd_slow"] < dataframe["signal_slow"])
            & (dataframe["hist_fast"] < 0)
            & (dataframe["hist_slow"] < 0)
            & (dataframe["close"] < dataframe["ema200"])
            & (dataframe["volume"] > 0),
            "enter_short",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Sair long: MACD lento vira para baixo (sinal mais robusto)
        dataframe.loc[
            (dataframe["macd_slow"] < dataframe["signal_slow"]),
            "exit_long",
        ] = 1

        # Sair short: MACD lento vira para cima
        dataframe.loc[
            (dataframe["macd_slow"] > dataframe["signal_slow"]),
            "exit_short",
        ] = 1

        return dataframe
