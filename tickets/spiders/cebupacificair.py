#-*- coding=utf-8

import sys
import re
import datetime, time

import scrapy
from tickets.items import CebuPacificAirTicket

class CebuPacificAirSpider(scrapy.Spider):
    name = 'CebuPacificAir'
    allow_domain = ["book.cebupacificair.com"]
    start_urls = ["https://book.cebupacificair.com/Select.aspx"]
    search_url = "https://book.cebupacificair.com/Search.aspx?culture=zh-tw"

    def __init__(self, fromCity, toCity, dateStart, dateEnd):
        self.fromCity = fromCity.upper()
        self.toCity = toCity.upper()
        self.dateStart = int(dateStart)
        self.dateEnd = int(dateEnd)

    def parse(self, response):
        formdata = {"__EVENTTARGET": "ControlGroupSearchView$AvailabilitySearchInputSearchView$LinkButtonNewSearch",
                    "__EVENTARGUMENT": "",
                    "__VIEWSTATE": "",
                    "ControlGroupSearchView$AvailabilitySearchInputSearchView$RadioButtonMarketStructure": "RoundTrip",
                    "ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin1": self.fromCity,
                    "ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination1": self.toCity,
                    "ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin2": "undefined",
                    "ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination2": "undefined",
                    "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_ADT": "1",
                    "ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_CHD": "0",
                    "ControlGroupSearchView$AvailabilitySearchInputSearchView$promoCodeID": ""}

        for plusDate in range(self.dateStart, self.dateEnd+1):
            flyingDate = datetime.date.today() + datetime.timedelta(days=plusDate)
            print flyingDate.strftime("%Y-%m-%d"), self.fromCity, self.toCity

            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDay1"] = flyingDate.strftime("%d")
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketMonth1"] = flyingDate.strftime("%Y-%m")
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDay2"] = flyingDate.strftime("%d")
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketMonth2"] = flyingDate.strftime("%Y-%m")
            formdata["date_picker_2"] = flyingDate.strftime("%Y-%m-%d")

            yield scrapy.FormRequest(url = CebuPacificAirSpider.search_url,
                                     formdata = formdata,
                                     dont_filter = True,
                                     method = "POST",
                                     callback = self.ticket)

    def ticket(self, response):
        flights = response.xpath("//input[re:test(@id, 'ControlGroupSelectView_AvailabilityInputSelectView_RadioButtonMkt\dFare')]/@value").extract()
        prices = response.xpath("//span[@class='ADTprice']/text()").extract()
        for idx in range(0, len(flights)):
            flight = flights[idx].split("~")
            #for i in range(0, len(flight)):
            #    print i, flight[i]
            price = re.sub("\s+", " ", prices[idx])
            #print price

            ticket = CebuPacificAirTicket()
            ticket["company"] = self.name
            ticket["fromCity"] = flight[11]
            ticket["toCity"] = flight[-3]
            ticket["price"] = price

            ticket["isTransferred"] = False
            ticket["datetimeStart"] = flight[12]
            if len(flight) > 17:
                ticket["fromCity"] = flight[18]
                ticket["isTransferred"] = True
                ticket["datetimeStart"] = flight[19]
                ticket["flight"] = "%s%s,%s%s" %(flight[14].split("|")[1], flight[15].strip(), flight[22].split("^")[1], flight[23].strip())
                ticket["flyingDate"] = flight[19].split(" ")[0]
            else:
                ticket["flight"] = "%s%s" %(flight[7].split("|")[1], flight[8].strip())

            ticket["datetimeEnd"] = flight[-2]

            yield ticket
