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

pattern = re.compile(r'https://selfiescorts.com/(.*)/.*')
main_url = 'https://www.escortsnatural.com/escorts'
cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'scorts_natural'
    #allowed_domains = ['www.cinescallao.es']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    # start_urls = [
    #     'https://www.escortsnatural.com/escorts/ciudad-de-mexico',
    #     'https://www.escortsnatural.com/escorts/quintana-roo',
    #     'https://www.escortsnatural.com/escorts/hidalgo',
    #     'https://www.escortsnatural.com/escorts/chihuahua',
    #     'https://www.escortsnatural.com/escorts/estado-de-mexico',
    #     'https://www.escortsnatural.com/escorts/guanajuato',
    #     'https://www.escortsnatural.com/escorts/michoacan',
    #     'https://www.escortsnatural.com/escorts/jalisco',
    #     'https://www.escortsnatural.com/escorts/puebla',
    #     'https://www.escortsnatural.com/escorts/queretaro',
    #     'https://www.escortsnatural.com/escorts/nuevo-leon',
    #     'https://www.escortsnatural.com/escorts/morelos'
    # ]
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
            url = f'{main_url}/{input_category}/'
            print(url)
        else:
            url = f'{main_url}/{input_category}/'
        
        yield scrapy.Request(url, callback=self.parse)


    def parse(self, response):

        links = set(response.xpath('//div[@id="Content"]/div[@class="row"]//a/@href').getall())
        print('Links',links)
        for idx, link in enumerate(links):
            logger.info(f'Links {idx} / {len(links)}')
            yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
       
 
        
        # next_page = response.xpath('//span[@class="next"]/a/@href').get()
        # if next_page:
        #     next_page = '{}{}'.format(main_url,next_page)
        #     yield response.follow(next_page, callback= self.s_parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']
        
        title = ' '.join(response.xpath('//h1//text()').getall()).strip()
        
        geo_zone = response.xpath('//ul[@class="ombre-table"]/li[contains(.,"LOCALIDAD")]/div[@class="ombre-table-right"]/text()').get()
        #Categoria
        category = geo_zone
        #Description
        try:
            len_description = len(response.xpath('//ul[@class="ombre-table"]/li'))
            box_desc = []
            for i in range(0,len_description):
                description = response.xpath(f'//ul[@class="ombre-table"]/li[{i}]//text()').getall()
                description = ' '.join(description).capitalize().strip()
                box_desc.append(description)
            box_desc.remove('')
            description = self.remove_spaces(' - '.join(box_desc))

        except Exception as e:
            print('\n')
            print(e)
            print('\n')
            description = None
        phone = response.xpath('//ul[@class="ombre-table"]/li[contains(.,"TELÉFONO")]/div[@class="ombre-table-right"]/a/text()').get()
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
            'Nombre de la Página':'Scorts Natural'
            }

    def remove_spaces(self,x):
        return x.replace('  ',' ').replace('\r','').replace('\t','').replace('\xa0','').replace('\n','').replace('                    ',' ').strip()

