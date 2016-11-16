import plugins
from webcocktail.log import get_log


class Scanner(object):
    DEFAULT = ['ScanTemp', 'FuzzHeader']

    def __init__(self, webcocktail):
        self.log = get_log(self.__class__.__name__)
        self.webcocktail = webcocktail
        self.plugins = plugins.all_plugins
        self.using = dict()
        self.log.info('All plugins: %s' % self.plugins)

    def _new_plugin(self, name):
        self.plugins[name] = self.plugins[name]()
        self.using[name] = self.plugins[name]

    def use(self, name):
        if name == 'all':
            self.using = self.plugins
        elif name == 'default':
            items = self.plugins.items()
            self.using.clear()
            self.using.update((k, v) for k, v in items if k in Scanner.DEFAULT)
        elif name in self.plugins:
            self.using[name] = self.plugins[name]
        self.log.info('Plugins: %s is using' % [p for p in self.using])

    def disuse(self, name):
        if name == 'all':
            self.using.clear()
        elif name in self.plugins:
            self.using.pop(name)

    def scan(self, request):
        results = []
        for name in self.using:
            if type(self.using[name]) is type:
                self._new_plugin(name)
            results.extend(self.using[name].get_results(request))
        return results

    def scan_all(self, requests):
        results = []
        for request in requests:
            results.extend(self.scan(request))
        return results
