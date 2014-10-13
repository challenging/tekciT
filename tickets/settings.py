# -*- coding: utf-8 -*-

# Scrapy settings for tickets project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'China Happy New Year'

SPIDER_MODULES = ['tickets.spiders']
NEWSPIDER_MODULE = 'tickets.spiders'

#ITEM_PIPELINES = {
#    "tickets.pipelines.BackpackersPipeline": 11
#}

DUPEFILTER_CLASS = 'tickets.duplicated_filter.SeenURLFilter'

DOWNLOAD_DELAY = 2

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'happy_newyear (+http://www.happynewyear.com)'
