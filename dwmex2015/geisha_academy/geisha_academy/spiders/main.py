from operator import ge
import scrapy 
import urllib
import subprocess
import re
import datetime as dt
import logging

from selenium import webdriver
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
        # elif input_category == 'todas' and input_geozone != 'todas':
        #     url = f'{main_url}/{input_geozone}/'
        # elif input_geozone == 'todas' and input_category != 'todas':
        #     url = f'{main_url}/anuncios-eroticos/{input_category}/'
        # else:
        #     url = f'{main_url}/anuncios-eroticos/{input_category}/{input_geozone}/'
        
        yield scrapy.Request(url, callback=self.parse)

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
        options = webdriver.FirefoxOptions()
        options.add_argument('--private')
        options.add_argument('--no-sandbox')
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 12.2; rv:97.0) Gecko/20100101 Firefox/97.0')
        options.add_argument("--headless")
        driver = webdriver.Firefox(executable_path='../driver/geckodriver', options=options)
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0")

        #processing
        driver.get(url)
        driver.find_element_by_xpath(xpath).text
        driver.close()