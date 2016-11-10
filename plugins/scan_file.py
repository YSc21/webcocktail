from webcocktail.log import get_log
from webcocktail.plugin import Plugin

logger = get_log(__name__)


class ScanFile(Plugin):
    name = __name__
    payload_file = 'payloads/hidden.file'

    def tamper_request(self, payload, request):
        request['url'] += payload
        return request
