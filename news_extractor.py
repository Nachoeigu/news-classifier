import requests
from lxml import html
from unidecode import unidecode
import re
import pandas as pd
import time
from lxml import etree
import html as html_module

from constants import TN_HEADERS

class TodoNoticias:

    def __init__(self):
        self.all_links = []
        self.labels = []
        self.content = []
        self.titles = []

    def __analyzing_page_errors(self, response):
        if response.status_code != 200:
            return True
        else:
            return False

    def request_server(self, type:str, topic=None, url=None):
        if type == 'links':
            for page in range(1, 550):
                response = requests.get(f'https://tn.com.ar/{topic}/pagina/{page}/', headers=TN_HEADERS)
                
                condition = False

                while condition == False:
                    if self.__analyzing_page_errors(response):
                        if str(response.content) == "b'Gateway Timeout'":
                            time.sleep(20)
                            response = requests.get(f'https://tn.com.ar/{topic}/pagina/{page}/', headers=TN_HEADERS)
                            if self.__analyzing_page_errors(response):
                                pass
                            else:
                                condition = True
                    else:
                        condition = True
                    
                data = html.fromstring(response.content.decode("utf-8"))
                urls = data.xpath('//article/a[@href]/@href')
                urls = ['https://www.tn.com.ar'+ url for url in urls]
                for enlace in urls:
                    self.all_links.append(enlace)
                    self.labels.append(topic)

        if type == 'articles':
            for idx, url in enumerate(self.all_links):
                print(f"Page number {idx}...")
                response = requests.get(f'{url}',  headers=TN_HEADERS)
                
                condition = False

                while condition == False:
                    if self.__analyzing_page_errors(response):
                        if str(response.content) == "b'Gateway Timeout'":
                            time.sleep(20)
                            response = requests.get(f'{url}',  headers=TN_HEADERS)
                            if self.__analyzing_page_errors(response):
                                pass
                            else:
                                condition = True

                        else:
                            break

                data = html.fromstring(response.content.decode("utf-8"))

                title = data.xpath('//h1/text()')[0]
                try:
                    first_lines = data.xpath('//h2[@class="article__dropline"]/text()')[0]
                except:
                    first_lines = ''
                paragraphs = data.xpath('//p[@class="paragraph" and not(.//i)]')
                
                complete_text = []
                for p in paragraphs:
                    text = html_module.unescape(etree.tostring(p).decode("utf-8"))
                    text =  re.sub('\<.*?\>','', text).strip()
                    complete_text.append(text)

                text = ' '.join(complete_text)

                text = unidecode((first_lines + ' ' + text).lower()).replace('  ',' ')
                
                self.titles.append(title)
                
                self.content.append(text)
    
    def save_csv(self, path_name):
        df = pd.DataFrame({'content': self.content,
                  'labels': self.labels})

        df.to_csv(f'{path_name}.csv', index = False)

    def load_files(self, path_name):
        return pd.read_csv(f'{path_name}')


