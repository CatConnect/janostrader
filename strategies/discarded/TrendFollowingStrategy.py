from pandas import DataFrame
from freqtrade.strategy import IStrategy
from freqtrade.enums import TradingMode, MarginMode

import talib.abstract as ta


class TrendFollowingStrategy(IStrategy):
    """
    Estratégia EMA 20 + OBV para futuros.
    Fonte: freqtrade/freqtrade-strategies (oficial)
    Adaptada para: Binance Futures, alavancagem máx 3x, conta ~$20 USDT
    Timeframe 5m = mais trades, dados acumulam mais rápido
    """

    INTERFACE_VERSION: int = 3

    # Futuros
    can_short = True
    trading_mode = TradingMode.FUTURES
    margin_mode = MarginMode.ISOLATED

    minimal_roi = {"0": 0.15, "30": 0.1, "60": 0.05}

    stoploss = -0.265

    trailing_stop = True
    trailing_stop_positive = 0.05
    trailing_stop_positive_offset = 0.1
    trailing_only_offset_is_reached = False

    timeframe = "5m"

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag,
                 side: str, **kwargs) -> float:
        return 3.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['obv'] = ta.OBV(dataframe['close'], dataframe['volume'])
        dataframe['trend'] = dataframe['close'].ewm(span=20, adjust=False).mean()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['close'] > dataframe['trend'])
            & (dataframe['close'].shift(1) <= dataframe['trend'].shift(1))
            & (dataframe['obv'] > dataframe['obv'].shift(1)),
            'enter_long'
        ] = 1

        dataframe.loc[
            (dataframe['close'] < dataframe['trend'])
            & (dataframe['close'].shift(1) >= dataframe['trend'].shift(1))
            & (dataframe['obv'] < dataframe['obv'].shift(1)),
            'enter_short'
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['close'] < dataframe['trend'])
            & (dataframe['close'].shift(1) >= dataframe['trend'].shift(1))
            & (dataframe['obv'] > dataframe['obv'].shift(1)),
            'exit_long'
        ] = 1

        dataframe.loc[
            (dataframe['close'] > dataframe['trend'])
            & (dataframe['close'].shift(1) <= dataframe['trend'].shift(1))
            & (dataframe['obv'] < dataframe['obv'].shift(1)),
            'exit_short'
        ] = 1

        return dataframe
