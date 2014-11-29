#coding=utf-8

import sys
import jsonlib2 as json

import scrapy
import socket, time, datetime

from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider, Rule

from pyvirtualdisplay import Display
import selenium.webdriver.support.ui as ui
from selenium import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, UnexpectedAlertPresentException

from tickets.items import PeachTicket

# http://book.flypeach.com/WebService/B2cService.asmx/GetQuoteSummary
class PeachSpider(CrawlSpider):
    name = "Peach"
    allowed_domains = ["book.flypeach.com", "www.flypeach.com"]
    start_urls = ["http://www.flypeach.com/tw/home.aspx"]

    def __init__(self, fromCity, toCity, dateStart, dateEnd):
        self.fromCity = fromCity
        self.toCity = toCity
        self.dateStart = int(dateStart)
        self.dateEnd = int(dateEnd)

        CrawlSpider.__init__(self)
        self.startWebDriver()

    def startWebDriver(self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        self.webDriver = webdriver.Chrome()

    def quitWebDriver(self):
        self.webDriver.quit()
        self.display.stop()

    def parse(self, response):
        for plusDate in range(self.dateStart, self.dateEnd+1):
            flyingDate = datetime.date.today() + datetime.timedelta(days=int(plusDate))

            url = ""
            maxTries = 3
            flights = []
            while not flights:
                if maxTries < 1:
                    break

                try:
                    driver = self.webDriver

                    url = "http://book.flypeach.com/default.aspx?ao=B2CZHTW&ori=%s&des=%s&dep=%s&adt=1&chd=0&inf=0&langculture=zh-TW&bLFF=false" %(self.fromCity, self.toCity, flyingDate.strftime("%Y-%m-%d"))
                    driver.get(url)

                    wait = ui.WebDriverWait(driver, 5)

                    tries = 3
                    while tries > 0:
                        try:
                            wait.until(lambda driver: len(driver.find_elements_by_xpath("//input[starts-with(@id, 'optOutward1_')]")) > 0)
                            break
                        except UnexpectedAlertPresentException as e:
                            tries -= 1

                    flights = driver.find_elements_by_xpath("//input[starts-with(@id, 'optOutward1_')]")
                except socket.timeout as e:
                    print e, url
                except NoSuchElementException as e:
                    print e, url
                except TimeoutException as e:
                    print e, url

                if flights:
                    for flight in flights:
                        raw = flight.get_attribute("value")
                        data = {}
                        for info in raw[1:len(raw)].split("|"):
                            [key, value] = info.split(":")
                            data[key] = value

                        ticket = PeachTicket()
                        ticket["company"] = self.name
                        ticket["flight"] = "%s%s" %(data["airline_rcd"], data["flight_number"])
                        ticket["url"] = url
                        ticket["fromCity"] = self.fromCity
                        ticket["toCity"] = self.toCity
                        ticket["flyingDate"] = data["arrival_date"]
                        ticket["info"] = flight.get_attribute("value")
                        ticket["price"] = data["adult_fare"]
                        ticket["currency"] = data["currency_rcd"]
                        ticket["datetimeStart"] = "%s %s" %(data["departure_date"], data["planned_departure_time"])
                        ticket["datetimeEnd"] = "%s %s" %(data["arrival_date"], data["planned_arrival_time"])

                        yield ticket

                    break

                maxTries -= 1

        self.quitWebDriver()
