import scrapy 
from scrapy.crawler import CrawlerProcess
from datetime import datetime
import urllib
import subprocess
import re
import datetime as dt

import logging
logger = logging.getLogger()
mes = datetime.now().month
dia = datetime.now().day
year = datetime.now().year

pattern_schedule = re.compile(r'\d+\s+de\s+\w+')
horario_patter = re.compile(r'(.*)al(.*)')
pattern_horario = re.compile(r'([A-Za-záéíóú]+ \d+ de [A-Za-záéíóú]+)( y \d+ de [A-Za-záéíóú]+)?( a las \d+:\d+)?')
main_url = 'https://mx.mundosexanuncio.com'


class Webscrape(scrapy.Spider):
    name = 'mundosexanuncio'
    #allowed_domains = ['www.cinescallao.es']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    start_urls = [ 'https://mx.mundosexanuncio.com/' ]
   # allowed_domains = ['https://mx.mundosexanuncio.com/']
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
            url = f'{main_url}/contactos-eroticos-en-{input_category}/'
        else:
            url = f'{main_url}/{input_category}-en-{input_geozone}/'
        
        yield scrapy.Request(url, callback=self.parse)


    def parse(self, response):
        url = response.request.url
        if url == main_url:
            links = set(response.xpath('//div[@class="navegacion br4pt clearfix"]/*[@id="categorias"]//a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Category {idx} / {len(links)}')
                yield response.follow(link, callback=self.parse)

        else:
            links = set(response.xpath('//div[@class="item_desc_box"]/h2/a[@class="title"]/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Links {idx} / {len(links)}')
                yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})

        next_page = response.xpath('//span[@class="next"]/a/@href').get()
        if next_page:
            next_page = '{}{}'.format(main_url,next_page)
            yield response.follow(next_page, callback= self.parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']
        title = response.xpath('//div[@class="main"]/p//text()').get()
        category = response.xpath('//div[@class="breadcrumb"]//li//span[@itemprop="name"]/text()').getall()[1]
        geo_zone = response.xpath('//div[@class="breadcrumb"]//li//span[@itemprop="name"]/text()').getall()
        geo_zone.remove(category)
        geo_zone = ' / '.join(geo_zone)
        description = ' '.join(response.xpath('//div[@class="a_content"]/p//text()').getall()).strip()
        try:
            phone = response.xpath('//*[@class="tel"]/a[@rel="nofollow"]/span/text()').get().strip()
        except:
            phone = None
        try:
            whatsapp = response.xpath('//*[@class="tel"]/a[@class="whatsapp"]/@href').get().strip()
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
            'Nombre de la Página':'Mundo Sex Anuncio'
            }