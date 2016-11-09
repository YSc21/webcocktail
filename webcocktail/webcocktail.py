import requests
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib import parse
from webcocktail.crawler.spiders.explore import ExploreSpider


class WebCocktail(object):

    def __init__(self, url='', extra_domain=[]):
        self.target = self._check_url(url)
        self.extra_domain = extra_domain
        self.reqs = {requests.get(url)}
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
        for r in self.reqs:
            print('status: %3s, Content-Length: %5s, url: %s' % (r.status_code, r.headers['Content-Length'], r.url))
