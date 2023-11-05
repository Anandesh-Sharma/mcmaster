from loguru import logger
import functools
import traceback
from selenium.common.exceptions import *

def error_handler(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            if func.__name__ == 'get_family':
                d = self.d1
                result = func(self, *args, **kwargs)
            elif func.__name__ == 'get_categories':
                d = self.d2
            else:
                d = self.d3

            url = d.current_url
            result = func(self, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            if isinstance(e, NoSuchElementException):
                logger.error(e)
            else:
                logger.error(e)
                self.driver.quit()
                self.init_driver(url)
                result = func(self, *args, **kwargs)
        return result
    return wrapper