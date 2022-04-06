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
main_url = 'https://angelesx.com'
cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'angeles_mex'
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
            input_category = '-'.join(input_category.split()).upper()
        
        # if input_category == 'escorts-y-putas':
        #     input_category = 'escorts'

        input_geozone = getattr(self,'geo_zone',None)
        if input_geozone is None:
            input_geozone = 'todas'
        else:
            input_geozone = '-'.join(input_geozone.split()).upper()

        if input_category == 'todas' and input_geozone == 'todas':
            url = main_url
        elif input_category == 'todas' and input_geozone != 'todas':
            url = f'{main_url}/escorts/{input_geozone}/'
        elif input_geozone == 'todas' and input_category != 'todas':
            url = f'{main_url}/escorts/{input_category}/'
        else:
            url = f'{main_url}/escorts/{input_category}'
        
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        url = response.request.url
        if url == main_url:
            links = set(response.xpath('//div[@class="text-center"]/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Category {idx} / {len(links)}')
                yield response.follow(link, callback=self.parse)

        else:
            links = set(response.xpath('//div[@class="card"]/a/@href').getall())
           # links = set(response.xpath('//article/figure/a/@href').getall())
            for idx, link in enumerate(links):
                logger.info(f'Links {idx} / {len(links)}')
                yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
 
        
        # next_page = response.xpath('//span[@class="next"]/a/@href').get()
        # if next_page:
        #     next_page = '{}{}'.format(main_url,next_page)
        #     yield response.follow(next_page, callback= self.s_parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']

        
        title = response.xpath('//h1//text()').get().capitalize()
        
        geo_zone = response.xpath('//a[@class="btn btn-red btn-sm m-1 rounded-pill"]//text()').get().strip()
        #Categoria
        category =  geo_zone
        #Description
        try:
            description = response.xpath('//h3[text()="CARACTERÍSTICAS:"]/following-sibling::*[@class="w2"]//text()').getall()
            description = ' '.join(description)
        except:
            description = None
        phone = response.xpath('//div[@class="text-center"]/h3[text()="DATOS DE CONTACTO:"]/following-sibling::a[@class="btn btn-outline-success btn-sm"]//text()').getall()
        phone = ''.join(phone).strip()
        try:
            whatsapp = response.xpath('//div[@class="text-center"]/h3[text()="DATOS DE CONTACTO:"]/following-sibling::a[@class="btn btn-outline-success btn-sm"]/@href').get()
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
            'Nombre de la Página':'Angeles Mex'
            }

    def extact_email(self,xpath,url):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(3000)
            page.mouse.wheel(0,4000)
            email = page.query_selector(xpath).inner_text()

            browser.close()
            return email

