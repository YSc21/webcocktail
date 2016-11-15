import json
import os
from pprint import pprint
import re
import requests
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib import parse
import webcocktail.utils as utils
from webcocktail.crawler.items import ResponseItem
from webcocktail.crawler.spiders.explore import ExploreSpider
from webcocktail.error import CrawlerError
from webcocktail.log import get_log
from webcocktail.scanner import Scanner


class WebCocktail(object):

    def __init__(self, url='', extra_domain=[]):
        self.log = get_log(self.__class__.__name__)
        self.target = utils.check_url(url)
        self.extra_domain = extra_domain
        self.active_pages = []
        self.active_hashes = []
        self.other_pages = []
        self.scanner = Scanner(self)

        self.add_page(requests.get(self.target))
        self.crawl(self.target, self.extra_domain)
        self.default_scan()

    def filter_page(self, category, response):
        hashes = self.__dict__[category + '_hashes']
        new_hash = utils.hash(response.content)
        if new_hash in hashes:
            self.log.info('%s has been in %s_pages' %
                          (response.url, category))
            return None
        else:
            hashes.append(new_hash)
        return response

    def add_page(self, response):
        url = response.url
        if response.status_code == 200:
            category = 'active'
            response = self.filter_page(category, response)
        else:
            category = 'other'

        if response is not None:
            self.__dict__[category + '_pages'].append(response)
        else:
            self.log.warning('Doesn\'t add %s to %s_pages' %
                             (url, category))

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
            if (utils.hash(response.content) !=
                    utils.hash(page['content'].encode())):
                self.log.warning(
                    'Different request %s content '
                    'between crawler and requests' % response.url)
            self.add_page(response)

        # TODO: how to extract 302, 404 in scrapy?
        # load other status code (302, 404, ...) response in crawler.log
        parsed_other = re.findall(
            '(?!.*\(200\).*).*DEBUG:.*\((\d*)\).*<(.*) (.*)> (.*)', log)
        for parsed in parsed_other:
            if parsed[0] == '302':
                status_code = parsed[0]
                method, url = re.findall('.*<(.*) (.*)>.*', parsed[-1])[0]
            else:
                status_code, method, url, _ = parsed
            item = ResponseItem()
            item['status_code'] = int(status_code)
            item['request'] = {'method': method, 'url': url,
                               'allow_redirects': False,
                               'verify': False}
            response = requests.request(**item['request'])
            if response.status_code != item['status_code']:
                self.log.warning(
                    'Different request between crawler and requests')
                self.log.warning(
                    '... %s should be %d but got %d' % (
                        item['request']['url'], item['status_code'],
                        response.status_code)
                )
            self.add_page(response)

    def default_scan(self):
        self.scanner.use('ScanFile')
        index_page = self.active_pages[0].request
        results = self.scanner.scan(index_page)

        self.scanner.use('default')
        requests = [p.request for p in self.active_pages[1:]]
        results.extend(self.scanner.scan_all(requests))

        for result in results:
            self.add_page(result)
        return results

    def show_pages(self):
        # TODO: make it pretty
        pprint(self.active_pages)
        pprint(self.other_pages)
        # for r in self.reqs:
        #     print('status code: %3s, Content-Length: %5s, url: %s' %
        #           (r.status_code, r.headers['Content-Length'], r.url))
