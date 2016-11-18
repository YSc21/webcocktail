import plugins
from webcocktail.log import get_log


class Scanner(object):
    DEFAULT = ['ScanTemp', 'FuzzHeader', 'FuzzParam']

    def __init__(self, webcocktail):
        self.log = get_log(self.__class__.__name__)
        self.webcocktail = webcocktail
        self.plugins = plugins.all_plugins
        self.using = []
        self.log.info('All plugins: %s' % self.plugins)

    def _new_plugin(self, module):
        plugin = module()
        name = plugin.__class__.__name__

        self.plugins[name] = plugin
        index = self.using.index(module)
        self.using[index] = self.plugins[name]
        return plugin

    def use(self, name):
        if name == 'all':
            self.using = [self.plugins[name] for name in self.plugins]
        elif name == 'default':
            self.using = [self.plugins[name] for name in Scanner.DEFAULT]
        elif name in self.plugins:
            self.using.append(self.plugins[name])
        self.log.info('Using plugins: %s' % self.using)

    def disuse(self, name):
        if name == 'all':
            self.using = []
        elif name in self.plugins:
            self.using.remove(self.plugins[name])
            self.log.info('%s is removed' % name)

    def scan(self, request):
        results = []
        for plugin in self.using:
            if type(plugin) is type:
                plugin = self._new_plugin(plugin)
            results.extend(plugin.get_results(request))
        return results

    def scan_all(self, requests):
        results = []
        for request in requests:
            results.extend(self.scan(request))
        return results
