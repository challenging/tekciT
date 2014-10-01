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
        self.browser = webdriver.Firefox()

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

    '''
0 去程2014年10月04日广州 - 墨尔本
1 头等舱
2 公务舱
3 高端经济舱
4 经济舱
5 CZ343
6 直达 空客333 09:00  广州
7 20:30  墨尔本
8 经济舱来回程票价
9 ¥9610
10 含税总价 ¥ 11672
11 查看票价使用条件
12 选择航班
13 显示详细信息
14 去程2014年10月04日广州 - 墨尔本
15 头等舱
16 公务舱
17 高端经济舱
18 经济舱
19 CZ321
20 直达 空客333 21:00  广州
21 09:40  墨尔本
22 10月05日 星期日
23 经济舱来回程票价
24 ¥10920
25 含税总价 ¥ 12982
26 查看票价使用条件
27 选择航班
28 显示详细信息
    '''
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
        for plusDate in range(self.dateStart, self.dateEnd+1):
            flyingDate = datetime.date.today() + datetime.timedelta(days=int(plusDate))
            backDate = datetime.date.today() + datetime.timedelta(days=int(plusDate)+1)

            self.browser.get(CsairSpider.search_url)
            time.sleep(3)

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
                    #for idx in range(0, len(infos)):
                    #    print idx, infos[idx]

                    '''
                    n = 14
                    for idx in range(0, len(infos)/n):
                        ticket = CsairTicket()
                        ticket["company"] = self.name
                        ticket["flight"] = infos[idx*n + 5]
                        ticket["fromCity"] = self.fromCityCode
                        ticket["toCity"] = self.toCityCode

                        for ii in range(0, n-1):
                            if u"含税总价 ¥" in infos[idx*n + ii]:
                                ticket["price"] = "".join(infos[idx*n + ii].split(" ")[1:])

                        ticket["info"] = "\n".join(infos)
                        ticket["flyingDate"] = infos[idx*n]
                        ticket["datetimeStart"] = infos[idx*n + 6].split(" ")[2]
                        ticket["datetimeEnd"] = infos[idx*n + 7].split(" ")[0]

                        yield ticket
                    '''
                    for ticket in self.flight(infos):
                        yield ticket
            except exceptions.IndexError as e:
                pass
            except TimeoutException as e:
                pass
            except StaleElementReferenceException as e:
                pass

        self.quitWebDriver()
