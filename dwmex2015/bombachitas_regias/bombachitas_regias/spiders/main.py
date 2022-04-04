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
main_url = 'https://www.bomboncitasregias.com/home.html'
# cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'bombachitas_regias'
    #allowed_domains = ['www.cinescallao.es']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    start_urls = [main_url]
        

    def parse(self, response):

        links = set(response.xpath('//table//tr/td/a/@href').getall())
        for idx, link in enumerate(links):
            logger.info(f'Category {idx} / {len(links)}')
            yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
            
 
        
        # next_page = response.xpath('//a[@id="button_arrow_pagination"]/@href').get()
        # if next_page:
        #     yield response.follow(next_page, callback= self.parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']

        
        title = response.xpath('//font[@size="7"]/text()').get()
        try:
            geo_zone = None
        except:
            geo_zone = None
        #Categoria
        category =  response.xpath('//font[@size="2"][@color="#800000"]/b/text()').get()
        #Description
        try:
            description = self.remove_spaces(' '.join(response.xpath('//b[text()="Descripción"]/ancestor::tr/following-sibling::tr//font/text()').getall()).strip())
        except:
            description = None
        phone =  response.xpath('//td/font[contains(.,"Télefono")]/following-sibling::font/text()').get()
        try:
            whatsapp = response.xpath('//td/font[contains(.,"Click para")]/following-sibling::a/@href').get()
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
            'Nombre de la Página':'Bombachitas Regias'
            }

    def remove_spaces(self,x):
        return x.replace('  ',' ').replace('\r','').replace('\t','').replace('\xa0','').replace('\n','').strip()


