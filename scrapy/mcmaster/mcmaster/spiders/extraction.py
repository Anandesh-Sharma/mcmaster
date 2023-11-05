import json
import os
import logging
import scrapy
import urllib.parse

from mcmaster.constants.vars import (
    BASEURL_MOBILE, FAMILIES, BASE_PARAMS
)


class ExtractionSpider(scrapy.Spider):
    name = 'mcmaster'
    logger_file = 'mcmaster.log'

    def __init__(self):
        logging.basicConfig(
            filename="log.txt", format="%(levelname)s: %(message)s", level=logging.INFO
        )

    @staticmethod
    def _save_json(file_path, data):
        with open(file_path, 'w') as f:
            f.write(json.dumps(data, indent=4))

    @staticmethod
    def _create_path(path):
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def _encode_url(url):
        return urllib.parse.quote_plus(url, safe=':/?&=')
    
    @staticmethod
    def _get_sub_category_requests(children, r=[]):
        if not children['Chldrn']:
            return r.append({
                'req': children['Lnk']['LnkUrl'],
                'relative_href': children['Lnk']['RelativeHref'],
            })
        else:
            for child in children['Chldrn']:
                ExtractionSpider._get_sub_category_requests(child, r)
            return r

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.mcmaster.com/init/McMasterApp/MobileInitData.aspx',
            callback=self._visitor_data,
            meta={'dont_cache': True}
        )

    def _visitor_data(self, response):
        mv_id = response.json().get('VolatileAssetVersion')
        if not mv_id:
            self.logger.error('Unable to get mv_id')
            raise Exception
        self.logger.info(f'Successfully got mv_id : {mv_id}')
        yield scrapy.Request(
            url=f"https://www.mcmaster.com/{mv_id}/webparts/mcmasterapp/mobilevisitordata.aspx?rtrv=branch&VersionDate=20500101&device=iPhone",
            callback=self._get_token,
            meta = {'dont_cache': True},
            cb_kwargs={'mv_id': mv_id}
        )
    
    def _get_token(self, response, mv_id):
        yield scrapy.Request(
            url=f"https://www.mcmaster.com/{mv_id}/TokenAuthorization.aspx",
            callback=self.get_families,
            meta = {'dont_cache': True},
            cb_kwargs={'mv_id': mv_id}
        )

    def get_families(self, response, mv_id):
        del response.meta['dont_cache']
        response.meta['mv_id'] = mv_id
        self.logger.info('Getting families data')

        for _ , family in enumerate(FAMILIES):
            self.logger.info(f'Fetching data for family : {family}')
            base_path = os.path.join(os.getcwd(), 'data', family)
            self._create_path(base_path)
            url = BASEURL_MOBILE.format(mv_id=mv_id) + f"request={family}&" + BASE_PARAMS
            encoded_url = self._encode_url(url)
            yield scrapy.Request(
                url=encoded_url,
                callback=self.get_categories,
                meta=response.meta,
                cb_kwargs={'path': base_path}
            )

    def get_categories(self, response, path):
        # From previous function
        data = response.json()
        self._save_json(os.path.join(path, 'categories.json'), data)

        self.logger.info('Getting categories')
        
        categories = data['flows'][0]['Chldrn']
        for category in categories:
            name = category['Lnk']['RelativeHref']
            request = category['Lnk']['RelativeHref']
            # create path for the category
            category_path = os.path.join(path, name)
            self._create_path(category_path)
            # encode url and call for extracting products
            url = BASEURL_MOBILE.format(mv_id=response.meta['mv_id']) + f"request={request}&" + BASE_PARAMS
            encoded_url = self._encode_url(url)
            yield scrapy.Request(
                url=encoded_url,
                callback=self.get_sub_categories,
                meta=response.meta,
                cb_kwargs={'path': category_path}
            )
    
    def get_sub_categories(self, response, path):
        # From previous function
        meta = response.meta
        data = response.json()
        self._save_json(os.path.join(path, 'sub-categories.json'), data)
        requests = self._get_sub_category_requests(data['CarouselFlows'][0], [])
        for i, request in enumerate(requests):
            url = BASEURL_MOBILE.format(mv_id=response.meta['mv_id']) + f"{request['req']}&{BASE_PARAMS}"
            encoded_url = self._encode_url(url)
            # meta['cookiejar'] = i
            yield scrapy.Request(
                url=encoded_url,
                callback=self.get_products,
                meta=meta,
                cb_kwargs={'path': os.path.join(path, '/'.join(request['relative_href'].split('/')[1:]))},
                dont_filter=True
            )

    def get_products(self, response, path):
        meta = response.meta
        data = response.json()
        self._create_path(path)
        self._save_json(os.path.join(path, 'products.json'), data)
        if not data.get('OrderedProductsInScope'):
            self.logger.info(f"No products found for {path}")
            return
        for part_number in data['OrderedProductsInScope']:
            url = BASEURL_MOBILE.format(mv_id=response.meta['mv_id']) + f"request=PARTNUMBER_{part_number}&" + BASE_PARAMS
            encoded_url = self._encode_url(url)
            # meta['cookiejar'] = response.meta['cookiejar']
            yield scrapy.Request(
                url=encoded_url,
                callback=self.extract_prodcut,
                meta=meta,
                cb_kwargs={'path': path},
                dont_filter=True
            )

    def extract_prodcut(self, response, path):
        data = response.json()
        part_path = os.path.join(path, 'parts_raw_json')
        self._create_path(part_path)
        self._save_json(os.path.join(part_path, f"{data['partNumber']}.json"), data)


        


    
