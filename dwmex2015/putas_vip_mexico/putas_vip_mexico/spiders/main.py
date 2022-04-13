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

pattern = re.compile(r'https://putasvipmexico.com/(.*)/(.*)(\?page=.)?.*')
main_url = 'https://putasvipmexico.com'
# cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'putas_vip_mexico'
   #] allowed_domains = ['https://mx.atlasescorts.com/']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    start_urls = [
            'https://putasvipmexico.com'
    ]


    def parse(self, response):

        links = set(response.xpath('//div[@class="col-6 home-box-states-in-category align-middle"]//a/@href').getall())
        for idx, link in enumerate(links):
            logger.info(f'Links {idx} / {len(links)}')
            yield response.follow(link, callback=self.f_parse)
       
 
    def f_parse(self, response):
        category = re.match(pattern,response.request.url).group(1)
        category = category.lower()
        geo_zone = re.match(pattern,response.request.url).group(2)
        geo_zone = geo_zone.lower()
        
        category_input = getattr(self, 'category', None)
        if category_input:
            category_input = category_input.lower() 
        else:
            category_input = 'all'

        geo_zone_input = getattr(self, 'geo_zone', None)
        if geo_zone_input:
            geo_zone_input = category_input.lower() 

        else:
            geo_zone_input = 'all'

        if category_input == category.lower() and geo_zone.lower() == geo_zone_input:  #Modificar para cambiar categorias
            links = set(response.xpath('//div[@class="row"]//div[@class="in-list-ad-title-ad"]/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Links {idx} / {len(links)}')
                yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link,'category':category,'geo_zone':geo_zone})

            next_page = response.xpath('//a[@rel="next"]/@href').get()
            if next_page:
                #next_page = '{}{}'.format(main_url,next_page)
                yield response.follow(next_page, callback= self.f_parse)
        
        
        elif category_input == 'all' and geo_zone_input == 'all':
            links = set(response.xpath('//div[@class="row"]//div[@class="in-list-ad-title-ad"]/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Links {idx} / {len(links)}')
                yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link,'category':category,'geo_zone':geo_zone})

            next_page = response.xpath('//a[@rel="next"]/@href').get()
            if next_page:
                #next_page = '{}{}'.format(main_url,next_page)
                yield response.follow(next_page, callback= self.f_parse)

        elif category_input == 'all' and geo_zone.lower() == geo_zone_input:
            links = set(response.xpath('//div[@class="row"]//div[@class="in-list-ad-title-ad"]/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Links {idx} / {len(links)}')
                yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link,'category':category,'geo_zone':geo_zone})

            next_page = response.xpath('//a[@rel="next"]/@href').get()
            if next_page:
                #next_page = '{}{}'.format(main_url,next_page)
                yield response.follow(next_page, callback= self.f_parse)

        elif geo_zone_input == 'all' and category_input == category.lower():
            links = set(response.xpath('//div[@class="row"]//div[@class="in-list-ad-title-ad"]/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Links {idx} / {len(links)}')
                yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link,'category':category,'geo_zone':geo_zone})

            next_page = response.xpath('//a[@rel="next"]/@href').get()
            if next_page:
                #next_page = '{}{}'.format(main_url,next_page)
                yield response.follow(next_page, callback= self.f_parse)

        else: 
            pass


    def new_parse(self, response, **kwargs):
        link = kwargs['link']
        
        
        title = ' '.join(response.xpath('//div[@class="title-ad-page"]/h1//text()').getall()).strip()
        
        geo_zone = kwargs['geo_zone'].split('?')[0]
        #Categoria
        category = kwargs['category']       
        #Description
        try:
            description =  ' '.join(response.xpath('//div[@class="in-ad-page-container-ad-content"]/text()').getall()).strip()
            description = self.remove_spaces(description)
        except:
            description = None
        phone = response.xpath('//div[@class="col-sm-12 col-lg-6 in-ad-page-container-ad-contact-link"]/a/text()').getall()[-1].strip()
        try:
            whatsapp = 'https://putasvipmexico.com' + response.xpath('//div[@class="col-sm-12 col-lg-6 in-ad-page-container-ad-contact-link"]/a[@target="_blank"]/@href').get()
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
            'Url del Anuncio':main_url + link,
            'Nombre de la Página':'Putas Vip Mexico'
            }

    def remove_spaces(self,x):
        return x.replace('  ',' ').replace('\r','').replace('\t','').replace('\xa0','').replace('\n','').strip()

