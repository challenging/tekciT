#-*- coding: utf-8 -*-

import sys, exceptions
import time, datetime
import socket, re

from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider

from tickets.items import VanillaAirTicket

from pyvirtualdisplay import Display
import selenium.webdriver.support.ui as ui
from selenium import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException

import lxml.html.clean as clean

class VanillaAirSpider(CrawlSpider):
    name = "VanillaAir"
    allowed_domains = ["www.vanilla-air.com"]
    start_urls = ["http://www.vanilla-air.com/tw"]
    #start_urls = ["http://www.vanilla-air.com/reservation/ibe/ibe/booking?origin=TPE&destination=NRT&travelDate=30-Sep-2014&travelDate=13-Oct-2014&tripType=RT&adults=1&children=0&infants=0&promoCode=&mode=searchResultInter&locale=tw&wvm=WVMD&channel=PB&cabinClass=ECONOMY&pointOfPurchase=OTHERS"]
    search_url = "http://www.vanilla-air.com/tw"

    def __init__(self, fromCity, toCity, plusDate):
        self.fromCity = fromCity.upper()
        self.toCity = toCity.upper()
        self.plusDate = int(plusDate)
       
        CrawlSpider.__init__(self)
        self.startWebDriver()
 
    def startWebDriver(self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        self.webDriver = webdriver.Firefox()

    def quitWebDriver(self):
        self.webDriver.quit()
        self.display.stop()

    def parse(self, response):
        def getIdx(city):
            idx = None
            if city == "NRT":
                idx = 1
            elif city == "CTS":
                idx = 2
            elif city == "OKA":
                idx = 3
            elif city == "ASJ":
                idx = 4
            elif city == "OKA":
                idx = 5
            elif city == "ASJ":
                idx = 6
            elif city == "ICN":
                idx = 7
            elif city == "TPE":
                idx = 8
            elif city == "KHH":
                idx = 9
            elif city == "HKG":
                idx = 10

            return idx

        def fromCity(city):
            idx = getIdx(city)
            if idx != None:
                self.webDriver.execute_script("document.getElementById('edit-origin').getElementsByTagName('option')[%d].selected = 'selected'" %idx)
                print "document.getElementById('edit-origin').getElementsByTagName('option')[%d].selected = 'selected'" %idx
            else:
                assert "Not Found" %city

        def toCity(city):
            idx = getIdx(city)
            if idx != None:
                self.webDriver.execute_script("document.getElementById('edit-destination').getElementsByTagName('option')[%d].selected = 'selected'" %idx)
                print "document.getElementById('edit-destination').getElementsByTagName('option')[%d].selected = 'selected'" %idx
            else:
                assert "Not Found" %city

        flyingDate = datetime.date.today() + datetime.timedelta(days=self.plusDate)

        flights = []
        maxTries = 5
        while not flights:
            if maxTries < 1:
                break

            try:
                browser = self.webDriver
                browser.get("http://www.vanilla-air.com/reservation/ibe/ibe/booking?origin=%s&destination=%s&travelDate=%s&travelDate=%s&tripType=RT&adults=1&children=0&infants=0&promoCode=&mode=searchResultInter&locale=tw&wvm=WVMD&channel=PB&cabinClass=ECONOMY&pointOfPurchase=OTHERS" %(self.fromCity, self.toCity, flyingDate.strftime("%d-%b-%Y"), flyingDate.strftime("%d-%b-%Y")))
                #time.sleep(3)

                '''
                fromCity(self.fromCity)
                toCity(self.toCity)
                browser.execute_script("document.getElementById('edit-submit--2').click()")
                isCompleted = ui.WebDriverWait(browser, 10).until(lambda broswer: browser.find_element_by_link_text("OK") != None)
                while isCompleted:
                    browser.find_element_by_link_text("OK").click()
                    break

                #browser.execute_script("document.getElementById('edit-traveldate1-datepicker-popup-0').value = '%s'" %flyingDate.strftime("%Y/%m/%d"))
                #print "document.getElementById('edit-traveldate1-datepicker-popup-0').value = '%s'" %flyingDate.strftime("%Y/%m/%d")
                #browser.execute_script("document.getElementById('edit-traveldate2-datepicker-popup-0').value = '%s'" %flyingDate.strftime("%Y/%m/%d"))
                #print "document.getElementById('edit-traveldate1-datepicker-popup-0').value = '%s'" %flyingDate.strftime("%Y/%m/%d")

                toCity(self.toCity)
                browser.execute_script("document.getElementById('edit-submit--2').click()")
                print "document.getElementById('edit-submit--2').click()"

                flights = []
                isCompleted = ui.WebDriverWait(browser, 10).until(lambda broswer: len(browser.find_elements_by_name("selectedFarepos_1")) > 0)
                if isCompleted:
                    flights = browser.find_elements_by_name("selectedFarepos_1")
                '''

                if ui.WebDriverWait(browser, 10).until(lambda browser: len(browser.find_elements_by_tag_name("ul")) > 0):
                    flights = browser.find_elements_by_tag_name("ul")[1:3]
            except socket.timeout as e:
                print e
            except NoSuchElementException as e:
                print e
            except TimeoutException as e:
                print e

            if flights:
                isGoing = True
                for flight in flights:
                    infos = flight.text.split("\n")
                    print infos

                    n = 2
                    for idx in range(0, len(infos)/n):
                        ticket = VanillaAirTicket()
                        ticket["company"] = self.name
                        ticket["flyingDate"] = infos[idx*n]
                        if isGoing:
                            ticket["fromCity"] = self.fromCity
                            ticket["toCity"] = self.toCity
                        else:
                            ticket["fromCity"] = self.toCity
                            ticket["toCity"] = self.fromCity
                        ticket["price"] = infos[idx*n + 1]

                        yield ticket

                    isGoing = False

            maxTries -= 1

        self.quitWebDriver()
