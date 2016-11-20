import config
from webcocktail.log import get_log
from webcocktail.plugin import Plugin


class ScanFile(Plugin):
    payload_file = config.SCANFILE_PAYLOAD

    def tamper_request(self, payload, request):
        request.allow_redirects = False
        request.verify = False
        request.url += payload
        return request
