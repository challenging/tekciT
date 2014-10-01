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

            if goFlyingDate[idx] != "0001-01-01-00-00-00":
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

            if backFlyingDate[idx] != "0001-01-01-00-00-00":
                yield ticket
    '''
    def parse(self, response):
        viewstate = response.xpath("//input[@id='viewState']/@value").extract()[0]

        flyingDate = datetime.date.today() + datetime.timedelta(days=self.plusDate)

        formdata = {"eventTarget": "",
                    "eventArgument": "",
                    "viewState": viewstate,
                    "pageToken": "",
                    "culture": "zh-TW",
                    "ControlGroupCompactView$AvailabilitySearchInputCompactView$RadioButtonMarketStructure": "RoundTrip",
                    "ControlGroupCompactView_AvailabilitySearchInputCompactVieworiginStation1": self.fromCity,
                    "ControlGroupCompactView$AvailabilitySearchInputCompactView$TextBoxMarketOrigin1": self.fromCity,
                    "ControlGroupCompactView_AvailabilitySearchInputCompactViewdestinationStation1": self.toCity,
                    "ControlGroupCompactView$AvailabilitySearchInputCompactView$TextBoxMarketDestination1": self.toCity,
                    "date_picker": flyingDate.strftime("%m/%d/%Y"),
                    "date_picket": "",
                    "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListMarketDay1": flyingDate.strftime("%d"),
                    "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListMarketMonth1": flyingDate.strftime("%Y-%m"),
                    "date_picker": flyingDate.strftime("%m/%d/%Y"),
                    "date_picker": "",
                    "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListMarketDay2": flyingDate.strftime("%d"),
                    "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListMarketMonth2": flyingDate.strftime("%Y-%m"),
                    "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListPassengerType_ADT": "1",
                    "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListPassengerType_CHD": "0",
                    "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListPassengerType_INFANT": "0",
                    "ControlGroupCompactView$MultiCurrencyConversionViewCompactSearchView$DropDownListCurrency": "default",
                    "ControlGroupCompactView$AvailabilitySearchInputCompactView$DropDownListSearchBy": "columnView",
                    "ControlGroupCompactView$ButtonSubmit": "搜尋",
                    "__EVENTTARGET": "",
                    "__EVENTARGUMENT": "",
                    "__VIEWSTATE": viewstate,}

        yield scrapy.FormRequest(url = AirAsiaSpider.search_url,
                                 formdata = formdata,
                                 dont_filter = True,
                                 method = "POST",
                                 callback = self.ticket)

    def ticket(self, response):
        tt = response.xpath("//a[@href='#']")
        for idx in range(0, len(tt)-1):
            t = tt[idx]

            flyingDate = t.xpath("span/text()").extract()[1]
            fare = None
            try:
                fare = t.xpath("span/text()").extract()[2]
            except exceptions.IndexError as e:
                continue

            ticket = JetStarTicket()
            ticket["company"] = self.name
            ticket["flyingDate"] = flyingDate

            if idx <= 6:
                ticket["fromCity"] = self.fromCity
                ticket["toCity"] = self.toCity
            else:
                ticket["fromCity"] = self.toCity
                ticket["toCity"] = self.fromCity

            if fare != u'\u7121\u822a\u73ed':
                ticket["price"] = fare
                yield ticket
    '''
