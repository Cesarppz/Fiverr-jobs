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

patter_category = re.compile(r'https://escortsmexico.net/(\w+)/.*')
main_url = 'https://escortsmexico.net'
# cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'escorts_mexico'
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
        elif input_category == 'mujeres':
            input_category = 'female-escorts'
        elif input_category == 'hombres':
            input_category = 'male-escorts'
        elif input_category == 'parejas':
            input_category = 'couple-escorts'
        elif input_category == 'gay':
            input_category = 'gay-escorts'
        elif input_category == 'travestis':
            input_category = 'transsexual-escorts'
        elif input_category == 'inpedendientes':
            input_category = 'independent-escorts'
        elif input_category == 'online-escorts':
            input_category = 'online-escorts'
        # else:
        #     input_category = '-'.join(input_category.split()).lower()
        
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
            url = f'{main_url}/escorts-from/{input_geozone}/'
            
        elif input_geozone == 'todas' and input_category != 'todas':
            url = f'{main_url}/{input_category}/'
        else:
            logger.warning('Elija una categoria o un estado, no ambos')
        
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):

        links = set(response.xpath('//div[@class="thumbwrapper"]/a/@href').getall())
        for idx, link in enumerate(links):
            logger.info(f'Links {idx} / {len(links)}')
            yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
            
 
        
        # next_page = response.xpath('//a[@id="button_arrow_pagination"]/@href').get()
        # if next_page:
        #     yield response.follow(next_page, callback= self.parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']

        
        title = response.xpath('//h3[@class="profile-title"]/text()').get()
        try:
            geo_zone = ' - '.join(response.xpath('//div[@itemprop="address"]/span[@class="valuecolumn"]//text()').getall())
        except:
            geo_zone = None
        #Categoria
        category =  re.match(patter_category, response.request.url).group(1)
        #Description
        try:
            description = self.remove_spaces(' '.join(response.xpath('//div[@class="aboutme"]/text()').getall()).strip()).replace('-','')
        except:
            description = None
        phone =  response.xpath('//div[@class="phone-box r"]/a/text()').get()
        try:
            whatsapp = None 
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
            'Nombre de la Página':'Escorts Mexico'
            }


    def remove_spaces(self,x):
        return x.replace('  ',' ').replace('\r','').replace('\t','').replace('\xa0','').replace('\n','').strip()


