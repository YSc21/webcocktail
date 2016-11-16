from webcocktail.log import get_log
from webcocktail.plugin import Plugin


class ScanFile(Plugin):
    payload_file = 'payloads/hidden_file.txt'

    def tamper_request(self, payload, request):
        request.allow_redirects = False
        request.verify = False
        request.url += payload
        return request
