import talib.abstract as ta
import numpy as np
from pandas import DataFrame
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
from freqtrade.enums import TradingMode, MarginMode


class BBStochRSIMeanReversion(IStrategy):
    """
    Estratégia de Mean Reversion: Bollinger Bands + StochRSI + ADX
    v2 — ajustada após backtest v1:
      - Timeframe: 1h → 4h (sinais mais confiáveis)
      - Stop: -4% → -8% (mean reversion precisa de espaço)
      - Alavancagem: 3x → 2x (mais conservador)
      - ADX máximo: 25 → 20 (mercado mais lateral)

    Complemento da FSupertrendStrategy:
    - Supertrend: opera em tendência (ADX > 25)
    - Esta: opera em lateralização (ADX < 20)
    """

    INTERFACE_VERSION: int = 3
    can_short = True
    trading_mode = TradingMode.FUTURES
    margin_mode = MarginMode.ISOLATED

    minimal_roi = {
        "0": 0.06,
        "120": 0.04,
        "240": 0.02,
        "480": 0.01
    }

    stoploss = -0.08

    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    timeframe = "4h"
    startup_candle_count = 30
    process_only_new_candles = True

    adx_max = IntParameter(15, 25, default=20, space="buy")
    bb_period = IntParameter(10, 30, default=20, space="buy")
    bb_std = DecimalParameter(1.5, 3.0, decimals=1, default=2.0, space="buy")
    rsi_period = IntParameter(7, 21, default=14, space="buy")
    stochrsi_low = DecimalParameter(0.05, 0.25, decimals=2, default=0.15, space="buy")
    stochrsi_high = DecimalParameter(0.75, 0.95, decimals=2, default=0.85, space="sell")

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag,
                 side: str, **kwargs) -> float:
        return 2.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)

        for period in self.rsi_period.range:
            dataframe[f'rsi_{period}'] = ta.RSI(dataframe, timeperiod=period)
            rsi = dataframe[f'rsi_{period}']
            rsi_min = rsi.rolling(14).min()
            rsi_max = rsi.rolling(14).max()
            dataframe[f'stochrsi_{period}'] = ((rsi - rsi_min) / (rsi_max - rsi_min + 1e-10)).fillna(0)

        for period in self.bb_period.range:
            for std in [1.5, 2.0, 2.5, 3.0]:
                std_int = int(std * 10)
                upper, mid, lower = ta.BBANDS(
                    dataframe['close'], timeperiod=period,
                    nbdevup=std, nbdevdn=std, matype=0
                )
                dataframe[f'bb_upper_{period}_{std_int}'] = upper
                dataframe[f'bb_mid_{period}_{std_int}'] = mid
                dataframe[f'bb_lower_{period}_{std_int}'] = lower

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        std_int = int(self.bb_std.value * 10)
        bb_upper = f'bb_upper_{self.bb_period.value}_{std_int}'
        bb_lower = f'bb_lower_{self.bb_period.value}_{std_int}'
        stochrsi = f'stochrsi_{self.rsi_period.value}'

        dataframe.loc[
            (dataframe['adx'] < self.adx_max.value)
            & (dataframe['close'] <= dataframe[bb_lower])
            & (dataframe[stochrsi] < self.stochrsi_low.value)
            & (dataframe['volume'] > 0),
            'enter_long'
        ] = 1

        dataframe.loc[
            (dataframe['adx'] < self.adx_max.value)
            & (dataframe['close'] >= dataframe[bb_upper])
            & (dataframe[stochrsi] > self.stochrsi_high.value)
            & (dataframe['volume'] > 0),
            'enter_short'
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        std_int = int(self.bb_std.value * 10)
        bb_mid = f'bb_mid_{self.bb_period.value}_{std_int}'

        dataframe.loc[
            (dataframe['close'] >= dataframe[bb_mid])
            | (dataframe['adx'] > self.adx_max.value + 8),
            'exit_long'
        ] = 1

        dataframe.loc[
            (dataframe['close'] <= dataframe[bb_mid])
            | (dataframe['adx'] > self.adx_max.value + 8),
            'exit_short'
        ] = 1

        return dataframe
