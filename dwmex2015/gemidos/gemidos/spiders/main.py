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
    name = 'gemidos'
    #allowed_domains = ['www.cinescallao.es']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    def start_requests(self):
        list_countries = ['/venezuela',
 '/uruguay',
 '/usa',
 '/united-arab-emirates',
 '/uk',
 '/republica-dominicana',
 '/peru',
 '/paraguay',
 '/panama',
 '/nicaragua',
 '/mexico',
 '/italy',
 '/ireland',
 '/india',
 '/honduras',
 '/guyane',
 '/france',
 '/espana',
 '/el-salvador',
 '/ecuador',
 '/costa-rica',
 '/colombia',
 '/chile',
 '/canada',
 '/brasil',
 '/bolivia',
 '/australia',
 '/argentina']

        for i in list_countries:
            link = '{}{}'.format(main_url,i)
            print(link)
            yield scrapy.Request(link, callback=self.parse)

    def parse(self, response):
       links = set(response.xpath('//a[@class="listing-link"]/@href').getall())
       for idx, link in enumerate(links):
           logger.info(f'Category {idx} / {len(links)}')
           yield response.follow(link, callback=self.new_parse,cb_kwargs={'link':link})
       
 
        
        # next_page = response.xpath('//span[@class="next"]/a/@href').get()
        # if next_page:
        #     next_page = '{}{}'.format(main_url,next_page)
        #     yield response.follow(next_page, callback= self.s_parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']

        
        title = response.xpath('//h1/text()').get()
        
        geo_zone = response.xpath('//div[@class="d-flex"]/div[@class="breadcrumb-item d-flex align-items-baseline mx-0"]//span[@itemprop="name"]/text()').getall()[1:]
        geo_zone = ' - '.join(geo_zone)        
        #Categoria
        category =  response.xpath('//span[@class="badge badge-accent "]//text()').getall()
        category = ' - '.join(category).replace('\n','')
        #Description
        try:
            description = response.xpath('//div[@class="pub-about-text pub-about-preview"]//text()').get().replace('\n',' ').capitalize().strip()
        except:
            description = None
        phone = response.xpath('//a[@class="btn btn-primary pub-menu-button"][@data-analytics="pub,call"]/@href').get()
        try:
            whatsapp = response.xpath('//a[@class="btn btn-primary pub-menu-button"][@data-analytics="pub,whatsapp,button"]/@href').get()
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
            'Nombre de la Página':'Gemidos TV'
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

