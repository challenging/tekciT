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
        self.webDriver = webdriver.Firefox()

    def quitWebDriver(self):
        self.webDriver.quit()
        self.display.stop()

    '''
    def start_requests(self):
        for plusDate in range(int(self.dateStart), int(self.dateEnd)+1):
            flyingDate = datetime.date.today() + datetime.timedelta(days=int(plusDate))

            url = "http://book.flypeach.com/WebService/B2cService.asmx/GetQuoteSummary"
            my_data = {"strFlightXml":"<flights><flight><flight_id>{8AF94BF6-A8B3-4A13-B3CF-07D72452209D}</flight_id><airline_rcd>MM</airline_rcd><flight_number>028</flight_number><origin_rcd>TPE</origin_rcd><destination_rcd>KIX</destination_rcd><fare_id>{3BACF111-A73F-475B-9A00-0C3F55E7C9FF}</fare_id><transit_airline_rcd></transit_airline_rcd><transit_flight_number></transit_flight_number><transit_flight_id></transit_flight_id><departure_date>20141030</departure_date><arrival_date>20141030</arrival_date><arrival_day>4</arrival_day><departure_day>4</departure_day><planned_departure_time>1850</planned_departure_time><planned_arrival_time>2215</planned_arrival_time><transit_departure_date></transit_departure_date><transit_departure_day></transit_departure_day><transit_arrival_date></transit_arrival_date><transit_arrival_day></transit_arrival_day><transit_planned_departure_time></transit_planned_departure_time><transit_planned_arrival_time></transit_planned_arrival_time><transit_airport_rcd></transit_airport_rcd><transit_fare_id></transit_fare_id><booking_class_rcd>U</booking_class_rcd><currency_rcd>TWD</currency_rcd></flight></flights>","strFlightType":"Outward"}
            yield Request(url = url, method = "POST", body = json.dumps(my_data), headers = {"Content-Type": "application/json; charset=UTF-8"}, callback = self.ticket)

    def ticket(self, response):
        print json.loads(response.body)
        print response.url
    '''

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

                        '''
                        u'flight_id:{E512628A-CD8E-42E5-A3F7-1687BBCF0408}|fare_id:{499E838D-39D3-4359-B7C3-5037D16A86CB}|boarding_class_rcd:Y|booking_class_rcd:Q|airline_rcd:MM|flight_number:024|origin_rcd:TPE|destination_rcd:KIX|departure_date:20140917|planned_departure_time:1105|planned_arrival_time:1445|transit_airline_rcd:|transit_flight_number:|transit_airport_rcd:|transit_boarding_class_rcd:|transit_booking_class_rcd:|transit_flight_id:|transit_fare_id:|transit_planned_departure_time:|transit_planned_arrival_time:|total_tax:0.00|adult_fare:6520|child_fare:6520|infant_fare:0.0000|transit_departure_date:|arrival_date:20140917|number_of_adult:1|number_of_child:0|number_of_infant:0|currency_rcd:TWD|transit_arrival_date:'
                        '''

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
