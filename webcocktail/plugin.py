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
            payload = self.tamper_payload(payload)
            yield payload

    def get_results(self, request):
        origin_request = request
        results = []
        for payload in self.payloads:
            session = requests.session()
            request = origin_request.copy()
            request = self.tamper_request(payload, request)
            response = session.send(request)
            self.log.info('{r} {r.url}'.format(r=response))

            response = self.filter_response(payload, response)
            if response:
                results.append(response)
        return results

    def tamper_payload(self, payload):
        return payload

    def tamper_request(self, payload, request):
        raise NotImplementedError('tamper_request should be implemented.')

    def filter_response(self, payload, response):
        if response.status_code != 404:
            return response
        return None
