#coding=utf-8

import sys, datetime, time

import scrapy
from tickets.items import JetStarTicket

class JetStarSpider(scrapy.Spider):
    name = 'JetStar'
    allow_domain = ['www.jetstar.com', "booknow.jetstar.com"]
    start_urls = ["http://booknow.jetstar.com/Search.aspx"]
    search_url = "http://booknow.jetstar.com/Search.aspx"
    calendar_search_url = "http://booknow.jetstar.com/CalendarSelect.aspx"

    def __init__(self, fromCity, toCity, plusDate):
        self.fromCity = fromCity.lower()
        self.toCity = toCity.lower()
        self.plusDate = int(plusDate)

    def parse(self, response):
        keys = response.xpath("//input/@name").extract()
        values = response.xpath("//input/@value").extract()

        '''
        0 eventTarget
        1 eentArgument
        2 viewState
        '''
        formdata = {}
        for idx in range(0, min(len(values), len(keys))):
            if keys[idx].lower() in ["eventtarget", "eventArgument", "viewstate"]:
                formdata["__%s" %keys[idx].upper()] = values[idx]
            else:
                formdata[keys[idx]] = values[idx]
            #formdata[keys[idx]] = values[idx]

        endDate = datetime.date.today() + datetime.timedelta(days=int(self.plusDate))
        flyingDateGo = endDate.strftime("%d/%m/%Y")

        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$RadioButtonMarketStructure"] = "RoundTrip"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin1"] = self.fromCity.upper()
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination1"] = self.toCity.upper()

        #formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDepartureDate1"] = "01/10/2014"
        #formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDestinationDate1"] = "01/10/2014"

        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin1"] = self.fromCity.upper()
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination1"] = self.toCity.upper()
        
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDepartureDate1"] = flyingDateGo
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDestinationDate1"] = flyingDateGo

        for i in range(2, 7):
            futureDate = endDate + datetime.timedelta(days = i*7)
            futureFlyingDate = futureDate.strftime("%d/%m/%Y")

            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin%d" %i] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination%d" %i] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDepartureDate%d" %i] = futureFlyingDate
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDestinationDate%d" %i] = "" 

            '''
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin3"] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination3"] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDepartureDate3"] = "08/10/2014"
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDestinationDate3"] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin4"] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination4"] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDepartureDate4"] = "15/10/2014"
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDestinationDate4"] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin5"] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination5"] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDepartureDate5"] = "22/10/2014"
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDestinationDate5"] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin6"] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination6"] = ""
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDepartureDate6"] = "29/10/2014"
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDestinationDate6"] = ""
            '''

        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_ADT"] = "1"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_CHD"] = "0"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_INFANT"] = "0"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$RadioButtonSearchBy"] = "SearchLFF"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMultiCityOrigin1"] = "Origin"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMultiCityDestination1"] = "Destination"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDepartureMultiDate1"] = ""
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMultiCityOrigin2"] = "Origin"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMultiCityDestination2"] = "Destination"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextboxDepartureMultiDate2"] = ""
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMultiPassengerType_ADT"] = "1"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMultiPassengerType_CHD"] = "0"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMultiPassengerType_INFANT"] = "0"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$numberTrips"] = "2"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$ButtonSubmit"] = ""

        yield scrapy.FormRequest(url = JetStarSpider.search_url,
                                 formdata = formdata,
                                 dont_filter = True,
                                 method = "POST",
                                 callback = self.ticket)

    def ticket(self, response):
        tt = response.xpath("//div[@class='low-fare-selector']//ul//li")
        for t in tt:

            ticket = JetStarTicket()
            ticket["company"] = self.name
            ticket["flyingDate"] = t.xpath("@data-date").extract()[0]
            ticket["fromCity"] = t.xpath("@data-origin").extract()[0]
            ticket["toCity"] = t.xpath("@data-destination").extract()[0]
            ticket["info"] = t.xpath("@class").extract()[0]
            ticket["price"] = t.xpath("@data-price").extract()[0]

            if ticket["fromCity"] != "":
                yield ticket
