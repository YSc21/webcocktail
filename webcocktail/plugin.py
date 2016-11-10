import requests
from webcocktail.log import get_log


class Plugin(object):
    def __init__(self):
        self.log = get_log(self.__class__.__name__)
        self._payloads = self.load_payloads()

    def load_payloads(self):
        payloads = []
        filename = self.__class__.payload_file
        with open(filename, 'r') as f:
            for line in f:
                line = line[:-1]
                if line == '' or line[0] == '#':
                    continue
                payloads.append(line)
        return payloads

    @property
    def payloads(self):
        for payload in self._payloads:
            payload = self.hook_payload(payload)
            yield payload

    def get_results(self, request):
        origin_request = request
        results = []
        for payload in self.payloads:
            request = origin_request.copy()
            request = self.hook_request(payload, request)
            response = requests.request(**request)
            self.log.info('{r} {r.url}'.format(r=response))
            response = self.hook_response(payload, response)
            if response:
                results.append(response)
        return results

    def hook_payload(self, payload):
        return payload

    def hook_request(self, payload, request):
        raise NotImplementedError('hook_request is not implemented.')

    def hook_response(self, payload, response):
        if response.status_code != 404:
            return response
        return None
