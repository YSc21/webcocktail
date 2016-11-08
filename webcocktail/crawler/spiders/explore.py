# -*- coding: utf-8 -*-
import scrapy
from urllib import parse


class ExploreSpider(scrapy.Spider):
    name = "explore"
    allowed_domains = ["127.0.0.1"]

    def start_requests(self):
        urls = [
            'http://127.0.0.1/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.logger.debug('===== %s =====' % response)
        # parse href
        for link in response.xpath('//a/@href'):
            link = link.extract()
            if link:
                next_page = response.urljoin(link)
                yield scrapy.Request(next_page, callback=self.parse)

        # parse form
        for form in response.xpath('//form'):
            action = form.xpath('@action').extract_first()
            method = form.xpath('@method').extract_first()
            inputs = form.xpath('input')

            def get_formdata(x):
                name = x.xpath('@name').extract_first()
                value = x.xpath('@value').extract_first()
                name = '' if name is None else name
                value = '' if value is None else value
                return (name, value)

            formdata = dict(list(map(get_formdata, inputs)))

            next_page = response.urljoin(action)
            if method == 'POST':
                req = scrapy.FormRequest(next_page, formdata=formdata,
                                         callback=self.parse)
            else:
                param = parse.urlencode(formdata)
                req = scrapy.Request('%s?%s' % (next_page, param),
                                     callback=self.parse)
            yield req
        self.logger.debug('=== END %s ===' % response)
