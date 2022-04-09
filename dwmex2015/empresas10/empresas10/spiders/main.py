from operator import ge
from turtle import pos
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

pattern_email = re.compile(r'.*@.*\..*')
pattern_geozone = re.compile(r'\d+ (.*)')
main_url = 'https://empresas10.com/mex/'
# cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'empresas10'
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
        # elif input_geozone == 'todas' and input_category != 'todas':
        #     url = f'{main_url}/{input_category}/'
        # else:
        #     url = f'{main_url}/{input_category}/{input_geozone}/'
        
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        url = response.request.url
        if url == main_url:
            links = set(response.xpath('//h3/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Category {idx} / {len(links)}')
                yield response.follow(link, callback=self.parse)

        else:
            links = set(response.xpath('//h3[@class="pt-cv-title"]/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Links {idx} / {len(links)}')
                yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
            
 
        
        # next_page = response.xpath('//a[@id="button_arrow_pagination"]/@href').get()
        # if next_page:
        #     yield response.follow(next_page, callback= self.parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']

        
        title = response.xpath('//h1/text()').get()
        try:
            geo_zone = ','.join(response.xpath('//p/strong[contains(.,"Ubicación:")]/parent::p/text()').get().split(',')[-2:]).strip()
            geo_zone = re.match(pattern_geozone,geo_zone).group(1)
        except:
            geo_zone = None
        #Categoria
        category =  geo_zone

        phone = response.xpath('//p/strong[contains(.,"Teléfonos:")]/parent::p/text()').get()
        try:
            postal =  response.xpath('//p/strong[contains(.,"Ubicación:")]/parent::p/text()').get().split(',')[-2].strip().split()[0]
        except:
            postal = None
        try:
            whatsapp = None
        except:
            whatsapp = None
        email_list =  response.xpath('//p/strong[contains(.,"Email:")]/parent::p/text()').getall()
        email_box = []
        for i in email_list:
            if re.match(pattern_email,i.strip()):
                email_box.append(i.strip())
        email = ' - '.join(list(set(email_box)))
        yield{
            'Nombre empresa':title,
            'Ciudad':geo_zone,
            'Categoría':category,
            'Titulo del Anuncio':title,
            'Telf':phone,
            'WhatsApp de Contacto Numero':None,
            'WhatsApp':whatsapp,
            'Email':email,
            'Postal':postal,
            'Web':link,
            'Nombre de la Página':'Empresas 10'
            }
     
    def remove_spaces(self,x):
        return x.replace('  ',' ').replace('\r','').replace('\t','').replace('\xa0','').replace('\n','').strip()


