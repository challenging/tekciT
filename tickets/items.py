# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class AgencyTicket(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    webpage = scrapy.Field()

    agency = scrapy.Field()
    fly = scrapy.Field()
    transfer = scrapy.Field()
    level = scrapy.Field()
    desc = scrapy.Field()
    date = scrapy.Field()
    amount = scrapy.Field()
    url = scrapy.Field()

    crawlingDate = scrapy.Field()

'''
航班    航段    起飛 / 抵達 飛行時間    機型    承運航班    中停    選擇
CI0156  TPE KIX 12-28 08:30/12-28 12:00 02:30   744 CI0156          --
CI0172  TPE KIX 12-28 14:20/12-28 17:50 02:30   333 CI0172          --
CI0158  TPE KIX 12-28 17:25/12-28 20:50 02:25   333 CI0158          --
'''
class ChinaAirlineFlight(scrapy.Item):
    flight = scrapy.Field()
    journey = scrapy.Field()
    flyingDate = scrapy.Field()
    duration = scrapy.Field()
    flightType = scrapy.Field()
    relayStation = scrapy.Field()

'''
1.  行程    TPE - KIX / RT
2.  成人票價    TWD 13035
    小孩票價    TWD 9776
3.  銷售日期    2014/08/15 - 2014/12/31
4.  最少訂票人數    1
5.  預購天數    0
6.  票價出發適用日期    2014/10/11 - 2014/12/31
7.  票價出發適用航班及時間  無限制
8.  票價出發適用星期    日,一,二,三,四,五,六
9.  票價回程適用航班及時間  無限制
10. 票價回程適用星期    日,一,二,三,四,五,六
11. 最少停留天數    0
12. 最大停留天數    1 個月
13. 訂位出發日期    2014-12-28
14. 回程最後使用期限    2015-01-28
15. 搭乘艙等    經濟艙
16. 訂位艙等    去程 M
17. 哩程累積    飛行哩程會因訂位艙等有不同累積比例，請參閱華航/華信哩程累積。查詢航段哩程
18. 選位    可
19. 航點變更    否
20. 機票轉讓    否
21. 退票    可, 退票手續費(每人): TWD700
22. 其他限制/相關手續費 台北(桃園)到大阪 經濟艙來回機票 限2014年10月11日至2014年12月31日出發有效 最少停留0天 最多停留1個月 退票手續費新台幣700改票除FARE RULE需收取之費用外,至CI櫃檯改票另行加收改票手續費在符合可更改之票價規則前提下，根據票價之差異，須支付更改行程或要求退票之相關手續費
'''

class ChinaAirlineTicket(scrapy.Item):
    journey = scrapy.Field()
    priceAdult = scrapy.Field()
    priceChild = scrapy.Field()
    salesDate = scrapy.Field()
    applicableGoDate = scrapy.Field()
    applicableGoFlight = scrapy.Field()
    applicableGoWeek = scrapy.Field()
    applicableBackDate = scrapy.Field()
    applicableBackFlight = scrapy.Field()
    applicableBackWeek = scrapy.Field()
    stayingMinPeriod = scrapy.Field()
    stayingMaxPeriod = scrapy.Field()
    goDate = scrapy.Field()
    backDate = scrapy.Field()
    cabin = scrapy.Field()
    cabinClass = scrapy.Field()
    seat = scrapy.Field()
    changeDestination = scrapy.Field()
    transferredTicket = scrapy.Field()
    allowRefund = scrapy.Field()
    others = scrapy.Field()

    possibleFlight = scrapy.Field()

    crawlingDate = scrapy.Field()

class OnewayTicket(scrapy.Item):
    flightCompany = scrapy.Field()
    fromCity = scrapy.Field()
    toCity = scrapy.Field()
    price = scrapy.Field()
    flyingDate = scrapy.Field()

'''
http://easternmiles.ceair.com/flight2014/jfk-pvg-140915_CNY.html#fliterParam=baseCabin-all
东方航空
MU58816:25
纽约肯尼迪机场34619:15
浦东机场¥4040起
限制赠达人券> 经济舱折扣(N舱)¥4040限制 须知赠达人券> U+随享(紧张)(P舱)¥52020限制赠达人券> 特惠头等舱(紧张)(P舱)¥46820
限制 须知赠达人券> U+随享(J舱)¥64020限制赠达人券> 公务舱折扣(I舱)¥21280
class ChinaEasternTicket(scrapy.Item):
    url = scrapy.Field()
    flight = scrapy.Field()
    company = scrapy.Field()
    fromCity = scrapy.Field()
    toCity = scrapy.Field()
    price = scrapy.Field()
    flyingDate = scrapy.Field()
'''

class ChinaEasternTicket(scrapy.Item):
    url = scrapy.Field()
    company = scrapy.Field()
    fromCity = scrapy.Field()
    toCity = scrapy.Field()
    info = scrapy.Field()
    flyingDate = scrapy.Field()
    price = scrapy.Field()
    flight = scrapy.Field()
    datetimeStart = scrapy.Field()
    datetimeEnd = scrapy.Field()
    transfer = scrapy.Field()

class EvrAirlineTicket(scrapy.Item):
    url = scrapy.Field()
    company = scrapy.Field()
    fromCity = scrapy.Field()
    toCity = scrapy.Field()
    info = scrapy.Field()
    flyingDate = scrapy.Field()
    price = scrapy.Field()
    duration = scrapy.Field()

class PeachTicket(scrapy.Item):
    url = scrapy.Field()
    company = scrapy.Field()
    flight = scrapy.Field()
    fromCity = scrapy.Field()
    toCity = scrapy.Field()
    info = scrapy.Field()
    flyingDate = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    datetimeStart = scrapy.Field()
    datetimeEnd = scrapy.Field()

class JetStarTicket(scrapy.Item):
    url = scrapy.Field()
    company = scrapy.Field()
    fromCity = scrapy.Field()
    toCity = scrapy.Field()
    info = scrapy.Field()
    flyingDate = scrapy.Field()
    price = scrapy.Field()

class CsairTicket(scrapy.Item):
    company = scrapy.Field()
    fromCity = scrapy.Field()
    toCity = scrapy.Field()
    info = scrapy.Field()
    flyingDate = scrapy.Field()
    flight = scrapy.Field()
    datetimeStart = scrapy.Field()
    datetimeEnd = scrapy.Field()
    price = scrapy.Field()

class VanillaAirTicket(scrapy.Item):
    company = scrapy.Field()
    fromCity = scrapy.Field()
    toCity = scrapy.Field()
    flyingDate = scrapy.Field()
    price = scrapy.Field()

class TigerAirTicket(scrapy.Item):
    company = scrapy.Field()
    flight = scrapy.Field()
    fromCity = scrapy.Field()
    toCity = scrapy.Field()
    price = scrapy.Field()
    flyingDate = scrapy.Field()
    datetimeStart = scrapy.Field()
    datetimeEnd = scrapy.Field()
    isTransferred = scrapy.Field()
