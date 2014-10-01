#coding=utf-8

import sys, datetime, time, exceptions

import scrapy
from tickets.items import JetStarTicket

class FlyscootSpider(scrapy.Spider):
    name = 'Flyscoot'
    allow_domain = ["book.flyscoot.com", "www.flycoot.com"]
    start_urls = ["http://www.flyscoot.com/index.php/zhtw/"]
    search_url = "http://book.flyscoot.com/Search.aspx"

    def __init__(self, fromCity, toCity, plusDate):
        self.fromCity = fromCity.upper()
        self.toCity = toCity.upper()
        self.plusDate = int(plusDate)

    def parse(self, response):
        eventTarget = response.xpath("//input[@name='__EVENTTARGET']/@value").extract()[0]

        flyingDate = datetime.date.today() + datetime.timedelta(days=self.plusDate)
        flyingDateGo = flyingDate.strftime("%m/%d/%Y")

        formdata = {"__EVENTTARGET": eventTarget,
                    "__EVENTARGUMENT": "",
                    "__VIEWSTATE": "",
                    "pageToken": "",
                    "AvailabilitySearchInput.SearchStationDatesList[0].DepartureStationCode": self.fromCity,
                    "AvailabilitySearchInput.SearchStationDatesList[0].ArrivalStationCode": self.toCity,
                    "AvailabilitySearchInput.SearchStationDatesList[0].DepartureDate": flyingDateGo,
                    "AvailabilitySearchInput.SearchStationDatesList[1].DepartureStationCode": self.toCity,
                    "AvailabilitySearchInput.SearchStationDatesList[1].ArrivalStationCode": self.fromCity,
                    "AvailabilitySearchInput.SearchStationDatesList[1].DepartureDate": flyingDateGo,
                    "a": "on",
                    "AvailabilitySearchInput.AdultsCount": "1",
                    "AvailabilitySearchInput.ChildsCount": "0",
                    "AvailabilitySearchInput.InfantsCount": "0",}

        yield scrapy.FormRequest(url = FlyscootSpider.search_url,
                                 formdata = formdata,
                                 dont_filter = True,
                                 method = "POST",
                                 callback = self.ticket)

    def ticket(self, response):
        tt = response.xpath("//div[@class='day_cell_wrapper']//ul[@class='day_cell']//li")
        for t in tt:
            ticket = JetStarTicket()
            ticket["company"] = self.name
            ticket["flyingDate"] = "%s/%s/%s" %(t.xpath("@year").extract()[0], t.xpath("@month").extract()[0], t.xpath("@day").extract()[0])
            ticket["fromCity"] = t.xpath("@arrstation").extract()[0]
            ticket["toCity"] = t.xpath("@depstation").extract()[0]

            try:
                ticket["price"] = t.xpath("div//strong//span/text()").extract()[0]
                yield ticket
            except exceptions.IndexError as e:
                pass
