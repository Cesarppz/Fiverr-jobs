from operator import ge
import scrapy 
import urllib
import subprocess
import re
import datetime as dt
import logging
import time
from playwright.sync_api import sync_playwright
from scrapy.crawler import CrawlerProcess
from datetime import datetime
from selenium import webdriver

logger = logging.getLogger()
mes = datetime.now().month
dia = datetime.now().day
year = datetime.now().year

# pattern_geozone = re.compile(r'(Localización|Ciudad): (.*)')
main_url = 'https://mx.skokka.com'
# cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'skokka'
    #allowed_domains = ['www.cinescallao.es']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    def start_requests(self):
        input_category = getattr(self,'category',None)
        # print('Input c',input_category)
        if input_category is None:
            input_category = 'todas'
        else:
            input_category = '-'.join(input_category.split()).lower()
        
        # if input_category == 'escorts-y-putas':
        #     input_category = 'escorts'

        input_geozone = getattr(self,'geo_zone',None)
        if input_geozone is None:
            input_geozone = 'todas'
        else:
            input_geozone = '-'.join(input_geozone.split()).lower()

        if input_category == 'todas' and input_geozone == 'todas':
            url = main_url
        elif input_category == 'todas' and input_geozone != 'todas':
            url = f'{main_url}/{input_geozone}/'
        elif input_geozone == 'todas' and input_category != 'todas':
            url = f'{main_url}/{input_category}/'
        else:
            url = f'{main_url}/{input_category}/{input_geozone}/'
        
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        url = response.request.url
        if url == main_url:
            links = set(response.xpath('//div[@class="col-md-4"]/a/@href').getall())
            print(links)
            for idx, link in enumerate(links):
                logger.info(f'Category {idx} / {len(links)}')
                yield response.follow(link, callback=self.parse)

        else:
            links = set(response.xpath('//p[@class="item-title"]/a/@href').getall())
           # links = set(response.xpath('//article/figure/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Category {idx} / {len(links)}')
                yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
            
 
        
        next_page = response.xpath('//a[@title="siguiente"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback= self.parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']

        
        title = response.xpath('//h1[@class="main-title"]/text()').get().capitalize()
        try:
            geo_zone = response.xpath('//b[@translate="translate"]/text()').get().strip()
        except:
            geo_zone = None
        #Categoria
        category =  response.xpath('////div[@class="notranslate"]/text()').get().strip()
        #Description
        try:
            description = self.remove_spaces(response.xpath('//h1[@class="main-title"]/following-sibling::p/text()').get())
        except:
            description = None
        phone =  self.find_element(link,'//div[@class="col-md-3 contactdk"]/a[@class="btn btn-primary btn-block mt-1"]')
        try:
            whatsapp = self.find_element(link,'//div[@class="col-md-3 contactdk"]/a[@class="btn btn-whatsapp btn-block mt-3 waves-effect waves-light"]')
        except:
            whatsapp = None
        email = None
        

        yield{
            'Categoria del Anuncio':category,
            'Zona Geografica (Estado y Ciudad)':geo_zone,
            'Titulo del Anuncio':title,
            'Descripcion del Anuncio':description,
            'Telefono de Contacto':phone,
            'WhatsApp de Contacto Numero':phone,
            'Link WhatsApp de Contacto Anuncio':whatsapp,
            'Email de Contacto':email,
            'ID Anuncio':None,
            'Url del Anuncio':link,
            'Nombre de la Página':'Skokka'
            }

    def extact_email(self,xpath,url):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(3000)
            page.mouse.wheel(0,4000)
            email = page.query_selector(xpath).inner_text()

            browser.close()
            return email
    def click(self,xpath,url):
        #Setting
        options = webdriver.FirefoxOptions()
        options.add_argument('--private')
        options.add_argument('--no-sandbox')
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 12.2; rv:97.0) Gecko/20100101 Firefox/97.0')
        options.add_argument('--headless')
        #options.add_argument("--headless")
        driver = webdriver.Firefox(executable_path='/home/cesar/Documents/job/web_scraping/javier/agenda/driver/geckodriver', options=options)

        #Process
        driver.get(url)
        time.sleep(2)

        previous_heigth = driver.execute_script('return document.body.scrollHeight')
        while True:
            try:
                driver.find_element_by_xpath('//button[@id="ue-accept-button-accept"]').click()
            except Exception as ex:
                pass

            driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            time.sleep(2)
            new_heigth = driver.execute_script('return document.body.scrollHeight')
            if new_heigth == previous_heigth:
                time.sleep(1)
                try:
                    driver.find_element_by_xpath('//*[@class="listing-load-more "]').click()
                except:
                    try:
                        driver.find_element_by_xpath('//*[@class="listing-load-more"]').click()
                    except:
                        break
            previous_heigth = new_heigth
        results = [i.get_attribute('href') for i in driver.find_elements_by_xpath(xpath)]
        return results             


    def remove_spaces(self,x):
        return x.replace('  ',' ').replace('\r','').replace('\t','').replace('\xa0','').replace('\n','').strip()

    def find_element(self,url,xpath,attribute='href'):
        #Setting
        options = webdriver.FirefoxOptions()
        options.add_argument('--private')
        options.add_argument('--no-sandbox')
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 12.2; rv:97.0) Gecko/20100101 Firefox/97.0')
        options.add_argument('--headless')
        #options.add_argument("--headless")
        driver = webdriver.Firefox(executable_path='/home/cesar/Documents/job/web_scraping/javier/agenda/driver/geckodriver', options=options)

        #Process
        driver.get(url)
        time.sleep(2)

        results = driver.find_element_by_xpath(xpath).get_attribute(attribute)
        driver.close()
        return results  