WebCocktail
===========

An automatic and lightweight web application scanning tool for CTF. The first thing you may want to do in CTF web problems. It has some features:

- **crawl** website
- show **web comments** and hidden inputs
- auto **scan hidden files**: .git, .svn, robots.txt, flag.php, phpMyAdmin/, ...
- auto **scan tmp files** for every page: .index.php.swp, SOME_PAGE.php~, ...
- **fuzz header**: X-Forwarded-For, shellshock, ...
- **fuzz parameters**: ', ", SOME_PARAM[]=, ...
- create your own **custom plugins**
- **colorize** information in results
- **diff** same url responses
- **interactive mode** for manipulating requests / responses


Requirements
------------

python3: `pip3 install -r ./requirements.txt`

```
requests==2.13.0
ipython==5.3.0
scrapy==1.3.2
```


Usage
-----

```
$ ./webcocktail.py --help
usage: webcocktail.py [-h] [--cookie cookie] [-debug] [--domain [d [d ...]]]
                      [-no-crawl] [-no-i] [-no-scan] [--urls [u [u ...]]]
                      url

An automatic and lightweight web application scanning tool for CTF.

positional arguments:
  url                   a website which you want to analysis

optional arguments:
  -h, --help            show this help message and exit
  --cookie cookie       set default cookie for requests
  -debug                plugins debug mode
  --domain [d [d ...]]  extra carwler doamins
  -no-crawl             without using default crawl
  -no-i                 without ipython interactive mode
  -no-scan              without using default scan plugin (just using ScanFile
                        plugin)
  --urls [u [u ...]]    other pages which you want to crawl
```

### Example

```
$ ./webcocktail.py http://127.0.0.1/
```

If you need cookies for login, you can add cookies in `--cookie`:

```
./webcocktail.py --cookie PHPSESSID=abc http://127.0.0.1/
```

### Skip plugin / request

You can press `CTRL + C` to skip the plugin or the request:

```
2017-02-28 | Scanner        | INFO | Using plugins: [<class 'scan_temp.ScanTemp'>, <class 'fuzz_header.FuzzHeader'>, <class 'fuzz_param.FuzzParam'>]
2017-02-28 | Scanner        | INFO | Using ScanTemp to scan http://127.0.0.1/
^C
Skip this (p)lugin, (r)equest? p
2017-02-28 | Scanner        | WARNING | Skip: Using ScanTemp to scan http://127.0.0.1/
```

In this example, `Skip this (p)lugin` means you will skip `ScanTemp` but still using `FuzzHeader` and `FuzzParam` to scan `http://127.0.0.1/`. `Skip this (r)equest` means you will skip all plugins to scan `http://127.0.0.1/`.


Interactive mode
----------------

It will pop ipython at the end. You can type `results` to get all scanned responses (the Response object in requests library).

Sometimes you want to rescan / resend a request:

```
IPython Interactive Mode!
You can use `wct.show_pages()` to show scanned pages or using `results` to get responses

In [1]: wct.scanner.using
Out[1]: 
[<scan_temp.ScanTemp at 0x7f4efa398438>,
 <fuzz_header.FuzzHeader at 0x7f4efa3a4b70>,
 <fuzz_param.FuzzParam at 0x7f4efa388ba8>]

In [2]: wct.scanner.disuse('all')

In [3]: wct.scanner.using
Out[3]: []

In [4]: wct.scanner.use('FuzzHeader')
2017-02-28 | Scanner        | INFO | Using plugins: [<fuzz_header.FuzzHeader object at 0x7f4efa3a4b70>]

In [5]: wct.scanner.using
Out[5]: [<fuzz_header.FuzzHeader object at 0x7f4efa3a4b70>]

In [6]: wct.scanner.using[0].log.setLevel('DEBUG')  # debug log if you want

In [7]: wct.scanner.scan(results[3].request)
2017-02-28 | Scanner        | INFO | Using FuzzHeader to scan http://127.0.0.1/action_post.php
2017-02-28 | FuzzHeader     | DEBUG | headers: {'Content-Length': '46', 'Accept-Encoding': 'gzip,deflate', 'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)', 'Referer': 'http://127.0.0.1/', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': '../;q=0.5'}
2017-02-28 | FuzzHeader     | DEBUG | <Response [200]> http://127.0.0.1/action_post.php
...

Out[7]: 
[<Response [200]>,
 <Response [200]>,
 <Response [200]>]
```

### Filter results

The example for finding 'debug.php' in results:

```
In [1]: def f(response):
   ...:     if 'debug.php' in response.url:
   ...:         return response
   ...:     return None
   ...: 

In [2]: wct.show_pages?
Signature: wct.show_pages(category='all', filter_function=None, **kwargs)
Docstring: <no docstring>
File:      ./webcocktail.py
Type:      method

In [3]: results = wct.show_pages(filter_function=f)
```


Plugins
-------

All plugins are in `./plugins/` and each plugin will handle a request at a time. All payloads are in `./payloads/` and a plugin will try all payloads in `payload_file` for a request.

### write a plugin

A simple plugin:

##### ./plugins/my_plugin.py

```
import config
from webcocktail.plugin import Plugin

class MyPlugin(Plugin):
    payload_file = 'payload/my_plugin_payload.txt'

    def tamper_request(self, payload, request):
        request.url += payload
        return request
```

##### ./payloads/my_plugin_payload.txt

```
a.php
b.php
# this is comment. it will not be a payload
c.php
```

> If you use this plugin to scan `http://127.0.0.1/`, it will request `http://127.0.0.1/a.php`, `http://127.0.0.1/b.php` and `http://127.0.0.1/c.php`.

In the simple plugin, we can modify:

- `payload_file` will set payload file. Each line in `payload_file` is a payload and the line started with `#` will be ignored.
- `tamper_request` can add each payload to the request. In this plugin, the parameter `payload` is `a.php`, `b.php` or `c.php` and `request.url` is always `http://127.0.0.1/`. The return value must be a request (python3 `requests.PreparedRequest`), requests (`list`) or `None`. `None` will not be send.

Other functions:

- `tamper_payload`
- `filter_response`
- `load_payloads`


License
-------

MIT