#coding=utf-8

import sys, datetime, time, exceptions

import scrapy
from tickets.items import JetStarTicket

class AirAsiaSpider(scrapy.Spider):
    name = 'AirAsia'
    allow_domain = ["booking.airasia.com", "booking11.airasia.com"]
    #start_urls = ["http://booking.airasia.com/Search.aspx"]
    start_urls = []
    search_url = "http://booking.airasia.com/Compact.aspx"

    def __init__(self, fromCity, toCity, plusDate):
        self.fromCity = fromCity.upper()
        self.toCity = toCity.upper()
        self.plusDate = int(plusDate)

        flyingDate = datetime.date.today() + datetime.timedelta(days=self.plusDate)
        url = "http://booking11.airasia.com/Page/SkySalesRedirectHandler.aspx?IsReturn=true&OriginStation=" + self.fromCity+ "&ArrivalStation=" + self.toCity+ "&DepartureDate=" + flyingDate.strftime("%Y-%m-%d")  + "&ReturnDate=" + flyingDate.strftime("%Y-%m-%d") + "&NoAdult=1&NoChild=0&NoInfant=0&Currency=TWD%20-%20Taiwanese%20NT%20Dollar&Culture=en-GB&RedirectTo=LowFare&pc=&respURL=http://booking.airasia.com/"

        self.start_urls.append(url)

    def parse(self, response):
        goFlyingDate = response.xpath("//ul[@id='BodyContent_lfcDepartCalendar_ulCalendar']//li/@data-std").extract()
        goPrice = response.xpath("//ul[@id='BodyContent_lfcDepartCalendar_ulCalendar']//li/@data-amt").extract()
        goCur = response.xpath("//ul[@id='BodyContent_lfcDepartCalendar_ulCalendar']//li/@data-cur").extract()

        for idx in range(0, len(goFlyingDate)):
            ticket = JetStarTicket()
            ticket["company"] = self.name
            ticket["flyingDate"] = goFlyingDate[idx]
            ticket["fromCity"] = self.fromCity
            ticket["toCity"] = self.toCity
            ticket["price"] = goPrice[idx]
            ticket["info"] = goCur[idx]

            if goFlyingDate[idx] != "0001-01-01-00-00-00" and goPrice[idx] != "0":
                yield ticket

        backFlyingDate = response.xpath("//ul[@id='BodyContent_lfcReturnCalendar_ulCalendar']//li/@data-std").extract()
        backPrice = response.xpath("//ul[@id='BodyContent_lfcReturnCalendar_ulCalendar']//li/@data-amt").extract()
        backCur = response.xpath("//ul[@id='BodyContent_lfcReturnCalendar_ulCalendar']//li/@data-cur").extract()

        for idx in range(0, len(backFlyingDate)):
            ticket = JetStarTicket()
            ticket["company"] = self.name
            ticket["flyingDate"] = backFlyingDate[idx]
            ticket["fromCity"] = self.toCity
            ticket["toCity"] = self.fromCity
            ticket["price"] = backPrice[idx]
            ticket["info"] = backCur[idx]

            if backFlyingDate[idx] != "0001-01-01-00-00-00" and backPrice[idx] != "0":
                yield ticket
