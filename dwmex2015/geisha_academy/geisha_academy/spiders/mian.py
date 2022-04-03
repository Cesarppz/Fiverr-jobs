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
main_url = 'https://geisha.academy/'
cop_pattern = re.compile(r'.*(COP|USD).*')


class Webscrape(scrapy.Spider):
    name = 'geisha_academy'
    #allowed_domains = ['www.cinescallao.es']
    custom_settings= {
                        'FEED_URI':f'results_{name}_{dia}_{mes}.csv',
                        'FEED_FORMAT':'csv',
                        'FEED_EXPORT_ENCODING':'utf-8'}

    start_urls = [ main_url ]
   # allowed_domains = ['https://mx.mundosexanuncio.com/']

    def parse(self, response):
       links = set(response.xpath('//*[@id="attachment_1631"]/a/@href').getall())
       for idx, link in enumerate(links):
           logger.info(f'Category {idx} / {len(links)}')
           yield response.follow(link, callback=self.s_parse)
       


    def s_parse(self, response):
        links = set(response.xpath('//div[@class="entry entry-content"]//div[@class="blog-thumnail"]/a/@href').getall())
        for idx, link in enumerate(links):
            if link:
                logger.info(f'Link {idx+1}/{len(links)}')
                yield response.follow(link, callback=self.new_parse, cb_kwargs={'link':link, 'idx':idx+1,'len':len(links)})
        
        # next_page = response.xpath('//span[@class="next"]/a/@href').get()
        # if next_page:
        #     next_page = '{}{}'.format(main_url,next_page)
        #     yield response.follow(next_page, callback= self.s_parse)


    def new_parse(self, response, **kwargs):
        link = kwargs['link']
        len_links = kwargs['len']
        idx_link = kwargs['idx']
        
        title = response.xpath('//h1//text()').get()
        
        geo_zone = response.xpath('//div[@class="entry entry-content"]//p//text()').getall()

        for i in geo_zone:
            geo_zone = re.findall(pattern_geozone,i)
            if geo_zone:
                geo_zone = geo_zone[0][1]
                break

        print(geo_zone)
        
        category =  geo_zone
        
        description = response.xpath('//div[@class="wp-caption aligncenter"]/following-sibling::p//text()').getall()
        box_description = []
        for i in description:
            if re.match(cop_pattern,i):
                break
            else:
                box_description.append(i)
        description = ' '.join(box_description).replace('\xa0','').replace('  ',' ').strip()


        phone = self.extact_email('//*[text()="¿CÓMO CONTACTARNOS?"]/../following-sibling::p/a[1]',link)
        try:
            whatsapp = response.xpath('//a[text()="For USD Dollar rates, write us on WhatsApp."]/@href').get()
        except:
            whatsapp = None
        email = self.extact_email('//*[text()="¿CÓMO CONTACTARNOS?"]/../following-sibling::p/a[2]',link)
        

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
            'Nombre de la Página':'Geisha Academy'
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

