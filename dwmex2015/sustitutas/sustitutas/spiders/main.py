from operator import ge
import scrapy 
import urllib
import subprocess
import re
import datetime as dt
import logging
import time
from scrapy.crawler import CrawlerProcess
from datetime import datetime
from selenium import webdriver

logger = logging.getLogger()
mes = datetime.now().month
dia = datetime.now().day
year = datetime.now().year

# pattern_geozone = re.compile(r'(Localización|Ciudad): (.*)')
main_url = 'https://mx.sustitutas.com'
# cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'sustitutas'
    #allowed_domains = ['www.cinescallao.es']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    def start_requests(self):
        input_category = getattr(self,'category',None)
        #print('Input c',input_category)
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
            links = set(response.xpath('//h3/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Category {idx} / {len(links)}')
                yield response.follow(link, callback=self.parse)

        else:
            links = set(response.xpath('//h2/a/@href').getall())
           # links = set(response.xpath('//article/figure/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Links {idx} / {len(links)}')
                yield response.follow(link, callback=self.s_parse,cb_kwargs={'link':link})
            
 
        
        # next_page = response.xpath('//a[@id="button_arrow_pagination"]/@href').get()
        # if next_page:
        #     yield response.follow(next_page, callback= self.parse)


    def s_parse(self,response, **kwargs):
        url = kwargs['link']
        links = set(self.get_links_by_scralling(url,xpath_expresion='//a'))
        for idx, link in enumerate(links):
            logger.info(f'Category {idx} / {len(links)}')
            yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})


    def new_parse(self, response, **kwargs):
        link = kwargs['link']

        
        title = response.xpath('//header/span[@itemprop="name"]/text()').get()
        try:
            geo_zone = response.xpath('//ul[@itemscope="itemscope"]/li[5]//text()').get()
        except:
            geo_zone = None
        #Categoria
        category =  geo_zone
        #Description
        try:
            description = ' '.join(response.xpath('//div[@class="profile-description pt-15px mw-600:pt-40px clear-both mb-25px"]/p//text()').getall()).strip()
        except:
            description = None
        phone =  response.xpath('//span[@class="title1 fr telephone-btn color-red-1 font-28px line-height-32px font-w-bold float-right"]//span/text()').get()
        try:
            whatsapp = response.xpath('//*[contains(.," Whatsapp")]/parent::a/@href').get()
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
            'Nombre de la Página':'Sustitutas'
            }


             
    def remove_spaces(self,x):
        return x.replace('  ',' ').replace('\r','').replace('\t','').replace('\xa0','').replace('\n','').strip()
    
    def get_links_by_scralling(self,url,xpath_expresion, attribute='href'):
        #Instanciar el navegador
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        #chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
        driver = webdriver.Firefox(executable_path='../drivers/geckodriver.exe', options=options)
        driver.get(url)
        #Get links scralling
        box = []
        previous_heigth = driver.execute_script('return document.body.scrollHeight')
        while True:
            driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            time.sleep(0.5)
            new_heigth = driver.execute_script('return document.body.scrollHeight')
            if new_heigth == previous_heigth:
                box.extend(driver.find_elements_by_xpath(xpath_expresion))
                break
            previous_heigth = new_heigth
        if attribute != 'text':
            box = [i.get_attribute(attribute) for i in box]
        else:
            box = [i.text for i in box]
        driver.close()
        return box
