#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, datetime, time, copy

import scrapy
from tickets.items import OnewayTicket

class ChinaAirlineSpider(scrapy.Spider):
    name = 'ChinaAirline'
    start_urls = ['https://caleb.china-airlines.com/olbn/travel.aspx']
    travel_url = 'https://caleb.china-airlines.com/olbn/travel.aspx'
    fare_url = 'https://caleb.china-airlines.com/olbn/Fare.aspx'
    flight_url = "https://caleb.china-airlines.com/olbn/Flight.aspx"
    fare_flight_url = "https://caleb.china-airlines.com/olbn/Fare_Flight.aspx"
    date_oneway_url = "https://caleb.china-airlines.com/olbn/Date_Oneway.aspx"

    def __init__(self, fromCity, toCity, periodType, plusDate):
        self.fromCity = [fromCity]
        self.toCity = [toCity]
        self.plusDate = [plusDate]
        self.periodType = int(periodType)

        self.ticketFromCity = None
        self.ticketToCity = None

    def parse(self, response):
        viewState = self.getViewState(response)
        eventValidation = self.getEventValidation(response)
        trip = response.xpath("//input[@name='ctl00$ContentPlaceHolder1$trip']//@value").extract()[0]
        backNotSure = response.xpath("//input[@name='ctl00$ContentPlaceHolder1$backNotSure']//@value").extract()[0]
        periodType = response.xpath("//input[@name='ctl00$ContentPlaceHolder1$periodType']//@value").extract()[0]

        url = None
        callback = None

        if self.periodType == 0:
            url = self.travel_url
            callback = self.dateOneway
        elif self.periodType == 2:
            url = self.travel_url
            callback = self.flight

        for fc in self.fromCity:
            for tc in self.toCity:
                for plusDate in self.plusDate:
                    endDate = datetime.date.today() + datetime.timedelta(days=int(plusDate))
                    month = endDate.strftime("%Y-%m")
                    day = endDate.strftime("%d")
                    goDate = endDate.strftime("%Y/%m/%d")

                    self.ticketFromCity = fc
                    self.ticketToCity = tc

                    self.formdata = {
                        '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$btnNext',
                        '__EVENTARGUMENT': '',
                        '__VIEWSTATE': viewState,
                        '__EVENTVALIDATION': eventValidation,
                        'ctl00$ContentPlaceHolder1$trip': trip,
                        'ctl00$ContentPlaceHolder1$startCity': fc,
                        'ctl00$ContentPlaceHolder1$goMonth': month,
                        'ctl00$ContentPlaceHolder1$goDay': day,
                        'ctl00$ContentPlaceHolder1$goDate': goDate,
                        'ctl00$ContentPlaceHolder1$endCity': tc,
                        'ctl00$ContentPlaceHolder1$backMonth': month,
                        'ctl00$ContentPlaceHolder1$backDay': day,
                        'ctl00$ContentPlaceHolder1$backDate': goDate,
                        'ctl00$ContentPlaceHolder1$backNotSure': backNotSure,
                        'ctl00$ContentPlaceHolder1$periodType': periodType,
                        'ctl00$ContentPlaceHolder1$cabinClass': "Y",
                        'ctl00$ContentPlaceHolder1$adultNumber': "1",
                        'ctl00$ContentPlaceHolder1$childNumber': "0",
                        'ctl00$ContentPlaceHolder1$errRedirect': "",
                        'ctl00$ContentPlaceHolder1$promoDateStr': "",
                    }

                    yield scrapy.FormRequest(url = url,
                                             formdata = self.formdata,
                                             dont_filter = True,
                                             method = "POST",
                                             callback = callback)

    def getViewState(self, response):
        infos = response.xpath("//input[@name='__VIEWSTATE']//@value").extract()
        if infos:
            return infos[0]
        else:
            return None

    def getEventValidation(self, response):
        infos = response.xpath("//input[@name='__EVENTVALIDATION']//@value").extract()
        if infos:
            return infos[0]
        else:
            return None

    def getOnewayTicket(self, response):
        tickets = []

        columnDate = response.xpath("//table[@class='tripSelectTable']//thead//tr//th//div/text()").extract()
        columnPrice = response.xpath("//div//label//span/text()").extract()

        for idx in range(0, len(columnDate)/2):
            ticket = OnewayTicket()
            ticket["flightCompany"] = self.name.upper()
            ticket["flyingDate"] = "%s - %s" %(columnDate[idx*2], columnDate[idx*2+1])
            ticket["price"] = columnPrice[idx]
            ticket["fromCity"] = self.ticketFromCity
            ticket["toCity"] = self.ticketToCity

            if ticket["price"].replace(",", "").isdigit():
                tickets.append(ticket)
            #else:
            #    print ticket["price"], ticket["price"].isdigit()

        return tickets

    def dateOneway(self, response):
        viewState = self.getViewState(response)
        eventValidation = self.getEventValidation(response)

        if viewState == None:
            print response.body
            return

        tickets = self.getOnewayTicket(response)
        for ticket in tickets:
            yield ticket

        formdata = {"__EVENTTARGET": "ctl00$ContentPlaceHolder1$LinkButton_Next_Week",
                    "__VIEWSTATE": viewState,
                    "__EVENTVALIDATION": eventValidation,
                    "__EVENTARGUMENT": "",
                    "ctl00$ContentPlaceHolder1$tripCell": "RadioButton_Cell_3",
                    "ctl00$ContentPlaceHolder1$errRedirect": ""}

        yield scrapy.FormRequest(url = self.date_oneway_url,
                                 formdata = formdata,
                                 dont_filter = True,
                                 method = "POST",
                                 callback = self.nextWeek)

    def nextWeek(self, response):
        tickets = self.getOnewayTicket(response)
        for ticket in tickets:
            yield ticket

    def travel(self, response):
        viewState = self.getViewState(response)
        eventValidation = self.getEventValidation(response)

        self.flights = []
        for td in response.xpath("//table[@id='gvFlight']//tr")[1:]:
            '''
            [u'CI0156', u'TPE KIX', u'02-24 08:30/02-24 12:00', u'02:30', u'744', u'CI0156', u' ', u'\r\n                --\r\n            ']
            '''

            td = td.xpath("td/text()").extract()

            flight = ChinaAirlineFlight()
            flight["flight"] = td[0]
            flight["journey"] = td[1]
            flight["flyingDate"] = td[2]
            flight["duration"] = td[3]
            flight["flightType"] = td[4]
            flight["relayStation"] = td[6].replace(" ", "")

            self.flights.append(flight)

        #print len(response.xpath("//input[re:test(@id, 'rdoSelectFare(\d+)')]/@name").extract())
        for value in response.xpath("//input[re:test(@id, 'rdoSelectFare(\d+)')]/@name").extract():
            formdata = copy.copy(self.formdata)
            formdata["__EVENTTARGET"] = value
            formdata["__VIEWSTATE"] = viewState
            formdata["__EVENTVALIDATION"] = eventValidation

            yield scrapy.FormRequest(url = self.fare_url,
                                     formdata = formdata,
                                     dont_filter = True,
                                     method = "POST",
                                     callback = self.ticket)

    def flight(self, response):
        viewState = self.getViewState(response)
        eventValidation = self.getEventValidation(response)

        # [u'CI0921', u'TPE HKG', u'02-25 22:10/02-25 23:55', u'01:45', u'333', u'CI0921']
        for tr in response.xpath("//table//tbody//tr")[2:]:
            tds = tr.xpath("td/text()").extract()

            flight = ChinaAirlineFlight()
            flight["flight"] = tds[0]
            flight["journey"] = tds[1]
            flight["flyingDate"] = tds[2]
            flight["duration"] = tds[3]
            flight["flightType"] = tds[4]
            if len(tds) > 5:
                flight["relayStation"] = tds[5].replace(" ", "")
            else:
                flight["relayStation"] = tds[6]

            name = tr.xpath("td//input/@name").extract()[0]
            value = tr.xpath("td//input/@value").extract()[0]

            formdata = {"__EVENTTARGET": "SelNo",
                        "__EVENTARGUMENT": "",
                        "__VIEWSTATE": viewState,
                        "__EVENTVALIDATION": eventValidation,
                        "ctl00$ContentPlaceHolder1$SelNo": str(value)}

            for key, value in formdata.items():
                print key, value

            yield scrapy.FormRequest(url = self.fare_flight_url,
                                     formdata = formdata,
                                     dont_filter = True,
                                     method = "POST",
                                     callback = self.ticket)

    def ticket(self, response):
        viewState = self.getViewState(response)

        ticket = ChinaAirlineTicket()
        ticket["possibleFlight"] = [dict(flight) for flight in self.flights]

        tds = response.xpath("//table[@id='gvTicketRuleMore']//tr//td/text()").extract()

        ticket["journey"] = tds[2]
        ticket["priceAdult"] = tds[5]
        ticket["priceChild"] = tds[8]
        ticket["salesDate"] = tds[11]
        ticket["applicableGoDate"] = tds[20]
        ticket["applicableGoFlight"] = tds[23]
        ticket["applicableGoWeek"] = tds[26]
        #ticket["applicableBackDate"] = tds[29]
        ticket["applicableBackFlight"] = tds[29]
        ticket["applicableBackWeek"] = tds[32]
        ticket["stayingMinPeriod"] = tds[35]
        ticket["stayingMaxPeriod"] = tds[38]
        ticket["goDate"] = tds[41]
        ticket["backDate"] = tds[44]
        ticket["cabin"] = tds[47]
        ticket["cabinClass"] = tds[50]
        ticket["seat"] = tds[57]
        ticket["changeDestination"] = tds[60]
        ticket["transferredTicket"] = tds[63]
        ticket["allowRefund"] = tds[65]
        ticket["others"] = tds[68]

        ticket["crawlingDate"] = time.time()

        yield ticket
