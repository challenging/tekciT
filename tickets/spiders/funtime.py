#coding=utf-8

import sys

import scrapy
import os, time, datetime

from scrapy import log
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.project import get_project_settings

from tickets.items import AgencyTicket

# http://www.funtime.com.tw/oveticket/result_content_list.php?t_list=a_tb&airline_str=&back_city_str=&offset=0&trans_str=&orderby=&asc=&t_type[]=&airline_array[]=&forward=NSTOP&source_array[]=&num_per_page=40&bfrom_city=TY&region=RE_ASIA_N&country=CN_JAPAN&city=OSA&departure=2014-12-20&backdate=2014-12-20&bclass=EC&type=ONE&fileName=undefined&checkin=undefined&checkout=undefined 
class FuntimeSpider(CrawlSpider):
    name = "funtime"
    allowed_domains = ["www.funtime.com.tw"]
    start_urls = []

    def __init__(self, country):
        settings = get_project_settings()

        ccs = country.split(",")
        if country == "all":
            ccs = [city.split("_")[1].lower() for city in settings.attributes.keys() if (city.split("_")[0] == self.__class__.__name__.upper() and city.split("_")[2] == "CITY" and len(city.split("_")) == 3)]

        for c in ccs:
            c = c.upper()

            destination = settings.get("%s_%s_CITY" %(self.__class__.__name__.upper(), c))
            region = settings.get("%s_%s_REGION" %(self.__class__.__name__.upper(), c))
            cc = settings.get("%s_%s_COUNTRY" %(self.__class__.__name__.upper(), c))

            now = datetime.date.today()
            date = []

            for day in [7, 14, 21, 30, 45, 60, 90, 120, 150, 180]:
                flyingDate = datetime.date.today() + datetime.timedelta(days=day)
                date.append(flyingDate.strftime("%Y-%m-%d"))

            for to in destination.split(","):
                for flyingDate in date:
                    self.start_urls.append("http://www.funtime.com.tw/oveticket/result_content_list.php?t_list=a_tb&offset=0&num_per_page=1000&bfrom_city=TY&region=%s&country=%s&city=%s&departure=%s&backdate=%s&bclass=EC&type=ONE" %(region, cc, to, flyingDate, flyingDate))

    # sel.xpath("//tr[@class='alt1']//td//span[@class='smallfont']//text()").extract()
    def parse(self, response):
        #self.log('Hi, this is an item page! %s' % response.url)
        for sel in response.xpath("//tr[@class='word product_tr']"):
            infos = sel.xpath("td//font[@color='']//text()").extract()            

            item = AgencyTicket()
            item["webpage"] = response.url

            item["agency"] = infos[1]
            item["fly"] = infos[0]
            item["transfer"] = infos[2]
            item["level"] = infos[3].replace("\r\n", "")
            item["desc"] = infos[4].replace("\r\n", "")
            item["date"] = infos[5] + infos[6] + infos[7]
            item["amount"] = infos[10]
            #item["url"] = infos[7]

            item["crawlingDate"] = time.time()

            yield item
