import re

import i18n


class BusinessException(RuntimeError):
    error_code: int = -1
    error_msg: str = ''
    error_more_msg: str = None

    # 匹配 xxx.xxx 或 xxx.xxx.xxx 格式的翻译 key，第一个部分只能是英文、下划线或连字符
    _I18N_KEY_PATTERN = re.compile(r'^[a-zA-Z_-]+\.\w+(\.\w+)*$')

    def __init__(self, error: list, more_msg: str = None):
        self.error_code = error[0]
        msg = error[1]
        # 如果是翻译 key 格式，则动态翻译
        if self._I18N_KEY_PATTERN.match(msg):
            msg = i18n.t(msg)
        self.error_msg = msg if more_msg is None else more_msg

    def __str__(self):
        return f'错误码={self.error_code}, 错误信息={self.error_msg}, 更多错误信息={self.error_more_msg}'
