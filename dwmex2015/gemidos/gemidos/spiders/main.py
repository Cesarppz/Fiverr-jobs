from operator import ge
import scrapy 
import urllib
import subprocess
import re
import datetime as dt
import logging

from scrapy.crawler import CrawlerProcess
from datetime import datetime

logger = logging.getLogger()
mes = datetime.now().month
dia = datetime.now().day
year = datetime.now().year

pattern_geozone = re.compile(r'(Localización|Ciudad): (.*)')
main_url = 'https://gemidos.tv'
cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'gemidos'
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
            url = f'{main_url}/categoria-{input_category}/'
        else:
            url = f'{main_url}/{input_geozone}/{input_category}/'
        
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
       links = set(response.xpath('//a[@class="listing-link"]/@href').getall())
       for idx, link in enumerate(links):
           logger.info(f'Links {idx} / {len(links)}')
           yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
        
        # next_page = response.xpath('//span[@class="next"]/a/@href').get()
        # if next_page:
        #     next_page = '{}{}'.format(main_url,next_page)
        #     yield response.follow(next_page, callback= self.s_parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']

        
        title = response.xpath('//h1/text()').get()
        
        geo_zone = response.xpath('//div[@class="d-flex"]/div[@class="breadcrumb-item d-flex align-items-baseline mx-0"]//span[@itemprop="name"]/text()').getall()[1:]
        geo_zone = ' - '.join(geo_zone)        
        #Categoria
        category =  response.xpath('//span[@class="badge badge-accent "]//text()').getall()
        category = ' - '.join(category).replace('\n','')
        #Description
        try:
            description = response.xpath('//div[@class="pub-about-text pub-about-preview"]//text()').get().replace('\n',' ').capitalize().strip()
        except:
            description = None
        phone = response.xpath('//a[@class="btn btn-primary pub-menu-button"][@data-analytics="pub,call"]/@href').get()
        try:
            whatsapp = response.xpath('//a[@class="btn btn-primary pub-menu-button"][@data-analytics="pub,whatsapp,button"]/@href').get()
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
            'Nombre de la Página':'Gemidos TV'
            }


