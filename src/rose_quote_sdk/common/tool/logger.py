import inspect
import logging
import os
import sys
from functools import wraps, partial
from typing import Annotated

logger = logging.getLogger(__package__)


def get_call_path(max_depth: int = 10) -> str:
    """
    获取从入口到当前函数的调用路径，如 'main → process → validate'
    """
    frames = inspect.stack()
    # frames[0]: current (get_call_path)
    # frames[1]: caller (likely the @log decorator)
    # frames[2]: the actual logged function
    # frames[3+]: ancestors
    path_funcs = []
    for frame in frames[3:3 + max_depth]:  # 从调用 @log 的函数开始往上
        func_name = frame.function
        # 跳过日志相关函数（可选）
        if 'logging' in frame.filename or func_name in ('function_log', '<module>'):
            continue
        path_funcs.append(func_name)
        if func_name == '<module>':  # 到达顶层
            break

    if not path_funcs:
        return "unknown"
    return " → ".join(reversed(path_funcs))


def init_logger(
    debug: Annotated[bool, 'debug模式'],
    package: Annotated[str, '包名'],
    level: Annotated[int, '日志级别'] = logging.INFO,
    logger_path: Annotated[str, '日志文件路径'] = None,
    _format: Annotated[str, '日志格式'] = '%(asctime)s - %(levelname)s - 进程%(process)d:线程%(thread)d - %(filename)s:%(funcName)s:%(lineno)d - %(message)s'
) -> None:
    logger.setLevel(level)
    formatter = logging.Formatter(fmt=_format)

    # Debug模式不输出日志文件
    if debug:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(fmt=formatter)
        logger.addHandler(hdlr=console_handler)
    else:
        if not logger_path or len(logger_path) == 0:
            logger_path = os.path.join(os.getcwd(), f"{package}.log")
        else:
            logger_path = os.path.join(logger_path, f"{package}.log")

        os.makedirs(os.path.dirname(logger_path), exist_ok=True)

        from logging.handlers import TimedRotatingFileHandler
        file_handler = TimedRotatingFileHandler(
            logger_path,
            encoding='utf-8',
            when='midnight',
            interval=1,
            backupCount=7
        )
        file_handler.suffix = '%Y-%m-%d'
        file_handler.setFormatter(fmt=formatter)
        logger.addHandler(hdlr=file_handler)


def log(func=None, *, tag=None):
    if func is None:
        return partial(log, tag=tag)

    # --- 阶段1：装饰时预处理 (只执行一次，不影响运行性能) ---

    # 获取函数参数名列表
    # 使用 inspect 获取参数签名（比直接读 __code__ 更稳健，能处理部分封装对象）
    try:
        sig_params = list(inspect.signature(func).parameters.keys())
    except Exception:
        sig_params = []

    # 判断是否需要跳过第一个参数
    # 如果参数列表不为空，且第一个参数叫 self 或 cls，则标记从第1个开始取
    start_index = 1 if sig_params and sig_params[0] in ('self', 'cls') else 0

    # 【新增】判断是否是异步函数
    is_async = inspect.iscoroutinefunction(func)

    # 提取公共的日志生成逻辑
    def _log(*args, **kwargs):
        real_args = args[start_index:]
        args_str_list = [str(a) for a in real_args]
        kwargs_str_list = [f"{k}={v}" for k, v in kwargs.items()]
        params_str = ", ".join(args_str_list + kwargs_str_list)
        # 注意：这里调用 get_call_path 时可能需要根据层级调整 max_depth
        return f"[{tag if tag else ''}] {get_call_path(max_depth=3)} → {func.__name__}({params_str})"

    if is_async:
        @wraps(func)
        async def function_log(*args, **kwargs):
            # 异步包装器
            logger.info(_log(*args, **kwargs))
            # 真正地等待异步函数执行完成
            result = await func(*args, **kwargs)
            return result
    else:
        @wraps(func)
        def function_log(*args, **kwargs):
            # 同步包装器
            logger.info(_log(*args, **kwargs))
            result = func(*args, **kwargs)
            return result

    return function_log


def print_box(message: str):
    return f"""
=================================================================
{message}
=================================================================
    """
