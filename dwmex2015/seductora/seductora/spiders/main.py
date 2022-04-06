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
main_url = 'https://seductoras.mx/'
cop_pattern = re.compile(r'.*(COP|USD).*')
geo_dict = {
        'puebla':'https://puebla.seductoras.mx/',
        'cuernavaca':'https://cuernavaca.seductoras.mx/',
        'cdmx':'https://cdmx.seductoras.mx/',
        'queretaro':'https://seductoras.mx/escorts/queretaro/queretaro/',
        'baja-california':'https://seductoras.mx/escorts/baja-california/tijuana/',
        'guanajuato':'https://seductoras.mx/escorts/guanajuato/leon/',
        'sinaloa':'https://seductoras.mx/escorts/sinaloa/culiacan/'
    }

class Webscrape(scrapy.Spider):
    name = 'seductora'
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
            url = geo_dict[input_geozone]
        elif input_geozone == 'todas' and input_category != 'todas':
            url = geo_dict[input_category]
        else:
            url = geo_dict[input_category]
        
        yield scrapy.Request(url, callback=self.parse)


    def parse(self, response):

        links = set(response.xpath('//article//a/@href').getall())
        for idx, link in enumerate(links):
            logger.info(f'Links {idx} / {len(links)}')
            yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
       
 
        
        # next_page = response.xpath('//span[@class="next"]/a/@href').get()
        # if next_page:
        #     next_page = '{}{}'.format(main_url,next_page)
        #     yield response.follow(next_page, callback= self.s_parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']
        
        title = response.xpath('//h1/text()').get()
        
        geo_zone = response.xpath('//div[@id="detalles"]/div[text()="Estoy en"]/following-sibling::div/strong/text()').get()
        #Categoria
        category = geo_zone       
        #Description
        try:
            description =  ' '.join(response.xpath('//div[@id="acercaDeMi"]//text()').getall())
            description = self.remove_spaces(description)
        except:
            description = None
        phone = response.xpath('//div[@id="nombreTel"]/a/text()').get()
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
            'Nombre de la Página':'Seductoras'
            }

    def remove_spaces(self,x):
        return x.replace('  ',' ').replace('\r','').replace('\t','').replace('\xa0','').replace('\n','').strip()