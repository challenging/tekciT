import scrapy

class SkyScannerSpider(scrapy.Spider):
    name = 'skyscanner'
    #start_urls = ['http://www.skyscanner.com.tw/']

    def start_requests(self):
        return [scrapy.FormRequest(url = "http://www.skyscanner.com.tw/r/Search/",
                                 formdata = {"departure-input": "TPE", "destination-input": "KIX", "prefer-directs": "0", "journey-type": "1", "departure-date-calendar": "140903", "return-date-calendar": "140910"},
                                 method = "POST",
                                 callback=self.ticket)]

    def ticket(self, response):
        #for value in response.xpath("//label[re:test(@for, 'rdoSelectFare(\d+)')]/text()").extract():
        print response.url
