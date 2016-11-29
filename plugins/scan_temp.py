import config
from urllib import parse
from webcocktail.plugin import Plugin


class ScanTemp(Plugin):
    payload_file = config.SCANTEMP_PAYLOAD
    ignore_pages = []

    def tamper_request(self, payload, request):
        if request.url in ScanTemp.ignore_pages:
            self.log.debug('Ignore url: %s' % request.url)
            return None
        uri = parse.urlparse(request.url)
        try:
            name, ext = uri.path.split('.')
            name = name.strip('/')
        except (IndexError, ValueError):
            self.log.error('url pathname %s doesn\'t match \{NAME\}.\{EXT\} . '
                           'ignore the url',
                           uri.path)
            ScanTemp.ignore_pages.append(request.url)
            return None
        payload = payload.replace('{PAGE}', name)
        uri = uri._replace(path=payload, params='', query='', fragment='')
        request.url = parse.urlunparse(uri)
        return request
