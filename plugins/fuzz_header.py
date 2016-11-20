import config
from webcocktail.log import get_log
from webcocktail.plugin import Plugin


class FuzzHeader(Plugin):
    payload_file = config.FUZZHEADER_PAYLOAD
    url = config.URL
    host = config.HOST
    port = config.PORT
    r_port = config.R_PORT

    def tamper_request(self, payload, request):
        request.allow_redirects = False
        request.verify = False
        headers = request.headers

        payload = payload.replace('{HOST}', FuzzHeader.host)
        payload = payload.replace('{PORT}', FuzzHeader.port)
        payload = payload.replace('{URL}', FuzzHeader.url)
        payload = payload.replace('{R_PORT}', FuzzHeader.r_port)
        field, value = payload.split(': ', 1)
        headers[field] = value
        self.log.debug('headers: %s' % (request.headers))
        return request
