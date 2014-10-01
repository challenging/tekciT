#coding=utf-8

import scrapy
import os, datetime

from scrapy import log
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.project import get_project_settings

from tickets.items import AgencyTicket

class BackpackersSpider(CrawlSpider):
    name = "backpackers"
    allowed_domains = ["www.backpackers.com.tw"]
    start_urls = []
    #rules = (
    #    Rule(SgmlLinkExtractor(allow=('page=[\d]+$',), deny=('pp=*', ), unique = True), callback = 'parse_item', follow = True),
    #)

    TO_EUROPE = "CPH,MOW,BUD,VIE,ATH,FRA,BER,CGN,DUS,HAM,MUC,OSL,PRG,BRU,PAR,LYS,STO,GVA,ZRH,LUX,ROM,MIL,VCE,HEL,LON,BHX,MAN,AMS,LIS,MAD,BCN"
    TO_NEWZEALAND = "SPN,ROR,NAN,BNE,MEL,PER,SYD,ADL,CBR,CNS,OOL,AKL,CHC,WLG,GUM"
    TO_JAPAN = "OSA,SPK,TYO,FSZ,FUK,HIJ,HKD,KMI,KOJ,NGO,OKA,SDJ,TOY"
    TO_KOREA = "SEL,CJU,PUS"

    def __init__(self, country):
        settings = get_project_settings()

        for c in country.split(","):
            destination = settings.get("%s_%s" %(self.__class__.__name__.upper(), c.upper()))

            now = datetime.date.today()
            date = []

            # 最近半年
            for halfMonth in [2, 3, 4, 5, 6, 7]:
                # 大小月問題未解決
                date.append("%d:%d" %(halfMonth, now.day))

            # 最近十五天
            for day15 in range(7, 16):
                endDate = datetime.date.today() + datetime.timedelta(days=day15)
                if now.month == endDate.month:
                    date.append("1:%d" %endDate.day)
                else:
                    date.append("2:%d" %endDate.day)

            # 第三週
            endDate = datetime.date.today() + datetime.timedelta(days=21)
            if endDate.month == now.month:
                date.append("1:%d" %endDate.day)
            else:
                date.append("2:%d" %endDate.day)

            # 最近四十五天
            endDate = datetime.date.today() + datetime.timedelta(days=45)
            if endDate.month == now.month+1:
                date.append("2:%d" %endDate.day)
            else:
                date.append("3:%d" %endDate.day)

            for to in destination.split(","):
                for pair in date:
                    [month, day] = pair.split(":")
                    month = int(month)
                    day = int(day)

                    self.start_urls.append(
                        "http://www.backpackers.com.tw/forum/airfare.php?city_to=%s&city_from=TPE&region_id=5&date_day=%d&date_month=%d&nonstop=on" %(to, day, month))

            self._rules = (
                Rule(SgmlLinkExtractor(allow=('page=[\d]+$',), deny=('pp=*', ), unique = True), callback = self.parse_item, follow = True),)

    # sel.xpath("//tr[@class='alt1']//td//span[@class='smallfont']//text()").extract()
    def parse_item(self, response):
        #self.log('Hi, this is an item page! %s' % response.url)
        for sel in response.xpath("//tr[re:test(@class, 'alt(1|2)')]"):
            infos = sel.xpath("td//span[@class='smallfont']//text()").extract()            

            #[agency, fly, transfer, level, desc, date, amount, url, oriURL] = sel.xpath("td//span[@class='smallfont']//text()").extract()
            if len(infos) >= 9:
                item = AgencyTicket()
                item["webpage"] = response.url

                item["agency"] = infos[0]
                item["fly"] = infos[1]
                item["transfer"] = infos[2]
                item["level"] = infos[3]
                item["desc"] = infos[4].replace("\r\n", "")
                item["date"] = infos[5]
                item["amount"] = infos[6]
                item["url"] = infos[7]

                yield item
