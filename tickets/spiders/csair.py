#coding=utf-8

import sys, datetime, time, exceptions
import re

import scrapy
from tickets.items import CsairTicket

from pyvirtualdisplay import Display
import selenium.webdriver.support.ui as ui
from selenium import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, StaleElementReferenceException, UnexpectedAlertPresentException
from selenium.webdriver.support.ui import Select

class CsairSpider(scrapy.Spider):
    name = 'Csair'
    allow_domain = ["b2c.csair.com", "www.csair.com"]
    start_urls = ["http://www.csair.com/cn/"]
    search_url = "http://www.csair.com/cn/"

    def __init__(self, fromCity, fromCityCode, toCity, toCityCode, dateStart, dateEnd):
        self.fromCity = fromCity
        self.fromCityCode = fromCityCode.upper()

        self.toCity = toCity
        self.toCityCode = toCityCode.upper()
        self.dateStart = int(dateStart)
        self.dateEnd = int(dateEnd)

        self.startWebDriver()

    def startWebDriver(self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        self.browser = webdriver.Chrome()

    def quitWebDriver(self):
        self.browser.quit()
        self.display.stop()

    def js(self, js):
        tries = 3
        while tries > 0:
            try:
                self.browser.execute_script(js)
                break
            except UnexpectedAlertPresentException as e:
                tries -= 1

    def flight(self, infos):
        lines = []

        ticket = None
        for info in infos:
            lines.append(info)

            if u"去程" in info:
                if ticket != None:
                    ticket["info"] = "\n".join(lines)
                    lines = []

                    yield ticket

                ticket = CsairTicket()

                ticket["company"] = self.name
                ticket["fromCity"] = self.fromCityCode
                ticket["toCity"] = self.toCityCode
                ticket["flyingDate"] = info
            elif u"含税总价 ¥" in info:
                ticket["price"] = "".join(info.split(" ")[1:])
            elif info.find("CZ") == 0:
                ticket["flight"] = info
            elif re.findall("(\d{2}:\d{2})", info):
                results = re.findall("(\d{2}:\d{2})", info)

                if "datetimeStart" in ticket:
                    ticket["datetimeStart"] = results[0]
                else:
                    ticket["datetimeEnd"] = results[0]

        if ticket:
            yield ticket

    def parse(self, response):
        count_fail = 0
        for plusDate in range(self.dateStart, self.dateEnd+1):
            if count_fail >= 7:
                break

            flyingDate = datetime.date.today() + datetime.timedelta(days=int(plusDate))
            backDate = datetime.date.today() + datetime.timedelta(days=int(plusDate)+1)

            self.browser.get(CsairSpider.search_url)
            time.sleep(5)

            self.js("document.getElementsByName(\"segtype_1\")[1].click();")

            self.js("document.getElementById(\"city1_code\").value = \"%s\";" %self.fromCityCode)
            self.js("document.getElementById(\"fromcity\").value = \"%s\";" %self.fromCity)

            self.js("document.getElementById(\"city2_code\").value = \"%s\";" %self.toCityCode)
            self.js("document.getElementById(\"tocity\").value = \"%s\";" %self.toCity)

            self.js("document.getElementById(\"DepartureDate\").value = \"%s\";" %flyingDate.strftime("%Y-%m-%d"))
            self.js("document.getElementById(\"ReturnDate\").value = \"%s\";" %backDate.strftime("%Y-%m-%d"))

            self.js("document.getElementById(\"submit_flight_btn\").click();")

            try:
                browser = self.browser
                isCompleted = ui.WebDriverWait(browser, 10).until(lambda browser: len(browser.find_elements_by_id("flight_info")) > 0 and len(browser.find_elements_by_id("flight_info")[0].text) > 0)
                if isCompleted:
                    infos = browser.find_elements_by_id("flight_info")[0].text.split("\n")

                    for ticket in self.flight(infos):
                        yield ticket

                    count_fail = -1

                count_fail += 1
            except exceptions.IndexError as e:
                pass
            except TimeoutException as e:
                pass
            except StaleElementReferenceException as e:
                pass

        self.quitWebDriver()
