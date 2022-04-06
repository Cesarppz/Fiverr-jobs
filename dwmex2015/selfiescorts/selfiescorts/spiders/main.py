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
main_url = 'https://selfiescorts.com'
cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'selfiescorts'
    #allowed_domains = ['www.cinescallao.es']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    start_urls = [
        '   /ahora/?country=mexico',
        'https://selfiescorts.com/maduras/?country=mexico',
        'https://selfiescorts.com/masajistas/?country=mexico',
        'https://selfiescorts.com/fantasias/?country=mexico',
        'https://selfiescorts.com/verificadas/?country=mexico',
        'https://selfiescorts.com/mas-visitadas/?country=mexico',
        'https://selfiescorts.com/mas-votadas/?country=mexico',
        'https://selfiescorts.com/mas-comentadas/?country=mexico',
        'https://selfiescorts.com/comparar/?country=mexico'
    ]

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
            url = 'https://selfiescorts.com/mexico/'
        elif input_category == 'todas' and input_geozone != 'todas':
            url = f'{main_url}/{input_geozone}'
        elif input_geozone == 'todas' and input_category != 'todas':
            url = f'{main_url}/{input_category}/?country=mexico'
        else:
            url = f'{main_url}/{input_category}/?country={input_geozone}/'
        
        yield scrapy.Request(url, callback=self.parse)



    def parse(self, response):
        category = re.match(pattern,response.request.url).group(1)
        if category == 'ahora':
            category = 'Disponibles ya'
        category =  category.capitalize()

        links = set(response.xpath('//ul[@class="sector"]//a[@class="i_link"]/@href').getall() + 
                    response.xpath('//ul[@class="sector"]//a[@class="n_link"]/@href').getall())
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
        
        title = response.xpath('//div[@class="master_name"]/text()').get()
        
        geo_zone = response.xpath('//h1[@class="ubise"]/a//text()').get().split('»')[0]
        #Categoria
        # category = re.match(pattern,response.request.url).group(1)
        # category =  ' '.join(category.split('-'))
        #Description
        try:
            len_description = len(response.xpath('//div[@class="dato_in pd_dato"]'))
            box_desc = []
            for i in range(0,len_description):
                description = response.xpath(f'//div[@class="dato_in pd_dato"][{i}]//text()').getall()
                description = ' '.join(description).capitalize().strip()
                box_desc.append(description)
            box_desc.remove('')
            description = ' - '.join(box_desc)

        except Exception as e:
            print('\n')
            print(e)
            print('\n')
            description = None
        phone = response.xpath('//div[@class="pc_num_c"]/text()').get()
        try:
            whatsapp = response.xpath('//a[@class="sumar_w"]/@href').get()
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
            'Nombre de la Página':'Selfiescorts'
            }

