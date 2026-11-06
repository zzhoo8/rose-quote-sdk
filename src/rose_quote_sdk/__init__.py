"""rose-quote-sdk 入口，RoseQuoteSdk 单例持有 host/app_code 全局配置。"""

from typing import Annotated, Optional

from pydantic import Field

from rose_quote_sdk.common.tool.logger import init_logger
from rose_quote_sdk.model.quote import Quote


class RoseQuoteSdk(object):
    """行情 SDK 客户端（单例），初始化后 host/app_code 全局唯一。"""

    _instance = None

    def __new__(
        cls,
        host: Annotated[Optional[str], Field(description='行情 API Host')] = None,
        app_code: Annotated[Optional[str], Field(description='行情 API AppCode')] = None,
    ):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.host = host
            cls._instance.app_code = app_code
            init_logger(debug=True, package=__package__)
        return cls._instance

    def __init__(self, host=None, app_code=None):
        pass

    def get_quote(self, security_code: str) -> Quote:
        """获取实时行情数据"""
        return Quote.get(host=self.host, security_code=security_code, app_code=self.app_code)
