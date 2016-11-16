from urllib import parse
from webcocktail.log import get_log
from webcocktail.plugin import Plugin


class FuzzHeader(Plugin):
    payload_file = 'payloads/header.txt'
    url = 'http://127.0.0.1:8080/'
    host = '127.0.0.1'
    port = '10080'
    r_port = '8080'

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
