from typing import Any, Callable
import time
import traceback
from functools import wraps


def try_except_log(logger_error: callable = None, text_browser=None, message_box=None) -> Callable[..., Any | None]:
    """
    用于捕获函数的异常并返回异常对象. 

    参数:
    - logger_error (callable, 可选): 用于记录异常的日志函数. 默认为None. 
    - textbrowser (QWidget, 可选): 用于显示异常信息的文本框. 默认为None. 

    返回值:
    Callable[..., Any | None]: 包装后的函数, 捕获函数的异常并返回异常对象. 
    """
    def try_decorator(func: callable) -> Callable[..., Any | None]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                e = traceback.format_exc()
                if logger_error:
                    logger_error(e, extra={'moduleName': func.__module__, 'functionName': func.__qualname__})
                else:
                    print(e)
                if text_browser:
                    text_browser.append_text(e)
                if message_box:
                    message_box.warning(None, 'Warning', e)
                return None
        return wrapper
    return try_decorator


def time_counter(func) -> Callable[..., tuple[Any, float]]:
    """
    这是一个装饰器函数, 用于计算函数的执行时间. 

    参数:
    - func: 被装饰的函数

    返回值:
    包装后的函数, 返回被装饰函数的执行结果和执行时间的元组
    """
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f'[{func.__module__}] - [{func.__qualname__}]-[runTime]:\t', end - start)
        return result
    return wrapper
