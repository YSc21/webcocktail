import config
from urllib import parse
from webcocktail.plugin import Plugin


class FuzzParam(Plugin):
    payload_file = config.FUZZPARAM_PAYLOAD

    def _get_payloads(self, query, payload):
        payloads = []
        origin_params = parse.parse_qs(query, keep_blank_values=True)
        origin_payload = payload
        for key in origin_params:
            params = origin_params.copy()
            if '{PARAM}' in origin_payload:
                payload = origin_payload.replace('{PARAM}', key)
                params.pop(key)
                p = parse.urlencode(params, doseq=True)
                p += '&%s' % payload
            else:
                params[key] = origin_payload
                p = parse.urlencode(params, doseq=True)
            p = parse.unquote(p)
            payloads.append(p)
        self.log.debug('payloads: %s' % payloads)
        return payloads

    def _get_query_requests(self, payload, request, uri):
        requests = []
        origin_request = request
        payloads = self._get_payloads(uri.query, payload)
        for payload in payloads:
            request = origin_request.copy()
            uri = uri._replace(query=payload)
            request.url = parse.urlunparse(uri)
            self.log.debug(request.url)
            requests.append(request)
        return requests

    def _get_body_requests(self, payload, request):
        requests = []
        origin_request = request
        payloads = self._get_payloads(request.body, payload)
        for payload in payloads:
            request = origin_request.copy()
            request.prepare_body(payload, None)
            self.log.debug(request.body)
            requests.append(request)
        return requests

    def tamper_request(self, payload, request):
        uri = parse.urlparse(request.url)
        self.log.debug('payload: %s' % payload)

        if uri.query:
            self.log.debug('GET')
            requests = self._get_query_requests(payload, request, uri)
        elif request.body:
            self.log.debug('POST')
            requests = self._get_body_requests(payload, request)
        else:
            requests = None
        return requests
