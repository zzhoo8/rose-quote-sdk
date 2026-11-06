"""行情相关数据模型 (Pydantic BaseModel)"""

from warnings import warn
from decimal import Decimal
from typing import Annotated, Any, Optional

import requests
from pydantic import BaseModel, Field, model_validator

from rose_quote_sdk.common.exception.business_exception import BusinessException
from rose_quote_sdk.common.exception.common_error import CommonError
from rose_quote_sdk.common.tool.logger import logger, log


class Transaction(BaseModel):
    """实时行情逐笔成交记录"""
    model_config = {'arbitrary_types_allowed': True, 'extra': 'allow'}

    time: Annotated[Optional[Any], Field(default=None, description='时间 (分、秒)')]
    price: Annotated[Optional[Decimal], Field(default=None, description='成交价格')]
    volume: Annotated[Optional[int], Field(default=None, description='成交量')]
    action: Annotated[Optional[str], Field(default=None, description='方向 (B买/S卖)')]
    amount: Annotated[Optional[Decimal], Field(default=None, description='成交金额')]


class Quote(BaseModel):
    """
    实时行情基础类

    参考: https://sites.google.com/site/stock2terms/financial-performance/the-committee
    """
    model_config = {'arbitrary_types_allowed': True, 'extra': 'allow'}

    security_code: Annotated[Optional[str], Field(default=None, description='股票代码，如 600000.SH, 000001.SZ, 00700.HK, USA.AAPL, USA.TSLA 等')]
    name: Annotated[Optional[str], Field(default=None, description='股票名称')]
    now: Annotated[Optional[Decimal], Field(default=None, description='最新价')]
    pre_close: Annotated[Optional[Decimal], Field(default=None, description='前收盘价')]
    close: Annotated[Optional[Decimal], Field(default=None, description='收盘价')]
    open: Annotated[Optional[Decimal], Field(default=None, description='开盘价')]
    high: Annotated[Optional[Decimal], Field(default=None, description='最高价')]
    low: Annotated[Optional[Decimal], Field(default=None, description='最低价')]
    average: Annotated[Optional[Decimal], Field(default=None, description='均价')]
    limit_up: Annotated[Optional[Decimal], Field(default=None, description='涨停价')]
    limit_down: Annotated[Optional[Decimal], Field(default=None, description='跌停价')]
    bid_volume: Annotated[Optional[int], Field(default=None, description='内盘')]
    ask_volume: Annotated[Optional[int], Field(default=None, description='外盘')]
    volume: Annotated[Optional[int], Field(default=None, description='成交量(手),对于港股是股')]
    quantity_relative_ratio: Annotated[Optional[Decimal], Field(default=None, description='量比')]
    committee: Annotated[Optional[Decimal], Field(default=None, description='委比')]
    amount: Annotated[Optional[Decimal], Field(default=None, description='成交额')]
    turnover: Annotated[Optional[int], Field(default=None, description='成交笔数')]
    turnover_ratio: Annotated[Optional[Decimal], Field(default=None, description='换手率')]
    pe_ttm: Annotated[Optional[Decimal], Field(default=None, description='市盈率(TTM)')]
    pe_dynamic: Annotated[Optional[Decimal], Field(default=None, description='市盈率(动态)')]
    pe_static: Annotated[Optional[Decimal], Field(default=None, description='市盈率(静态)')]
    circulation_market_value: Annotated[Optional[Decimal], Field(default=None, description='流通市值')]
    total_market_value: Annotated[Optional[Decimal], Field(default=None, description='总市值')]
    pb: Annotated[Optional[Decimal], Field(default=None, description='市净率')]

    # ----- 委买盘口 (Bid 1~5) -----
    bid1: Annotated[Optional[Decimal], Field(default=None, description='买一价')]
    bid2: Annotated[Optional[Decimal], Field(default=None, description='买二价')]
    bid3: Annotated[Optional[Decimal], Field(default=None, description='买三价')]
    bid4: Annotated[Optional[Decimal], Field(default=None, description='买四价')]
    bid5: Annotated[Optional[Decimal], Field(default=None, description='买五价')]

    bid1_volume: Annotated[Optional[int], Field(default=None, description='买一量')]
    bid2_volume: Annotated[Optional[int], Field(default=None, description='买二量')]
    bid3_volume: Annotated[Optional[int], Field(default=None, description='买三量')]
    bid4_volume: Annotated[Optional[int], Field(default=None, description='买四量')]
    bid5_volume: Annotated[Optional[int], Field(default=None, description='买五量')]

    # ----- 委卖盘口 (Ask 1~5) -----
    ask1: Annotated[Optional[Decimal], Field(default=None, description='卖一价')]
    ask2: Annotated[Optional[Decimal], Field(default=None, description='卖二价')]
    ask3: Annotated[Optional[Decimal], Field(default=None, description='卖三价')]
    ask4: Annotated[Optional[Decimal], Field(default=None, description='卖四价')]
    ask5: Annotated[Optional[Decimal], Field(default=None, description='卖五价')]

    ask1_volume: Annotated[Optional[int], Field(default=None, description='卖一量')]
    ask2_volume: Annotated[Optional[int], Field(default=None, description='卖二量')]
    ask3_volume: Annotated[Optional[int], Field(default=None, description='卖三量')]
    ask4_volume: Annotated[Optional[int], Field(default=None, description='卖四量')]
    ask5_volume: Annotated[Optional[int], Field(default=None, description='卖五量')]

    datetime: Annotated[Optional[str], Field(default=None, description='行情时间')]
    transactions: Annotated[list[Transaction], Field(default_factory=list, description='逐笔成交记录')]
    size: Annotated[Optional[int], Field(default=None, description='每手股数')]

    @model_validator(mode='before')
    @classmethod
    def convert_empty_str_for_decimal(cls, data: Any) -> Any:
        if isinstance(data, dict):
            new_data = data.copy()
            for k, v in data.items():
                if v == "":
                    field = cls.model_fields.get(k)
                    # 极简判断：如果字段类型注解中包含 "decimal"，则转为 None
                    if field and "decimal" in str(field.annotation).lower():
                        new_data[k] = None
            return new_data
        return data

    @classmethod
    def get(cls, host: str, security_code: str, app_code: Optional[str] = None) -> 'Quote':
        """获取单只股票的实时行情"""
        if not security_code:
            raise BusinessException(CommonError.PARAMETER_ERROR)

        _quote = cls(security_code=security_code)
        try:
            headers = {}
            if app_code:
                headers['Authorization'] = f'APPCODE {app_code}'
            resp = requests.get(
                url=f'{host}/api/v2/quote/real',
                headers=headers,
                params=_quote.model_dump(exclude_none=True),
            )
            if resp.status_code != 200:
                logger.info(f'行情服务返回错误: {resp.text}')
            resp = resp.json()
        except Exception as e:
            logger.error(e)
            raise BusinessException(error=CommonError.QUOTE_ERROR)
        if resp['code'] != 0:
            logger.error(resp['msg'])
            raise BusinessException(error=CommonError.QUOTE_ERROR)
        return cls.model_validate(resp['data'][0])

    @classmethod
    def gets(cls, host: str, security_codes: str, fields: Optional[str] = None) -> list['Quote']:
        """批量获取多只股票的实时行情数据"""
        if not security_codes:
            raise BusinessException(CommonError.PARAMETER_ERROR)
        _quote = cls(security_code=security_codes)
        params = _quote.model_dump(exclude_none=True)
        params['fields'] = fields
        try:
            resp = requests.get(url=f'{host}/api/v2/quote/real', params=params)
            if resp.status_code != 200:
                logger.info(f'行情服务返回错误: {resp.text}')
            resp = resp.json()
        except Exception as e:
            logger.error(e)
            raise BusinessException(error=CommonError.QUOTE_ERROR)
        if resp['code'] != 0:
            logger.error(resp['msg'])
            raise BusinessException(error=CommonError.QUOTE_ERROR)
        return [cls.model_validate(item) for item in resp['data']]

    def zip(self) -> str:
        """压缩格式，减少数据传输量。格式: security_code,now,close"""
        return f'{self.security_code},{self.now},{self.close}'

    @classmethod
    def unzip(cls, quote_zip: str) -> 'Quote':
        """解析压缩格式的行情数据"""
        parts = quote_zip.split(',')
        return cls(security_code=parts[0], now=parts[1], close=parts[2])


