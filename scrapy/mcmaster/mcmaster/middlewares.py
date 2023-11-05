# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import re
import time
import random
from scrapy import signals


import requests



class McmasterSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ProxyMiddleware:
    def __init__(self, settings):
        self.proxy_dns = settings.get('PROXY_DNS')
        self.proxy_username = settings.get('PROXY_USERNAME')
        self.proxy_password = settings.get('PROXY_PASSWORD')
        self.proxy_url = f'http://{self.proxy_username}:{self.proxy_password}@{self.proxy_dns}'
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        request.meta['proxy'] = self.proxy_url


class McmasterDownloaderMiddleware(ProxyMiddleware):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self, settings):
        self.settings = settings
        self.proxy_url = self._get_proxy(settings)
        self.headers=settings.get('DEFAULT_REQUEST_HEADERS')

    @staticmethod
    def _get_proxy(settings):
        proxy_dns = settings.get('PROXY_DNS')
        proxy_username = settings.get('PROXY_USERNAME')
        proxy_password = settings.get('PROXY_PASSWORD')
        return f'http://{proxy_username}:{proxy_password}@{proxy_dns}'


    def _init_cookies(self):
        with requests.Session() as session:
            session.headers.update(self.headers)
            session.proxies.update({
                'http': self.proxy_url,
                'https': self.proxy_url
            })
            # init data
            response = session.get('https://www.mcmaster.com/init/McMasterApp/MobileInitData.aspx')
            if response.status_code == 200:
                mv_id = response.json().get('VolatileAssetVersion')
            else:
                raise Exception(f"Unable to get mv_id: {response.status_code}")
            # visitor cookies
            response = session.get(url=f"https://www.mcmaster.com/{mv_id}/webparts/mcmasterapp/mobilevisitordata.aspx?rtrv=branch&VersionDate=20500101&device=iPhone") 
            if response.status_code != 200:
                raise Exception(f"Unable to get visitor data : {response.status_code}")
            # get token
            response = session.get(url=f"https://www.mcmaster.com/{mv_id}/TokenAuthorization.aspx")
            if response.status_code != 200:
                raise Exception(f"Unable to get token : {response.status_code}")

            return session.cookies

    def _refresh_token(self, mv_id, cookies):

        with requests.Session() as session:
            session.headers.update(self.headers)
            session.proxies.update({
                'http': self.proxy_url,
                'https': self.proxy_url
            })
            # visitor cookies
            response = session.get(url=f"https://www.mcmaster.com/{mv_id}/webparts/mcmasterapp/mobilevisitordata.aspx?rtrv=branch&VersionDate=20500101&device=iPhone") 
            if response.status_code != 200:
                raise Exception(f"Unable to get visitor data : {response.status_code}")
            
            response = session.get(url=f"https://www.mcmaster.com/{mv_id}/TokenAuthorization.aspx")
            if response.status_code != 200:
                raise Exception(f"Unable to get auth token : {response.status_code}")
            
            cat = session.cookies.get('cat')
        return cat
    
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(crawler.settings)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        if response.status in [420, 403]:
            spider.logger.info('Sleeping for 1 minute')
            time.sleep(60)

            spider.logger.info(f'Refreshing Token for url: {request.url}')
            cookies = self._init_cookies()
            for cookie in cookies:
                request.cookies[cookie.name] = cookie.value
            return request

        elif response.status == 200:
            # spider.logger.info(f'Successfully fetched data for url : {request.url}')
            return response
        
        else:
            spider.logger.error(f'Unable to fetch data status_code : {response.status}')
            raise Exception('Unable to fetch data')

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


if __name__ == "__main__":
    cookies = McmasterDownloaderMiddleware._init_cookies()
    for k, v in cookies.get_dict():
        print(k, v)
