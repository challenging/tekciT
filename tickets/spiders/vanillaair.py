#-*- coding: utf-8 -*-

import sys, exceptions
import time, datetime
import socket, re

from scrapy.contrib.spiders import CrawlSpider

from tickets.items import VanillaAirTicket

import selenium.webdriver.support.ui as ui

from pyvirtualdisplay import Display
from selenium import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException

class VanillaAirSpider(CrawlSpider):
    name = "VanillaAir"
    allowed_domains = ["www.vanilla-air.com"]
    start_urls = ["http://www.vanilla-air.com/tw"]
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
