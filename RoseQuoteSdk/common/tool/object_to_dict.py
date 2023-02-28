# coding:utf-8
import datetime
from decimal import Decimal
from enum import Enum

try:
    from cassandra.cqlengine.models import Model
    from cassandra.util import Date
except ModuleNotFoundError as e:
    print(e)


def object2dict(obj, fields: str = None):
    """
    oject 转换为dict（不能序列化的方法也已经转换为字符串）
    这里需要注意：obj可能为dict，也可能为list，里面可能会嵌套dict和list
    :param obj:
    :param fields: 不转换这些key
    :return:
    """
    rst_dict = dict()
    # for public_key in self.__table__.columns
    if obj is None:
        return None
    if isinstance(obj, (tuple, list)):
        dicts = []
        for each in obj:
            dicts.append(object2dict(each, fields=fields))
        return dicts
    if isinstance(obj, dict):
        tmp_dict = obj
    # 兼容未安装cassandra的情况
    elif 'Model' in globals().keys() and isinstance(obj, Model):
        # 使用_as_dict会导致Date值错误
        # tmp_dict = obj._as_dict()
        tmp_dict = dict((k, v) for k, v in obj.items())
    else:
        if hasattr(obj, "__dict__"):
            # 是类实例, 获得实例的所有属性
            # todo 用__dict__对于继承的父类属性，在这里取不到，都是空
            tmp_dict = obj.__dict__
            # tmp_dict = dict()
            # for k in dir(obj):
            #     if k.startswith('_'):
            #         continue
            #     if getattr(obj, k) is None:
            #         continue
            #     if isinstance(getattr(obj, k), MethodType):
            #         continue
            #     tmp_dict[k] = getattr(obj, k)
            # tmp_dict = dict([(k, getattr(obj, k)) for k in dir(obj) if not k.startswith('_') and getattr(obj, k) is not None and not isinstance(getattr(obj, k), MethodType)])
        else:
            # 简单的值
            return obj

    for (key, value) in tmp_dict.items():
        if isinstance(value, list):
            rst_dict[key] = object2dict(value, fields=fields)
        elif isinstance(value, dict):
            rst_dict[key] = object2dict(value, fields=fields)
        elif isinstance(value, datetime.datetime):
            if fields and key not in fields.split(','):
                continue
            rst_dict[key] = value.strftime("%Y-%m-%d %H:%M:%S.%f")
        elif isinstance(value, datetime.date):
            if fields and key not in fields.split(','):
                continue
            rst_dict[key] = value.strftime("%Y-%m-%d")
        elif isinstance(value, Decimal):
            if fields and key not in fields.split(','):
                continue
            rst_dict[key] = str(value)
        elif isinstance(value, Enum):
            if fields and key not in fields.split(','):
                continue
            rst_dict[key] = value.value
        # 兼容未安装cassandra的情况
        elif 'Date' in globals().keys() and isinstance(value, Date):
            rst_dict[key] = value.__str__()
        elif key == '_sa_instance_state':
            continue
        elif hasattr(value, '__dict__'):
            # 如果成员是object, 需要递归序列化
            rst_dict[key] = object2dict(value, fields=fields)
        else:
            # 简单变量 isinstance(value, (int, str, list))
            # 只跳过值是简单变量的fields
            if fields and key not in fields.split(','):
                continue
            rst_dict[key] = value
    return rst_dict

