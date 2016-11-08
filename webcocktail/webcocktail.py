import requests
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from webcocktail.crawler.spiders.explore import ExploreSpider


class WebCocktail(object):
    def __init__(self, url=None):
        self.target = self._check_url(url)
        self.reqs = {requests.get(url)}
        self.crawl()
        # self.scan()

    def _check_url(self, url):
        url = url + '/' if url[-1] != '/' else url
        print('target: %s' % url)
        return url

    def crawl(self):
        process = CrawlerProcess(get_project_settings())
        process.crawl(ExploreSpider)
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
