import config
from urllib import parse
from webcocktail.log import get_log
from webcocktail.plugin import Plugin


class ScanTemp(Plugin):
    payload_file = config.SCANTEMP_PAYLOAD

    def tamper_request(self, payload, request):
        request.allow_redirects = False
        request.verify = False
        uri = parse.urlparse(request.url)
        try:
            name, ext = uri.path.split('.')
            name = name.strip('/')
        except (IndexError, ValueError):
            self.log.error('url pathname %s doesn\'t match \{NAME\}.\{EXT\}',
                           uri.path)
            return None
        payload = payload.replace('{PAGE}', name)
        uri = uri._replace(path=payload)
        request.url = parse.urlunparse(uri)
        return request
