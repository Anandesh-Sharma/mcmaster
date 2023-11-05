
import time 
import math
import datetime
import os
import json
import hashlib
import time
from loguru import logger
from ..settings import BASE_URL


class CacheHTMLPages:
    def __init__(self):
        self.create_cache_folder_with_date()
        
    def create_cache_folder_with_date(self):
        self.cache_path = f'{os.getcwd()}/cache/{datetime.datetime.now().strftime("%Y-%m-%d")}'
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

    def set_cache(self, driver):
        url = driver.current_url
        try:
            html = driver.find_element("xpath", "//*").get_attribute("outerHTML")
        except Exception as e:
            logger.error(e)
            html = None
        url_hash = hashlib.sha1(str.encode(url)).hexdigest()
        url_path = f'{self.cache_path}/{url_hash}'
        if not os.path.exists(url_path):
            os.makedirs(url_path)
        
        metadata = {
            "url": url,
            "hashed_url": url_hash + '.html',
            "cache_path": self.cache_path,
            "size": f"{math.ceil(len(html) / 1024)} KB",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            
        }

        with open(f'{url_path}/{metadata["hashed_url"]}', 'w') as f:
            f.write(html.replace('href="/', 'href="https://www.mcmaster.com/'))
        with open(f'{url_path}/metadata.json', 'a') as f:
            f.write(json.dumps(metadata) + '\n')

    def get_cache(self, driver, url):
        if 'http' not in url:
            url = f'{BASE_URL}{url}'
        url_hash = hashlib.sha1(str.encode(url)).hexdigest()
        url_path = f'{self.cache_path}/{url_hash}'
        if os.path.exists(url_path):
            driver.get(f'file://{url_path}/{url_hash}.html')
            return True
        else:
            logger.info(f'Caching => {url}')
            return False