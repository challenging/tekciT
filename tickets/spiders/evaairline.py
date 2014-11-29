#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys, exceptions
import time, datetime
import socket, re

from scrapy.http import Request, TextResponse
from scrapy.contrib.spiders import CrawlSpider

from tickets.items import EvrAirlineTicket

from pyvirtualdisplay import Display
import selenium.webdriver.support.ui as ui
from selenium import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.support.ui import Select

from urlparse import urlparse, parse_qs

class EvaAirlineSpider(CrawlSpider):
    name = "EvaAirline"
    allowed_domains = ["eservice.evaair.com", "wftc3.e-travel.com"]
    start_urls = ["http://www.evaair.com/zh-tw/index.html"]
    search_url = "http://www.evaair.com/zh-tw/index.html"

    def __init__(self, fromArea, fromCity, dateStart, dateEnd):
        self.fromCity = fromCity.lower()

        self.fromArea = None
        if fromArea == "europe":
            self.fromArea = u"歐洲"
        elif fromArea in ["asia", "china"]:
            self.fromArea = u"亞洲"
        elif fromArea == "america":
            self.fromArea = u"美洲"
        elif fromArea == "oceania":
            self.fromArea = u"大洋洲"

        self.dateStart = int(dateStart)
        self.dateEnd = int(dateEnd)

        self.destinationCities = []

        self.tickets = []

        CrawlSpider.__init__(self)
        self.startWebDriver()
 
    def startWebDriver(self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        self.webDriver = webdriver.Chrome()

    def quitWebDriver(self):
        self.webDriver.quit()
        self.display.stop()

    def optionClick(self, select, text):
        for option in select.options:
            print text, "|", option.text
            if text in option.text.replace(u"年", "-").lower():
                print "click - ", option.text
                return option

    def parse(self, response):
        for plusDate in range(self.dateStart, self.dateEnd+1, 7):
            flyingDate = datetime.date.today() + datetime.timedelta(days=int(plusDate))

            destination = {}
            # Get destination cities
            try:
                self.webDriver.get(EvaAirlineSpider.search_url)

                goDepArea = self.webDriver.find_element_by_id("gDepArea")
                self.optionClick(Select(goDepArea), self.fromArea).click()

                goDep = self.webDriver.find_element_by_id("gGoDep")
                option = self.optionClick(Select(goDep), self.fromCity)
                if option:
                    option.click()

                goArrArea = self.webDriver.find_element_by_id("gArrArea")
                select = Select(goArrArea)
                for option in select.options:
                    toArea = option.text
                    destination[toArea] = []

                    self.optionClick(select, toArea).click()

                    goArr = self.webDriver.find_element_by_id("gGoArr")
                    for option in Select(goArr).options:
                        if option.get_attribute("value") != u"":
                            destination[toArea].append(option.get_attribute("value"))
            except socket.timeout as e:
                print e
            except NoSuchElementException as e:
                print e
            except TimeoutException as e:
                print e

            for area, cities in destination.items():
                for city in cities:
                    for ticket in self.going(self.webDriver, flyingDate, area, city):
                        yield ticket

        self.quitWebDriver()

    def going(self, driver, flyingDate, area, city):
        tickets = []

        maxTries = 3
        while maxTries > 0:
            try:
                driver.get(EvaAirlineSpider.search_url)
                trip = driver.find_element_by_id("Radio3")
                trip.click()

                goDepArea = driver.find_element_by_id("gDepArea")
                self.optionClick(Select(goDepArea), self.fromArea).click()

                goDep = driver.find_element_by_id("gGoDep")
                option = self.optionClick(Select(goDep), self.fromCity)
                if option:
                    option.click()
                else:
                    break

                goArrArea = driver.find_element_by_id("gArrArea")
                self.optionClick(Select(goArrArea), area).click()

                goArr = driver.find_element_by_id("gGoArr")
                option = self.optionClick(Select(goArr), city)
                if option:
                    option.click()

                goMonth = driver.find_element_by_id("gGoYYYYMM")
                self.optionClick(Select(goMonth), flyingDate.strftime("%Y-%m").replace("-0", "-")).click()

                goDay = driver.find_element_by_id("gGoDD")
                self.optionClick(Select(goDay), re.sub(r"^0", "", flyingDate.strftime("%d"))).click()

                submit = driver.find_element_by_xpath("//table//th/a")
                submit.click()

                wait = ui.WebDriverWait(driver, 10)
                tries = 3
                while tries > 0:
                    try:
                        wait.until(lambda driver: len(driver.find_elements_by_xpath("//a[@class='wdk-waiting-link']")) > 1)
                        break
                    except UnexpectedAlertPresentException as e:
                        tries -= 1

                flights = driver.find_elements_by_xpath("//a[@class='wdk-waiting-link']")
                flights = flights[:len(flights)-1]
                tts = driver.find_elements_by_xpath("//div//a[@class='wdk-waiting-link']//span[@class='date']")
                #print len(tts), tts, city
                #print len(flights), flights, city

                for idx in range(0, len(flights)):
                    flight = flights[idx]

                    href = tts[idx].get_attribute("datetime")
                    tt = href[len(href)-12:]
                    #print "1. ", tt, city
                    price = flight.find_element_by_xpath("//span[@class='price']//span[@class='number']").text
                    #print "2. ", price, city

                    ticket = EvrAirlineTicket()
                    ticket["url"] = driver.current_url
                    ticket["company"] = self.name
                    ticket["fromCity"] = self.fromCity.upper()
                    ticket["toCity"] = city.upper()

                    ticket["flyingDate"] = "%s-%s-%s" %(tt[0:4], tt[4:6], tt[6:8])
                    ticket["price"] = price

                    while ticket["price"] == u"":
                        time.sleep(2)
                        ticket["price"] = flight.find_element_by_xpath("//span[@class='price']//span[@class='number']").text

                    #print "3. ", ticket
                    tickets.append(ticket)
            except socket.timeout as e:
                print e
            except TimeoutException as e:
                print e
            except UnexpectedAlertPresentException as e:
                print e
            except NoSuchElementException as e:
                print e

            if tickets:
                break

            maxTries -= 1

        return tickets
