import scrapy 
from scrapy.crawler import CrawlerProcess
from datetime import datetime
import urllib
import subprocess
import re
import datetime as dt

from agenda_tools import download_images, get_title, get_schedule, get_category
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
    name = 'scorts'
    #allowed_domains = ['www.cinescallao.es']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    start_urls = [ 'https://mx.mundosexanuncio.com/' ]
   # allowed_domains = ['https://mx.mundosexanuncio.com/']

    def parse(self, response):
       links = response.xpath('//div[@class="navegacion br4pt clearfix"]/*[@id="categorias"]//a/@href').getall()
       for idx, link in enumerate(links):
           logger.info(f'Category {idx} / {len(links)}')
           yield response.follow(link, callback=self.s_parse)
       


    def s_parse(self, response):
        links = set( response.xpath('//div[@class="item_desc_box"]/h2/a[@class="title"]/@href').getall())
        for idx, link in enumerate(links):
            if link:
                logger.info(f'Link {idx+1}/{len(links)}')
                yield response.follow(link, callback=self.new_parse, cb_kwargs={'link':link, 'idx':idx+1,'len':len(links)})
        
        next_page = response.xpath('//span[@class="next"]/a/@href').get()
        if next_page:
            next_page = '{}{}'.format(main_url,next_page)
            yield response.follow(next_page, callback= self.s_parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']
        len_links = kwargs['len']
        idx_link = kwargs['idx']
        title = response.xpath('//div[@class="main"]/p//text()').get()
        category = response.xpath('//div[@class="breadcrumb"]//li//span[@itemprop="name"]/text()').getall()[1]
        geo_zone = response.xpath('//div[@class="breadcrumb"]//li//span[@itemprop="name"]/text()').getall()
        geo_zone.remove(category)
        geo_zone = ' / '.join(geo_zone)
        description = ' '.join(response.xpath('//div[@class="a_content"]/p//text()').getall()).strip()
        phone = response.xpath('//*[@class="tel"]/a[@rel="nofollow"]/span/text()').get().strip()
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
            'Url del Anuncio':link


        }