class QuoteOld(Quote):
    """
    兼容阿里云市场老接口格式 (已弃用，请使用 Quote)

    老接口使用驼峰命名，金额单位为毫秒级整数
    """
    model_config = {'arbitrary_types_allowed': True, 'extra': 'allow'}

    def __init__(self, **data):
        warn('QuoteOld 已弃用，请使用 Quote', DeprecationWarning, stacklevel=2)
        super().__init__(**data)

    securityCode: Annotated[Optional[str], Field(default=None, description='股票代码 (兼容老接口)')]

    # 兼容老接口
    bid1Volume: Annotated[Optional[int], Field(default=None, description='买一量 (兼容老接口)')]
    bid2Volume: Annotated[Optional[int], Field(default=None, description='买二量 (兼容老接口)')]
    bid3Volume: Annotated[Optional[int], Field(default=None, description='买三量 (兼容老接口)')]
    bid4Volume: Annotated[Optional[int], Field(default=None, description='买四量 (兼容老接口)')]
    bid5Volume: Annotated[Optional[int], Field(default=None, description='买五量 (兼容老接口)')]

    ask1Volume: Annotated[Optional[int], Field(default=None, description='卖一量 (兼容老接口)')]
    ask2Volume: Annotated[Optional[int], Field(default=None, description='卖二量 (兼容老接口)')]
    ask3Volume: Annotated[Optional[int], Field(default=None, description='卖三量 (兼容老接口)')]
    ask4Volume: Annotated[Optional[int], Field(default=None, description='卖四量 (兼容老接口)')]
    ask5Volume: Annotated[Optional[int], Field(default=None, description='卖五量 (兼容老接口)')]

    @classmethod
    def adapter(cls, quote: Quote) -> 'QuoteOld':
        """将新格式行情转为老接口格式 (Decimal -> 毫秒级整数)"""
        if not quote:
            raise BusinessException(CommonError.PARAMETER_ERROR)
        quote_old = cls(**quote.model_dump())
        quote_old.securityCode = quote.security_code
        quote_old.now = int(Decimal(quote.now) * 1000)
        quote_old.open = int(Decimal(quote.open) * 1000)
        quote_old.close = int(Decimal(quote.close) * 1000)
        quote_old.high = int(Decimal(quote.high) * 1000)
        quote_old.low = int(Decimal(quote.low) * 1000)

        quote_old.ask1 = int(Decimal(quote_old.ask1) * 1000) if quote_old.ask1 else None
        quote_old.ask2 = int(Decimal(quote_old.ask2) * 1000) if quote_old.ask2 else None
        quote_old.ask3 = int(Decimal(quote_old.ask3) * 1000) if quote_old.ask3 else None
        quote_old.ask4 = int(Decimal(quote_old.ask4) * 1000) if quote_old.ask4 else None
        quote_old.ask5 = int(Decimal(quote_old.ask5) * 1000) if quote_old.ask5 else None
        quote_old.bid1 = int(Decimal(quote_old.bid1) * 1000) if quote_old.bid1 else None
        quote_old.bid2 = int(Decimal(quote_old.bid2) * 1000) if quote_old.bid2 else None
        quote_old.bid3 = int(Decimal(quote_old.bid3) * 1000) if quote_old.bid3 else None
        quote_old.bid4 = int(Decimal(quote_old.bid4) * 1000) if quote_old.bid4 else None
        quote_old.bid5 = int(Decimal(quote_old.bid5) * 1000) if quote_old.bid5 else None

        quote_old.bid1Volume = quote_old.bid1_volume
        quote_old.bid2Volume = quote_old.bid2_volume
        quote_old.bid3Volume = quote_old.bid3_volume
        quote_old.bid4Volume = quote_old.bid4_volume
        quote_old.bid5Volume = quote_old.bid5_volume

        quote_old.ask1Volume = quote_old.ask1_volume
        quote_old.ask2Volume = quote_old.ask2_volume
        quote_old.ask3Volume = quote_old.ask3_volume
        quote_old.ask4Volume = quote_old.ask4_volume
        quote_old.ask5Volume = quote_old.ask5_volume

        transactions = list()
        for transaction in quote_old.transactions:
            transaction.price = int(Decimal(transaction.price) * 1000) if transaction.price else None
            transaction.amount = int(Decimal(transaction.amount) * 1000) if transaction.amount else None
            transactions.append(transaction)
        quote_old.transactions = transactions
        return quote_old


