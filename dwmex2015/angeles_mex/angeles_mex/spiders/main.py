from operator import ge
import scrapy 
import urllib
import subprocess
import re
import datetime as dt
import logging

from playwright.sync_api import sync_playwright
from scrapy.crawler import CrawlerProcess
from datetime import datetime

logger = logging.getLogger()
mes = datetime.now().month
dia = datetime.now().day
year = datetime.now().year

pattern_geozone = re.compile(r'(Localización|Ciudad): (.*)')
main_url = 'https://gemidos.tv'
cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'angeles_mex'
    #allowed_domains = ['www.cinescallao.es']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    start_urls = [
        'https://angelesx.com/escorts/AGUASCALIENTES',
        'https://angelesx.com/escorts/CANCUN',
        'https://angelesx.com/escorts/CDMX',
        'https://angelesx.com/escorts/CORDOBA',
        'https://angelesx.com/escorts/VERACRUZ',
        'https://angelesx.com/escorts/ZACATECAS'
    ]


    def parse(self, response):
       links = set(response.xpath('//div[@class="card"]/a/@href').getall())
       for idx, link in enumerate(links):
           logger.info(f'Links {idx} / {len(links)}')
           yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
       
 
        
        # next_page = response.xpath('//span[@class="next"]/a/@href').get()
        # if next_page:
        #     next_page = '{}{}'.format(main_url,next_page)
        #     yield response.follow(next_page, callback= self.s_parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']

        
        title = response.xpath('//h1//text()').get()
        
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

