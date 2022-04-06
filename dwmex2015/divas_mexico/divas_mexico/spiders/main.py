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

# cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'divas_mexico'
    
    #allowed_domains = ['www.cinescallao.es']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    def start_requests(self):
        input_category = getattr(self,'category',None)
        global main_url
        main_url = getattr(self,'main_url','https://divasmexico.com.mx')

        # print('Input c',input_category)
        if input_category is None:
            input_category = 'todas'
        else:
            input_category = '-'.join(input_category.split()).lower()
        
        # if input_category == 'escorts-y-putas':
        #     input_category = 'escorts'

        # input_geozone = getattr(self,'geo_zone',None)
        # if input_geozone is None:
        #     input_geozone = 'todas'

        # else:
        #     input_geozone = '-'.join(input_geozone.split()).lower()

        if input_category == 'todas' :
            url = main_url

        elif  input_category != 'todas':
            url = f'{main_url}/{input_category}/'
   
        
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        url = response.request.url
        if url == main_url:
            links = set(response.xpath('//div[@class="categories_title"]/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Category {idx} / {len(links)}')
                yield response.follow(link, callback=self.parse)

        else:
            links = set(response.xpath('//div[@class="item_list gallery"]/span[@class="titleAd"]/a/@href').getall())
           # links = set(response.xpath('//article/figure/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Links {idx} / {len(links)}')
                yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
            
 
        
        next_page = response.xpath('//a[text()=">"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback= self.parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']

        
        title = response.xpath('//h1[@class="product_name"]/text()').get()
        try:
            geo_zone = response.xpath('//li/a[contains(.,"Provincia")]/b/text()').get()
        except:
            geo_zone = None
        #Categoria
        category =  response.xpath('//li/a[contains(.,"Categoría")]/b/text()').get()
        #Description
        try:
            description = self.remove_spaces(' '.join(response.xpath('//h3[@itemprop="description"]//text()').getall()).strip())
        except:
            description = None
        try:
            phone =  response.xpath('//span[@class="contact_phone"]/text()').get().replace('Llamar','').strip()
        except:
            phone = None
        try:
            whatsapp = response.xpath('//span[@class="contact_mail"]/parent::a/@href').get().strip()
        except:
            whatsapp = None
        email = None
        
        if phone:
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
            'Nombre de la Página':'Divas Mexico'
            }


  
    def remove_spaces(self,x):
        return x.replace('  ',' ').replace('\r','').replace('\t','').replace('\xa0','').replace('\n','').strip()


