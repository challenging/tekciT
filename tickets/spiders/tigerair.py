#coding=utf-8

import sys, datetime, time, socket

import scrapy
from tickets.items import TigerAirTicket

from pyvirtualdisplay import Display
import selenium.webdriver.support.ui as ui
from selenium import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, UnexpectedAlertPresentException

class TigerAirSpider(scrapy.Spider):
    name = 'TigerAir'
    allow_domain = ['www.tigerair.com', "booking.tigerair.com"]
    start_urls = ["https://booking.tigerair.com/Search.aspx"]
    search_url = "https://www.tigerair.com/tw/zh/index.php"

    def __init__(self, fromCity, toCity, dateStart, dateEnd):
        self.fromCity = fromCity
        self.toCity = toCity
        self.dateStart = int(dateStart)
        self.dateEnd = int(dateEnd)

        self.startWebDriver()

    def startWebDriver(self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()

        self.webDriver = webdriver.Firefox()

    def quitWebDriver(self):
        self.webDriver.quit()
        self.display.stop()

    def parse(self, response):
        for plusDate in range(self.dateStart, self.dateEnd+1):
            flyingDate = datetime.date.today() + datetime.timedelta(days=plusDate)

            maxTries = 2
            while maxTries > 0:
                try:
                    browser = self.webDriver
                    browser.get(TigerAirSpider.search_url)

                    tries = 3
                    while tries > 0:
                        try:
                            browser.execute_script("document.getElementById('dateDepart').value = '%s'" %flyingDate.strftime("%d %b %Y"))
                            browser.execute_script("document.getElementById('dateReturn').value = '%s'" %flyingDate.strftime("%d %b %Y"))

                            browser.execute_script("document.getElementsByName('ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDay1')[0].value = '%s'" %flyingDate.strftime("%d"))
                            browser.execute_script("document.getElementsByName('ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketMonth1')[0].value = '%s'" %flyingDate.strftime("%Y-%m"))

                            browser.execute_script("document.getElementsByName('ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDay2')[0].value = '%s'" %flyingDate.strftime("%d"))
                            browser.execute_script("document.getElementsByName('ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketMonth2')[0].value = '%s'" %flyingDate.strftime("%Y-%m"))

                            browser.execute_script("document.getElementById('%s').click()" %self.fromCity)
                            browser.execute_script("document.getElementById('%s').click()" %self.toCity)
                            browser.execute_script("document.getElementById('submitSearch').removeAttribute('disabled')")
                            browser.execute_script("document.getElementById('submitSearch').click()")

                            if ui.WebDriverWait(browser, 10).until(lambda browser: len("//td[@class='light prices']//label//input") > 0):
                                backs = browser.find_elements_by_xpath("//td[@class='light prices']//label//input")
                                prices = browser.find_elements_by_xpath("//td[@class='light prices']//label//span[@class='price']")
                                #print len(backs), len(prices)
                                for idx in range(0, len(backs)):
                                    infos = backs[idx].get_attribute("value").split("~")
                                    #for i in range(0, len(infos)):
                                    #    print i, infos[i]

                                    ticket = TigerAirTicket()
                                    ticket["company"] = self.name
                                    ticket["flyingDate"] = flyingDate.strftime("%Y-%m-%d")
                                    ticket["fromCity"] = infos[10]
                                    ticket["toCity"] = infos[-2]
                                    ticket["price"] = prices[idx].text

                                    ticket["isTransferred"] = False
                                    ticket["datetimeStart"] = infos[11]
                                    if len(infos) > 17:
                                        ticket["fromCity"] = infos[16]
                                        ticket["isTransferred"] = True
                                        ticket["datetimeStart"] = infos[17]
                                        ticket["flight"] = "%s%s,%s%s" %(infos[12].split("|")[1], infos[13], infos[19].split("^")[1], infos[20])
                                    else:
                                        ticket["flight"] = "%s%s" %(infos[6].split("|")[1], infos[7].strip())

                                    ticket["datetimeEnd"] = infos[-1]

                                    yield ticket

                                maxTries = -1
                                break
                        except UnexpectedAlertPresentException as e:
                            tries -= 1
                            print e
                        except WebDriverException as e:
                            tries -= 1
                            print e

                except socket.timeout as e:
                    print e
                except TimeoutException as e:
                    print e

                maxTries -= 1

        self.quitWebDriver()

    '''
    def parse(self, response):
        viewstate = response.xpath("//input[@name='viewState']").extract()[0]
        formdata = {"__VIEWSTATE": viewstate}

        p = response.xpath("//form[@id='SkySales']//input")
        for pp in p:
            name = pp.xpath("@name").extract()
            if len(name) > 0:
                value = pp.xpath("@value").extract()

                if len(value) > 0:
                    if name[0].lower() in ["viewstate", "eventtarget", "eventargument"]:
                        formdata["__%s" %name[0].upper()] = value[0]
                    else:
                        formdata[name[0]] = value[0]
                else:
                    formdata[name[0]] = ""

        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$RadioButtonMarket"] = "RoundTrip"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$RadioButtonMarketStructure"] = "RoundTrip"
        formdata["ControlGroupSearchView_AvailabilitySearchInputSearchVieworiginStation1"] = self.fromCity.upper()
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin1"] = self.fromCity.upper()
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination2"] = self.fromCity.upper()

        formdata["ControlGroupSearchView_AvailabilitySearchInputSearchViewdestinationStation1"] = self.toCity.upper()
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination1"] = self.toCity.upper()
        formdata["ControlGroupSearchView_AvailabilitySearchInputSearchVieworiginStation2"] = self.toCity.upper()
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin2"] = self.toCity.upper()

        formdata["ControlGroupSearchView_AvailabilitySearchInputSearchViewdestinationStation2"] = ""

        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDateRange1"] = "1|1"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDateRange2"] = "1|1"

        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_ADT"] = "1"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_CHD"] = "0"
        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_INFANT"] = "0"

        formdata["hiddendAdultSelection"] = "1"
        formdata["hiddendChildSelection"] = "0"

        formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMCCCurrency"] = ""

        for i in range(1, self.plusDate):
            futureDate = datetime.date.today() + datetime.timedelta(days = i*7)

            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDay1"] = futureDate.strftime("%d")
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketMonth1"] = futureDate.strftime("%Y-%m")

            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDay2"] = futureDate.strftime("%d")
            formdata["ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketMonth2"] = futureDate.strftime("%Y-%m")

            #for key, value in formdata.items():
            #    print key, value

            yield scrapy.FormRequest(url = TigerAirSpider.search_url,
                                     formdata = formdata,
                                     dont_filter = True,
                                     method = "POST",
                                     callback = self.ticket)

    def ticket(self, response):
        print response.body
        #print response.url

        prices = response.xpath("//td[@class='light prices']//h3[@class='fareprice']/text()").extract()
        infos = response.xpath("//td[@class='light prices']//input[@name='ControlGroupSelectBundleView$AvailabilityInputSelectBundleView$market1']/@value").extract()
        for idx in range(0, len(infos)):
            print prices[idx], infos[idx]
    '''
