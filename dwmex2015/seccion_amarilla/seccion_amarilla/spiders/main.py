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

pattern_geozone = re.compile(r'\d+ (.*)')
main_url = 'https://www.seccionamarilla.com.mx/resultados'
# cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'seccion_amarilla'
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

        global input_geozone
        input_geozone = getattr(self,'geo_zone',None)
        if input_geozone is None:
            input_geozone = 'todas'
        
        
        else:
            input_geozone = '-'.join(input_geozone.split()).lower()

        if input_category == 'todas' :
            url = main_url
        # elif input_category == 'todas' and input_geozone != 'todas':
        #     url = f'{main_url}/{input_geozone}/'
        elif input_geozone == 'todas' and input_category != 'todas':
            url = f'{main_url}/{input_category}/1'
        # else:
        #     url = f'{main_url}/{input_category}/{input_geozone}/'
        
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        url = response.request.url
        if url == main_url:
            links = set(response.xpath('//div[@class="search-icons"]/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Category {idx} / {len(links)}')
                yield response.follow(link, callback=self.parse)

        else:
            try:
                links = set(response.xpath('//h2/span[@itemprop="name"]/ancestor::a/@href').getall())
                for idx in range(1,len(links)+1):

                    title = response.xpath(f'//ul[@class="list"]/li[{idx}]//h2/span[@itemprop="name"]/text()').get()
                    try:
                        geo_zone = response.xpath(f'//ul[@class="list"]/li[{idx}]//div[@class="l-address"]/span[@itemprop="addressRegion"]/text()').get().replace(',','').strip()
                        if input_geozone == 'todas':
                            geo_zone = geo_zone
                        else:
                            if geo_zone.lower() != input_geozone:
                                break
                            else:
                                geo_zone = geo_zone
                    except:
                        geo_zone = None
                    #Categoria
                    category =  response.xpath(f'//ul[@class="list"]/li[{idx}]//div[@class="l-categoria-tags"]/a/span/text()').get()

                    phone = response.xpath(f'//ul[@class="list"]/li[{idx}]//span[@itemprop="telephone"]/text()').get().replace(',','').strip()
                    try:
                        postal =  response.xpath(f'//ul[@class="list"]/li[{idx}]//div[@class="l-address"]/span[@itemprop="postalCode"]/text()').get().replace(',','').strip()
                    except:
                        postal = None
                    try:
                        whatsapp = None
                    except:
                        whatsapp = None
                    email =  None
                    try:
                        link =response.xpath(f'//ul[@class="list"]/li[{idx}]//div[@class="row l-btn-container"]//span[@class="icon-web"]/parent::a/@href').get()
                    except:
                        link = None
                    

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
                        'Nombre de la Página':'Seccion Amarilla'
                        }
            except:
                pass
                    
 
        
        next_page = response.xpath('//span[@class="icon-page-right"]/parent::a/@href').get()
        if next_page:
            yield response.follow(next_page, callback= self.parse)


    # def new_parse(self, response, **kwargs):
    #     #link = kwargs['link']

        
     
    def remove_spaces(self,x):
        return x.replace('  ',' ').replace('\r','').replace('\t','').replace('\xa0','').replace('\n','').strip()


