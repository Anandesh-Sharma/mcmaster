from selenium.webdriver.common.by import By
import pandas as pd
import math
import os
from ..log import logger

class ExtractData:
    def __init__(self, body, head, filepath, product_url):
        self.headers = list()
        self.body_data = list()   
        self.product_url = product_url
        self.process_table_headers(head)
        self.process_table_body(body) 
        self.merge_headers()
        self.save_data(filepath)
    
    @staticmethod
    def _clean(text, type=None):
        if type == 'headers':
            


    
    @staticmethod
    def _validate_and_merge_headers(headers):
        if headers[0] * len(headers) == sum([len(i) for i in headers]):
            return list(map(lambda x: x[0], headers))
        else:
            logger.debug(headers)
            return False
    

    @staticmethod
    def _validate_body(headers, body):
        if len(headers[0]) != len(body[0]):
            return 
        
    
    def process_table_headers(self, head):
        table_titles = head.find_elements(By.XPATH, './tr')
        for index, tr in enumerate(table_titles):
            if tr.find_elements(By.XPATH, './td'):
                main_title = [i.text for i in tr.find_elements(By.XPATH, './td')]
                self.headers.append(main_title)
            else:
                titlen = []
                ths = tr.find_elements(By.XPATH, './th')
                for tr1 in ths:
                    col_span = tr1.get_attribute('colspan')
                    titlen += ([tr1.text] * int(col_span))
                
                self.headers.append(titlen)

        # validate and merge headers
        if not self._validate_and_merge_headers(self.headers):
            logger.error('headers validation failed for {}'.format(self.product_url))
            return False
        # merge headers
        
    def process_table_body(self, body):
        table_body = body.find_elements(By.XPATH, './tr')
        row_headers = ''
        for index, tr in enumerate(table_body):
            # row is a header actually
            if tr.find_elements(By.XPATH, './th'):
                row_headers = tr.text
                continue
            else:
                tds = tr.find_elements(By.XPATH, './td')
                row = []
                for index1, td in enumerate(tds):
                    row.append(td.text)
                
                if row_headers:
                    row.append(row_headers)

            self.body_data.append(row)

    def save_data(self, filepath):
        # generate the path and file name
        df = pd.DataFrame(self.body_data, columns=[v for k, v in self.headers.items()])