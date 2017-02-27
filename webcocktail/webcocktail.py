import config
import json
from multiprocessing import Process
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
from webcocktail.log import get_log
from webcocktail.log import print_response
from webcocktail.scanner import Scanner
import webcocktail.utils as utils


class WebCocktail(object):
    CATEGORY = ['active', 'other']

    def __init__(self, url='', extra_url=[], extra_domain=[], debug=False,
                 crawl=True, scan=True):
        self.log = get_log(self.__class__.__name__)
        self.target = utils.check_url(url)
        self.extra_domain = extra_domain
        self.extra_url = extra_url

        self.active_pages = []
        self.active_hashes = dict()
        self.other_pages = []
        self.other_hashes = dict()
        self.scanner = Scanner(self, debug)

        self.extra_url.extend(self.get_robots_disallow(self.target))

        if crawl:
            self.crawl(self.target, self.extra_url, self.extra_domain)
        else:
            self.add_page(utils.send_url(url=self.target))

        if scan:
            self.default_scan()
        else:
            self._scan_index()

    def _add_hash(self, category, response):
        hashes = self.__dict__[category + '_hashes']
        url_path, new_hash = utils.get_path_hash(response)

        if url_path not in hashes:
            hashes[url_path] = []
        hashes[url_path].append(new_hash)

    def _add_crawled_page(self, response, page=None, status_code=None):
        response.wct_found_by = 'crawler'
        if page:
            response.wct_comments = page['comments']
            response.wct_hidden_inputs = page['hidden_inputs']
        for r in response.history:
            r.wct_found_by = 'crawler'
        if (page and
                utils.hash(response.content) !=
                utils.hash(page['content'].encode())):
            self.log.warning(
                'Different request %s content '
                'between crawler and requests. '
                'The url may be dynamic page.' % response.url)
            self.log.debug(response.request.headers)
            self.log.debug(page['request']['headers'])
        if (status_code and response.status_code != status_code
                and status_code != 302 and status_code):
            self.log.warning(
                'Different request between crawler and requests: '
                '%s should be %d but got %d' % (
                    response.url, status_code, response.status_code)
            )
        self.add_page(response)

    def _scan_index(self):
        index_request = self.active_pages[0].request

        self.scanner.use('ScanFile')
        results = self.scanner.scan(index_request)
        for result in results:
            self.add_page(result)

    def filter_page(self, category, response):
        hashes = self.__dict__[category + '_hashes']
        url_path, new_hash = utils.get_path_hash(response)

        if url_path in hashes and new_hash in hashes[url_path]:
            self.log.info('%s has been in %s_pages' %
                          (response.url, category))
            return None
        return response

    def add_page(self, response):
        # check history response (302)
        if response.history:
            for r in response.history:
                self.add_page(r)

        if response.status_code == 200:
            category = 'active'
        else:
            category = 'other'
        response = self.filter_page(category, response)

        if response is not None:
            self.__dict__[category + '_pages'].append(response)
            self._add_hash(category, response)
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

    def crawl(self, target, extra_url=[], extra_domain=[]):
        self.log.info('===== Crawling =====')
        urls = [target] + extra_url
        domains = [parse.urlparse(target).hostname] + extra_domain
        kwargs = {'urls': urls, 'allowed_domains': domains}

        if os.path.isfile(config.CRAWLER_LOG):
            os.remove(config.CRAWLER_LOG)
        if os.path.isfile(config.CRAWLER_RESULT):
            os.remove(config.CRAWLER_RESULT)

        def _crawl():
            process = CrawlerProcess(get_project_settings())
            process.crawl(ExploreSpider, **kwargs)
            process.start()
            process.stop()
        p = Process(target=_crawl)
        p.start()
        p.join()

        self.log.info('Parsing crawler log')
        f = open(config.CRAWLER_LOG, 'r')
        for log in f:
            if 'Error: ' in log:
                self.log.critical('There are some errors in crawler. '
                                  'Please check up %s' % config.CRAWLER_LOG)
                self.log.critical(log)
                exit()
            # load other status code 302, 404,.. response in config.CRAWLER_LOG
            parsed_other = re.findall(
                '(?!.*\(200\).*).*DEBUG:.*\((\d*)\).*<(.*) (.*)> (.*)', log)
            for parsed in parsed_other:
                if parsed[0] == '302':
                    status_code = parsed[0]
                    method, url = re.findall('.*<(.*) (.*)>.*', parsed[-1])[0]
                else:
                    status_code, method, url, _ = parsed
                status_code = int(status_code)
                response = utils.send_url(method=method, url=url)
                self._add_crawled_page(response, status_code=status_code)
        f.close()

        # load status code 200 page
        self.log.info('Parsing crawler result')
        try:
            with open(config.CRAWLER_RESULT, 'r') as f:
                crawled_pages = json.load(f)
        except json.decoder.JSONDecodeError:
            self.log.error('Parse json result error')
            crawled_pages = {}
        for page in crawled_pages:
            page['request'].update(config.REQUEST)
            if 'Cookie' in page['request']['headers']:
                cookies = page['request']['headers']['Cookie']
                cookies = dict(parse.parse_qsl(cookies))
                page['request']['cookies'] = cookies
            response = requests.request(**page['request'])
            self._add_crawled_page(response, page=page)

    def default_scan(self):
        self.log.info('===== Default Scan =====')

        self._scan_index()

        self.scanner.use('default')
        # scan active pages
        requests = [p.request for p in self.active_pages]
        results = self.scanner.scan_all(requests)
        for result in results:
            self.add_page(result)
        # scan 302 pages
        pages_302 = [p for p in self.other_pages if p.status_code == 302]
        requests = [p.request for p in pages_302]
        results = self.scanner.scan_all(requests)
        for result in results:
            self.add_page(result)

    def nmap(self, url):
        # TODO: create a plugin
        uri = parse.urlparse(url)
        url = uri.hostname
        print('===== nmap %s =====' % url)
        try:
            call(['nmap', '-v', '-A', '-Pn', url])
        except:
            pass
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
                        print_response(i, response, pages, **kwargs)
                        i += 1
                print()
        return ret_pages
