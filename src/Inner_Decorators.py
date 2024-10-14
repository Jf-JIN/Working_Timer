from typing import Any, Callable
import traceback
from functools import wraps


def try_except_log(logger_error: callable = None, text_browser=None, message_box=None) -> Callable[..., Any | None]:
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
