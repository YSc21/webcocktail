import json
import os
from pprint import pprint
import re
import requests
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib import parse
from webcocktail.crawler.items import ResponseItem
from webcocktail.crawler.spiders.explore import ExploreSpider
from webcocktail.error import CrawlerError


class WebCocktail(object):

    def __init__(self, url='', extra_domain=[]):
        self.target = self._check_url(url)
        self.extra_domain = extra_domain
        self.active_pages = []
        self.other_pages = []

        self.crawl(self.target, self.extra_domain)
        # self.scan()

    def _check_url(self, url):
        if not url.startswith('http') and not url.startswith('https'):
            url = 'http://' + url
        uri = parse.urlparse(url)
        target = '{uri.scheme}://{uri.netloc}/'.format(uri=uri)
        print('target: ' + target)
        return target

    def crawl(self, target, extra_domain):
        domains = [parse.urlparse(target).netloc] + extra_domain
        kwargs = {'urls': [target], 'allowed_domains': domains}
        if os.path.isfile('crawler.log'):
            os.remove('crawler.log')
        if os.path.isfile('crawler.json'):
            os.remove('crawler.json')
        process = CrawlerProcess(get_project_settings())
        process.crawl(ExploreSpider, **kwargs)
        process.start()

        # load status code 200 page
        with open('crawler.json', 'r') as f:
            self.active_pages = json.load(f)

        with open('crawler.log', 'r') as f:
            lines = f.readlines()
        log = ''.join(lines)
        if 'Error: ' in log:
            raise CrawlerError('There are some errors in crawler. '
                               'Please check up crawler.log')

        # TODO: how to extract 302, 404 in scrapy?
        # load other status code (302, 404, ...) response in crawler.log
        responses = re.findall(
            '(?!.*\(200\).*).*DEBUG:.*\((\d*)\).*<(.*) (.*)> (.*)', log)
        for response in responses:
            if response[0] == '302':
                status = response[0]
                method, url = re.findall('.*<(.*) (.*)>.*', response[-1])[0]
            else:
                status, method, url, _ = response
            item = ResponseItem()
            item['status'] = int(status)
            item['request'] = {'method': method, 'url': url}
            self.other_pages.append(item)

    def scan(self):
        with open('payload/hidden.file', 'r') as f:
            for path in f:
                path = path.strip()
                if path == '' or path[0] == '#':
                    continue
                r = requests.get(self.target + path)
                if r.status_code != 404:
                    self.reqs.add(r)

    def show_pages(self):
        # TODO: make it pretty
        pprint(self.active_pages)
        pprint(self.other_pages)
        # for r in self.reqs:
        #     print('status: %3s, Content-Length: %5s, url: %s' %
        #           (r.status_code, r.headers['Content-Length'], r.url))
