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
from webcocktail.log import get_log
from webcocktail.scanner import Scanner


class WebCocktail(object):

    def __init__(self, url='', extra_domain=[]):
        self.log = get_log(self.__class__.__name__)
        self.target = self._check_url(url)
        self.extra_domain = extra_domain
        self.active_pages = []
        self.other_pages = []
        self.scanner = Scanner(self)

        self.crawl(self.target, self.extra_domain)
        self.default_scan()

    def _check_url(self, url):
        if not url.startswith('http') and not url.startswith('https'):
            url = 'http://' + url
        uri = parse.urlparse(url)
        target = '{uri.scheme}://{uri.netloc}/'.format(uri=uri)
        self.log.info('Target: ' + target)
        return target

    def filter_page(self, category, response):
        # TODO: filter existed page
        return response

    def add_page(self, response):
        if response.status_code == 200:
            category = 'active'
            response = self.filter_page(category, response)
        else:
            category = 'other'

        if response:
            self.__dict__[category + '_pages'].append(response)
            return True
        return False

    def crawl(self, target, extra_domain=[]):
        domains = [parse.urlparse(target).netloc] + extra_domain
        kwargs = {'urls': [target], 'allowed_domains': domains}
        if os.path.isfile('crawler.log'):
            os.remove('crawler.log')
        if os.path.isfile('crawler.json'):
            os.remove('crawler.json')
        process = CrawlerProcess(get_project_settings())
        process.crawl(ExploreSpider, **kwargs)
        process.start()
        process.stop()

        with open('crawler.log', 'r') as f:
            lines = f.readlines()
        log = ''.join(lines)
        if 'Error: ' in log:
            raise CrawlerError('There are some errors in crawler. '
                               'Please check up crawler.log')

        # load status code 200 page
        with open('crawler.json', 'r') as f:
            crawled_pages = json.load(f)
        for page in crawled_pages:
            response = requests.request(**page['request'])
            response.comments = page['comments']
            response.hidden_inputs = page['hidden_inputs']
            self.add_page(response)

        # TODO: how to extract 302, 404 in scrapy?
        # load other status code (302, 404, ...) response in crawler.log
        responses = re.findall(
            '(?!.*\(200\).*).*DEBUG:.*\((\d*)\).*<(.*) (.*)> (.*)', log)
        for response in responses:
            if response[0] == '302':
                status_code = response[0]
                method, url = re.findall('.*<(.*) (.*)>.*', response[-1])[0]
            else:
                status_code, method, url, _ = response
            item = ResponseItem()
            item['status_code'] = int(status_code)
            item['request'] = {'method': method, 'url': url}
            response = requests.request(**item['request'])
            # FIXME: response is 200, should be 403
            if not self.add_page(response):
                self.log.warning(
                    'Different request between crawler ans requests')

    def default_scan(self):
        self.scanner.use('default')
        index_page = self.active_pages[0].request
        results = self.scanner.scan(index_page)
        for result in results:
            self.add_page(result)
        return results
        # TODO: save result to self.active_pages

    def show_pages(self):
        # TODO: make it pretty
        pprint(self.active_pages)
        pprint(self.other_pages)
        # for r in self.reqs:
        #     print('status code: %3s, Content-Length: %5s, url: %s' %
        #           (r.status_code, r.headers['Content-Length'], r.url))
