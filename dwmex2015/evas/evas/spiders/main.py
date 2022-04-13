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

pattern = re.compile(r'https://evas.mx/ciudad/(.*)/')
main_url = 'https://evas.mx'
cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'evas'
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
            url = f'{main_url}/cuidad/{input_geozone}/'
        elif input_geozone == 'todas' and input_category != 'todas':
            url = f'{main_url}/ciudad/{input_category}/'
        else:
            url = f'{main_url}/ciudad/{input_category}/'
        
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        actual_url = response.request.url
        if actual_url == main_url:
            category = 'No category'   
        else:
            category = re.match(pattern,actual_url).group(1)
            category =  ' '.join(category.split('-')) 

        links = set(response.xpath('//div[@class="row"]/div[@class="escort-item col-12 col-sm-12 col-md-4 col-lg-2"]/a/@href').getall())
        for idx, link in enumerate(links):
            logger.info(f'Links {idx} / {len(links)}')
            yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link,'category':category})
       
 
        
        # next_page = response.xpath('//span[@class="next"]/a/@href').get()
        # if next_page:
        #     next_page = '{}{}'.format(main_url,next_page)
        #     yield response.follow(next_page, callback= self.s_parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']
        category = kwargs['category']
        
        title = response.xpath('//h2[@class="single-escort-name"]/text()').get().split('-')[0].replace('.','')
        
        geo_zone = response.xpath('//h2[@class="single-escort-name"]/text()').get().split('-')[1]
        if category == 'No category':
            category = geo_zone
        #Categoria
        # category = re.match(pattern,response.request.url).group(1)
        # category =  ' '.join(category.split('-'))
        #Description
        try:
            eliminar = response.xpath('//div[@class="name-phone col-md-12 pt-4 pb-2 pl-0 pr-0"]/h4/text()').get()
            description = response.xpath('//div[@class="name-phone col-md-12 pt-4 pb-2 pl-0 pr-0"]//text()').getall()
            description = ' '.join(description)
            eliminar = re.search(eliminar,description).span()[-1]
            description = description[eliminar:].replace('\r','').replace('\n','').replace('  ',' ').strip()
        except:
            description = None
        phone = response.xpath('//span[@class="single-escort-phone"]/text()').get()
        try:
            whatsapp = response.xpath('//div[@class="name-phone col-md-4 pt-4 pb-2 pl-0 pr-0 text-right"]/a/@href').get()
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
            'Nombre de la Página':'Evas'
            }


