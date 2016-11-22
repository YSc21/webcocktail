from urllib import parse
from webcocktail.log import get_log
import webcocktail.utils as utils


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

    def filter_response(self, response):
        if response.status_code == 404:
            return None
        return response

    def get_results(self, request):
        origin_request = request
        results = []
        for payload in self.payloads:
            request = origin_request.copy()
            request = utils.get_default_request(request)
            request = self.tamper_request(payload, request)

            requests = request if type(request) is list else [request]
            for request in requests:
                if request is None:
                    self.log.debug(
                        'origin payload: %s and url: %s doesn\'t request'
                        % (payload, origin_request.url))
                    continue
                response = utils.send(request)
                self.log.debug('{r} {r.url}'.format(r=response))

                # also check 302 history
                responses = [response] + response.history
                for response in responses:
                    response.wct_found_by = self.__class__.__name__
                    response.wct_payload = payload
                    response = self.filter_response(response)
                    # use `if response is not None` rather than `if response`
                    # because 403 in `if response` will be False
                    if response is not None:
                        results.append(response)
        return results

    def tamper_payload(self, payload):
        return payload

    def tamper_request(self, payload, request):
        raise NotImplementedError('tamper_request should be implemented.')
