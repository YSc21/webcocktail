import config
import json
import os
from pprint import pprint
import re
import requests
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from subprocess import call
from urllib import parse
from webcocktail.crawler.items import ResponseItem
from webcocktail.crawler.spiders.explore import ExploreSpider
from webcocktail.error import CrawlerError
from webcocktail.log import get_log
from webcocktail.log import print_response
from webcocktail.scanner import Scanner
import webcocktail.utils as utils


class WebCocktail(object):
    CATEGORY = ['active', 'other']

    def __init__(self, url='', extra_url=[], extra_domain=[], debug=False):
        self.log = get_log(self.__class__.__name__)
        self.target = utils.check_url(url)
        self.extra_domain = extra_domain
        self.extra_url = extra_url

        self.active_pages = []
        self.active_hashes = dict()
        self.other_pages = []
        self.scanner = Scanner(self, debug)

        self.extra_url.extend(self.get_robots_disallow(self.target))
        self.crawl(self.target, self.extra_domain)
        self.default_scan()

    def filter_page(self, category, response):
        hashes = self.__dict__[category + '_hashes']
        url = response.url
        new_hash = utils.hash(response.content)

        if (url in hashes and new_hash in hashes[url]):
            self.log.info('%s has been in %s_pages' %
                          (response.url, category))
            return None
        return response

    def add_page(self, response):
        if response.status_code == 200:
            category = 'active'
            response = self.filter_page(category, response)
        else:
            category = 'other'

        if response is not None:
            self.__dict__[category + '_pages'].append(response)
            if category != 'other':
                hashes = self.__dict__[category + '_hashes']
                url = response.url
                new_hash = utils.hash(response.content)
                if url not in hashes:
                    hashes[url] = []
                hashes[url].append(new_hash)
            self.log.info(
                'Found a new response: {r} {r.url}'.format(r=response))

    def get_robots_disallow(self, url):
        self.log.info('===== Checking robots.txt disallow =====')
        ret_urls = []
        if not url.endswith('robots.txt'):
            url += 'robots.txt'
        response = utils.send_url(url=url)
        pages = re.findall('Disallow: (.*)', response.text)
        for page in pages:
            page = page[1:] if page[0] == '/' else page
            self.log.info('Found %s' % self.target + page)
            ret_urls.append(self.target + page)
        return ret_urls

    def crawl(self, target, extra_domain=[]):
        self.log.info('===== crawling =====')
        urls = [target] + self.extra_url
        domains = [parse.urlparse(target).hostname] + extra_domain
        kwargs = {'urls': urls, 'allowed_domains': domains}

        if os.path.isfile(config.CRAWLER_LOG):
            os.remove(config.CRAWLER_LOG)
        if os.path.isfile(config.CRAWLER_RESULT):
            os.remove(config.CRAWLER_RESULT)
        process = CrawlerProcess(get_project_settings())
        process.crawl(ExploreSpider, **kwargs)
        process.start()
        process.stop()

        with open(config.CRAWLER_LOG, 'r') as f:
            lines = f.readlines()
        log = ''.join(lines)
        if 'Error: ' in log:
            raise CrawlerError('There are some errors in crawler. '
                               'Please check up %s' % config.CRAWLER_LOG)

        # load status code 200 page
        with open(config.CRAWLER_RESULT, 'r') as f:
            crawled_pages = json.load(f)
        for page in crawled_pages:
            response = requests.request(**page['request'])
            response.wct_found_by = 'crawler'
            response.wct_comments = page['comments']
            response.wct_hidden_inputs = page['hidden_inputs']
            if (utils.hash(response.content) !=
                    utils.hash(page['content'].encode())):
                self.log.warning(
                    'Different request %s content '
                    'between crawler and requests. '
                    'The url may be dynamic page.' % response.url)
            self.add_page(response)

        # TODO: how to extract 302, 404 in scrapy?
        # load other status code (302, 404, ...) response in config.CRAWLER_LOG
        parsed_other = re.findall(
            '(?!.*\(200\).*).*DEBUG:.*\((\d*)\).*<(.*) (.*)> (.*)', log)
        for parsed in parsed_other:
            if parsed[0] == '302':
                status_code = parsed[0]
                method, url = re.findall('.*<(.*) (.*)>.*', parsed[-1])[0]
            else:
                status_code, method, url, _ = parsed
            response = utils.send_url(method=method, url=url)
            response.wct_found_by = 'crawler'
            if response.status_code != int(status_code):
                self.log.warning(
                    'Different request between crawler and requests: '
                    '%s should be %d but got %d' % (
                        response.url, int(status_code), response.status_code)
                )
            self.add_page(response)

    def default_scan(self):
        self.log.info('===== default scan =====')
        index_request = self.active_pages[0].request

        self.scanner.use('ScanFile')
        results = self.scanner.scan(index_request)
        for result in results:
            self.add_page(result)

        self.scanner.use('default')
        requests = [p.request for p in self.active_pages[1:]]
        results.extend(self.scanner.scan_all(requests))

        for result in results:
            self.add_page(result)
        return results

    def nmap(self, url):
        # TODO: create a plugin
        print('===== nmap %s =====' % url)
        call(['nmap', '-v', '-A', '-Pn', url])
        print()

    def show_pages(self, category='all', filter_function=None, **kwargs):
        if not filter_function:
            def filter_function(response):
                return response
        ret_pages = []
        i = 0
        for define_category in WebCocktail.CATEGORY:
            if category == define_category or category == 'all':
                print('===== %s pages =====' % define_category)
                pages = self.__dict__[define_category + '_pages']
                for response in pages:
                    if filter_function(response) is not None:
                        ret_pages.append(response)
                        print_response(i, response, **kwargs)
                        i += 1
        return ret_pages
