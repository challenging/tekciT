#-*- coding: utf-8 -*-

import sys, exceptions
import time, datetime
import socket
import re

from scrapy.contrib.spiders import CrawlSpider

from tickets.items import ChinaEasternTicket

from pyvirtualdisplay import Display
import selenium.webdriver.support.ui as ui
from selenium import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, UnexpectedAlertPresentException

class ChinaEasternSpider(CrawlSpider):
    name = "ChinaEastern"
    allowed_domains = ["easternmiles.ceair.com"]
    start_urls = ["http://easternmiles.ceair.com"]
    search_url = "http://easternmiles.ceair.com"

    def __init__(self, fromCity, toCity, dateStart, dateEnd, maxTries = 7):
        (self.fromCity, self.fromValue, self.fromNation, self.fromRegion, self.fromCityCode) = fromCity.split(",")
        self.fromValue += "#"
        print self.fromCity, self.fromValue, self.fromNation, self.fromRegion, self.fromCityCode
        (self.toCity, self.toValue, self.toNation, self.toRegion, self.toCityCode) = toCity.split(",")
        self.toValue += "#"
        print self.toCity, self.toValue, self.toNation, self.toRegion, self.toCityCode
        self.dateStart = int(dateStart)
        self.dateEnd = int(dateEnd)

        self.maxTries = maxTries

        CrawlSpider.__init__(self)
        self.startWebDriver()
 
    def startWebDriver(self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()

        self.webDriver = webdriver.Firefox()

    def quitWebDriver(self):
        self.webDriver.quit()
        self.display.stop()

    def detail(self, infos):
        flights = []

        def merge():
            if len(flights) > 1:
                flights[-2]["flight"].extend(flights[-1]["flight"])
                flights[-2]["transfer"].extend(flights[-1]["transfer"])
                flights[-2]["datetimeStart"].extend(flights[-1]["datetimeStart"])
                flights[-2]["datetimeEnd"].extend(flights[-1]["datetimeEnd"])

                del flights[-1]

        def clear():
            for idx in range(len(flights)-1, -1, -1):
                if u"/" in flights[idx]["price"]:
                    del flights[idx]

        for info in infos:
            if info == u"东方航空":
                if len(flights) > 0 and "price" not in flights[-1] and len(flights[-1]["flight"]) == 1:
                    merge()

                flights.append({"flight": [], "transfer": [], "datetimeStart": [], "datetimeEnd": []})

                flights[-1]["company"] = self.name
            elif info.startswith("MU"):
                flights[-1]["flight"].append(info)
            elif info.startswith(u"¥"):
                flights[-1]["price"] = info
            elif info.startswith(u"中转"):
                flights[-1]["transfer"].append(info)
            elif re.match("^(\d){2}:(\d){2}$", info):
                if len(flights[-1]["datetimeStart"]) == len(flights[-1]["datetimeEnd"]):
                    flights[-1]["datetimeStart"].append(info)
                else:
                    flights[-1]["datetimeEnd"].append(info)

        if len(flights) > 0 and "price" not in flights[-1] and len(flights[-1]["flight"]) == 1:
            merge()

        clear()
        print "The size of flights is %d" %len(flights)
        return flights

    def flight(self, text, url, flyingDate):
        infos = text.split("\n")
        flights = self.detail(infos)
        for flight in flights:
            ticket = ChinaEasternTicket()
            ticket["url"] = url
            ticket["flight"] = " / ".join(flight["flight"])
            ticket["company"] = self.name
            ticket["fromCity"] = self.fromCity.upper()
            ticket["toCity"] = self.toCity.upper()
            ticket["flyingDate"] = flyingDate.strftime("%Y%m%d")
            ticket["info"] = text
            ticket["price"] = flight["price"]
            ticket["datetimeStart"] = " / ".join(flight["datetimeStart"])
            ticket["datetimeEnd"] = " / ".join(flight["datetimeEnd"])
            ticket["transfer"] = " / ".join(flight["transfer"])

            yield ticket

    def waitFlight(self, idx):
        text = ""

        try:
            driver = self.webDriver

            wait = ui.WebDriverWait(driver, 20)
            wait.until(lambda driver: driver.find_elements_by_id("flight-info")[idx].text != "")
            text = driver.find_elements_by_id("flight-info")[idx].text
        except NoSuchElementException as e:
            print e
        except exceptions.IndexError as e:
            print e

        return text

    def parse(self, response):
        for plusDate in range(self.dateStart, self.dateEnd+1):
            flyingDate = datetime.date.today() + datetime.timedelta(days=int(plusDate))

            url = "http://easternmiles.ceair.com/flight%s/%s-%s-%s_CNY.html#fliterParam=baseCabin-all" %(flyingDate.strftime("%Y"), self.fromCity, self.toCity, flyingDate.strftime("%y%m%d"))

            text = ""
            maxTries = 2
            while maxTries > 0:
                try:
                    driver = self.webDriver
                    driver.get(ChinaEasternSpider.search_url)

                    tries = 3
                    while tries > 0:
                        try:
                            driver.execute_script("document.getElementsByName('tripType')[1].click()")
                            break
                        except UnexpectedAlertPresentException:
                            tries -= 1

                    driver.execute_script("document.getElementsByClassName('input city')[2].value='%s'" %self.fromCity)
                    driver.execute_script("document.getElementsByName('deptCd')[0].value = '%s'" %self.fromValue)
                    driver.execute_script("document.getElementsByName('deptCd')[0].setAttribute('nation', '%s')" %self.fromNation)
                    driver.execute_script("document.getElementsByName('deptCd')[0].setAttribute('region', '%s')" %self.fromRegion)
                    driver.execute_script("document.getElementsByName('deptCd')[0].setAttribute('citycode', '%s')" %self.fromCityCode)

                    driver.execute_script("document.getElementsByClassName('input city')[3].value='%s'" %self.toCity)
                    driver.execute_script("document.getElementsByName('arrCd')[0].value = '%s'" %self.toValue)
                    driver.execute_script("document.getElementsByName('arrCd')[0].setAttribute('nation', '%s')" %self.toNation)
                    driver.execute_script("document.getElementsByName('arrCd')[0].setAttribute('region', '%s')" %self.toRegion)
                    driver.execute_script("document.getElementsByName('arrCd')[0].setAttribute('citycode', '%s')" %self.toCityCode)
                    
                    driver.execute_script("document.getElementsByClassName('input date')[0].value='%s'" %flyingDate.strftime("%Y-%m-%d"))
                    driver.execute_script("document.getElementsByClassName('input date')[1].value='%s'" %flyingDate.strftime("%Y-%m-%d"))

                    time.sleep(2)
                    driver.find_element_by_id("btn_member_search").click()

                    text = self.waitFlight(0)
                except socket.timeout as e:
                    print url, e
                except TimeoutException as e:
                    print url, e

                if text != "":
                    hasTicket = False
                    for ticket in self.flight(text, url, flyingDate):
                        hasTicket = True
                        yield ticket

                    # Choose the back flight
                    if hasTicket:
                        driver.execute_script("document.getElementsByClassName('button lightred')[0].click()")
                        text = self.waitFlight(1)
                        if text != "":
                            for ticket in self.flight(text, url, flyingDate):
                                yield ticket

                    time.sleep(2)
                    maxTries = -1

                maxTries -= 1

            if text == "":
                self.maxTries -= 1
            else:
                self.maxTries += 1

            if self.maxTries < 0:
                print "Exit (maxTries = %d)" %self.maxTries
                break

        self.quitWebDriver()

'''
0 东方航空
1 MU787
2
3
4
5 12:30
6 浦东机场
7 33E
8 19:10
9 菲乌米奇诺机场
10 ¥3410起
11 限制
12
13 赠达人券>
14  经济舱折扣(S舱)
15 ¥3410
16 限制
17
18 须知
19
20 赠达人券>
21  U+随享(J舱)
22 ¥47180
23 限制
24
25 赠达人券>
26  公务舱折扣(非常紧张)(I舱)
27 ¥13990
'''

'''
0 东方航空
1 MU219
2
3
4
5 00:05
6 浦东机场
7 33E
8 06:05
9 法兰克福
10 ¥4010起
11 中转 法兰克福 中间停留4小时10分
12
13 东方航空
14 MU8280
15
16
17
18 10:15
19 法兰克福
20 EMJ
21 11:35
22 阿姆斯特丹
23
24 东方航空
25 MU553
26
27
28
29 00:05
30 浦东机场
31 33H
32 06:30
33 巴黎戴高乐机场
34 ¥4010起
35 中转 巴黎 中间停留5小时10分
36
37 东方航空
38 MU8673
39
40
41
42 11:40
43 巴黎戴高乐机场
44 321
45 12:55
46 阿姆斯特丹
47
48 东方航空
49 MU553
50
51
52
53 00:05
54 浦东机场
55 33H
56 06:30
57 巴黎戴高乐机场
58 ¥4530起
59 中转 巴黎 中间停留2小时20分
60
61 东方航空
62 MU8278
63
64
65
66 08:50
67 巴黎戴高乐机场
68 737
69 10:05
70 阿姆斯特丹
71
72 东方航空
73 MU787
74
75
76
77 12:30
78 浦东机场
79 33E
80 19:10
81 菲乌米奇诺机场
82 ¥4530起
83 中转 罗马 中间停留17小时45分
84
85 东方航空
86 MU8290
87
88
89
90 12:55
91 菲乌米奇诺机场
92 737
93 15:25
94 阿姆斯特丹
95
96 东方航空
97 MU553
98
99
100
101 00:05
102 浦东机场
103 33H
104 06:30
105 巴黎戴高乐机场
106 ¥6930起
107 中转 巴黎 中间停留13小时45分
108
109 东方航空
110 MU8276
111
112
113
114 20:15
115 巴黎戴高乐机场
116 737
117 21:25
118 阿姆斯特丹
119
120 东方航空
121 MU569
122
123
124
125 12:30
126 浦东机场
127 33H
128 19:05
129 巴黎戴高乐机场
130 ¥6930起
131 中转 巴黎 中间停留13小时45分
132
133 东方航空
134 MU8278
135
136
137
138 08:50
139 巴黎戴高乐机场
140 737
141 10:05
142 阿姆斯特丹
143
144 东方航空
145 MU8663
146
147
148
149 10:20
150 浦东机场
151 77W
152 16:35
153 巴黎戴高乐机场
154 ¥6930起
155 中转 巴黎 中间停留3小时40分
156
157 东方航空
158 MU8276
159
160
161
162 20:15
163 巴黎戴高乐机场
164 737
165 21:25
166 阿姆斯特丹
167
168 东方航空
169 MU8663
170
171
172
173 10:20
174 浦东机场
175 77W
176 16:35
177 巴黎戴高乐机场
178 ¥6930起
179 中转 巴黎 中间停留16小时15分
180
181 东方航空
182 MU8278
183
184
185
186 08:50
187 巴黎戴高乐机场
188 737
189 10:05
190 阿姆斯特丹
191
192 东方航空
193 MU8661
194
195
196
197 23:30
198 浦东机场
199 77W
200 05:35
201 巴黎戴高乐机场
202 ¥6930起
203 中转 巴黎 中间停留3小时15分
204
205 东方航空
206 MU8278
207
208
209
210 08:50
211 巴黎戴高乐机场
212 737
213 10:05
214 阿姆斯特丹
215
216 东方航空
217 MU8661
218
219
220
221 23:30
222 浦东机场
223 77W
224 05:35
225 巴黎戴高乐机场
226 ¥6930起
227 中转 巴黎 中间停留14小时40分
228
229 东方航空
230 MU8276
231
232
233
234 20:15
235 巴黎戴高乐机场
236 737
237 21:25
238 阿姆斯特丹
239
240 东方航空
241 MU8273
242
243
244
245 12:15
246 浦东机场
247 74M
248 18:00
249 阿姆斯特丹
250 ¥/起
'''
