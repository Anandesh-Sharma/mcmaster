import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
import undetected_chromedriver as uc
from undetected_chromedriver import ChromeOptions

from .cache import CacheHTMLPages
from ..settings import ARGUMENTS

class Driver(CacheHTMLPages):
    def __init__(self, args=ARGUMENTS) -> None:
        super().__init__()
        options = ChromeOptions()
        for i in args:
            options.add_argument(i)
        self.driver = uc.Chrome(headless=False, use_subprocess=True, options=options)
    def get(self, url):
        # get cache file if exists
        if not self.get_cache(self.driver, url):
            self.driver.get(url)
            time.sleep(3)
            self.set_cache(self.driver)