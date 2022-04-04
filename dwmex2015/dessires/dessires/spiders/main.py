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
main_url = 'https://www.dessires.com/mx/es/'
# cop_pattern = re.compile(r'.*(COP|USD).*')
dict_cities = {
 'cancun': 'ciudad.php?id=5',
 'cd. méxico': 'ciudad.php?id=1',
 'cuernavaca': 'ciudad.php?id=10',
 'guadalajara': 'ciudad.php?id=2',
 'los cabos': 'ciudad.php?id=28',
 'playa del carmen': 'ciudad.php?id=15',
 'puebla': 'ciudad.php?id=3',
 'queretaro': 'ciudad.php?id=4',
 'toluca': 'ciudad.php?id=7',
 'tulum': 'ciudad.php?id=73'}


class Webscrape(scrapy.Spider):
    name = 'dessires'
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
        
        

        input_geozone = getattr(self,'geo_zone',None)
        if input_geozone is None:
            input_geozone = 'todas'
        else:
            input_geozone = input_geozone.lower()


        if input_category == 'todas' and input_geozone == 'todas':
            url = main_url
        elif input_category == 'todas' and input_geozone != 'todas':
            url = f'{main_url}/{dict_cities[input_geozone]}'
        # elif input_geozone == 'todas' and input_category != 'todas':
        #     url = f'{main_url}/{input_category}/'
        # else:
        #     url = f'{main_url}/{input_category}/{input_geozone}/'
        
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        url = response.request.url
        if url == main_url:
            links = set(response.xpath('//div[@class="search-box"]//div[@class="row"]//li/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Category {idx} / {len(links)}')
                yield response.follow(link, callback=self.parse)

        else:
            links = set(response.xpath('//div[@class="module"]//a/@href').getall())
           # links = set(response.xpath('//article/figure/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Links {idx} / {len(links)}')
                yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
            
 
        
        # next_page = response.xpath('//a[@id="button_arrow_pagination"]/@href').get()
        # if next_page:
        #     yield response.follow(next_page, callback= self.parse)


    def new_parse(self, response, **kwargs):
        link =f'{main_url}{kwargs["link"]}'

        
        title = response.xpath('//h1[@class="text-gold"]/text()').get().capitalize()
        try:
            geo_zone = response.xpath('//div[@class="item-anunciate"]//li[@class="breadcrumb-item"]/a/text()').getall()[1]
        except:
            geo_zone = None
        #Categoria
        category =  geo_zone
        #Description
        try:
            description1 = response.xpath('//div[@class="col-sm-6 gray-box space-right-border"]/table//tr/td/span/text()').getall()
            description2 = response.xpath('//div[@class="col-sm-6 gray-box space-right-border"]/table//tr/td/text()').getall()
            description = self.remove_spaces( ' -- '.join([' '.join(i) for i in list(zip(description1,description2))]) )
        except:
            description = None
        phone =  self.remove_spaces( response.xpath('//h4/i[@class="ion-ios-telephone"]/following-sibling::a/text()').get() )
        try:
            whatsapp = response.xpath('//h4/i[@class="ion-social-whatsapp"]/following-sibling::a/@href').get()
        except:
            whatsapp = None
        email = None
        

        yield{
            'Categoria del Anuncio':category,
            'Zona Geografica (Estado y Ciudad)':geo_zone,
            'Titulo del Anuncio':title,
            'Descripcion del Anuncio':description,
            'Telefono de Contacto':phone,
            'WhatsApp de Contacto Numero':self.remove_spaces(response.xpath('//h4/i[@class="ion-social-whatsapp"]/following-sibling::a/text()').get()),
            'Link WhatsApp de Contacto Anuncio':whatsapp,
            'Email de Contacto':email,
            'ID Anuncio':None,
            'Url del Anuncio':link,
            'Nombre de la Página':'Dessires'
            }


    def remove_spaces(self,x):
        return x.replace('  ',' ').replace('\r','').replace('\t','').replace('\xa0','').replace('\n','').strip()


