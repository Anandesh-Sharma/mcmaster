import os

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from utils.driver import Driver
from utils.extract_data import ExtractData
import xpath as xp

class MCMaster(Driver):
    def __init__(self, family_url):
        self.d1 = Driver()
        self.d2 = Driver()
        self.d3 = Driver()
        self.family_url = family_url
        self.family_name = family_url.split('/')[-2] if family_url.endswith('/') else family_url.split('/')[-1]

    @staticmethod
    def _get_filepath(family_name, product_url):
        if product_url.endswith('/'):
            product_url = product_url[:-1]
        return os.path.join(
            family_name, 
            product_url.replace('https://www.mcmaster.com/products/', '') + '.csv'
        )
        

    def get_family(self):
        self.d1.get(self.family_url)
        categories = self.d1.driver.find_elements(By.XPATH, xp.CATEGORIES)
        for i in categories:
            category_url, category_name = i.get_attribute('href'), i.text.replace(', ', '-').replace(' & ', '-').replace(' ', '-')
            self.get_categories(category_url, category_name)
    

    def get_categories(self, category_url):
        self.d2.get(category_url)
        products = self.d2.driver.find_elements(By.XPATH, xp.PRODUCTS)
        for i in products:
            product_urls = [j.get_attribute('href') for j in i.find_elements(By.XPATH, xp.PRODUCT_URLS)]
            for product_url in product_urls:
                self.get_products(product_url)
                break


    def get_products(self, product_url):
        self.d3.get(product_url)
        for table in self.d3.driver.find_elements(By.XPATH, xp.TABLES):
            try:
                head = table.find_element(By.XPATH, './thead')
                body = table.find_element(By.XPATH, './tbody')
                filepath = self._get_filepath_and_filename(self.family_name, product_url)
                ed = ExtractData(body=body, head=head, filepath=filepath, product_url=product_url)
                print(ed.headers)
                print(ed.body_data)

            except NoSuchElementException:
                continue


if __name__ == '__main__':
    mc = MCMaster(
        family_url='https://www.mcmaster.com/pulling-lifting'
    )
    mc.get_family()