class Timeline(BaseModel):
    """分时图数据"""
    model_config = {'arbitrary_types_allowed': True, 'extra': 'allow'}

    id: Annotated[Optional[str], Field(default=None, description='唯一标识')]
    security_code: Annotated[Optional[str], Field(default=None, description='股票代码')]
    open: Annotated[Optional[Decimal], Field(default=None, description='开盘价')]
    close: Annotated[Optional[Decimal], Field(default=None, description='收盘价')]
    low: Annotated[Optional[Decimal], Field(default=None, description='最低价')]
    high: Annotated[Optional[Decimal], Field(default=None, description='最高价')]
    volume: Annotated[Optional[int], Field(default=None, description='成交量')]
    datetime: Annotated[Optional[str], Field(default=None, description='结束时间 (打点时间)')]

    @classmethod
    def gets(cls, kids: Optional[str] = None) -> list['Timeline']:
        """批量获取未打点分时数据"""
        pass

    @classmethod
    @log
    def get(cls, kid: str) -> 'Timeline':
        """获取单条未打点分时数据"""
        pass


class KLine(Timeline):
    """分时图和1分钟k线数据可以合并，这样只需要计算一次"""
    average: Annotated[Optional[Decimal], Field(default=None, description='均价')]
    ma5: Annotated[Optional[Decimal], Field(default=None, description='5日均线')]
    ma10: Annotated[Optional[Decimal], Field(default=None, description='10日均线')]
    ma20: Annotated[Optional[Decimal], Field(default=None, description='20日均线')]
    ma30: Annotated[Optional[Decimal], Field(default=None, description='30日均线')]
    date: Annotated[Optional[str], Field(default=None, description='日期 (兼容日k、周k等)')]


