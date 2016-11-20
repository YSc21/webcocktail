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


def send(request):
    session = requests.session()
    if 'requests' in request.headers['User-Agent']:
        request.headers['User-Agent'] = config.USER_AGENT
    response = session.send(request)
    return response
