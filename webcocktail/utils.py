import config
import hashlib
import requests
from urllib import parse
from webcocktail.log import get_log

log = get_log('utils')


def check_url(url):
    if not url.startswith('http') and not url.startswith('https'):
        url = 'http://' + url
    uri = parse.urlparse(url)
    target = '{uri.scheme}://{uri.netloc}/'.format(uri=uri)
    log.info('Url: ' + target)
    return target


def hash(value):
    sha1 = hashlib.sha1()
    sha1.update(value)
    return sha1.hexdigest()


def get_path_hash(response):
    # use url without params, query and fragment
    uri = parse.urlparse(response.url)
    url_path = parse.urlunparse(uri._replace(params='', query='', fragment=''))
    new_hash = hash(response.content)
    return url_path, new_hash


def get_default_request(request):
    for field in config.HEADERS:
        request.headers[field] = config.HEADERS[field]
    return request


def send(request):
    session = requests.session()
    try:
        response = session.send(request, **config.REQUEST)
    except requests.exceptions.ConnectionError:
        log.critical('Can\'t access the website %s' % request.url)
        exit()
    return response


def send_url(method='GET', url=''):
    if not url:
        log.error('Empty url in send_url')
        exit()
    request = {'method': method, 'url': url, 'headers': config.HEADERS}
    request.update(config.REQUEST)
    try:
        response = requests.request(**request)
    except requests.exceptions.ConnectionError:
        log.critical('Can\'t access the website %s' % url)
        exit()
    return response
