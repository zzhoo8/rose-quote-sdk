# coding:utf-8


class CommonError(object):

    CODE = 10000
    SUCCESS = [0, "success", 'success']
    INVALID_MOLE = [CODE + 10001, '非法的内部调用', '']
    PARAMETER_ERROR = [CODE + 10002, '参数错误', '']
    QUOTE_ERROR = [CODE + 10003, '市场数据错误', '']

    BE_PATIENT = [CODE + 10005, '请耐心等待', '']
    CONFIG_ERROR = [CODE + 10006, '全局配置错误', '']
    DATA_SOURCE_ERROR = [CODE + 10012, '数据源错误', '']
