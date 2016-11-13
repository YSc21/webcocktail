# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ResponseItem(scrapy.Item):
    comments = scrapy.Field()
    content = scrapy.Field()
    hidden_inputs = scrapy.Field()
    length = scrapy.Field()
    request = scrapy.Field()
    status_code = scrapy.Field()


class RequestItem(scrapy.Item):
    # all elements are parameters of requests
    method = scrapy.Field()
    url = scrapy.Field()
    params = scrapy.Field()
    data = scrapy.Field()
    json = scrapy.Field()
    headers = scrapy.Field()
    cookies = scrapy.Field()
    files = scrapy.Field()
    auth = scrapy.Field()
    timeout = scrapy.Field()
    allow_redirects = scrapy.Field()
    proxies = scrapy.Field()
    verify = scrapy.Field()
    stream = scrapy.Field()
    cert = scrapy.Field()
