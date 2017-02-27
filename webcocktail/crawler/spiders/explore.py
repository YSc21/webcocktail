# -*- coding: utf-8 -*-
import config
import scrapy
from webcocktail.crawler.items import RequestItem
from webcocktail.crawler.items import ResponseItem
from urllib import parse


class ExploreSpider(scrapy.Spider):
    name = "explore"

    def __init__(self, **kwargs):
        super(ExploreSpider, self).__init__(**kwargs)
        if not self.urls:
            raise ValueError("%s must have an url" % type(self).__name__)
        if not self.allowed_domains:
            raise ValueError("%s must have a domain" % type(self).__name__)
        ExploreSpider.allowed_domains = self.allowed_domains
        self.requested_form = set()

    def _get_input_data(self, attr_input):
        name = attr_input.xpath('@name').extract_first()
        value = attr_input.xpath('@value').extract_first()
        name = '' if name is None else name
        value = '' if value is None else value
        return (name, value)

    def _dict_byte2str(self, d):
        ret = {}
        for key in d:
            value = d.get(key)
            value = value[0] if type(value) is list else value
            ret[key.decode()] = value.decode()
        return ret

    def _get_item(self, response):
        hidden_inputs = response.xpath('//input[@type="hidden"]').extract()
        request = response.request

        request_item = RequestItem()
        request_item['method'] = request.method
        request_item['url'] = request.url
        request_item['headers'] = self._dict_byte2str(request.headers)
        # request_item['cookies'] = self._dict_byte2str(request.cookies)
        # TODO: post json data
        if request.body != b'':
            request_item['data'] = request.body.decode()

        item = ResponseItem()
        item['comments'] = response.xpath('//comment()').extract()
        item['content'] = response.body.decode()
        item['hidden_inputs'] = hidden_inputs
        item['length'] = len(response.body)
        item['request'] = request_item
        item['status_code'] = response.status
        return item

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, headers=config.HEADERS,
                                 callback=self.parse)

    def parse(self, response):
        self.logger.debug('===== %s =====' % response)
        yield self._get_item(response)

        # parse href
        for link in response.xpath('//a/@href'):
            link = link.extract()
            if link:
                next_page = response.urljoin(link)
                req = scrapy.Request(next_page, callback=self.parse)
                yield req

        # parse form
        for form in response.xpath('//form'):
            action = form.xpath('@action').extract_first()
            method = form.xpath('@method').extract_first().upper()
            if not method:
                method = 'GET'
            inputs = form.xpath('.//input')

            formdata_list = list(map(self._get_input_data, inputs))
            formdata_list = list(filter(lambda x: x[0] != '', formdata_list))
            formdata = dict(formdata_list)
            if str(formdata) in self.requested_form:
                continue
            else:
                self.requested_form.add(str(formdata))

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
