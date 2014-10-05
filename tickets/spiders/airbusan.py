#coding=utf-8

import sys
import socket, time, datetime

from pyvirtualdisplay import Display

import selenium.webdriver.support.ui as ui
from selenium import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, UnexpectedAlertPresentException

from scrapy.contrib.spiders import CrawlSpider
from tickets.items import AirBusanTicket

class AirBusanSpider(CrawlSpider):
    name = "AirBusan"
    allowed_domains = ["rsvweb.airbusan.com", "www.airbusan.com"]
    start_urls = ["http://www.airbusan.com/AB/airbusan/CN/main.jsp?"]
    search_url = "https://rsvweb.airbusan.com/web%s/InternationalReserve/FBookIntCheck001?lang=tw&depCity=%s&arrCity=%s&depDate=&arrDate=&journey=2&ADCnt=1&CHCnt=0&INCnt=0&start_date=%s&return_date=%s&minyn=null"

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
        self.webDriver = webdriver.Firefox()

    def quitWebDriver(self):
        self.webDriver.quit()
        self.display.stop()

    def parse(self, response):
        driver = self.webDriver

        for plusDate in range(self.dateStart, self.dateEnd+1):
            flyingDate = datetime.date.today() + datetime.timedelta(days=int(plusDate))

            url = ""
            maxTries = 3
            while maxTries > 0:
                try:
                    url = AirBusanSpider.search_url %(flyingDate.strftime("%Y"), self.fromCity, self.toCity, flyingDate.strftime("%Y/%m/%d"), flyingDate.strftime("%Y/%m/%d"))
                    driver.get(url)
                    print url, maxTries

                    tries = 3
                    while tries > 0:
                        try:
                            #time.sleep(2)
                            if ui.WebDriverWait(driver, 5).until(lambda driver: len(driver.find_elements_by_id("Adddep")) > 0):
                                go = driver.find_elements_by_id("Adddep")[0].find_elements_by_tag_name("tr")[1:]
                                # u'BX 793\n11:05 12:25 321 9'
                                # u'BX 794\n\u53f0\u5317\n13:15 \u91dc\u5c71\n16:25 321 9'
                                flightGo = []
                                for flight in go:
                                    flightGo.append(flight.text.split("\n")[0])

                                datetimeGos = []
                                if len(go) > 1:
                                    # u'BX 794\n\u53f0\u5317\n13:15 \u91dc\u5c71\n16:25 321 9'
                                    datetimeGos.append(go[0].text.split("\n")[2].split(" ")[0])
                                    datetimeGos.append(go[1].text.split("\n")[-1].split(" ")[0])
                                else:
                                    datetimeGos = go[0].text.split("\n")[1].split(" ")[0:2]

                                #datetimeBack = driver.find_elements_by_id("Addarr")[0].find_elements_by_tag_name("tr")[1].text

                                flights = driver.find_elements_by_xpath("//input[@name='cls_radio']")
                                for flight in flights:
                                    if flight.is_enabled():
                                        info = flight.get_attribute("value")
                                        price = None
                                        for t in info.split("|"):
                                            if t == "TWD":
                                                price = "TWD"
                                            elif price == "TWD":
                                                price += " %s" %t
                                                break

                                        ticket = AirBusanTicket()
                                        ticket["company"] = self.name
                                        ticket["fromCity"] = self.fromCity
                                        ticket["toCity"] = self.toCity
                                        ticket["price"] = price
                                        ticket["flight"] = ",".join(flightGo)
                                        ticket["flyingDate"] = flyingDate.strftime("%Y-%m-%d")
                                        ticket["datetimeStart"] = "%s %s" %(flyingDate.strftime("%Y-%m-%d"), datetimeGos[0])
                                        ticket["datetimeEnd"] = "%s %s" %(flyingDate.strftime("%Y-%m-%d"), datetimeGos[1])

                                        ticket["isTransferred"] = False
                                        if len(go) > 1:
                                            ticket["isTransferred"] = True

                                        # u'V|SMART 17 WEB(V)|N|Y|Y|N|VP17|17\u5929|TWD|6599|TWD|6599|0|0794/0792|0793/0791|N|0D|17D| | |9|N|'
                                        ticket["info"] = flight.get_attribute("value")

                                        yield ticket
                              
                            maxTries = -1
                            break
                        except UnexpectedAlertPresentException as e:
                            tries -= 1
                        except WebDriverException as e:
                            tries -= 1

                except socket.timeout as e:
                    print e, url
                except NoSuchElementException as e:
                    print e, url
                except TimeoutException as e:
                    print e, url

                maxTries -= 1

        self.quitWebDriver()