class AStockSituation(BaseModel):
    """A股大盘概况"""
    ups: Annotated[int, Field(default=0, description='上涨家数')]
    downs: Annotated[int, Field(default=0, description='下跌家数')]
    evens: Annotated[int, Field(default=0, description='平盘家数')]
    stop_ups: Annotated[int, Field(default=0, description='涨停家数')]
    stop_downs: Annotated[int, Field(default=0, description='跌停家数')]
    _10_8: Annotated[int, Field(default=0, description='< -8% 家数')]
    _8_6: Annotated[int, Field(default=0, description='-8% ~ -6% 家数')]
    _6_4: Annotated[int, Field(default=0, description='-6% ~ -4% 家数')]
    _4_2: Annotated[int, Field(default=0, description='-4% ~ -2% 家数')]
    _2_0: Annotated[int, Field(default=0, description='-2% ~ 0% 家数')]
    _0_2: Annotated[int, Field(default=0, description='0% ~ +2% 家数')]
    _2_4: Annotated[int, Field(default=0, description='+2% ~ +4% 家数')]
    _4_6: Annotated[int, Field(default=0, description='+4% ~ +6% 家数')]
    _6_8: Annotated[int, Field(default=0, description='+6% ~ +8% 家数')]
    _8_10: Annotated[int, Field(default=0, description='+8% ~ +10% 家数')]
