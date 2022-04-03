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

pattern = re.compile(r'https://evas.mx/ciudad/(.*)/')
#main_url = 'https://gemidos.tv'
cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'atlas_escorts'
   #] allowed_domains = ['https://mx.atlasescorts.com/']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    start_urls = [
            'https://mx.atlasescorts.com/search',
            'https://mx.atlasescorts.com/category/shemale-escorts',
            'https://mx.atlasescorts.com/category/escorts'
    ]


    def parse(self, response):

        links = set(response.xpath('//div[@class="nova-card"]/a/@href').getall())
        for idx, link in enumerate(links):
            logger.info(f'Links {idx} / {len(links)}')
            yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
       
 
        
        next_page = response.xpath('//nav[@class="pagination-bar pagination-sm"]//li[@class="page-item"][last()]/a/@href').get()
        if next_page:
            #next_page = '{}{}'.format(main_url,next_page)
            yield response.follow(next_page, callback= self.parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']
        
        title = response.xpath('//h1/text()').get().strip()
        
        geo_zone = response.xpath('//div[@class="additional x1"][text()=" City"]/following-sibling::div[@class="additional x2"]/a/text()').get().strip()
        #Categoria
        category = response.xpath('//div[@class="additional x1"][text()=" Category"]/following-sibling::div[@class="additional x2"]/a/text()').get().strip()       
        #Description
        try:
            description =  ' '.join(response.xpath('//div[@class="details-post-description"]/p//text()').getall()).strip()
            description = self.remove_spaces(description)
        except:
            description = None
        phone = response.xpath('//div[@class="ev-action phone-img"]/a[@class="btn btn-primary btn-block"]/@href').get()
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
            'Nombre de la Página':'Atlas Escorts'
            }

    def remove_spaces(self,x):
        return x.replace('  ',' ').replace('\r','').replace('\t','').replace('\xa0','').replace('\n','').strip()


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

