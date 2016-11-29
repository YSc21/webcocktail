import config
from webcocktail.plugin import Plugin


class ScanFile(Plugin):
    payload_file = config.SCANFILE_PAYLOAD

    def tamper_request(self, payload, request):
        request.url += payload
        return request
