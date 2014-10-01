# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals

import time
import jsonlib2 as json

class BackpackersPipeline(object):
    def __init__(self, settings):
        pass
        #self.file = open("backpackers.%s.j1" %time.strftime("%Y%m%d"), "wb")

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        instance = cls(settings['CUSTOM_SETTINGS_VARIABLE'])
        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        return instance

    def spider_opened(self, spider):
        self.file = open("%s.%s.json" %(spider.name, time.strftime("%Y%m%d")), "ab")

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)

        return item

    def spider_closed(self, spider):
        self.file.close()
