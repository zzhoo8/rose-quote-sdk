from enum import auto, Enum, unique


@unique
class KLineInterval(Enum):

    k_1min = '1m'
    k_5min = '5m'
    k_15min = '15m'
    k_30min = '30m'
    k_60min = '60m'
    k_1D = '1D'
    k_1W = '1W'
    k_1M = '1M'


class QuoteOrder(str, Enum):
    """
    行情排序
    """
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

    UP = auto()
    DOWN = auto()
